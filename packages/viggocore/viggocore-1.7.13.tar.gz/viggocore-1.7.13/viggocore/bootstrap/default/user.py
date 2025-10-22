from viggocore.common import utils
from viggocore.common.subsystem.apihandler import Api
from viggocore.subsystem.grant.resource import Grant
from viggocore.subsystem.user.resource import User


class BootstrapUser(object):

    def __init__(self, api: Api) -> None:
        self.user_manager = api.users()
        self.grant_manager = api.grants()

    def execute(self, domain_id: str, role_id: str) -> User:
        user = self._get_user_default(domain_id)
        grant = self._get_grant_default(user.id, role_id)
        self._save(user, grant)
        return user

    def _get_user_default(self, domain_default_id: str) -> User:
        return User(id=utils.random_uuid(),
                    domain_id=domain_default_id,
                    name=User.SYSADMIN_USERNAME,
                    email='sysadmin@example.com')

    def _get_grant_default(self, user_id: str, role_id: str) -> Grant:
        return Grant(id=utils.random_uuid(),
                     user_id=user_id,
                     role_id=role_id)

    def _save(self, user: User, grant: Grant) -> None:
        self.user_manager.create(**user.to_dict())
        self.user_manager.reset(id=user.id, password='123456')
        self.grant_manager.create(**grant.to_dict())
