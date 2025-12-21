from abc import ABC, abstractmethod


class OfferCalculator(ABC):

    @abstractmethod
    def calculate_discount(self, product, quantity, unit_price, offer):
        pass

    @abstractmethod
    def applies_to(self, quantity, offer):
        pass
