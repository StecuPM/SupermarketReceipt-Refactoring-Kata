import pytest
from model_objects import Product, ProductUnit, Offer, SpecialOfferType
from offer_calculators import (
    ThreeForTwoCalculator,
    PercentageDiscountCalculator,
    TwoForAmountCalculator,
    FiveForAmountCalculator,
)


class TestThreeForTwoCalculator:

    def test_applies_to_three_items(self):
        calc = ThreeForTwoCalculator()
        offer = Offer(SpecialOfferType.THREE_FOR_TWO, None, 0)
        assert calc.applies_to(3, offer) is True

    def test_not_applies_to_two_items(self):
        calc = ThreeForTwoCalculator()
        offer = Offer(SpecialOfferType.THREE_FOR_TWO, None, 0)
        assert calc.applies_to(2, offer) is False

    def test_calculate_discount_three_items(self):
        calc = ThreeForTwoCalculator()
        product = Product("test", ProductUnit.EACH)
        offer = Offer(SpecialOfferType.THREE_FOR_TWO, product, 0)

        discount = calc.calculate_discount(product, 3, 1.00, offer)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-1.00, 0.01)
        assert "3 for 2" in discount.description

    def test_calculate_discount_six_items(self):
        calc = ThreeForTwoCalculator()
        product = Product("test", ProductUnit.EACH)
        offer = Offer(SpecialOfferType.THREE_FOR_TWO, product, 0)

        discount = calc.calculate_discount(product, 6, 0.99, offer)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-1.98, 0.01)


class TestPercentageDiscountCalculator:
    def test_applies_to_any_quantity(self):
        calc = PercentageDiscountCalculator()
        offer = Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, None, 10.0)
        assert calc.applies_to(1, offer) is True
        assert calc.applies_to(0.5, offer) is True

    def test_calculate_ten_percent_discount(self):
        calc = PercentageDiscountCalculator()
        product = Product("rice", ProductUnit.EACH)
        offer = Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, product, 10.0)

        discount = calc.calculate_discount(product, 1, 2.49, offer)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-0.249, 0.01)
        assert "10.0% off" in discount.description

    def test_calculate_twenty_percent_discount(self):
        calc = PercentageDiscountCalculator()
        product = Product("apples", ProductUnit.KILO)
        offer = Offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, product, 20.0)

        discount = calc.calculate_discount(product, 2.5, 1.99, offer)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-0.995, 0.01)


class TestTwoForAmountCalculator:

    def test_applies_to_two_items(self):
        calc = TwoForAmountCalculator()
        offer = Offer(SpecialOfferType.TWO_FOR_AMOUNT, None, 0.99)
        assert calc.applies_to(2, offer) is True
        assert calc.applies_to(3, offer) is True

    def test_not_applies_to_one_item(self):
        calc = TwoForAmountCalculator()
        offer = Offer(SpecialOfferType.TWO_FOR_AMOUNT, None, 0.99)
        assert calc.applies_to(1, offer) is False

    def test_calculate_discount_two_items(self):
        """Calculate discount for exactly 2 items"""
        calc = TwoForAmountCalculator()
        product = Product("tomatoes", ProductUnit.EACH)
        offer = Offer(SpecialOfferType.TWO_FOR_AMOUNT, product, 0.99)

        discount = calc.calculate_discount(product, 2, 0.69, offer)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-0.39, 0.01)
        assert "2 for 0.99" in discount.description

    def test_calculate_discount_three_items(self):
        calc = TwoForAmountCalculator()
        product = Product("tomatoes", ProductUnit.EACH)
        offer = Offer(SpecialOfferType.TWO_FOR_AMOUNT, product, 0.99)

        discount = calc.calculate_discount(product, 3, 0.69, offer)

        # 1 pair at 0.99 + 1 single at 0.69 = 1.68
        # Without discount: 3 * 0.69 = 2.07
        # Discount: 2.07 - 1.68 = 0.39
        assert discount is not None
        assert discount.discount_amount == pytest.approx(-0.39, 0.01)


class TestFiveForAmountCalculator:

    def test_applies_to_five_items(self):
        calc = FiveForAmountCalculator()
        offer = Offer(SpecialOfferType.FIVE_FOR_AMOUNT, None, 7.49)
        assert calc.applies_to(5, offer) is True
        assert calc.applies_to(7, offer) is True

    def test_not_applies_to_four_items(self):
        calc = FiveForAmountCalculator()
        offer = Offer(SpecialOfferType.FIVE_FOR_AMOUNT, None, 7.49)
        assert calc.applies_to(4, offer) is False

    def test_calculate_discount_five_items(self):
        calc = FiveForAmountCalculator()
        product = Product("toothpaste", ProductUnit.EACH)
        offer = Offer(SpecialOfferType.FIVE_FOR_AMOUNT, product, 7.49)

        discount = calc.calculate_discount(product, 5, 1.79, offer)

        assert discount is not None
        assert discount.discount_amount == pytest.approx(-1.46, 0.01)
        assert "5 for 7.49" in discount.description

    def test_calculate_discount_seven_items(self):
        calc = FiveForAmountCalculator()
        product = Product("toothpaste", ProductUnit.EACH)
        offer = Offer(SpecialOfferType.FIVE_FOR_AMOUNT, product, 7.49)

        discount = calc.calculate_discount(product, 7, 1.79, offer)

        # 1 set at 7.49 + 2 singles at 1.79 = 11.07
        # Without discount: 7 * 1.79 = 12.53
        # Discount: 12.53 - 11.07 = 1.46
        assert discount is not None
        assert discount.discount_amount == pytest.approx(-1.46, 0.01)
