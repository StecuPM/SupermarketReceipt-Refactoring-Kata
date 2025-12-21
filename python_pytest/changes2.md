# Step 2: Refactoring - Code Smell Elimination

## Overview
Refactored monolithic offer handling into Strategy pattern.
Eliminated all 5 code smells identified in Step 1 (changes1.md).

## Summary of Changes

### New Files Added
1. src/offer_calculator.py - strategy interface
2. src/offer_calculators.py - 4 calculator implementations
3. src/offer_factory.py - calculator factory
4. tests/test_offer_calculators.py - 16 new tests

### Modified Files
5. src/teller.py - owns offer logic
6. src/shopping_cart.py - simplified, removed handle_offers()

## Results
- 53 tests passing (38 + 15 new)
- eliminated identified code smells