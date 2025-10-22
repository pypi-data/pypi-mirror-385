from zou.app.blueprints.crud.base import BaseModelResource, BaseModelsResource

from zou.app.models.entity_type import EntityType
from zou.app.utils import events
from zou.app.services import entities_service, assets_service

from zou.app.services.exception import WrongParameterException


class EntityTypesResource(BaseModelsResource):
    def __init__(self):
        BaseModelsResource.__init__(self, EntityType)

    def all_entries(self, query=None, relations=False):
        if query is None:
            query = self.model.query

        return [
            asset_type.serialize(relations=relations)
            for asset_type in query.all()
        ]

    def check_read_permissions(self, options=None):
        return True

    def emit_create_event(self, instance_dict):
        events.emit("asset-type:new", {"asset_type_id": instance_dict["id"]})

    def post_creation(self, instance):
        assets_service.clear_asset_type_cache()
        return instance.serialize(relations=True)

    def check_creation_integrity(self, data):
        entity_type = EntityType.query.filter(
            EntityType.name.ilike(data.get("name", ""))
        ).first()
        if entity_type is not None:
            raise WrongParameterException(
                "Entity type with this name already exists"
            )
        return data


class EntityTypeResource(BaseModelResource):
    def __init__(self):
        BaseModelResource.__init__(self, EntityType)

    def check_read_permissions(self, instance):
        return True

    def emit_update_event(self, instance_dict):
        events.emit(
            "asset-type:update", {"asset_type_id": instance_dict["id"]}
        )

    def emit_delete_event(self, instance_dict):
        events.emit(
            "asset-type:delete", {"asset_type_id": instance_dict["id"]}
        )

    def post_update(self, instance_dict, data):
        entities_service.clear_entity_type_cache(instance_dict["id"])
        assets_service.clear_asset_type_cache()
        instance_dict["task_types"] = [
            str(task_types.id) for task_types in self.instance.task_types
        ]
        return instance_dict

    def post_delete(self, instance_dict):
        entities_service.clear_entity_type_cache(instance_dict["id"])
        assets_service.clear_asset_type_cache()
        return instance_dict
