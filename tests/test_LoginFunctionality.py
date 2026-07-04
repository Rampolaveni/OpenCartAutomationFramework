import pytest
from scenarios.loginScenarios import LoginScenarios

@pytest.mark.sanity
def test_userLogin(pages):
    LoginScenarios(pages).verify_successful_login()


