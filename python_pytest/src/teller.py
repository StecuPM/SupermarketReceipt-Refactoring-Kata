from model_objects import Offer
from receipt import Receipt
from offer_factory import OfferCalculatorFactory


class Teller:

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}
        self.calculator_factory = OfferCalculatorFactory()

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = Offer(offer_type, product, argument)

    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()

        # Add all cart items to receipt
        for pq in the_cart.items:
            p = pq.product
            quantity = pq.quantity
            unit_price = self.catalog.unit_price(p)
            price = quantity * unit_price
            receipt.add_product(p, quantity, unit_price, price)

        # Apply all offers using calculator strategies
        self._apply_offers(receipt, the_cart)

        return receipt

    def _apply_offers(self, receipt, cart):
        product_quantities = cart.product_quantities

        for product, quantity in product_quantities.items():
            # Skip products without offers
            if product not in self.offers:
                continue

            # Get offer and calculator
            offer = self.offers[product]
            calculator = self.calculator_factory.get_calculator(offer.offer_type)

            # Calculate discount
            unit_price = self.catalog.unit_price(product)
            discount = calculator.calculate_discount(
                product, quantity, unit_price, offer
            )

            # Add discount to receipt if applicable
            if discount:
                receipt.add_discount(discount)
