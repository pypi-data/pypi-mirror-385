"""
Utilidades para Django Dynamic Paginator.
"""

from django.db import models
from typing import Dict, Any, Set, Optional, List
from .exceptions import ModelNotFoundError, InvalidFieldError


def get_model_field_names(model: models.Model) -> Set[str]:
    """
    Obtiene los nombres de campos de un modelo Django.
    
    Args:
        model: Modelo Django del cual obtener los campos
        
    Returns:
        Set de nombres de campos del modelo
        
    Raises:
        ModelNotFoundError: Si el objeto no es un modelo Django válido
    """
    if not hasattr(model, '_meta'):
        raise ModelNotFoundError(f"El objeto {model} no es un modelo Django válido")
    
    return {f.name for f in model._meta.get_fields()}


def build_fk_mapping(model: models.Model) -> Dict[str, str]:
    """
    Construye el mapeo automático de ForeignKeys.
    
    Mapea nombres de campos ForeignKey a sus campos _id correspondientes.
    Ejemplo: 'user' -> 'user_id'
    
    Args:
        model: Modelo Django del cual generar el mapeo
        
    Returns:
        Diccionario con el mapeo {field_name: field_name_id}
        
    Raises:
        ModelNotFoundError: Si el objeto no es un modelo Django válido
    """
    if not hasattr(model, '_meta'):
        raise ModelNotFoundError(f"El objeto {model} no es un modelo Django válido")
    
    fk_mapping = {}
    for field in model._meta.get_fields():
        if (hasattr(field, 'related_model') and 
            hasattr(field, 'many_to_one') and 
            field.many_to_one and 
            not field.one_to_one):
            fk_mapping[field.name] = f"{field.name}_id"
    
    return fk_mapping


def validate_model_fields(model: models.Model, fields: List[str]) -> bool:
    """
    Valida que una lista de campos exista en el modelo.
    
    Args:
        model: Modelo Django a validar
        fields: Lista de nombres de campos a verificar
        
    Returns:
        True si todos los campos son válidos
        
    Raises:
        InvalidFieldError: Si algún campo no existe en el modelo
    """
    if not fields:
        return True
        
    model_fields = get_model_field_names(model)
    invalid_fields = []
    
    for field in fields:
        # Permitir campos relacionados (con __)
        if '__' in field:
            base_field = field.split('__')[0]
            if base_field not in model_fields:
                invalid_fields.append(field)
        elif field not in model_fields:
            invalid_fields.append(field)
    
    if invalid_fields:
        raise InvalidFieldError(
            f"Los campos {invalid_fields} no existen en el modelo {model.__name__}"
        )
    
    return True


def validate_serializer_fields(serializer_class, only_fields: Optional[List[str]] = None) -> bool:
    """
    Valida que los campos de only_fields existan en el serializer.
    
    Args:
        serializer_class: Clase del serializador DRF
        only_fields: Lista de campos a validar
        
    Returns:
        True si todos los campos son válidos
        
    Raises:
        InvalidFieldError: Si algún campo no existe en el serializer
    """
    if not only_fields:
        return True
    
    try:
        # Crear instancia temporal del serializer para obtener campos
        serializer_instance = serializer_class()
        serializer_fields = set(serializer_instance.get_fields().keys())
        only_fields_set = set(only_fields)
        
        invalid_fields = only_fields_set - serializer_fields
        if invalid_fields:
            raise InvalidFieldError(
                f"Los campos {invalid_fields} no existen en {serializer_class.__name__}"
            )
        
        return True
    except Exception as e:
        if isinstance(e, InvalidFieldError):
            raise
        raise InvalidFieldError(f"Error validando serializer {serializer_class.__name__}: {e}")


def clean_filter_value(value: Any) -> Any:
    """
    Limpia y normaliza valores de filtros.
    
    Args:
        value: Valor del filtro a limpiar
        
    Returns:
        Valor limpio y normalizado
    """
    if isinstance(value, str):
        # Limpiar espacios en blanco
        value = value.strip()
        
        # Convertir strings boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Convertir strings numéricos
        if value.isdigit():
            return int(value)
        
        try:
            return float(value)
        except ValueError:
            pass
    
    return value


def build_search_query_parts(search_query: str, search_fields: List[str]) -> Dict[str, str]:
    """
    Construye las partes de una consulta de búsqueda.
    
    Args:
        search_query: Término de búsqueda
        search_fields: Lista de campos donde buscar
        
    Returns:
        Diccionario con los filtros de búsqueda construidos
    """
    if not search_query or not search_fields:
        return {}
    
    search_filters = {}
    for field in search_fields:
        search_filters[f"{field}__icontains"] = search_query
    
    return search_filters