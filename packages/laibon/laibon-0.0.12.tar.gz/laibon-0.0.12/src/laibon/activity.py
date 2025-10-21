#  Copyright (c) 2023 Wenceslaus Mumala

import logging

from django.db import transaction

from laibon import accessor
from laibon import common
from laibon import db
from laibon import exception


class PersistentDataAccessor:
    _KEY = common.ContainerKey("PersistentData")

    @staticmethod
    def set(data, data_container: common.Container):
        raise exception.InvalidArgumentException("Please use PersistentData#add")

    @staticmethod
    def get(data_container: common.Container) -> db.PersistentData:
        res = data_container.get(PersistentDataAccessor._KEY)
        if res is None:
            res = db.PersistentData()
            data_container.put(PersistentDataAccessor._KEY, res)
        return res


class WriteDataActivity(common.Activity):
    LOGGER = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

    class Result(common.ActivityResult):
        SUCCESS = "Success"
        WRITE_ERROR = "Failed"

    def get_result_codes(self):
        return [self.Result.SUCCESS, self.Result.WRITE_ERROR]

    def create_entity(self, entity_adapter: db.Adapter):
        try:
            entity = entity_adapter.to_model()
            entity.save()
            return entity
        except Exception as e:
            self.LOGGER.debug("Failed to store new data because of ", exc_info=True)
            raise exception.PersistenceException(cause=e)

    def update_entity(self, delta: db.Adapter):
        try:
            existing = delta.get_model_class().objects.get(id=delta.id)
            delta.to_model(existing).save()
        except Exception as e:
            self.LOGGER.debug("Failed to update data because of ", exc_info=True)
            raise exception.PersistenceException(cause=e)

    def delete_entity(self, delta: db.Adapter):
        # Should be discouraged - also prone to error
        try:
            existing = delta.get_model_class().objects.get(id=delta.id)
            return existing.delete()
        except Exception as e:
            self.LOGGER.debug("Error removing data because of ", exc_info=True)
            raise exception.PersistenceException(cause=e)

    def get_changes(self, data_container: common.Container) -> db.PersistentData:
        changes: db.PersistentData = PersistentDataAccessor.get(data_container)
        return changes

    def process(self, data_container: common.Container):
        WriteDataActivity.LOGGER.debug("Writing flow data to database")
        try:
            changes = self.get_changes(data_container)
            if changes.get_size() > 0:
                self._write_changes(changes)
            else:
                WriteDataActivity.LOGGER.debug("No changes to write")
        except Exception as e:
            accessor.DelayedExceptionAccessor.set(e, data_container)
            WriteDataActivity.LOGGER.debug("Failed to write data because of ", exc_info=True)
            return self.Result.WRITE_ERROR
        return common.goto_next()

    @transaction.atomic
    def _write_changes(self, changes: db.PersistentData):
        for change in changes.iterator():
            try:
                if not change.is_valid():
                    continue
                change_type: db.PersistentChange.ChangeType = change.get_change_type()
                if db.PersistentChange.ChangeType.CREATE == change_type:
                    self.create_entity(change.get_data())
                elif db.PersistentChange.ChangeType.UPDATE == change_type:
                    self.update_entity(change.get_data())
                elif db.PersistentChange.ChangeType.DELETE == change_type:
                    self.delete_entity(change.get_data())
            except Exception as e:
                self.LOGGER.debug("Failed to write {}".format(change.__class__))
                raise e
        WriteDataActivity.LOGGER.debug("Done writing data")
