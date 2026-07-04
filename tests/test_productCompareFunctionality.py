import pytest
from scenarios.productScenarios import ProductScenarios


@pytest.mark.sanity
def test_productCompareFunctionality(pages):
    ProductScenarios(pages).verify_product_comparison()
