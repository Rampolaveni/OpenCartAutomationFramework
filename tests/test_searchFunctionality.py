import pytest
from scenarios.productScenarios import ProductScenarios

@pytest.mark.testrail(case_id='C50')
@pytest.mark.sanity
def test_searchFunctionality(pages):
    ProductScenarios(pages).verify_product_search()
