from dotenv import load_dotenv
load_dotenv()
import os
import vonage

# Load environment variables
VONAGE_APPLICATION_ID = os.getenv("VONAGE_APPLICATION_ID")
VONAGE_PRIVATE_KEY = os.getenv("VONAGE_PRIVATE_KEY")

if not VONAGE_APPLICATION_ID or not VONAGE_PRIVATE_KEY:
    raise RuntimeError("Vonage credentials missing. Check Fly secrets.")

# Create Vonage auth (JWT-based)
auth = vonage.Auth(
    application_id=VONAGE_APPLICATION_ID,
    private_key=VONAGE_PRIVATE_KEY,
)

# Create Vonage client (THIS IS THE KEY FIX)
client = vonage.Vonage(auth=auth)

# Voice interface
voice = client.voice
