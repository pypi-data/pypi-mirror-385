# utils/mappers.py
import decimal
from typing import Type, TypeVar, Any
from django.db import models
from ..domain.exceptions import [[ entity_name.capitalize() ]]ValueError
from ..domain.schemas import FileData

T = TypeVar("T", bound=BaseModel)

class Mapper:

    @staticmethod
    def model_to_entity(model_instance: models.Model, entity_class: Type[T]) -> T:
        """Convierte modelo Django → entidad Pydantic con validación y submodelos"""
        
        if not model_instance:
            raise PromotionValueError("Model_instance_cannot_be_None_Cannot_convert_None_to_entity")

        data = {}

        for field_name, field_info in entity_class.model_fields.items():
            model_field_name = field_info.alias or field_name

            if not hasattr(model_instance, model_field_name):
                # Usar default si está definido
                if field_info.default_factory:
                    data[field_name] = field_info.default_factory()
                elif field_info.default is not None:
                    data[field_name] = field_info.default
                continue

            value = getattr(model_instance, model_field_name)
            field_object = None
            try:
                field_object = model_instance._meta.get_field(model_field_name)
            except Exception:
                pass

            # ManyToMany
            if isinstance(value, models.Manager):
                value = list(value.values_list('pk', flat=True)) if value else []

            # ForeignKey / OneToOne
            elif hasattr(value, 'pk') and value is not None:
                value = value.pk

            # Archivos
            elif field_object and isinstance(field_object, (models.FileField, models.ImageField)):
                try:
                    if value and value.name and hasattr(value, 'url'):
                        file_info = {"file_name": value.name, "url": value.url}
                        if field_info.annotation == FileData:
                            value = FileData(**file_info)
                        else:
                            value = file_info
                    else:
                        value = None
                except (ValueError, AttributeError):
                    value = None

            # Decimal → float
            elif isinstance(value, decimal.Decimal):
                value = float(value)

            # Submodelos Pydantic
            elif isinstance(field_info.annotation, type) and issubclass(field_info.annotation, BaseModel):
                if isinstance(value, dict):
                    value = field_info.annotation.model_validate(value)

            data[field_name] = value

        return entity_class.model_validate(data)    

    @staticmethod
    def entity_to_dict(entity_instance: BaseModel) -> dict:
        """Convierte una entidad Pydantic a diccionario"""
        return entity_instance.model_dump()

    @staticmethod
    def model_to_dict(model_instance: models.Model) -> dict:
        """Convierte modelo Django → dict (sin pasar por entidad)"""
        # Tu implementación actual aquí (no cambia)
        data = {}
        for field in model_instance._meta.get_fields():
            try:
                value = getattr(model_instance, field.name)
                if isinstance(field, models.ManyToManyField):
                    data[field.name] = list(value.values_list('pk', flat=True))
                elif isinstance(field, models.ForeignKey) and value:
                    data[field.name] = value.pk
                else:
                    data[field.name] = value
            except (AttributeError, ValueError):
                continue
        return data


        
