
class RegistrationPrompts:
    ASK_EMAIL = "To proceed with your booking, please provide your **email address**. 📧"
    
    ASK_NAME = "It looks like you're new here! Let's get you registered.\n\nWhat is your **name**? 👤"
    
    ASK_PASSWORD = (
        "Please create a **password** for your account. 🔒\n"
        "(Make sure it's secure!)"
    )
    
    ASK_CONFIRM_PASSWORD = "Please **confirm your password**. 🔐"
    
    WELCOME_BACK = (
        "Welcome back, **{name}**! 👋\n"
        "Let's continue with your booking.\n\n"
        "When would you like to **check-in**? 📅\n"
        "(Please enter a date within the next 30 days.)"
    )
    
    REGISTRATION_SUCCESS = (
        "🎉 **Registration Successful!**\n"
        "You are now logged in as **{name}**.\n\n"
        "Now, let's get back to it. When would you like to **check-in**? 📅\n"
        "(Please enter a date within the next 30 days.)"
    )

    INVALID_EMAIL = "⚠️ That doesn't look like a valid email address. Please try again."
    
    EMAIL_NOT_FOUND_CHOICE = (
        "I couldn't find an account with the email **{email}**. 🤔\n\n"
        "How would you like to proceed?\n"
        "1. **Re-enter email** (if there was a typo) ✏️\n"
        "2. **Register as a new user** ✨"
    )
    
    PASSWORD_MISMATCH = "⚠️ Passwords do not match. Please try confirming your password again."
    
    GENERIC_ERROR = "⚠️ Something went wrong. Please try again."
