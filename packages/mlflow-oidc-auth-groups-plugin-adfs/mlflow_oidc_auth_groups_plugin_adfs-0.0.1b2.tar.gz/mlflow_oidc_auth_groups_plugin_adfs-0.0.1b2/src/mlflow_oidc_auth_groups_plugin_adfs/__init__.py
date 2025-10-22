"""mlflow-oidc-auth-groups-plugin-adfs package.


"""

from __future__ import annotations

from .groups import get_user_groups

__all__: list[str] = ["get_user_groups"]
