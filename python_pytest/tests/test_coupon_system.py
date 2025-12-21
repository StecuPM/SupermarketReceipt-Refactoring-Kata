import pytest
from datetime import date, timedelta
from model_objects import Product, ProductUnit
from coupon_system import Coupon, CouponRegistry, apply_coupons
from fake_catalog import FakeCatalog
from shopping_cart import ShoppingCart


class TestCoupon:
    """Tests for Coupon class"""

    def test_valid_coupon_within_dates(self):
        """Coupon should be valid between start and end dates"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        coupon = Coupon(
            "TEST10", "percentage", 10.0, valid_from=yesterday, valid_until=tomorrow
        )

        assert coupon.is_valid_date(today) is True

    def test_expired_coupon(self):
        """Expired coupon should not be valid"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)

        coupon = Coupon(
            "EXPIRED", "percentage", 10.0, valid_from=last_week, valid_until=yesterday
        )

        assert coupon.is_valid_date(today) is False

    def test_future_coupon(self):
        """Future-dated coupon should not be valid yet"""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        coupon = Coupon(
            "FUTURE", "percentage", 10.0, valid_from=tomorrow, valid_until=next_week
        )

        assert coupon.is_valid_date(today) is False

    def test_coupon_with_no_dates(self):
        """Coupon with no date restrictions should always be valid"""
        coupon = Coupon("ALWAYS", "percentage", 10.0)

        today = date.today()
        past = today - timedelta(days=365)
        future = today + timedelta(days=365)

        assert coupon.is_valid_date(today) is True
        assert coupon.is_valid_date(past) is True
        assert coupon.is_valid_date(future) is True

    def test_coupon_usage_limit(self):
        """Coupon should track usage and enforce limit"""
        coupon = Coupon("ONCE", "percentage", 10.0, max_uses=1)

        assert coupon.has_uses_remaining() is True

        coupon.redeem()

        assert coupon.has_uses_remaining() is False
        assert coupon.usage_count == 1

    def test_coupon_multiple_uses(self):
        """Coupon should allow multiple uses up to limit"""
        coupon = Coupon("MULTI", "percentage", 10.0, max_uses=3)

        assert coupon.has_uses_remaining() is True

        coupon.redeem()
        assert coupon.has_uses_remaining() is True

        coupon.redeem()
        assert coupon.has_uses_remaining() is True

        coupon.redeem()
        assert coupon.has_uses_remaining() is False

    def test_minimum_purchase_requirement(self):
        """Coupon should enforce minimum purchase amount"""
        coupon = Coupon("MIN50", "percentage", 10.0, min_purchase_amount=50.0)

        assert coupon.meets_minimum_purchase(60.0) is True
        assert coupon.meets_minimum_purchase(50.0) is True
        assert coupon.meets_minimum_purchase(49.99) is False

    def test_percentage_discount_calculation(self):
        """Percentage coupon should calculate correct discount"""
        coupon = Coupon("SAVE20", "percentage", 20.0)

        discount = coupon.calculate_discount(100.0)

        assert discount == pytest.approx(20.0, 0.01)

    def test_fixed_discount_calculation(self):
        """Fixed coupon should calculate correct discount"""
        coupon = Coupon("FIXED10", "fixed", 10.0)

        discount = coupon.calculate_discount(100.0)

        assert discount == pytest.approx(10.0, 0.01)

    def test_fixed_discount_capped_at_total(self):
        """Fixed discount should not exceed cart total"""
        coupon = Coupon("BIG50", "fixed", 50.0)

        discount = coupon.calculate_discount(30.0)

        # Should be capped at 30.0, not 50.0
        assert discount == pytest.approx(30.0, 0.01)

    def test_can_be_applied_all_conditions(self):
        """Coupon should be applicable when all conditions met"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        coupon = Coupon(
            "VALID",
            "percentage",
            10.0,
            valid_from=today,
            valid_until=tomorrow,
            max_uses=1,
            min_purchase_amount=20.0,
        )

        assert coupon.can_be_applied(25.0, today) is True


class TestCouponRegistry:
    """Tests for CouponRegistry"""

    def test_register_and_get_coupon(self):
        """Should register and retrieve coupon"""
        coupon = Coupon("TEST", "percentage", 10.0)
        registry = CouponRegistry()

        registry.register_coupon(coupon)
        retrieved = registry.get_coupon("TEST")

        assert retrieved is coupon

    def test_get_nonexistent_coupon(self):
        """Returns None for non-existent coupon"""
        registry = CouponRegistry()

        result = registry.get_coupon("NOTFOUND")

        assert result is None

    def test_apply_valid_coupon(self):
        """Applies valid coupon and return discount"""
        coupon = Coupon("SAVE10", "percentage", 10.0)
        registry = CouponRegistry()
        registry.register_coupon(coupon)

        discount = registry.apply_coupon("SAVE10", 100.0)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-10.0, 0.01)
        assert coupon.usage_count == 1

    def test_apply_invalid_coupon_code(self):
        """Returns None for invalid coupon code"""
        registry = CouponRegistry()

        discount = registry.apply_coupon("INVALID", 100.0)

        assert discount is None

    def test_apply_expired_coupon(self):
        """Returns None for expired coupon"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)

        coupon = Coupon(
            "EXPIRED", "percentage", 10.0, valid_from=last_week, valid_until=yesterday
        )
        registry = CouponRegistry()
        registry.register_coupon(coupon)

        discount = registry.apply_coupon("EXPIRED", 100.0, today)

        assert discount is None

    def test_apply_coupon_below_minimum(self):
        """Returns None when cart below minimum"""
        coupon = Coupon("MIN50", "percentage", 10.0, min_purchase_amount=50.0)
        registry = CouponRegistry()
        registry.register_coupon(coupon)

        discount = registry.apply_coupon("MIN50", 40.0)

        assert discount is None

    def test_apply_exhausted_coupon(self):
        """Returns None when coupon uses exhausted"""
        coupon = Coupon("ONCE", "percentage", 10.0, max_uses=1)
        registry = CouponRegistry()
        registry.register_coupon(coupon)

        # First use - should work
        discount1 = registry.apply_coupon("ONCE", 100.0)
        assert discount1 is not None

        # Second use - should fail
        discount2 = registry.apply_coupon("ONCE", 100.0)
        assert discount2 is None


class TestApplyCoupons:
    """Tests for apply_coupons"""

    def test_apply_single_coupon_to_cart(self):
        """applies coupon to cart total"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)

        cart = ShoppingCart()
        cart.add_item(toothbrush)
        cart.add_item(toothpaste)

        coupon = Coupon("SAVE10", "percentage", 10.0)
        registry = CouponRegistry()
        registry.register_coupon(coupon)

        discounts = apply_coupons(cart, catalog, registry, ["SAVE10"])

        assert len(discounts) == 1
        # Cart total: 0.99 + 1.79 = 2.78
        # 10% discount = 0.278
        assert discounts[0].discount_amount == pytest.approx(-0.278, 0.01)

    def test_apply_multiple_coupons(self):
        """applies multiple coupons to cart"""
        rice = Product("rice", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(rice, 100.0)

        cart = ShoppingCart()
        cart.add_item(rice)

        coupon1 = Coupon("SAVE10", "percentage", 10.0)
        coupon2 = Coupon("FIXED5", "fixed", 5.0)

        registry = CouponRegistry()
        registry.register_coupon(coupon1)
        registry.register_coupon(coupon2)

        discounts = apply_coupons(cart, catalog, registry, ["SAVE10", "FIXED5"])

        assert len(discounts) == 2

    def test_ignore_invalid_coupons(self):
        """Should skip invalid coupons and continue with valid ones"""
        rice = Product("rice", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(rice, 100.0)

        cart = ShoppingCart()
        cart.add_item(rice)

        coupon = Coupon("VALID", "percentage", 10.0)
        registry = CouponRegistry()
        registry.register_coupon(coupon)

        discounts = apply_coupons(
            cart, catalog, registry, ["INVALID", "VALID", "NOTFOUND"]
        )

        assert len(discounts) == 1
        assert discounts[0].discount_amount == pytest.approx(-10.0, 0.01)
