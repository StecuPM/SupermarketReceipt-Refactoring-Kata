"""
Loyalty Program
- Points earning on purchases
- Points redemption as payment
- Customer account management
- Configurable earning and redemption rates
"""

from model_objects import Discount


class LoyaltyAccount:

    def __init__(self, customer_id, points_balance=0):
        self.customer_id = customer_id
        self.points_balance = points_balance
        self.transaction_history = []  # List of (type, amount, description)

    def add_points(self, points, description="Points earned"):
        self.points_balance += points
        self.transaction_history.append(("EARN", points, description))

    def redeem_points(self, points, description="Points redeemed"):
        if points > self.points_balance:
            return False

        self.points_balance -= points
        self.transaction_history.append(("REDEEM", points, description))
        return True

    def can_redeem(self, points):
        return self.points_balance >= points

    def get_balance(self):
        return self.points_balance


class LoyaltyProgram:

    def __init__(self, points_per_dollar=1.0, dollars_per_point=0.01):
        self.points_per_dollar = points_per_dollar
        self.dollars_per_point = dollars_per_point
        self.accounts = {}  # customer_id -> LoyaltyAccount

    def create_account(self, customer_id):
        if customer_id in self.accounts:
            return self.accounts[customer_id]

        account = LoyaltyAccount(customer_id)
        self.accounts[customer_id] = account
        return account

    def get_account(self, customer_id):
        return self.accounts.get(customer_id)

    def calculate_points_earned(self, purchase_amount):
        return int(purchase_amount * self.points_per_dollar)

    def calculate_redemption_value(self, points):
        return points * self.dollars_per_point

    def earn_points(self, customer_id, purchase_amount):
        account = self.get_account(customer_id)
        if account is None:
            return 0

        points = self.calculate_points_earned(purchase_amount)
        account.add_points(points, f"Purchase ${purchase_amount:.2f}")
        return points

    def redeem_points(self, customer_id, points):
        account = self.get_account(customer_id)
        if account is None:
            return None

        if not account.can_redeem(points):
            return None  # Insufficient points

        # Calculate discount value
        discount_amount = self.calculate_redemption_value(points)

        # Redeem points
        success = account.redeem_points(points, f"Redeemed {points} points")
        if not success:
            return None

        # Create discount
        description = f"Loyalty points ({points} pts)"
        return Discount(None, description, -discount_amount)


def process_loyalty_transaction(
    cart, catalog, loyalty_program, customer_id, redeem_points=0
):
    result = {"redemption_discount": None, "points_earned": 0, "points_balance": 0}

    # Calculate cart total
    cart_total = 0.0
    for product, quantity in cart.product_quantities.items():
        unit_price = catalog.unit_price(product)
        cart_total += quantity * unit_price

    # Apply points redemption if requested
    if redeem_points > 0:
        redemption_discount = loyalty_program.redeem_points(customer_id, redeem_points)
        result["redemption_discount"] = redemption_discount

        # Reduce cart total by redemption amount
        if redemption_discount:
            cart_total += redemption_discount.discount_amount  # Note: negative

    # Award points for purchase (after redemption)
    points_earned = loyalty_program.earn_points(customer_id, cart_total)
    result["points_earned"] = points_earned

    # Get updated balance
    account = loyalty_program.get_account(customer_id)
    if account:
        result["points_balance"] = account.get_balance()

    return result
