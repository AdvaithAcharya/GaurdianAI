"""
Check Twilio configuration
"""
from config import settings

print("=" * 60)
print("🔧 TWILIO CONFIGURATION CHECK")
print("=" * 60 + "\n")

print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID[:10]}..." if settings.TWILIO_ACCOUNT_SID else "TWILIO_ACCOUNT_SID: (empty)")
print(f"TWILIO_AUTH_TOKEN: {settings.TWILIO_AUTH_TOKEN[:10]}..." if settings.TWILIO_AUTH_TOKEN else "TWILIO_AUTH_TOKEN: (empty)")
print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")

print("\n" + "=" * 60)

if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
    print("✅ All Twilio credentials are configured!")
else:
    print("❌ Twilio credentials are MISSING or incomplete")
    print("\nMake sure .env file contains:")
    print("TWILIO_ACCOUNT_SID=AC...")
    print("TWILIO_AUTH_TOKEN=...")
    print("TWILIO_PHONE_NUMBER=+1...")
