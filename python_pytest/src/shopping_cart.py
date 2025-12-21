from model_objects import ProductQuantity


class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        return self._items

    @property
    def product_quantities(self):
        return self._product_quantities

    def add_item(self, product):
        self.add_item_quantity(product, 1.0)

    def add_item_quantity(self, product, quantity):
        # Add to items list (preserves order)
        self._items.append(ProductQuantity(product, quantity))

        # Update aggregated quantities
        if product in self._product_quantities.keys():
            self._product_quantities[product] = (
                self._product_quantities[product] + quantity
            )
        else:
            self._product_quantities[product] = quantity
