from zou.app.models.project_status import ProjectStatus
from zou.app.blueprints.crud.base import BaseModelResource, BaseModelsResource


class ProjectStatussResource(BaseModelsResource):
    def __init__(self):
        BaseModelsResource.__init__(self, ProjectStatus)

    def check_read_permissions(self, options=None):
        return True


class ProjectStatusResource(BaseModelResource):
    def __init__(self):
        BaseModelResource.__init__(self, ProjectStatus)

    def check_read_permissions(self, instance):
        return True
