"""
SimpleDynamicPaginatorService - Paginador dinámico optimizado para Django REST Framework.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q, F
from typing import List, Optional, Dict, Any
from .utils import get_model_field_names, build_fk_mapping, validate_model_fields
from .exceptions import PaginatorError, InvalidFilterError, ModelNotFoundError


class SimpleDynamicPaginatorService:
    """
    Paginador dinámico que construye el queryset desde cero con múltiples opciones de filtrado.
    
    Este paginador está optimizado para construir consultas eficientes con soporte para:
    - Filtros base (account_by, status, etc.)
    - Q objects complejos para consultas avanzadas (_q_filter)
    - Exclusiones (exclude_id, exclude_status, etc.)
    - Combinación inteligente de filtros de la misma tabla relacionada (evita dobles JOINs)
    - Rango de fechas dinámico
    - Filtros permitidos definidos
    - Búsqueda en múltiples campos
    - Ordenamiento personalizable
    - Optimizaciones con select_related y prefetch_related
    - Optimización only() para campos específicos
    - Opción para devolver todos los resultados sin paginación
    
    Args:
        model: Modelo de Django sobre el que se realizará la consulta
        serializer_class: Clase del serializador DRF para los resultados
        search_fields (list): Lista de campos donde se aplicará la búsqueda
        page_size (int): Número de elementos por página (default: 50)
        allowed_filters (list): Lista de campos permitidos para filtrado dinámico
        select_related (list): Lista de campos ForeignKey para optimizar con JOIN
        prefetch_related (list): Lista de relaciones Many-to-Many para optimizar
        only_fields (list): Lista de campos específicos a cargar (optimización SQL SELECT)
        allow_unlimited (bool): Permite desactivar la paginación via query param (default: False)
    """
    
    def __init__(self, model, serializer_class, search_fields=None, page_size=50, allowed_filters=None, 
                 select_related=None, prefetch_related=None, only_fields=None, allow_unlimited=False):
        
        # Validar que el modelo sea válido
        if not hasattr(model, '_meta'):
            raise ModelNotFoundError(f"El objeto {model} no es un modelo Django válido")
        
        self.model = model
        self.serializer_class = serializer_class
        self.search_fields = search_fields or []
        self.page_size = page_size
        self.allowed_filters = allowed_filters or []
        self.select_related = select_related or []
        self.prefetch_related = prefetch_related or []
        self.only_fields = only_fields or []
        self.allow_unlimited = allow_unlimited
        
        # Validar campos del modelo
        if self.search_fields:
            validate_model_fields(model, self.search_fields)
        
        # Pre-calcular campos del modelo una sola vez para optimización
        self.model_field_names = get_model_field_names(model)
        self.valid_sort_fields = self.model_field_names.union({'id', 'pk'})
        
        # Auto-detectar ForeignKeys para mapeo automático
        self.fk_mapping = build_fk_mapping(model)
    
    def handle_request(self, request, **base_filters):
        """
        Construye y ejecuta la consulta con todos los filtros aplicados.
        
        El orden de aplicación de los filtros es:
        1. Filtros base (obligatorios como account_by) o Q objects complejos
        2. Combinación inteligente de filtros relacionados (evita dobles JOINs)
        3. Exclusiones (exclude_id, exclude_status, etc.)
        4. Optimizaciones de consulta (select_related, prefetch_related, only)
        5. Filtros de rango de fechas
        6. Filtros dinámicos permitidos
        7. Filtros de tipo _in (para múltiples valores)
        8. Búsqueda en campos específicos
        9. Ordenamiento
        10. Paginación (opcional según query param 'unlimited')
        
        Args:
            request: Objeto HttpRequest de Django
            **base_filters: Filtros base que siempre se aplican
                - Filtros normales: account_by=account, status=1, etc.
                - Filtros relacionados: group_unit__group_id=2, group_unit__account_id=3 (se combinan automáticamente)
                - Filtros Q objects: _q_filter=Q(...) para consultas complejas
                - Exclusiones: exclude_id=5 se convierte en .exclude(id=5)
            
        Query Parameters:
            unlimited (str): Si es 'true', devuelve todos los resultados sin paginación
            search (str): Término de búsqueda para search_fields
            sortBy (str): Campo por el cual ordenar
            sortDesc (str): 'true' para orden descendente
            startDate (str): Fecha de inicio para filtrado de fechas
            endDate (str): Fecha fin para filtrado de fechas
            field_date (str): Campo de fecha a usar (default: 'created_at')
            
        Returns:
            Response: Respuesta HTTP paginada o lista completa según el parámetro 'unlimited'
        """
        
        try:
            # 1. Separar filtros normales, exclusiones, Q objects y combinar filtros de misma tabla
            normal_filters = {}
            exclude_filters = {}
            q_filter = None
            related_filters = {}  # Agrupar filtros por tabla relacionada
            
            for key, value in base_filters.items():
                if key.startswith('exclude_'):
                    # Remover el prefijo 'exclude_' del nombre del campo
                    field_name = key.replace('exclude_', '', 1)
                    exclude_filters[field_name] = value
                elif key == '_q_filter':
                    # Soporte para Q objects
                    q_filter = value
                elif '__' in key:
                    # Detectar filtros de tablas relacionadas
                    relation = key.split('__')[0]
                    if relation not in related_filters:
                        related_filters[relation] = {}
                    field = key.split('__', 1)[1]
                    related_filters[relation][field] = value
                else:
                    normal_filters[key] = value
            
            # 2. Combinar TODOS los filtros en una sola operación (evita dobles JOINs)
            all_filters_combined = Q()
            
            # Agregar filtros normales
            if normal_filters:
                for field, value in normal_filters.items():
                    all_filters_combined &= Q(**{field: value})
            
            # Agregar filtros relacionados combinados por tabla
            for relation, relation_filters in related_filters.items():
                # Combinar todos los filtros de la misma relación en un solo Q object
                relation_q = Q()
                for field, value in relation_filters.items():
                    relation_q &= Q(**{f"{relation}__{field}": value})
                all_filters_combined &= relation_q
            
            # Aplicar Q filter si existe
            if q_filter:
                all_filters_combined &= q_filter
            
            # Una sola llamada a filter() con todos los filtros combinados
            if all_filters_combined:
                queryset = self.model.objects.filter(all_filters_combined)
                if q_filter:  # Si hay Q objects complejos, agregar distinct
                    queryset = queryset.distinct()
            else:
                queryset = self.model.objects.all()
            
            # 3. Aplicar exclusiones
            if exclude_filters:
                queryset = queryset.exclude(**exclude_filters)
            
            # 4. Solo aplicar optimizaciones de consulta si son necesarias
            search_query = request.query_params.get('search', '').strip()
            has_relationships = bool(self.select_related or self.prefetch_related)
            
            if has_relationships:
                if self.select_related:
                    queryset = queryset.select_related(*self.select_related)
                if self.prefetch_related:
                    queryset = queryset.prefetch_related(*self.prefetch_related)
            
            # Aplicar only() después de select_related para evitar conflictos
            # only() solo si no hay búsqueda (search puede necesitar otros campos)
            if self.only_fields and not search_query:
                queryset = queryset.only(*self.only_fields)
            
            # 5. Filtros de fecha dinámicos
            fecha_inicio = request.query_params.get('startDate')
            fecha_fin = request.query_params.get('endDate')
            campo_fecha = request.query_params.get('field_date', 'created_at')
            
            if fecha_inicio:
                queryset = queryset.filter(**{f"{campo_fecha}__gte": fecha_inicio})
            if fecha_fin:
                queryset = queryset.filter(**{f"{campo_fecha}__lte": fecha_fin})
            
            # 6. Filtros permitidos dinámicos con combinación inteligente de relaciones
            allowed_related_filters = {}  # Agrupar filtros relacionados de query params
            
            for key, value in request.query_params.items():
                if key in self.allowed_filters and value:
                    
                    if '__' in key:
                        # Filtro relacionado desde query params
                        relation = key.split('__')[0]
                        if relation not in allowed_related_filters:
                            allowed_related_filters[relation] = {}
                        field = key.split('__', 1)[1]
                        allowed_related_filters[relation][field] = value
                    elif key in self.fk_mapping:
                        # Mapear automáticamente ForeignKey: 'assigned_technician' -> 'assigned_technician_id'
                        filter_field = self.fk_mapping[key]
                        queryset = queryset.filter(**{filter_field: value})
                    elif key in ['status', 'priority', 'id'] or key.endswith('_id'):
                        # Campos numéricos - coincidencia exacta (sin mapeo automático)
                        queryset = queryset.filter(**{key: value})
                    else:
                        # Campos de texto - búsqueda parcial
                        queryset = queryset.filter(**{f"{key}__icontains": value})
            
            # Aplicar filtros relacionados combinados de query params (evita dobles JOINs)
            for relation, relation_filters in allowed_related_filters.items():
                combined_q = Q()
                for field, value in relation_filters.items():
                    combined_q &= Q(**{f"{relation}__{field}": value})
                queryset = queryset.filter(combined_q)
            
            # 7. Filtros _in dinámicos más eficientes (aplicar todos juntos)
            in_filters = {}
            for key, value in request.query_params.items():
                if key.endswith('_in') and value:
                    field_name = key.rsplit('_in', 1)[0]
                    value_list = [v.strip() for v in value.split(',') if v.strip()]
                    if value_list:
                        in_filters[f"{field_name}__in"] = value_list
            
            if in_filters:
                queryset = queryset.filter(**in_filters)
            
            # 8. Búsqueda automática desde query_params con Q objects mejorados
            if search_query and self.search_fields:
                if len(self.search_fields) == 1:
                    queryset = queryset.filter(**{f"{self.search_fields[0]}__icontains": search_query})
                else:
                    # Construir Q objects de forma más eficiente
                    q_objects = [Q(**{f"{field}__icontains": search_query}) for field in self.search_fields]
                    combined_q = Q()
                    for q_obj in q_objects:
                        combined_q |= q_obj
                    queryset = queryset.filter(combined_q)
            
            # 9. Ordenamiento con validación de campos
            sort_by = request.query_params.get('sortBy')
            sort_desc = request.query_params.get('sortDesc', 'false').lower() == 'true'
            
            if sort_by:
                # Validar que el campo de ordenamiento existe usando campos pre-calculados
                if sort_by in self.valid_sort_fields or '__' in sort_by:
                    
                    # Limpiar cualquier ordenamiento previo
                    queryset = queryset.order_by()
                    
                    # Manejar campos que pueden ser NULL (como last_login)
                    if 'last_login' in sort_by:
                        if sort_desc:
                            # DESC NULLS LAST: usuarios con login más reciente primero, NULL al final
                            queryset = queryset.order_by(F(sort_by).desc(nulls_last=True))
                        else:
                            # ASC NULLS LAST: usuarios con login más antiguo primero, NULL al final
                            queryset = queryset.order_by(F(sort_by).asc(nulls_last=True))
                    else:
                        # Ordenamiento normal para otros campos
                        order = f"{'-' if sort_desc else ''}{sort_by}"
                        try:
                            queryset = queryset.order_by(order)
                        except Exception:
                            # Si el campo no es válido para ordenamiento, usar default
                            queryset = queryset.order_by('-id')
                else:
                    # Campo no válido, usar ordenamiento default
                    queryset = queryset.order_by('-id')
            else:
                queryset = queryset.order_by('-id')
            
            # 10. Verificar si se debe omitir la paginación
            unlimited = request.query_params.get('unlimited', 'false').lower() == 'true'
            
            if self.allow_unlimited and unlimited:
                # Devolver todos los resultados sin paginación
                serializer = self.serializer_class(queryset, many=True)
                return Response({
                    'results': serializer.data,
                    'count': len(serializer.data),
                    'unlimited': True
                })
            
            # 11. Paginación normal
            paginator = PageNumberPagination()
            paginator.page_size = self.page_size
            
            result_page = paginator.paginate_queryset(queryset, request)
            
            # 12. Serialización
            serializer = self.serializer_class(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            # Re-lanzar excepciones específicas del paginador
            if isinstance(e, (PaginatorError, InvalidFilterError, ModelNotFoundError)):
                raise
            
            # Convertir otras excepciones en PaginatorError
            raise PaginatorError(f"Error en paginador: {str(e)}") from e