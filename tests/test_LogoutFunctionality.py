import pytest
from scenarios.logoutScenarios import LogoutScenarios

@pytest.mark.testrail(case_id='C47')
@pytest.mark.sanity
def test_userLogout(pages):
    LogoutScenarios(pages).verify_user_logout()

