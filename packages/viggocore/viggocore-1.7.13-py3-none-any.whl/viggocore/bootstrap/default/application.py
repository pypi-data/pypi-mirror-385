from viggocore.common.subsystem.apihandler import Api
from typing import Dict

from viggocore.common import utils
from viggocore.subsystem.application.resource import Application


class BootstrapApplication(object):

    def __init__(self, api: Api) -> None:
        self.application_manager = api.applications()

    def execute(self) -> Application:
        application = self._get_application_default()
        return self._save_application(application)

    def _get_application_default(self) -> Application:
        return Application(id=utils.random_uuid(),
                           name=Application.DEFAULT,
                           description="Application Default")

    def _save_application(self, application: Application) -> Application:
        data = application.to_dict()
        if 'settings' in data.keys():
            data.pop('settings')
        return self.application_manager.create(**data)
