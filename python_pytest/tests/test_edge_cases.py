import pytest
from model_objects import Product, SpecialOfferType, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from fake_catalog import FakeCatalog


class TestNoOffers:
    """Test scenarios without any special offers"""

    def test_single_product_no_offer(self):
        """Test single product purchase without offer"""
        catalog = FakeCatalog()
        milk = Product("milk", ProductUnit.EACH)
        catalog.add_product(milk, 1.50)

        teller = Teller(catalog)
        cart = ShoppingCart()
        cart.add_item(milk)

        receipt = teller.checks_out_articles_from(cart)

        assert 1.50 == pytest.approx(receipt.total_price(), 0.01)
        assert 0 == len(receipt.discounts)
        assert 1 == len(receipt.items)

    def test_multiple_products_no_offers(self):
        """Test multiple different products without offers"""
        catalog = FakeCatalog()
        milk = Product("milk", ProductUnit.EACH)
        bread = Product("bread", ProductUnit.EACH)
        catalog.add_product(milk, 1.50)
        catalog.add_product(bread, 2.00)

        teller = Teller(catalog)
        cart = ShoppingCart()
        cart.add_item(milk)
        cart.add_item_quantity(bread, 2)

        receipt = teller.checks_out_articles_from(cart)

        assert 5.50 == pytest.approx(receipt.total_price(), 0.01)
        assert 0 == len(receipt.discounts)
        assert 2 == len(receipt.items)


class TestBelowOfferThreshold:
    """Test quantities below offer thresholds"""

    def test_three_for_two_with_two_items(self):
        """Test 3-for-2 offer with only 2 items (below threshold)"""
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 0.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 2)

        receipt = teller.checks_out_articles_from(cart)

        assert 1.98 == pytest.approx(receipt.total_price(), 0.01)
        assert 0 == len(receipt.discounts)

    def test_three_for_two_with_one_item(self):
        """Test 3-for-2 offer with only 1 item"""
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 0.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)

        cart = ShoppingCart()
        cart.add_item(toothbrush)

        receipt = teller.checks_out_articles_from(cart)

        assert 0.99 == pytest.approx(receipt.total_price(), 0.01)
        assert 0 == len(receipt.discounts)

    def test_two_for_amount_with_one_item(self):
        """Test 2-for-amount offer with only 1 item"""
        catalog = FakeCatalog()
        tomatoes = Product("tomatoes", ProductUnit.EACH)
        catalog.add_product(tomatoes, 0.69)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, tomatoes, 0.99)

        cart = ShoppingCart()
        cart.add_item(tomatoes)

        receipt = teller.checks_out_articles_from(cart)

        assert 0.69 == pytest.approx(receipt.total_price(), 0.01)
        assert 0 == len(receipt.discounts)

    def test_five_for_amount_with_four_items(self):
        """Test 5-for-amount offer with only 4 items"""
        catalog = FakeCatalog()
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothpaste, 1.79)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)

        cart = ShoppingCart()
        cart.add_item_quantity(toothpaste, 4)

        receipt = teller.checks_out_articles_from(cart)

        assert 7.16 == pytest.approx(receipt.total_price(), 0.01)
        assert 0 == len(receipt.discounts)


class TestWeightedProducts:
    """Test products sold by weight (KILO unit)"""

    def test_weighted_product_without_offer(self):
        """Test weighted product purchase without offer"""
        catalog = FakeCatalog()
        apples = Product("apples", ProductUnit.KILO)
        catalog.add_product(apples, 1.99)

        teller = Teller(catalog)
        cart = ShoppingCart()
        cart.add_item_quantity(apples, 0.5)

        receipt = teller.checks_out_articles_from(cart)

        assert 0.995 == pytest.approx(receipt.total_price(), 0.01)
        assert 0 == len(receipt.discounts)

    def test_weighted_product_with_discount(self):
        """Test weighted product with percentage discount"""
        catalog = FakeCatalog()
        bananas = Product("bananas", ProductUnit.KILO)
        catalog.add_product(bananas, 1.50)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, bananas, 15.0)

        cart = ShoppingCart()
        cart.add_item_quantity(bananas, 1.2)

        receipt = teller.checks_out_articles_from(cart)

        assert 1.53 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)


class TestMixedCart:
    """Test shopping cart with multiple different products"""

    def test_mixed_products_some_with_offers(self):
        """Test cart with mix of products - some with offers, some without"""
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        milk = Product("milk", ProductUnit.EACH)
        apples = Product("apples", ProductUnit.KILO)

        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(milk, 1.50)
        catalog.add_product(apples, 1.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, apples, 20.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 3)
        cart.add_item_quantity(milk, 2)
        cart.add_item_quantity(apples, 1.5)

        receipt = teller.checks_out_articles_from(cart)

        assert 7.368 == pytest.approx(receipt.total_price(), 0.01)
        assert 2 == len(receipt.discounts)
        assert 3 == len(receipt.items)

    def test_same_product_added_multiple_times(self):
        """Test adding same product in separate operations"""
        catalog = FakeCatalog()
        milk = Product("milk", ProductUnit.EACH)
        catalog.add_product(milk, 1.50)

        teller = Teller(catalog)
        cart = ShoppingCart()
        cart.add_item(milk)
        cart.add_item(milk)
        cart.add_item(milk)

        receipt = teller.checks_out_articles_from(cart)

        assert 4.50 == pytest.approx(receipt.total_price(), 0.01)
        assert 3 == len(receipt.items)


class TestEmptyCart:
    """Test edge case of empty cart"""

    def test_empty_cart(self):
        """Test checking out an empty cart"""
        catalog = FakeCatalog()
        teller = Teller(catalog)
        cart = ShoppingCart()

        receipt = teller.checks_out_articles_from(cart)

        assert 0.0 == receipt.total_price()
        assert 0 == len(receipt.discounts)
        assert 0 == len(receipt.items)


class TestLargeQuantities:
    """Test with large quantities to verify calculation accuracy"""

    def test_large_quantity_three_for_two(self):
        """Test 3-for-2 with 100 items"""
        catalog = FakeCatalog()
        item = Product("item", ProductUnit.EACH)
        catalog.add_product(item, 1.00)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, item, 0)

        cart = ShoppingCart()
        cart.add_item_quantity(item, 100)

        receipt = teller.checks_out_articles_from(cart)

        assert 67.00 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)
        