from services.base_service import BaseService
from config.database import database
from promt.registration_prompts import RegistrationPrompts
import re
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class AuthService(BaseService):
    # States
    STATE_IDLE = "IDLE"
    STATE_WAITING_EMAIL = "WAITING_EMAIL"
    STATE_WAITING_EMAIL_CHOICE = "WAITING_EMAIL_CHOICE"
    STATE_WAITING_NAME = "WAITING_NAME"
    STATE_WAITING_PASSWORD = "WAITING_PASSWORD"
    STATE_WAITING_CONFIRM_PASSWORD = "WAITING_CONFIRM_PASSWORD"
    STATE_AUTHENTICATED = "AUTHENTICATED"

    def __init__(self):
        self.reset()
        self.user_data = {}  # Temporary storage for registration details

    def reset(self):
        self.state = self.STATE_IDLE
        self.user_data = {}
        self.current_user = None

    def is_authenticated(self):
        return self.current_user is not None

    def start_auth(self):
        self.state = self.STATE_WAITING_EMAIL
        return RegistrationPrompts.ASK_EMAIL

    def handle(self, message: str):
        text = message.strip()

        if self.state == self.STATE_WAITING_EMAIL:
            return self._handle_email(text)

        if self.state == self.STATE_WAITING_EMAIL_CHOICE:
            return self._handle_email_choice(text)

        if self.state == self.STATE_WAITING_NAME:
            return self._handle_name(text)

        if self.state == self.STATE_WAITING_PASSWORD:
            return self._handle_password(text)

        if self.state == self.STATE_WAITING_CONFIRM_PASSWORD:
            return self._handle_confirm_password(text)

        return RegistrationPrompts.GENERIC_ERROR

    def _handle_email(self, email):
        # Basic Email Validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return RegistrationPrompts.INVALID_EMAIL

        self.user_data["email"] = email
        
        # Check if user exists
        user = self._get_user_by_email(email)
        
        if user:
            # Login successful
            self.current_user = user
            self.state = self.STATE_AUTHENTICATED
            return RegistrationPrompts.WELCOME_BACK.format(name=user.get("name", "User"))
        else:
            # Email not found - Ask user what to do
            self.state = self.STATE_WAITING_EMAIL_CHOICE
            return RegistrationPrompts.EMAIL_NOT_FOUND_CHOICE.format(email=email)

    def _handle_email_choice(self, choice):
        if "1" in choice:
            self.state = self.STATE_WAITING_EMAIL
            return RegistrationPrompts.ASK_EMAIL
        elif "2" in choice:
            self.state = self.STATE_WAITING_NAME
            return RegistrationPrompts.ASK_NAME
        else:
            return (
                "⚠️ Invalid option. Please select:\n"
                "1. Re-enter email ✏️\n"
                "2. Register as a new user ✨"
            )

    def _handle_name(self, name):
        self.user_data["name"] = name
        self.state = self.STATE_WAITING_PASSWORD
        return RegistrationPrompts.ASK_PASSWORD

    def _handle_password(self, password):
        self.user_data["password"] = password
        self.state = self.STATE_WAITING_CONFIRM_PASSWORD
        return RegistrationPrompts.ASK_CONFIRM_PASSWORD

    def _handle_confirm_password(self, confirm_password):
        if confirm_password != self.user_data["password"]:
            return RegistrationPrompts.PASSWORD_MISMATCH

        # Hash Password using bcrypt
        hashed_password = bcrypt.generate_password_hash(self.user_data["password"]).decode('utf-8')
        
        # Save User
        new_user = {
            "name": self.user_data["name"],
            "email": self.user_data["email"],
            "password": hashed_password,
            "role": "user",
            # Add timestamps if needed, relying on Mongo or manual
        }
        
        self._save_user(new_user)
        
        self.current_user = new_user
        self.state = self.STATE_AUTHENTICATED
        
        return RegistrationPrompts.REGISTRATION_SUCCESS.format(name=self.user_data["name"])

    def _get_user_by_email(self, email):
        try:
            return database.db["users"].find_one({"email": email})
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

    def _save_user(self, user_dict):
        try:
            from datetime import datetime
            user_dict["createdAt"] = datetime.utcnow()
            user_dict["updatedAt"] = datetime.utcnow()
            user_dict["__v"] = 0
            database.db["users"].insert_one(user_dict)
        except Exception as e:
            print(f"Error saving user: {e}")
