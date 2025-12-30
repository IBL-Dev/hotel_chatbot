from services.base_service import BaseService
from config.database import database
from promt.registration_prompts import RegistrationPrompts
import re
from flask_bcrypt import Bcrypt
from utils.id_generator import generate_user_id

bcrypt = Bcrypt()

class AuthService(BaseService):
    # States
    STATE_IDLE = "IDLE"
    STATE_WAITING_EMAIL = "WAITING_EMAIL"
    STATE_WAITING_EMAIL_CHOICE = "WAITING_EMAIL_CHOICE"
    STATE_WAITING_NAME = "WAITING_NAME"
    STATE_WAITING_NIC = "WAITING_NIC"
    STATE_WAITING_PHONE = "WAITING_PHONE"
    STATE_WAITING_PASSWORD = "WAITING_PASSWORD"
    STATE_WAITING_CONFIRM_PASSWORD = "WAITING_CONFIRM_PASSWORD"
    STATE_WAITING_REGISTRATION_CONFIRMATION = "WAITING_REGISTRATION_CONFIRMATION"
    STATE_WAITING_REGISTRATION_UPDATE_CHOICE = "WAITING_REGISTRATION_UPDATE_CHOICE"
    STATE_AUTHENTICATED = "AUTHENTICATED"

    def __init__(self):
        self.reset()
        self.user_data = {}  # Temporary storage for registration details
        self.is_updating = False

    def reset(self):
        self.state = self.STATE_IDLE
        self.user_data = {}
        self.current_user = None
        self.is_updating = False

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

        if self.state == self.STATE_WAITING_NIC:
            return self._handle_nic(text)

        if self.state == self.STATE_WAITING_PHONE:
            return self._handle_phone(text)

        if self.state == self.STATE_WAITING_PASSWORD:
            return self._handle_password(text)

        if self.state == self.STATE_WAITING_CONFIRM_PASSWORD:
            return self._handle_confirm_password(text)

        if self.state == self.STATE_WAITING_REGISTRATION_CONFIRMATION:
            return self._handle_registration_confirmation(text)

        if self.state == self.STATE_WAITING_REGISTRATION_UPDATE_CHOICE:
            return self._handle_registration_update_choice(text)

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
        if self.is_updating:
            return self._get_confirmation_summary()
        self.state = self.STATE_WAITING_NIC
        return RegistrationPrompts.ASK_NIC

    def _handle_nic(self, nic):
        self.user_data["nic"] = nic
        if self.is_updating:
            return self._get_confirmation_summary()
        self.state = self.STATE_WAITING_PHONE
        return RegistrationPrompts.ASK_PHONE

    def _handle_phone(self, phone):
        self.user_data["phone"] = phone
        if self.is_updating:
            return self._get_confirmation_summary()
        self.state = self.STATE_WAITING_PASSWORD
        return RegistrationPrompts.ASK_PASSWORD

    def _handle_password(self, password):
        self.user_data["password"] = password
        self.state = self.STATE_WAITING_CONFIRM_PASSWORD
        return RegistrationPrompts.ASK_CONFIRM_PASSWORD

    def _handle_confirm_password(self, confirm_password):
        if confirm_password != self.user_data["password"]:
            return RegistrationPrompts.PASSWORD_MISMATCH

        return self._get_confirmation_summary()

    def _get_confirmation_summary(self):
        """Helper to return the registration summary and set state to confirmation."""
        self.state = self.STATE_WAITING_REGISTRATION_CONFIRMATION
        self.is_updating = False # Reset update flag
        return RegistrationPrompts.REGISTRATION_CONFIRMATION.format(
            name=self.user_data.get("name", "N/A"),
            email=self.user_data.get("email", "N/A"),
            nic=self.user_data.get("nic", "N/A"),
            phone=self.user_data.get("phone", "N/A")
        )

    def _handle_registration_confirmation(self, text: str):
        if text == "1": # Confirm
            # Hash Password using bcrypt
            hashed_password = bcrypt.generate_password_hash(self.user_data["password"]).decode('utf-8')
            
            # Save User
            new_user = {
                "userId": generate_user_id(database.db),
                "name": self.user_data["name"],
                "email": self.user_data["email"],
                "password": hashed_password,
                "phoneNumber": self.user_data.get("phone"),
                "nicNumber": self.user_data.get("nic"),
                "role": "user",
                "profileImage": "https://th.bing.com/th/id/OIP.x7X2oAehk5M9IvGwO_K0PgHaHa?w=189&h=189&c=7&r=0&o=7&cb=ucfimg2&dpr=1.3&pid=1.7&rm=3&ucfimg=1"
            }
            
            self._save_user(new_user)
            self.current_user = new_user
            self.state = self.STATE_AUTHENTICATED
            
            return RegistrationPrompts.REGISTRATION_SUCCESS.format(name=self.user_data["name"])

        if text == "2": # Change
            self.state = self.STATE_WAITING_REGISTRATION_UPDATE_CHOICE
            return RegistrationPrompts.UPDATE_CHOICE

        return self._get_confirmation_summary()

    def _handle_registration_update_choice(self, text: str):
        options = {
            "1": (self.STATE_WAITING_NAME, RegistrationPrompts.ASK_NAME),
            "2": (self.STATE_WAITING_NIC, RegistrationPrompts.ASK_NIC),
            "3": (self.STATE_WAITING_PHONE, RegistrationPrompts.ASK_PHONE),
            "4": (self.STATE_WAITING_PASSWORD, RegistrationPrompts.ASK_PASSWORD)
        }

        if text in options:
            state, prompt = options[text]
            self.state = state
            self.is_updating = True # Set update flag
            return prompt

        return RegistrationPrompts.UPDATE_CHOICE

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
