import pytest
from scenarios.productScenarios import ProductScenarios

@pytest.mark.testrail(case_id='C48')
@pytest.mark.sanity
def test_productCompareFunctionality(pages):
    ProductScenarios(pages).verify_product_comparison()
