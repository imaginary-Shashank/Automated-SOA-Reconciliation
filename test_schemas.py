from pydantic import ValidationError
from decimal import Decimal

# Import the updated schemas
from schemas import TerminationCharge, ReconciliationBatch

print("-" * 60)
print("Testing Updated Pydantic Schema Validation (No Dates)")
print("-" * 60)

# TEST 1: Exact row from your screenshot (Row 2)
try:
    row_2_charge = TerminationCharge(
        carrier_name="6GTech Systems - YO0619",
        amount=0.0716,
        status="Done",
        comment=None  # Column D is empty in the screenshot
    )
    print("✅ TEST 1 PASSED: Standard Excel Row")
    print(f"   Carrier: {row_2_charge.carrier_name}")
    print(f"   Amount (as strict Decimal): {repr(row_2_charge.amount)}")
    print(f"   Status: {row_2_charge.status}")
except ValidationError as e:
    print(f"❌ TEST 1 FAILED:\n{e}")

# TEST 2: Messy Excel data and partial columns
try:
    messy_charge = TerminationCharge(
        carrier_name="  Comoretel Holdings - NA0419  ",  # Messy whitespace
        amount="$30.7413",  # Formatted as currency string
        # Intentionally leaving out status and comment to test optional fields
    )
    print("\n✅ TEST 2 PASSED: Data Cleaning & Optional Fields")
    print(f"   Stripped Carrier: '{messy_charge.carrier_name}'")
    print(f"   Cleaned Amount: {repr(messy_charge.amount)}")
    print(f"   Status defaults to: {messy_charge.status}")
except ValidationError as e:
    print(f"❌ TEST 2 FAILED:\n{e}")

# TEST 3: Batch Calculation
try:
    batch = ReconciliationBatch(records=[row_2_charge, messy_charge])
    print("\n✅ TEST 3 PASSED: Batch Logic")
    print(f"   Total records: {len(batch.records)}")
    print(f"   Calculated Total Amount: {batch.total_amount}")
except Exception as e:
    print(f"❌ TEST 3 FAILED:\n{e}")

# TEST 4: The Bouncer (Testing Defensive Error Catching)
try:
    print("\n--- Testing The Bouncer (Expect an error here) ---")
    bad_charge = TerminationCharge(
        carrier_name="",  # Fails min_length validation
        amount="Free",    # Cannot be coerced to Decimal
    )
    print("❌ TEST 4 FAILED: Pydantic should have blocked this!")
except ValidationError as e:
    print("✅ TEST 4 PASSED: Pydantic successfully blocked corrupted data.")
    print(f"   Caught {e.error_count()} distinct errors in the raw data.")
    
print("-" * 60)