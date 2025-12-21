import pytest
from model_objects import Product, ProductUnit
from bundle_discounts import Bundle, BundleRegistry, calculate_bundle_discounts
from fake_catalog import FakeCatalog
from shopping_cart import ShoppingCart


class TestBundle:
    """Tests for Bundle class"""

    def test_bundle_contains_all_products(self):
        """Bundle should detect when all products are in cart"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0)

        cart_products = {toothbrush, toothpaste}
        assert bundle.contains_all_products(cart_products) is True

    def test_bundle_missing_product(self):
        """Bundle should detect when products are missing"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0)

        cart_products = {toothbrush}  # Missing toothpaste
        assert bundle.contains_all_products(cart_products) is False

    def test_bundle_calculate_total(self):
        """Bundle should calculate total price of bundle products"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0)

        cart_quantities = {toothbrush: 1, toothpaste: 1}
        total = bundle.calculate_bundle_total(cart_quantities, catalog)

        assert total == pytest.approx(2.78, 0.01)  # 0.99 + 1.79


class TestBundleRegistry:
    """Tests for BundleRegistry"""

    def test_register_and_get_bundle(self):
        """Should register and retrieve bundle"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0)
        registry = BundleRegistry()

        registry.register_bundle(bundle)
        retrieved = registry.get_bundle("oral-care")

        assert retrieved is bundle

    def test_find_applicable_bundles(self):
        """Should find all applicable bundles for cart"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        apples = Product("apples", ProductUnit.KILO)

        bundle1 = Bundle("oral-care", [toothbrush, toothpaste], 10.0)
        bundle2 = Bundle("fruit", [apples], 5.0)

        registry = BundleRegistry()
        registry.register_bundle(bundle1)
        registry.register_bundle(bundle2)

        cart_products = {toothbrush, toothpaste}
        applicable = registry.find_applicable_bundles(cart_products)

        assert len(applicable) == 1
        assert applicable[0].bundle_id == "oral-care"


class TestBundleDiscounts:
    """Tests for bundle discount calculation"""

    def test_complete_bundle_gets_discount(self):
        """Complete bundle should receive percentage discount"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0, "Oral Care Bundle")
        registry = BundleRegistry()
        registry.register_bundle(bundle)

        cart = ShoppingCart()
        cart.add_item(toothbrush)
        cart.add_item(toothpaste)

        discounts = calculate_bundle_discounts(cart, catalog, registry)

        assert len(discounts) == 1
        # 10% off 2.78 = 0.278
        assert discounts[0].discount_amount == pytest.approx(-0.278, 0.01)
        assert "Oral Care Bundle" in discounts[0].description
        assert "-10.0%" in discounts[0].description

    def test_incomplete_bundle_no_discount(self):
        """Incomplete bundle should not receive discount"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0)
        registry = BundleRegistry()
        registry.register_bundle(bundle)

        cart = ShoppingCart()
        cart.add_item(toothbrush)  # Only toothbrush, missing toothpaste

        discounts = calculate_bundle_discounts(cart, catalog, registry)

        assert len(discounts) == 0

    def test_multiple_bundles(self):
        """Multiple complete bundles should all get discounts"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        rice = Product("rice", ProductUnit.EACH)
        milk = Product("milk", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)
        catalog.add_product(rice, 2.49)
        catalog.add_product(milk, 1.50)

        bundle1 = Bundle("oral-care", [toothbrush, toothpaste], 10.0)
        bundle2 = Bundle("breakfast", [rice, milk], 15.0)

        registry = BundleRegistry()
        registry.register_bundle(bundle1)
        registry.register_bundle(bundle2)

        cart = ShoppingCart()
        cart.add_item(toothbrush)
        cart.add_item(toothpaste)
        cart.add_item(rice)
        cart.add_item(milk)

        discounts = calculate_bundle_discounts(cart, catalog, registry)

        assert len(discounts) == 2

    def test_bundle_with_multiple_quantities(self):
        """Bundle discount should apply to quantities in cart"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0)
        registry = BundleRegistry()
        registry.register_bundle(bundle)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 2)  # 2 toothbrushes
        cart.add_item_quantity(toothpaste, 2)  # 2 toothpastes

        discounts = calculate_bundle_discounts(cart, catalog, registry)

        assert len(discounts) == 1
        # Total: 2*0.99 + 2*1.79 = 5.56
        # 10% off = 0.556
        assert discounts[0].discount_amount == pytest.approx(-0.556, 0.01)

    def test_bundle_with_extra_products(self):
        """Bundle discount should apply when cart has extra products"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        apples = Product("apples", ProductUnit.KILO)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)
        catalog.add_product(apples, 1.99)

        bundle = Bundle("oral-care", [toothbrush, toothpaste], 10.0)
        registry = BundleRegistry()
        registry.register_bundle(bundle)

        cart = ShoppingCart()
        cart.add_item(toothbrush)
        cart.add_item(toothpaste)
        cart.add_item_quantity(apples, 1.5)  # Extra product not in bundle

        discounts = calculate_bundle_discounts(cart, catalog, registry)

        # Bundle discount should only apply to bundle products
        assert len(discounts) == 1
        # 10% off (0.99 + 1.79) = 0.278, apples not included
        assert discounts[0].discount_amount == pytest.approx(-0.278, 0.01)
