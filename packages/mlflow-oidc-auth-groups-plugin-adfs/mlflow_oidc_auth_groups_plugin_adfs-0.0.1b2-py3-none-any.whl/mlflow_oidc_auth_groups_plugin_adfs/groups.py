from mlflow_oidc_auth import auth
from mlflow_oidc_auth.config import config

def _normalize_list(groups) -> list:
    """
        Return always list from str or list
    """
    if isinstance(groups, str):
        return [groups]
    elif isinstance(groups, list):
        return groups
    else:
        raise TypeError("Input must be a string or a list")


def decode_and_validate_token(access_token: str):
    payload = auth.validate_token(access_token)

    return payload

def get_claim_groups(decoded_token: dict):
    print(decoded_token)
    return decoded_token[config.OIDC_GROUPS_ATTRIBUTE]


def get_user_groups(access_token) -> list:
    decoded_token = decode_and_validate_token(access_token=access_token)
    groups = get_claim_groups(decoded_token=decoded_token)

    return _normalize_list(groups)
