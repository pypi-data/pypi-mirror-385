from typing import Optional

from .client.base_client import BaseGraphQLClient, GGNomadSDKConfig
from .auth import AuthModule
from .user import UserModule
from .workspace import WorkspaceModule
from .rbac import RBACModule
from .team import TeamModule
from .project import ProjectModule
from .resources import ResourceModule
from .billing import BillingModule
from .organization import OrganizationModule
from .payment import PaymentModule
from .quota import QuotaModule
from .store import StoreModule
from .support import SupportModule
from .usage import UsageModule
from .utils import SDKUtils
from .addon import AddOnModule
from .plan import PlanModule
from .product import ProductModule
from .config import ConfigModule
from .types.common import *

__version__ = "0.1.3"


class GGNomadSDK:
    def __init__(self, config: GGNomadSDKConfig):
        self.client = BaseGraphQLClient(config)

        # Initialize all modules
        self.auth = AuthModule(self.client)
        self.users = UserModule(self.client)
        self.workspaces = WorkspaceModule(self.client)
        self.rbac = RBACModule(self.client)
        self.teams = TeamModule(self.client)
        self.projects = ProjectModule(self.client)
        self.resources = ResourceModule(self.client)
        self.billing = BillingModule(self.client)
        self.organizations = OrganizationModule(self.client)
        self.payments = PaymentModule(self.client)
        self.quotas = QuotaModule(self.client)
        self.store = StoreModule(self.client)
        self.support = SupportModule(self.client)
        self.usage = UsageModule(self.client)
        self.utils = SDKUtils(self.client)
        self.addons = AddOnModule(self.client)
        self.plans = PlanModule(self.client)
        self.products = ProductModule(self.client)
        self.config = ConfigModule(self.client)

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        self.client.set_tokens(access_token=access_token, refresh_token=refresh_token)

    def clear_tokens(self) -> None:
        self.client.clear_tokens()

    def get_tokens(self) -> Optional[dict]:
        tokens = self.client.get_tokens()
        return (
            {"access_token": tokens.access_token, "refresh_token": tokens.refresh_token}
            if tokens
            else None
        )

    def set_endpoint(self, endpoint: str) -> None:
        self.client.set_endpoint(endpoint)

    def get_endpoint(self) -> str:
        return self.client.get_endpoint()


__all__ = [
    "GGNomadSDK",
    "GGNomadSDKConfig",
    "BaseGraphQLClient",
    "AuthModule",
    "UserModule",
    "WorkspaceModule",
    "RBACModule",
    "TeamModule",
    "ProjectModule",
    "ResourceModule",
    "BillingModule",
    "OrganizationModule",
    "PaymentModule",
    "QuotaModule",
    "StoreModule",
    "SupportModule",
    "UsageModule",
    "SDKUtils",
    "AddOnModule",
    "PlanModule",
    "ProductModule",
    "ConfigModule",
]
