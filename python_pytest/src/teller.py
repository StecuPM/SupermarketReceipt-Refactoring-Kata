"""
Responsible for:
1. Creating receipts from shopping carts
2. Applying special offers using calculator strategies
3. Applying bundle discounts
4. Applying coupon discounts
5. Processing loyalty transactions
6. Managing product catalog access
"""

from model_objects import Offer
from receipt import Receipt
from offer_factory import OfferCalculatorFactory
from bundle_discounts import BundleRegistry, calculate_bundle_discounts
from coupon_system import CouponRegistry, apply_coupons
from loyalty_program import LoyaltyProgram, process_loyalty_transaction


class Teller:
    def __init__(self, catalog):
        self.catalog = catalog

        # Offer system
        self.offers = {}
        self.calculator_factory = OfferCalculatorFactory()

        # Bundle system
        self.bundle_registry = BundleRegistry()

        # Coupon system
        self.coupon_registry = CouponRegistry()

        # Loyalty program
        self.loyalty_program = LoyaltyProgram()

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = Offer(offer_type, product, argument)

    # Bundle Discounts

    def register_bundle(self, bundle):
        self.bundle_registry.register_bundle(bundle)

    # Coupon System

    def register_coupon(self, coupon):
        self.coupon_registry.register_coupon(coupon)

    # Loyalty Program

    def create_loyalty_account(self, customer_id):
        return self.loyalty_program.create_account(customer_id)

    def get_loyalty_account(self, customer_id):
        return self.loyalty_program.get_account(customer_id)

    # Main Checkout Method

    def checks_out_articles_from(
        self, the_cart, coupon_codes=None, customer_id=None, redeem_points=0
    ):
        receipt = Receipt()

        # Add all cart items to receipt
        for pq in the_cart.items:
            p = pq.product
            quantity = pq.quantity
            unit_price = self.catalog.unit_price(p)
            price = quantity * unit_price
            receipt.add_product(p, quantity, unit_price, price)

        # Apply product-specific offers
        self._apply_offers(receipt, the_cart)

        # Apply bundle discounts
        self._apply_bundle_discounts(receipt, the_cart)

        # Apply coupon discounts
        if coupon_codes:
            self._apply_coupons(receipt, the_cart, coupon_codes)

        # Process loyalty transaction
        loyalty_result = None
        if customer_id:
            loyalty_result = self._process_loyalty(
                receipt, the_cart, customer_id, redeem_points
            )

        if coupon_codes or customer_id:
            return {"receipt": receipt, "loyalty": loyalty_result}
        else:
            return receipt

    def _apply_offers(self, receipt, cart):
        product_quantities = cart.product_quantities

        for product, quantity in product_quantities.items():
            if product not in self.offers:
                continue

            offer = self.offers[product]
            calculator = self.calculator_factory.get_calculator(offer.offer_type)
            unit_price = self.catalog.unit_price(product)

            discount = calculator.calculate_discount(
                product, quantity, unit_price, offer
            )

            if discount:
                receipt.add_discount(discount)

    def _apply_bundle_discounts(self, receipt, cart):
        bundle_discounts = calculate_bundle_discounts(
            cart, self.catalog, self.bundle_registry
        )

        for discount in bundle_discounts:
            receipt.add_discount(discount)

    def _apply_coupons(self, receipt, cart, coupon_codes):
        coupon_discounts = apply_coupons(
            cart, self.catalog, self.coupon_registry, coupon_codes
        )

        for discount in coupon_discounts:
            receipt.add_discount(discount)

    def _process_loyalty(self, receipt, cart, customer_id, redeem_points):
        loyalty_result = process_loyalty_transaction(
            cart, self.catalog, self.loyalty_program, customer_id, redeem_points
        )

        # Add redemption discount to receipt if applicable
        if loyalty_result["redemption_discount"]:
            receipt.add_discount(loyalty_result["redemption_discount"])

        return loyalty_result
