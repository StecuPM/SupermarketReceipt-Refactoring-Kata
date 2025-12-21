import pytest
from model_objects import Product, ProductUnit
from loyalty_program import LoyaltyAccount, LoyaltyProgram, process_loyalty_transaction
from fake_catalog import FakeCatalog
from shopping_cart import ShoppingCart


class TestLoyaltyAccount:
    """Tests for LoyaltyAccount class"""

    def test_create_account_with_zero_balance(self):
        """New account should start with zero balance"""
        account = LoyaltyAccount("customer123")

        assert account.customer_id == "customer123"
        assert account.points_balance == 0

    def test_create_account_with_initial_balance(self):
        """Account can be created with initial balance"""
        account = LoyaltyAccount("customer123", points_balance=100)

        assert account.points_balance == 100

    def test_add_points(self):
        """Should add points to balance"""
        account = LoyaltyAccount("customer123")

        account.add_points(50)

        assert account.points_balance == 50

    def test_add_points_multiple_times(self):
        """Should accumulate points from multiple additions"""
        account = LoyaltyAccount("customer123")

        account.add_points(25)
        account.add_points(30)
        account.add_points(45)

        assert account.points_balance == 100

    def test_redeem_points_success(self):
        """Should redeem points when sufficient balance"""
        account = LoyaltyAccount("customer123", points_balance=100)

        success = account.redeem_points(50)

        assert success is True
        assert account.points_balance == 50

    def test_redeem_points_insufficient_balance(self):
        """Should fail redemption when insufficient balance"""
        account = LoyaltyAccount("customer123", points_balance=30)

        success = account.redeem_points(50)

        assert success is False
        assert account.points_balance == 30  # Balance unchanged

    def test_can_redeem_sufficient_points(self):
        """Should return true when enough points available"""
        account = LoyaltyAccount("customer123", points_balance=100)

        assert account.can_redeem(50) is True
        assert account.can_redeem(100) is True

    def test_can_redeem_insufficient_points(self):
        """Should return false when not enough points"""
        account = LoyaltyAccount("customer123", points_balance=30)

        assert account.can_redeem(50) is False

    def test_transaction_history(self):
        """Should track transaction history"""
        account = LoyaltyAccount("customer123")

        account.add_points(50, "Purchase")
        account.redeem_points(20, "Redemption")

        assert len(account.transaction_history) == 2
        assert account.transaction_history[0] == ("EARN", 50, "Purchase")
        assert account.transaction_history[1] == ("REDEEM", 20, "Redemption")


class TestLoyaltyProgram:
    """Tests for LoyaltyProgram class"""

    def test_create_new_account(self):
        """Should create new loyalty account"""
        program = LoyaltyProgram()

        account = program.create_account("customer123")

        assert account.customer_id == "customer123"
        assert account.points_balance == 0

    def test_create_duplicate_account(self):
        """Should return existing account if already created"""
        program = LoyaltyProgram()

        account1 = program.create_account("customer123")
        account2 = program.create_account("customer123")

        assert account1 is account2

    def test_get_existing_account(self):
        """Should retrieve existing account"""
        program = LoyaltyProgram()
        original = program.create_account("customer123")

        retrieved = program.get_account("customer123")

        assert retrieved is original

    def test_get_nonexistent_account(self):
        """Should return None for non-existent account"""
        program = LoyaltyProgram()

        account = program.get_account("unknown")

        assert account is None

    def test_calculate_points_earned_default_rate(self):
        """Should calculate points at 1 point per dollar"""
        program = LoyaltyProgram(points_per_dollar=1.0)

        points = program.calculate_points_earned(25.50)

        assert points == 25  # Rounded down

    def test_calculate_points_earned_custom_rate(self):
        """Should calculate points at custom rate"""
        program = LoyaltyProgram(points_per_dollar=2.0)

        points = program.calculate_points_earned(25.00)

        assert points == 50

    def test_calculate_redemption_value_default(self):
        """Should calculate redemption at $0.01 per point"""
        program = LoyaltyProgram(dollars_per_point=0.01)

        value = program.calculate_redemption_value(100)

        assert value == pytest.approx(1.00, 0.01)

    def test_calculate_redemption_value_custom(self):
        """Should calculate redemption at custom rate"""
        program = LoyaltyProgram(dollars_per_point=0.02)

        value = program.calculate_redemption_value(100)

        assert value == pytest.approx(2.00, 0.01)

    def test_earn_points_on_purchase(self):
        """Should award points for purchase"""
        program = LoyaltyProgram()
        program.create_account("customer123")

        points = program.earn_points("customer123", 50.00)

        assert points == 50
        account = program.get_account("customer123")
        assert account.points_balance == 50

    def test_earn_points_nonexistent_customer(self):
        """Should return 0 for non-existent customer"""
        program = LoyaltyProgram()

        points = program.earn_points("unknown", 50.00)

        assert points == 0

    def test_redeem_points_success(self):
        """Should redeem points for discount"""
        program = LoyaltyProgram(dollars_per_point=0.01)
        account = program.create_account("customer123")
        account.add_points(100)

        discount = program.redeem_points("customer123", 50)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-0.50, 0.01)
        assert "50 pts" in discount.description
        assert account.points_balance == 50

    def test_redeem_points_insufficient_balance(self):
        """Should fail redemption with insufficient points"""
        program = LoyaltyProgram()
        account = program.create_account("customer123")
        account.add_points(30)

        discount = program.redeem_points("customer123", 50)

        assert discount is None
        assert account.points_balance == 30  # Unchanged

    def test_redeem_points_nonexistent_customer(self):
        """Should return None for non-existent customer"""
        program = LoyaltyProgram()

        discount = program.redeem_points("unknown", 50)

        assert discount is None


class TestProcessLoyaltyTransaction:
    """Tests for process_loyalty_transaction function"""

    def test_earn_points_without_redemption(self):
        """Should earn points for purchase without redemption"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 10.00)

        cart = ShoppingCart()
        cart.add_item(toothbrush)

        program = LoyaltyProgram(points_per_dollar=1.0)
        program.create_account("customer123")

        result = process_loyalty_transaction(
            cart, catalog, program, "customer123", redeem_points=0
        )

        assert result["points_earned"] == 10
        assert result["redemption_discount"] is None
        assert result["points_balance"] == 10

    def test_redeem_points_with_earning(self):
        """Should redeem points and earn new points"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 10.00)

        cart = ShoppingCart()
        cart.add_item(toothbrush)

        program = LoyaltyProgram(
            points_per_dollar=1.0, dollars_per_point=0.10  # $0.10 per point
        )
        account = program.create_account("customer123")
        account.add_points(100)  # Start with 100 points

        result = process_loyalty_transaction(
            cart, catalog, program, "customer123", redeem_points=50
        )

        # Redemption: 50 points * $0.10 = $5.00 discount
        assert result["redemption_discount"] is not None
        assert result["redemption_discount"].discount_amount == pytest.approx(
            -5.00, 0.01
        )

        # Cart total after redemption: $10.00 - $5.00 = $5.00
        # Points earned: $5.00 * 1.0 = 5 points
        assert result["points_earned"] == 5

        # Balance: 100 - 50 (redeemed) + 5 (earned) = 55
        assert result["points_balance"] == 55

    def test_insufficient_points_for_redemption(self):
        """Should not redeem when insufficient points"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 10.00)

        cart = ShoppingCart()
        cart.add_item(toothbrush)

        program = LoyaltyProgram()
        account = program.create_account("customer123")
        account.add_points(30)  # Only 30 points

        result = process_loyalty_transaction(
            cart, catalog, program, "customer123", redeem_points=50
        )

        # Redemption fails
        assert result["redemption_discount"] is None

        # Still earn points for full purchase
        assert result["points_earned"] == 10

        # Balance: 30 + 10 = 40
        assert result["points_balance"] == 40

    def test_multiple_products_transaction(self):
        """Should handle cart with multiple products"""
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)

        catalog = FakeCatalog()
        catalog.add_product(toothbrush, 0.99)
        catalog.add_product(toothpaste, 1.79)

        cart = ShoppingCart()
        cart.add_item(toothbrush)
        cart.add_item(toothpaste)

        program = LoyaltyProgram(points_per_dollar=1.0)
        program.create_account("customer123")

        result = process_loyalty_transaction(
            cart, catalog, program, "customer123", redeem_points=0
        )

        # Total: 0.99 + 1.79 = 2.78
        # Points: 2 (rounded down)
        assert result["points_earned"] == 2
        assert result["points_balance"] == 2
