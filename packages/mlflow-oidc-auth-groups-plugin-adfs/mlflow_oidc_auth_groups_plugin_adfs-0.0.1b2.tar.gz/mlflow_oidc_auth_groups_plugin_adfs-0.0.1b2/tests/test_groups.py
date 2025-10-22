import pytest

from mlflow_oidc_auth_groups_plugin_adfs import groups



def _function_clean_token_userinfo(token_userinfo):
    del(token_userinfo["azp"])
    del(token_userinfo["uid"])
    
    return token_userinfo


class TestGroups:
    def test_decode_token(self, fixture_data):
        decoded_token = groups.decode_and_validate_token(fixture_data.access_token)

        expect = fixture_data.decoded_token
        result = _function_clean_token_userinfo(decoded_token)

        assert result == expect
    

    def test_get_claim_groups(self, fixture_data):
        expect = fixture_data.token_groups
        result = groups.get_claim_groups(fixture_data.decoded_token)

        assert result == expect
    
    
    def test_get_user_groups(self, fixture_data):
        expect = fixture_data.groups_expect
        result = groups.get_user_groups(access_token=fixture_data.access_token)

        assert result == expect