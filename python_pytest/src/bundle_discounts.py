"""
Bundle Discounts
- Buy all items in bundle → get X% off bundle total
- Only complete bundles are discounted
- Partial bundles charged at regular price
"""

from model_objects import Discount


class Bundle:

    def __init__(self, bundle_id, products, discount_percentage, description=None):
        self.bundle_id = bundle_id
        self.products = set(products)  # Use set for fast membership testing
        self.discount_percentage = discount_percentage
        self.description = description or f"Bundle {bundle_id}"

    def contains_all_products(self, cart_products):
        return self.products.issubset(set(cart_products))

    def calculate_bundle_total(self, cart_quantities, catalog):
        total = 0.0
        for product in self.products:
            if product in cart_quantities:
                quantity = cart_quantities[product]
                unit_price = catalog.unit_price(product)
                total += quantity * unit_price
        return total


class BundleRegistry:

    def __init__(self):
        self.bundles = {}  # bundle_id -> Bundle

    def register_bundle(self, bundle):
        self.bundles[bundle.bundle_id] = bundle

    def get_bundle(self, bundle_id):
        return self.bundles.get(bundle_id)

    def get_all_bundles(self):
        return list(self.bundles.values())

    def find_applicable_bundles(self, cart_products):
        applicable = []
        for bundle in self.bundles.values():
            if bundle.contains_all_products(cart_products):
                applicable.append(bundle)
        return applicable


def calculate_bundle_discounts(cart, catalog, bundle_registry):
    """
    Calculate all applicable bundle discounts for cart.
    Returns:
        list: Discount instances for applicable bundles
    """
    discounts = []
    cart_products = cart.product_quantities.keys()

    # Find all applicable bundles
    applicable_bundles = bundle_registry.find_applicable_bundles(cart_products)

    # Calculate discount for each bundle
    for bundle in applicable_bundles:
        bundle_total = bundle.calculate_bundle_total(cart.product_quantities, catalog)

        discount_amount = bundle_total * (bundle.discount_percentage / 100.0)

        # Create pseudo-product for bundle discount
        # (bundles don't have single product, so we use None)
        discount = Discount(
            None,  # Bundle applies to multiple products
            f"{bundle.description} (-{bundle.discount_percentage}%)",
            -discount_amount,
        )

        discounts.append(discount)

    return discounts
