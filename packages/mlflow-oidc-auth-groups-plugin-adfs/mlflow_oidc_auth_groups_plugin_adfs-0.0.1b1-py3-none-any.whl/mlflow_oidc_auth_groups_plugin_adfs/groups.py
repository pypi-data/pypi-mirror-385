
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


def get_user_groups(token) -> list:
    groups = token["userinfo"]["groups"]
    
    return _normalize_list(groups)
