"""
Technospam SDK - Python SDK for Technospam API
CI/CD Pipeline Test
"""

from typing import Optional

from .addon import AddOnModule
from .auth import AuthModule
from .billing import BillingModule
from .client.base_client import BaseGraphQLClient, TechnospamSDKConfig
from .config import ConfigModule
from .organization import OrganizationModule
from .payment import PaymentModule
from .plan import PlanModule
from .product import ProductModule
from .project import ProjectModule
from .quota import QuotaModule
from .rbac import RBACModule
from .resources import ResourceModule
from .store import StoreModule
from .support import SupportModule
from .team import TeamModule
from .types.common import *
from .usage import UsageModule
from .user import UserModule
from .utils import SDKUtils
from .workspace import WorkspaceModule

__version__ = "0.1.0"


class TechnospamSDK:
    def __init__(self, config: TechnospamSDKConfig):
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
    "TechnospamSDK",
    "TechnospamSDKConfig",
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
