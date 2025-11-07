import os, sys
from hmac import compare_digest

expected = os.getenv("HACKATHON_ENTRY_KEY")  # secret kept OUTSIDE code
if not expected:
    print("🔒 Entry key not configured. Set HACKATHON_ENTRY_KEY.")
    sys.exit(1)

entry = input("Enter entry key: ").strip()
if not compare_digest(entry, expected):
    print("🔒 Invalid key — exiting.")
    sys.exit(1)
