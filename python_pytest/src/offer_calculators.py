import math
from offer_calculator import OfferCalculator
from model_objects import Discount


class ThreeForTwoCalculator(OfferCalculator):

    def applies_to(self, quantity, offer):
        return int(quantity) >= 3

    def calculate_discount(self, product, quantity, unit_price, offer):
        quantity_as_int = int(quantity)

        if not self.applies_to(quantity, offer):
            return None

        number_of_sets = math.floor(quantity_as_int / 3)
        remaining_items = quantity_as_int % 3

        # Calculate total with discount
        total_with_discount = (number_of_sets * 2 * unit_price) + (remaining_items * unit_price)
        total_without_discount = quantity * unit_price
        discount_amount = total_without_discount - total_with_discount

        return Discount(product, "3 for 2", -discount_amount)


class PercentageDiscountCalculator(OfferCalculator):

    def applies_to(self, quantity, offer):
        return quantity > 0

    def calculate_discount(self, product, quantity, unit_price, offer):
        discount_percentage = offer.argument
        discount_amount = quantity * unit_price * discount_percentage / 100.0
        description = f"{discount_percentage}% off"

        return Discount(product, description, -discount_amount)


class TwoForAmountCalculator(OfferCalculator):

    def applies_to(self, quantity, offer):
        return int(quantity) >= 2

    def calculate_discount(self, product, quantity, unit_price, offer):
        quantity_as_int = int(quantity)

        if not self.applies_to(quantity, offer):
            return None

        special_price = offer.argument
        pairs = quantity_as_int // 2
        singles = quantity_as_int % 2

        # Calculate total with discount
        total_with_discount = (pairs * special_price) + (singles * unit_price)
        total_without_discount = quantity * unit_price
        discount_amount = total_without_discount - total_with_discount

        description = f"2 for {special_price}"
        return Discount(product, description, -discount_amount)


class FiveForAmountCalculator(OfferCalculator):

    def applies_to(self, quantity, offer):
        return int(quantity) >= 5

    def calculate_discount(self, product, quantity, unit_price, offer):
        quantity_as_int = int(quantity)

        if not self.applies_to(quantity, offer):
            return None

        special_price = offer.argument
        sets = quantity_as_int // 5
        remainder = quantity_as_int % 5

        # Calculate total with discount
        total_with_discount = (sets * special_price) + (remainder * unit_price)
        total_without_discount = quantity * unit_price
        discount_amount = total_without_discount - total_with_discount

        description = f"5 for {special_price}"
        return Discount(product, description, -discount_amount)
