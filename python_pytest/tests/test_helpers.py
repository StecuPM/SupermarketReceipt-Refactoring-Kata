"""
Test helper utilities for creating common test fixtures
"""
from model_objects import Product, ProductUnit
from fake_catalog import FakeCatalog
from teller import Teller


def create_standard_catalog():
    """
    Create a catalog with standard products for testing

    Returns:
        tuple: (FakeCatalog, dict of products)
    """
    catalog = FakeCatalog()

    products = {
        'toothbrush': Product("toothbrush", ProductUnit.EACH),
        'toothpaste': Product("toothpaste", ProductUnit.EACH),
        'apples': Product("apples", ProductUnit.KILO),
        'rice': Product("rice", ProductUnit.EACH),
        'cherry_tomatoes': Product("cherry tomatoes", ProductUnit.EACH),
        'milk': Product("milk", ProductUnit.EACH),
    }

    catalog.add_product(products['toothbrush'], 0.99)
    catalog.add_product(products['toothpaste'], 1.79)
    catalog.add_product(products['apples'], 1.99)
    catalog.add_product(products['rice'], 2.49)
    catalog.add_product(products['cherry_tomatoes'], 0.69)
    catalog.add_product(products['milk'], 1.50)

    return catalog, products


def create_teller_with_standard_offers(catalog, products):
    """
    Create a teller with standard special offers

    Args:
        catalog: FakeCatalog instance
        products: dict of Product instances

    Returns:
        Teller instance with offers configured
    """
    from model_objects import SpecialOfferType

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, products['toothbrush'], 0)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, products['toothpaste'], 7.49)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, products['apples'], 20.0)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, products['rice'], 10.0)
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, products['cherry_tomatoes'], 0.99)

    return teller