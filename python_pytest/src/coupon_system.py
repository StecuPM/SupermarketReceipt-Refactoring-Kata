"""
Coupon System
- Date-limited validity
- Quantity limits
- One-time redemption tracking
- Various discount types (percentage, fixed amount)
"""

from datetime import datetime, date
from model_objects import Discount


class Coupon:

    def __init__(
        self,
        coupon_code,
        discount_type,
        discount_value,
        valid_from=None,
        valid_until=None,
        max_uses=1,
        min_purchase_amount=0.0,
        description=None,
    ):
        self.coupon_code = coupon_code
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.max_uses = max_uses
        self.min_purchase_amount = min_purchase_amount
        self.description = description or f"Coupon {coupon_code}"
        self.usage_count = 0  # Track redemptions

    def is_valid_date(self, check_date=None):
        if check_date is None:
            check_date = date.today()

        # Convert datetime to date if needed
        if isinstance(check_date, datetime):
            check_date = check_date.date()

        # Check start date
        if self.valid_from:
            valid_from = (
                self.valid_from.date()
                if isinstance(self.valid_from, datetime)
                else self.valid_from
            )
            if check_date < valid_from:
                return False

        # Check end date
        if self.valid_until:
            valid_until = (
                self.valid_until.date()
                if isinstance(self.valid_until, datetime)
                else self.valid_until
            )
            if check_date > valid_until:
                return False

        return True

    def has_uses_remaining(self):
        return self.usage_count < self.max_uses

    def meets_minimum_purchase(self, cart_total):
        return cart_total >= self.min_purchase_amount

    def can_be_applied(self, cart_total, check_date=None):
        return (
            self.is_valid_date(check_date)
            and self.has_uses_remaining()
            and self.meets_minimum_purchase(cart_total)
        )

    def calculate_discount(self, cart_total):
        if self.discount_type == "percentage":
            return cart_total * (self.discount_value / 100.0)
        elif self.discount_type == "fixed":
            # Fixed amount, but not more than cart total
            return min(self.discount_value, cart_total)
        else:
            raise ValueError(f"Unknown discount type: {self.discount_type}")

    def redeem(self):
        self.usage_count += 1


class CouponRegistry:
    """
    Registry for managing coupons and tracking redemptions.
    """

    def __init__(self):
        """Initialize empty coupon registry."""
        self.coupons = {}  # coupon_code -> Coupon

    def register_coupon(self, coupon):
        """
        Register a coupon.
        """
        self.coupons[coupon.coupon_code] = coupon

    def get_coupon(self, coupon_code):
        """
        Get coupon by code.
        Returns:
            Coupon instance or None if not found
        """
        return self.coupons.get(coupon_code)

    def apply_coupon(self, coupon_code, cart_total, check_date=None):
        """
        Apply coupon if valid.
        Returns:
            Discount instance or None if coupon cannot be applied
        """
        coupon = self.get_coupon(coupon_code)

        if coupon is None:
            return None  # Coupon not found

        if not coupon.can_be_applied(cart_total, check_date):
            return None  # Coupon invalid or not applicable

        # Calculate discount
        discount_amount = coupon.calculate_discount(cart_total)

        # Mark as redeemed
        coupon.redeem()

        # Create discount
        description = f"{coupon.description}"
        if coupon.discount_type == "percentage":
            description += f" (-{coupon.discount_value}%)"
        else:
            description += f" (-${coupon.discount_value:.2f})"

        return Discount(None, description, -discount_amount)


def apply_coupons(cart, catalog, coupon_registry, coupon_codes, check_date=None):
    """
    Apply multiple coupons to cart.
    Returns:
        list: Discount instances for valid coupons
    """
    # Calculate cart total before discounts
    cart_total = 0.0
    for product, quantity in cart.product_quantities.items():
        unit_price = catalog.unit_price(product)
        cart_total += quantity * unit_price

    # Apply each coupon
    discounts = []
    for coupon_code in coupon_codes:
        discount = coupon_registry.apply_coupon(coupon_code, cart_total, check_date)
        if discount:
            discounts.append(discount)

    return discounts
