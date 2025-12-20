# Step 1: Test Development and bug detecting
## Overview
Firstly focused on creating tests coverage for the code to ensure safe refactoring in future commits.
The implementation achieved 98% code coverage with 43 tests across multiple test categories.
Then the bug was fixed and all tests passed.

## Summary of Changes
### New Files Added
1. **tests/test_offers.py** (13 tests)
   - tests for all four special offer types
2. **tests/test_edge_cases.py** (12 tests)
   - Edge cases tests
3. **tests/test_receipt_printer.py** (14 tests)
   - Receipt formatting and calculation tests
4. **tests/test_helpers.py**
   - Reusable test helper functions
5. **.coveragerc**
   - Configuration for code coverage analysis

### Source Code Fixed
6. **src/shopping_cart.py**
   - Fixed TWO_FOR_AMOUNT calculation (line 45)
   - Changed float division `/` to floor division `//`
   - Bug discovered by test suite

### Test Results
- 38 tests implemented (37 from new files + 1 existing)
- 38 tests passing (after bug fix)
- Execution time: 0.57s
- 1 bug discovered and fixed during test development

## Detailed Changes
### 1. Test for Special Offer Types (test_offers.py)
#### TestThreeForTwo Class
Tests the THREE_FOR_TWO offer type (buy 3, pay for 2):
- `test_three_for_two_exact_quantity` - Exactly 3 items, expects discount for 1 item
- `test_three_for_two_six_items` - 6 items, expects discount for 2 items
- `test_three_for_two_four_items` - 4 items, expects discount for 1 item
**Rationale:** Verifies that the 3-for-2 promotion correctly applies discounts for complete sets of 3 items and handles remainders properly.

#### TestTenPercentDiscount Class
Tests percentage-based discount offers:
- `test_ten_percent_on_single_item` - 10% discount on single item
- `test_ten_percent_on_multiple_items` - 10% discount on multiple items
- `test_twenty_percent_discount` - 20% discount on weighted products
**Rationale:** Ensures percentage discounts work correctly for both EACH and KILO products, with proper decimal handling.

#### TestTwoForAmount Class
Tests the TWO_FOR_AMOUNT offer (2 items for special price):
- `test_two_for_amount_exact` - Exactly 2 items at special price
- `test_two_for_amount_four_items` - 4 items, expects 2 pairs at special price
- `test_two_for_amount_three_items` - 3 items, 1 pair at special + 1 at regular
**Rationale:** Validates that pairs are priced correctly and odd quantities receive partial discounts.

#### TestFiveForAmount Class
Tests the FIVE_FOR_AMOUNT offer (5 items for special price):
- `test_five_for_amount_exact` - Exactly 5 items at special price
- `test_five_for_amount_ten_items` - 10 items, expects 2 sets at special price
- `test_five_for_amount_seven_items` - 7 items, 1 set at special + 2 at regular
**Rationale:** Confirms that multi-item bundles are calculated correctly with proper remainder handling.

### 2. Edge Case Tests (test_edge_cases.py)
#### TestNoOffers Class (2 tests)
Tests scenarios without special offers:
- `test_single_product_no_offer` - Single product at regular price
- `test_multiple_products_no_offers` - Multiple products without offers
**Rationale:** Ensures the system works correctly when no special offers are active.

#### TestBelowOfferThreshold Class (4 tests)
Tests quantities below offer activation thresholds:
- `test_three_for_two_with_two_items` - 2 items where 3 are needed
- `test_three_for_two_with_one_item` - 1 item where 3 are needed
- `test_two_for_amount_with_one_item` - 1 item where 2 are needed
- `test_five_for_amount_with_four_items` - 4 items where 5 are needed
**Rationale:** Verifies that offers are not incorrectly applied when minimum quantities are not met.

#### TestWeightedProducts Class (2 tests)
Tests products sold by weight (KILO unit):
- `test_weighted_product_without_offer` - Fractional quantities without offers
- `test_weighted_product_with_discount` - Fractional quantities with percentage discount
**Rationale:** Ensures correct handling of non-integer quantities and decimal calculations.

#### TestMixedCart Class (2 tests)
Tests shopping carts with multiple product types:
- `test_mixed_products_some_with_offers` - Mix of products with and without offers
- `test_same_product_added_multiple_times` - Same product added in multiple operations
**Rationale:** Validates that the system correctly handles complex shopping scenarios.

#### TestEmptyCart Class (1 test)
- `test_empty_cart` - Empty shopping cart checkout
**Rationale:** Edge case protection against null/empty scenarios.

#### TestLargeQuantities Class (1 test)
- `test_large_quantity_three_for_two` - 100 items with 3-for-2 offer
**Rationale:** Verifies calculation accuracy with large numbers.

### 3. Receipt Printer Tests (test_receipt_printer.py)
#### TestReceiptPrinter Class
Tests receipt formatting and output:
- `test_receipt_single_item_no_discount` - Single item receipt format
- `test_receipt_multiple_items_with_quantity` - Quantity display for multiple items
- `test_receipt_weighted_product` - Weighted product formatting (3 decimal places)
- `test_receipt_with_discount` - Discount information display
- `test_receipt_column_width_default` - Default 40-column width
- `test_receipt_custom_column_width` - Custom column width
- `test_receipt_multiple_discounts` - Multiple discounts on one receipt
**Rationale:** Ensures receipts are formatted correctly and consistently.

#### TestReceiptCalculations Class
Tests mathematical accuracy:
- `test_receipt_item_count` - Correct item count tracking
- `test_receipt_discount_count` - Correct discount count tracking
- `test_receipt_total_with_no_discounts` - Total equals sum of items
- `test_receipt_total_with_discounts` - Total includes discount amounts
**Rationale:** Validates that all calculations are mathematically correct.

#### TestReceiptItems Class
Tests receipt data structures:
- `test_receipt_item_properties` - ReceiptItem contains correct data
- `test_receipt_discount_properties` - Discount contains correct data
**Rationale:** Ensures data integrity in receipt objects.

### 4. Test Helpers (test_helpers.py)
#### create_standard_catalog()
Creates a FakeCatalog with 6 standard products:
- toothbrush (0.99)
- toothpaste (1.79)
- apples (1.99/kg)
- rice (2.49)
- cherry tomatoes (0.69)
- milk (1.50)
**Rationale:** Reduces code duplication across test files.

#### create_teller_with_standard_offers()
Creates a Teller with pre-configured standard offers.
**Rationale:** Simplifies test setup for common scenarios.

### 5. Coverage Configuration (.coveragerc)
Configuration for pytest-cov:
- Source: src directory
- Omits: test files and cache
- HTML report output
- Precision: 2 decimal places
**Rationale:** Provides consistent coverage measurement across runs.

## Test Coverage Results
### Test Execution Summary
- **Total tests:** 38
- **Passed:** 38 
- **Failed:** 0 (after fix)
- **Execution time:** 0.57s

## Code Smells Identified
The following code smells were identified for step 2 - refactoring so far:

### 1. Long Method
**Location:** `ShoppingCart.handle_offers()`
- 50+ lines of code
- Multiple responsibilities (offer detection, calculation, discount creation)
- Complex nested conditionals
**Recommendation:** Extract offer calculation logic into separate calculator classes.

### 2. Feature Envy
**Location:** `ShoppingCart.handle_offers()`
- Accesses catalog.unit_price() extensively
- Accesses receipt.add_discount() directly
- Uses more external object methods than own class methods
**Recommendation:** Move offer handling to Teller or separate OfferEngine class.

### 3. Complex Conditional Logic
**Location:** `ShoppingCart.handle_offers()`
- Multiple nested if-statements for offer types
- Variable x used inconsistently
- Difficult to add new offer types
**Recommendation:** Implement Strategy pattern for offer calculations.

### 4. Magic Numbers
**Location:** Throughout offer calculations
- Numbers like 2, 3, 5 embedded in logic
- Percentages like 100.0 for calculations
**Recommendation:** Extract to named constants.

### 5. Duplicated Code
**Location:** Offer calculation blocks
- Similar patterns for TWO_FOR_AMOUNT and FIVE_FOR_AMOUNT
- Repeated total calculation logic
**Recommendation:** Extract common calculation methods.

## Bug Discovered and Fixed
### TWO_FOR_AMOUNT Calculation Error
**Location:** `shopping_cart.py:45`
**Problem Discovered:** Test `test_two_for_amount_three_items` failed during initial run.
**Root Cause:** Float division used instead of floor division
```python
# BEFORE (incorrect):
total = offer.argument * (quantity_as_int / x) + quantity_as_int % 2 * unit_price

# AFTER (correct):
total = offer.argument * (quantity_as_int // x) + quantity_as_int % 2 * unit_price
```