from model_objects import SpecialOfferType
from offer_calculators import (
    ThreeForTwoCalculator,
    PercentageDiscountCalculator,
    TwoForAmountCalculator,
    FiveForAmountCalculator,
)


class OfferCalculatorFactory:

    # Singleton calculator instances (stateless, can be reused)
    _calculators = {
        SpecialOfferType.THREE_FOR_TWO: ThreeForTwoCalculator(),
        SpecialOfferType.TEN_PERCENT_DISCOUNT: PercentageDiscountCalculator(),
        SpecialOfferType.TWO_FOR_AMOUNT: TwoForAmountCalculator(),
        SpecialOfferType.FIVE_FOR_AMOUNT: FiveForAmountCalculator(),
    }

    @classmethod
    def get_calculator(cls, offer_type):
        calculator = cls._calculators.get(offer_type)
        if calculator is None:
            raise ValueError(f"No calculator registered for offer type: {offer_type}")
        return calculator

    @classmethod
    def register_calculator(cls, offer_type, calculator):
        cls._calculators[offer_type] = calculator

    @classmethod
    def get_supported_types(cls):
        return list(cls._calculators.keys())
