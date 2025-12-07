
class RegistrationPrompts:
    ASK_EMAIL = "To proceed with your booking, please provide your **email address**. 📧"
    
    ASK_NAME = "It looks like you're new here! Let's get you registered.\n\nWhat is your **name**? 👤"
    
    ASK_PASSWORD = (
        "Please create a **password** for your account. 🔒\n"
        "(Make sure it's secure!)"
    )
    
    ASK_CONFIRM_PASSWORD = "Please **confirm your password**. 🔐"
    
    WELCOME_BACK = "Welcome back, **{name}**! 👋\nLet's continue with your booking."
    
    REGISTRATION_SUCCESS = "🎉 **Registration Successful!**\nYou are now logged in as **{name}**.\n\nNow, let's get back to it. When would you like to **check-in**? 📅"

    INVALID_EMAIL = "⚠️ that doesn't look like a valid email address. Please try again."
    
    PASSWORD_MISMATCH = "⚠️ Passwords do not match. Please try confirming your password again."
    
    GENERIC_ERROR = "⚠️ Something went wrong. Please try again."
