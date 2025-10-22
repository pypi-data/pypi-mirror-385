from zou.app.models.task_type import TaskType
from zou.app.services.exception import WrongParameterException
from zou.app.services import tasks_service

from zou.app.blueprints.crud.base import BaseModelResource, BaseModelsResource


class TaskTypesResource(BaseModelsResource):
    def __init__(self):
        BaseModelsResource.__init__(self, TaskType)

    def check_read_permissions(self, options=None):
        return True

    def update_data(self, data):
        data = super().update_data(data)
        name = data.get("name", None)
        task_type = TaskType.get_by(name=name)
        if task_type is not None:
            raise WrongParameterException(
                "A task type with similar name already exists"
            )
        return data

    def post_creation(self, instance):
        tasks_service.clear_task_type_cache(str(instance.id))
        return instance.serialize()


class TaskTypeResource(BaseModelResource):
    def __init__(self):
        BaseModelResource.__init__(self, TaskType)

    def check_read_permissions(self, instance):
        return True

    def update_data(self, data, instance_id):
        data = super().update_data(data, instance_id)
        name = data.get("name", None)
        if name is not None:
            task_type = TaskType.get_by(name=name)
            if task_type is not None and instance_id != str(task_type.id):
                raise WrongParameterException(
                    "A task type with similar name already exists"
                )
        return data

    def post_update(self, instance_dict, data):
        tasks_service.clear_task_type_cache(instance_dict["id"])
        return instance_dict

    def post_delete(self, instance_dict):
        tasks_service.clear_task_type_cache(instance_dict["id"])
        return instance_dict
