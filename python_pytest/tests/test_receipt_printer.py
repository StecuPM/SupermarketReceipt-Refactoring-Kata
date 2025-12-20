import pytest
from model_objects import Product, SpecialOfferType, ProductUnit
from shopping_cart import ShoppingCart
from receipt_printer import ReceiptPrinter
from test_helpers import create_standard_catalog, create_teller_with_standard_offers


class TestReceiptPrinter:
    """Tests for receipt formatting and printing"""

    def test_receipt_single_item_no_discount(self):
        """Test receipt format for single item without discount"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item(products['milk'])

        receipt = teller.checks_out_articles_from(cart)
        printer = ReceiptPrinter()
        output = printer.print_receipt(receipt)

        assert "milk" in output
        assert "1.50" in output
        assert "Total:" in output

    def test_receipt_multiple_items_with_quantity(self):
        """Test receipt shows quantity for items > 1"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['toothbrush'], 3)

        receipt = teller.checks_out_articles_from(cart)
        printer = ReceiptPrinter()
        output = printer.print_receipt(receipt)

        assert "toothbrush" in output
        assert "3" in output
        assert "0.99" in output

    def test_receipt_weighted_product(self):
        """Test receipt format for weighted products"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['apples'], 2.5)

        receipt = teller.checks_out_articles_from(cart)
        printer = ReceiptPrinter()
        output = printer.print_receipt(receipt)

        assert "apples" in output
        assert "2.500" in output
        assert "1.99" in output

    def test_receipt_with_discount(self):
        """Test receipt shows discount information"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['toothbrush'], 3)

        receipt = teller.checks_out_articles_from(cart)
        printer = ReceiptPrinter()
        output = printer.print_receipt(receipt)

        assert "3 for 2" in output
        assert "toothbrush" in output
        assert "-" in output

    def test_receipt_column_width_default(self):
        """Test receipt uses default 40 column width"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item(products['milk'])

        receipt = teller.checks_out_articles_from(cart)
        printer = ReceiptPrinter()
        output = printer.print_receipt(receipt)

        lines = output.split('\n')
        for line in lines:
            if line.strip():
                assert len(line) <= 41

    def test_receipt_custom_column_width(self):
        """Test receipt with custom column width"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item(products['milk'])

        receipt = teller.checks_out_articles_from(cart)
        printer = ReceiptPrinter(columns=50)
        output = printer.print_receipt(receipt)

        assert "milk" in output
        assert "Total:" in output

    def test_receipt_multiple_discounts(self):
        """Test receipt with multiple different discounts"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['toothbrush'], 3)
        cart.add_item_quantity(products['apples'], 2.0)

        receipt = teller.checks_out_articles_from(cart)
        printer = ReceiptPrinter()
        output = printer.print_receipt(receipt)

        assert "3 for 2" in output
        assert "20.0% off" in output
        assert output.count("-") >= 2


class TestReceiptCalculations:
    """Tests for receipt calculation accuracy"""

    def test_receipt_item_count(self):
        """Test receipt tracks correct number of items"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item(products['milk'])
        cart.add_item(products['rice'])
        cart.add_item_quantity(products['apples'], 1.5)

        receipt = teller.checks_out_articles_from(cart)

        assert 3 == len(receipt.items)

    def test_receipt_discount_count(self):
        """Test receipt tracks correct number of discounts"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['toothbrush'], 3)
        cart.add_item(products['rice'])
        cart.add_item(products['milk'])

        receipt = teller.checks_out_articles_from(cart)

        assert 2 == len(receipt.discounts)

    def test_receipt_total_with_no_discounts(self):
        """Test receipt total equals sum of item prices when no discounts"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item(products['milk'])

        receipt = teller.checks_out_articles_from(cart)

        items_total = sum(item.total_price for item in receipt.items)
        assert items_total == pytest.approx(receipt.total_price(), 0.01)

    def test_receipt_total_with_discounts(self):
        """Test receipt total correctly includes discounts"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['toothbrush'], 3)

        receipt = teller.checks_out_articles_from(cart)

        items_total = sum(item.total_price for item in receipt.items)
        discounts_total = sum(d.discount_amount for d in receipt.discounts)
        expected_total = items_total + discounts_total

        assert expected_total == pytest.approx(receipt.total_price(), 0.01)


class TestReceiptItems:
    """Tests for individual receipt items"""

    def test_receipt_item_properties(self):
        """Test receipt item contains all expected properties"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['toothbrush'], 2)

        receipt = teller.checks_out_articles_from(cart)

        assert 1 == len(receipt.items)
        item = receipt.items[0]

        assert item.product == products['toothbrush']
        assert item.quantity == 2
        assert item.price == 0.99
        assert item.total_price == pytest.approx(1.98, 0.01)

    def test_receipt_discount_properties(self):
        """Test discount contains all expected properties"""
        catalog, products = create_standard_catalog()
        teller = create_teller_with_standard_offers(catalog, products)

        cart = ShoppingCart()
        cart.add_item_quantity(products['toothbrush'], 3)

        receipt = teller.checks_out_articles_from(cart)

        assert 1 == len(receipt.discounts)
        discount = receipt.discounts[0]

        assert discount.product == products['toothbrush']
        assert "3 for 2" in discount.description
        assert discount.discount_amount < 0