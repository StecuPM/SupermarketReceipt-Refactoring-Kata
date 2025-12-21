import pytest
from model_objects import Product, SpecialOfferType, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from fake_catalog import FakeCatalog


class TestThreeForTwo:
    """Tests for THREE_FOR_TWO offer type: Buy 3, pay for 2"""

    def test_three_for_two_exact_quantity(self):
        """Test buying exactly 3 items with 3-for-2 offer"""
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 0.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 3)

        receipt = teller.checks_out_articles_from(cart)

        assert 1.98 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)
        assert -0.99 == pytest.approx(receipt.discounts[0].discount_amount, 0.01)

    def test_three_for_two_six_items(self):
        """Test buying 6 items - should get 2 free (pay for 4)"""
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 0.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 6)

        receipt = teller.checks_out_articles_from(cart)

        assert 3.96 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)
        assert -1.98 == pytest.approx(receipt.discounts[0].discount_amount, 0.01)

    def test_three_for_two_four_items(self):
        """Test buying 4 items - should get 1 free (pay for 3)"""
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 0.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 4)

        receipt = teller.checks_out_articles_from(cart)

        assert 2.97 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)


class TestTenPercentDiscount:
    """Tests for TEN_PERCENT_DISCOUNT offer type"""

    def test_ten_percent_on_single_item(self):
        """Test 10% discount on 1 item"""
        catalog = FakeCatalog()
        rice = Product("rice", ProductUnit.EACH)
        catalog.add_product(rice, 2.49)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)

        cart = ShoppingCart()
        cart.add_item(rice)

        receipt = teller.checks_out_articles_from(cart)

        assert 2.241 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)
        assert -0.249 == pytest.approx(receipt.discounts[0].discount_amount, 0.01)

    def test_ten_percent_on_multiple_items(self):
        """Test 10% discount on multiple items"""
        catalog = FakeCatalog()
        rice = Product("rice", ProductUnit.EACH)
        catalog.add_product(rice, 2.49)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, rice, 10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(rice, 3)

        receipt = teller.checks_out_articles_from(cart)

        assert 6.723 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)

    def test_twenty_percent_discount(self):
        """Test 20% discount on weighted product"""
        catalog = FakeCatalog()
        apples = Product("apples", ProductUnit.KILO)
        catalog.add_product(apples, 1.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, apples, 20.0)

        cart = ShoppingCart()
        cart.add_item_quantity(apples, 2.5)

        receipt = teller.checks_out_articles_from(cart)

        assert 3.98 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)


class TestTwoForAmount:
    """Tests for TWO_FOR_AMOUNT offer type: 2 items for special price"""

    def test_two_for_amount_exact(self):
        """Test buying exactly 2 items with special price"""
        catalog = FakeCatalog()
        cherry_tomatoes = Product("cherry tomatoes", ProductUnit.EACH)
        catalog.add_product(cherry_tomatoes, 0.69)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)

        cart = ShoppingCart()
        cart.add_item_quantity(cherry_tomatoes, 2)

        receipt = teller.checks_out_articles_from(cart)

        assert 0.99 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)
        assert -0.39 == pytest.approx(receipt.discounts[0].discount_amount, 0.01)

    def test_two_for_amount_four_items(self):
        """Test buying 4 items - 2 pairs at special price"""
        catalog = FakeCatalog()
        cherry_tomatoes = Product("cherry tomatoes", ProductUnit.EACH)
        catalog.add_product(cherry_tomatoes, 0.69)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)

        cart = ShoppingCart()
        cart.add_item_quantity(cherry_tomatoes, 4)

        receipt = teller.checks_out_articles_from(cart)

        assert 1.98 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)

    def test_two_for_amount_three_items(self):
        """Test buying 3 items - 1 pair at special price + 1 at regular"""
        catalog = FakeCatalog()
        cherry_tomatoes = Product("cherry tomatoes", ProductUnit.EACH)
        catalog.add_product(cherry_tomatoes, 0.69)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, cherry_tomatoes, 0.99)

        cart = ShoppingCart()
        cart.add_item_quantity(cherry_tomatoes, 3)

        receipt = teller.checks_out_articles_from(cart)

        assert 1.68 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)


class TestFiveForAmount:
    """Tests for FIVE_FOR_AMOUNT offer type: 5 items for special price"""

    def test_five_for_amount_exact(self):
        """Test buying exactly 5 items with special price"""
        catalog = FakeCatalog()
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothpaste, 1.79)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)

        cart = ShoppingCart()
        cart.add_item_quantity(toothpaste, 5)

        receipt = teller.checks_out_articles_from(cart)

        assert 7.49 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)
        assert -1.46 == pytest.approx(receipt.discounts[0].discount_amount, 0.01)

    def test_five_for_amount_ten_items(self):
        """Test buying 10 items - 2 sets at special price"""
        catalog = FakeCatalog()
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothpaste, 1.79)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)

        cart = ShoppingCart()
        cart.add_item_quantity(toothpaste, 10)

        receipt = teller.checks_out_articles_from(cart)

        assert 14.98 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)

    def test_five_for_amount_seven_items(self):
        """Test buying 7 items - 1 set at special price + 2 at regular"""
        catalog = FakeCatalog()
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothpaste, 1.79)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)

        cart = ShoppingCart()
        cart.add_item_quantity(toothpaste, 7)

        receipt = teller.checks_out_articles_from(cart)

        assert 11.07 == pytest.approx(receipt.total_price(), 0.01)
        assert 1 == len(receipt.discounts)
