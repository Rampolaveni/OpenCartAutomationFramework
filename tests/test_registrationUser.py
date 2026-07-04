import pytest

from scenarios.registrationScenarios import RegistrationScenarios


@pytest.mark.sanity
def test_registerUser(pages):
    RegistrationScenarios(pages).verify_user_registration()







