# Copyright Wenceslaus Mumala 2023. See LICENSE file.

import enum
import uuid
from abc import abstractmethod

from django.db import models

from laibon import common
from laibon import exception


class BaseModel(models.Model):
    """Base Django model with UUID primary key.
    
    All Laibon models should inherit from this to ensure consistent
    UUID-based identification across the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Adapter(object):
    """Abstract adapter pattern for converting between domain objects and Django models.
    
    Provides a clean separation between business logic and persistence layer.
    Subclasses must implement to_model() and get_model_class().
    
    Example:
        class UserAdapter(Adapter):
            def __init__(self, entity_id=None, name=None, email=None):
                super().__init__(entity_id)
                self.name = name
                self.email = email
            
            def to_model(self, existing=None):
                if existing:
                    existing.name = self.name
                    existing.email = self.email
                    return existing
                return UserModel(name=self.name, email=self.email)
            
            def get_model_class(self):
                return UserModel
    """
    
    def __init__(self, entity_id: str = None):
        self._model_instance = None
        if entity_id:  # check that id is valid uuid
            uuid.UUID(entity_id)

        self._id = entity_id

    def from_model(self, model_instance: BaseModel):
        """Create adapter from existing model instance.
        
        Args:
            model_instance: Django model instance to wrap
        """
        self._id = str(model_instance.id)
        self._model_instance = model_instance

    def get_id(self):
        """Return the entity ID as string."""
        return self._id

    @abstractmethod
    def to_model(self, existing: models.Model = None) -> models.Model:
        """Convert adapter to Django model for persistence.
        
        Args:
            existing: Optional existing model to update
            
        Returns:
            Django model instance ready for saving
        """
        raise NotImplementedError

    @abstractmethod
    def get_model_class(self) -> type:
        raise NotImplementedError

    def _get_model_instance(self) -> models.Model:
        return self._model_instance


class View:
    def __init__(self):
        pass


class PersistentChange:
    class ChangeType(enum.Enum):
        CREATE = 0
        UPDATE = 1
        DELETE = 2

    def __init__(self, data: Adapter):
        self._data = data

    def get_change_type(self) -> ChangeType:
        raise NotImplementedError

    def is_valid(self) -> bool:
        return True

    def get_data(self):
        return self._data


class PersistentData(common.ListData):
    def __init__(self):
        super().__init__()

    def get_data_class(self):
        return PersistentChange


class UpdateChange(PersistentChange):
    def __init__(self, data: Adapter):
        super().__init__(data)

    def get_change_type(self):
        return PersistentChange.ChangeType.UPDATE


class CreateChange(PersistentChange):
    def __init__(self, data: Adapter):
        super().__init__(data)

    def get_change_type(self):
        return PersistentChange.ChangeType.CREATE


class DeleteChange(PersistentChange):
    def __init__(self, data: Adapter):
        super().__init__(data)

    def get_change_type(self):
        return PersistentChange.ChangeType.DELETE


class DataAccessFilter:
    def __init__(self, throw_on_empty_result_set=False):
        self.throw_if_empty = throw_on_empty_result_set

    def _create_queries(self):
        return []

    def create_filter(self):
        queries = self._create_queries()
        q_len = len(queries)
        if q_len == 0:
            raise exception.InvalidQueryException("No parameters found to generate query.")
        query = None
        for q in queries:
            if not query:
                query = q
            else:
                query = query & q
        return query

    @abstractmethod
    def get_model_class(self) -> type:
        raise NotImplementedError

    @abstractmethod
    def get_adapter_class(self) -> type:
        raise NotImplementedError

    def pre_process(self, query_set):
        """Method allows for order by clauses to be processed on the query set"""
        return query_set

    def run(self):
        """Runs a query against the database and returns an array of Adapter"""
        result = []
        try:
            q = self.create_filter()
            query_set = self.get_model_class().objects.filter(q)
        except Exception as e:
            raise exception.QueryExecutionException(cause=e)
        try:
            for entry in query_set:
                data_adapter = self.get_adapter_class()()
                result.append(data_adapter.from_model(entry))
        except Exception as e:
            raise exception.ResultsetProcessingException(cause=e)
        return result
