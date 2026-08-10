import logging
from matcher import find_soa_file, _match_key, CARRIER_DELIMITER

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 2. Paste the path you copied from Finder inside the quotes below
REAL_DRIVE_PATH = ' '

# 3. Type a full carrier name EXACTLY as it appears in your report, including the hyphen
TEST_CARRIER = " " 

# Show exactly what the system is extracting to verify the deterministic logic
extracted_key = _match_key(TEST_CARRIER, CARRIER_DELIMITER)
print(f"Original Input:  '{TEST_CARRIER}'")
print(f"Extracted Key:   '{extracted_key}'  <-- This is what the system will search for")
print("-" * 70)

# 4. Call your function and store the result
matched_path = find_soa_file(TEST_CARRIER, REAL_DRIVE_PATH)

# 5. Display the final result
print("-" * 70)
if matched_path:
    print("✅ SUCCESS! The exact matched path is:")
    print(matched_path)
else:
    print("❌ FAILED. No matching SOA file found.")
