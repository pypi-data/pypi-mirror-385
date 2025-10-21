
"""
Los servicios en DDD son responsables de manejar la lógica de negocio 
y las operaciones CRUD relacionadas con una entidad específica. 
Este servicio proporciona métodos para listar, contar, crear, recuperar, actualizar y eliminar instancias de la entidad entity1. 
Cada método maneja la validación necesaria y utiliza un repositorio para interactuar con la persistencia de datos.
son utiles para:
- Centralizar la lógica de negocio relacionada con una entidad.
- Facilitar la reutilización de código en diferentes partes de la aplicación.
- Proporcionar una interfaz clara para interactuar con las entidades.
- Facilitar la implementación de patrones como CQRS (Command Query Responsibility Segregation).
- Permitir la separación de preocupaciones entre la lógica de negocio y la persistencia de datos.
- Facilitar la implementación de pruebas unitarias y de integración.
- Facilitar la gestión de transacciones y la consistencia de datos.
- Permitir la implementación de reglas de negocio complejas que pueden involucrar múltiples entidades o servicios.
- Facilitar la implementación de patrones de diseño como el patrón de servicio, unidad de trabajo, repositorio, etc.
- Proporcionar una interfaz coherente para interactuar con diferentes tipos de almacenamiento de datos (por ejemplo, bases de datos, servicios web, etc.).
"""

from typing import List, Optional

# importa las entidades utilizadas aqui
from ..domain.entities import Entity1Entity

# importa las excepciones utilizadas aqui
from ..domain.exceptions import (
    Entity1ValueError,
    Entity1ValidationError,
    Entity1AlreadyExistsError,
    Entity1NotFoundError,
    Entity1OperationNotAllowedError,
    Entity1PermissionError
)
from ..infrastructure.exceptions import RepositoryError, ConnectionDataBaseError

# importa los repositorios utilizados aqui
from ..infrastructure.entity1_repository import Entity1Repository

class Entity1Service:
    """
    Servicio para manejar las operaciones CRUD relacionadas con entity1.

    Métodos disponibles:
        - list: Lista todas las instancias de entity1.
        - count_all: Cuenta todas las instancias de entity1.
        - create: Crea una nueva instancia de entity1.
        - retrieve: Recupera una instancia de entity1 por ID.
        - update: Actualiza una instancia existente de entity1.
        - delete: Elimina una instancia de entity1.
    """

    #Si necesitas mantener un estado de lista de entidades
    # entity1_list = []    


    def __init__(self, repository: Optional[ Entity1Repository ] = None):
        """
        Inicializa el servicio con el repositorio correspondiente.

        params:
            repository: Repositorio que maneja la persistencia de entity1.
        """

        self.repository = repository or Entity1Repository()


    def list(self, filters: Optional[dict] = None) -> List[dict]:
        """
        Lista instancias de entity1.

        params:
            filters: Filtros opcionales para la consulta.
        return: 
            Lista de la entidad
        raises:
            Entity1ValueError:  Si el valor de entrada no es válido.
            ConnectionDataBaseError: Si hay un error al conectar a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).
        """

        entity_list = self.repository.get_all(filters=filters)

        return [entity.to_dict() for entity in entity_list]      


    def count_all(self, filters: Optional[dict] = None) -> int:
        """
        Cuenta todas las instancias de entity1.

        param: 
            filters: Filtros opcionales para la consulta.
        return: 
            Número total de instancias.
        raises: 
            Entity1ValueError:  Si el valor de entrada no es válido.
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.       
            RepositoryError: Si ocurre un error inesperado (interno del sistema).             
        """

        return self.repository.count_all(filters=filters)


    def create(self, data, external_id: Optional[int]=None, externals: Optional[List[int]]=None, adicionalData=None) -> dict:
        """
        Crea una nueva instancia de entity1.

        params: 
            data: Diccionario o DTO con los datos necesarios para crear la instancia.
            external_id: ID del padre si es necesario (opcional).
            externals: Lista de IDs de entidades relacionadas (opcional).
            adicionalData: Datos adicionales a incluir en la creación.
        return: 
            La entidad creada.
        raises: 
            Entity1ValueError: Si el valor de entrada no es válido.
            Entity1ValidationError: Si los datos no son válidos.
            Entity1AlreadyExistsError: Si ya existe un registro con el mismo nombre.            
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).            
        """

        # Validación de reglas de negocio (opcional)
        if self.repository.exists_by_field(field_name="attributeName", value=data.get("attributeName")):
            raise Entity1ValueError(field="attributeName", detail="An instance with this attributeName already exists")

        #crear y validar la entidad
        entity = Entity1Entity.from_dict(data)
        entity.validate()       

        # Guardar en el repositorio
        saved_entity = self.repository.create(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

        return saved_entity.to_dict()


    def retrieve(self, entity_id: int = None, entity_uuid: str = None) -> dict:
        """
        Recupera una instancia de entity1 por su ID o UUID.

        param: 
            entity_id: ID de la instancia a recuperar.
            entity_uuid: UUID de la instancia a recuperar.
        return: 
            La entidad recuperada.
        raises:
            Entity1ValueError: Si el valor de entrada no es válido.         
            Entity1NotFoundError: Si no existe el registro con el ID dado.
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).
        """

        entity = self.repository.get_by_id(id=entity_id, uuid=entity_uuid)

        return entity.to_dict()


    def update(self, entity_id: int = None, entity_uuid: str = None, data = None, external_id: Optional[int]=None, externals: Optional[List[int]]=None, adicionalData=None) -> dict:
        """
        Actualiza una instancia existente de entity1.

        params:
            entity_id: ID de la instancia a actualizar.
            entity_uuid: UUID de la instancia a actualizar.
            data: Diccionario o DTO con los datos a actualizar.
            external_id: ID del padre si es necesario (opcional).
            externals: Lista de IDs de entidades relacionadas (opcional).
            adicionalData: Datos adicionales a incluir en la actualización.
        return: 
            La entidad actualizada.
        raises: 
            Entity1NotFoundError: Si no existe el registro con el ID dado.
            Entity1ValueError: Si el valor de entrada no es válido.                 
            Entity1ValidationError: Si los datos no son válidos.            
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).
        """
        # Validación de entrada
        if not entity_id and not entity_uuid:
            raise Entity1ValueError(field="id/uuid", detail="The id or uuid field is required")
        
        if not data:
            raise Entity1ValueError(field="data", detail="The data field is required")

        # Recuperar la entidad
        entity = self.repository.get_by_id(id=entity_id, uuid=entity_uuid)

        if not entity:
            raise Entity1NotFoundError(id=entity_id or entity_uuid)

        # actualizar la instancia y validar
        entity.update(data)     
        entity.validate()   

        # Guardar en el repositorio
        updated_entity = self.repository.update(entity=entity, external_id=external_id, externals=externals, adicionalData=adicionalData)

        return updated_entity.to_dict()


    def delete(self, entity_id: int = None, entity_uuid: str = None) -> bool:
        """
        Elimina una instancia de entity1.

        params:
            entity_id: ID de la instancia a eliminar.
            entity_uuid: UUID de la instancia a eliminar.
        return: 
            True/False (depende del exito de la operacion)
        raises:
            Entity1NotFoundError: Si no se encuentra la instancia.
            Entity1ValueError: Si el valor de entrada no es válido.
            Entity1ValidationError: Si los datos no son válidos.            
            ConnectionDataBaseError: Si ocurre un error al acceder a la base de datos.
            RepositoryError: Si ocurre un error inesperado (interno del sistema).            
        """
        # Validación de entrada
        if not entity_id and not entity_uuid:
            raise Entity1ValueError(field="id/uuid", detail="The id or uuid field is required")

        # Eliminación en el repositorio
        self.repository.delete(id=entity_id, uuid=entity_uuid)

        return True
