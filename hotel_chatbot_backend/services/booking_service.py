from services.base_service import BaseService
from services.auth_service import AuthService
from utils.date_validator import DateValidator
from config.database import database
import re
from datetime import datetime, timedelta
from models.booking_model import BookingModel

class ServiceHandler(BaseService):
    
    # Constants for State Keys
    KEY_CHECKIN = "checkin"
    KEY_CHECKOUT = "checkout"
    KEY_GUESTS = "guests"
    KEY_ROOM_CONDITION = "room_condition"
    KEY_AVAILABLE_ROOMS = "available_rooms"
    KEY_SELECTED_ROOM = "selected_room"
    KEY_MODIFICATION_MODE = "modification_mode"
    KEY_MODIFYING_FIELD = "modifying_field"
    KEY_WAITING_OVERFLOW = "waiting_for_guest_overflow_choice"

    # Constants for User Choices
    CHOICE_AC = "AC"
    CHOICE_NON_AC = "Non-AC"

    def __init__(self):
        self.auth_service = AuthService() # Initialize Auth Service
        self.reset()
        self.completed = False

    def reset(self):
        """Resets the booking state to initial values."""
        self.booking_state = {
            self.KEY_CHECKIN: None,
            self.KEY_CHECKOUT: None,
            self.KEY_GUESTS: None,
            self.KEY_ROOM_CONDITION: None,
            self.KEY_AVAILABLE_ROOMS: [],
            self.KEY_SELECTED_ROOM: None,
            self.KEY_MODIFICATION_MODE: False,
            self.KEY_MODIFYING_FIELD: None,
            self.KEY_WAITING_OVERFLOW: False
        }
        self.completed = False
        if hasattr(self, 'auth_service'):
            self.auth_service.reset()

    def is_complete(self):
        return self.completed

    # ===============================
    # FETCH AVAILABLE ROOMS
    # ===============================
    def get_available_rooms(self, guests, room_condition):
        try:
            query = {
                "noOfPerson": {"$gte": guests},
                "roomType": room_condition
            }
            
            projection = {
                "roomNo": 1, 
                "noOfPerson": 1, 
                "price": 1, 
                "images": 1, 
                "roomType": 1
            }

            rooms = list(database.db["rooms"].find(query, projection))
            return rooms

        except Exception as e:
            print(f"Error fetching rooms: {e}")
            return []

    # ===============================
    # MAIN BOOKING HANDLER
    # ===============================
    def handle(self, message: str):
        """
        Main handler that delegates to specific sub-handlers based on the current state.
        """
        text = message.strip()

        # 0. Handle Authentication (NEW)
        if not self.auth_service.is_authenticated():
            if self.auth_service.state == AuthService.STATE_IDLE:
                return self.auth_service.start_auth()
            return self.auth_service.handle(text)

        # 1. Handle Guest Overflow Choice
        if self.booking_state.get(self.KEY_WAITING_OVERFLOW):
            return self._handle_guest_overflow(text)

        # 2. Handle Modification Mode Selection
        if self.booking_state[self.KEY_MODIFICATION_MODE]:
            return self._handle_modification_mode(text)

        # 3. Handle Check-in Date
        if self.booking_state[self.KEY_CHECKIN] is None:
            return self._handle_checkin(text)

        # 4. Handle Check-out Date
        if self.booking_state[self.KEY_CHECKOUT] is None:
            return self._handle_checkout(text)

        # 5. Handle Room Condition
        if self.booking_state[self.KEY_ROOM_CONDITION] is None:
            return self._handle_room_condition(text)

        # 6. Handle Guest Count
        if self.booking_state[self.KEY_GUESTS] is None:
            return self._handle_guest_count(text)

        # 7. Handle Room Selection
        if self.booking_state[self.KEY_SELECTED_ROOM] is None:
            return self._handle_room_selection(text)

        # 8. Handle Confirmation
        return self._handle_confirmation(text)

    # ===============================
    # SUB-HANDLERS
    # ===============================
    def _handle_guest_overflow(self, text: str):
        if text == "1":
            self.booking_state[self.KEY_GUESTS] = None
            self.booking_state[self.KEY_WAITING_OVERFLOW] = False
            return "Please enter the number of guests: 👨‍👩‍👧"
        elif text == "2":
            self.reset()
            return "Thank you for visiting! We hope to see you again soon. 👋"
        else:
            return (
                "⚠️ Invalid option.\n"
                "Please select:\n"
                "1. Enter a different guest count 🔢\n"
                "2. Close booking flow ❌"
            )

    def _handle_modification_mode(self, text: str):
        options = {
            "1": (self.KEY_CHECKIN, "Sure! When would you like to **check-in**? 📅"),
            "2": (self.KEY_CHECKOUT, "Okay! When is your new **check-out date**? 📅"),
            "3": (self.KEY_ROOM_CONDITION, "Would you like an **AC or Non-AC** room? ❄️🔥\n1. AC\n2. Non-AC"),
            "4": (self.KEY_GUESTS, "How many **guests** will be staying? 👨‍👩‍👧"),
            "5": (self.KEY_SELECTED_ROOM, None) # Special case for room selection
        }

        if text in options:
            field, prompt = options[text]
            
            # Reset relevant fields
            self.booking_state[self.KEY_MODIFICATION_MODE] = False
            self.booking_state[self.KEY_MODIFYING_FIELD] = field
            
            # Specific resets based on field dependencies
            if field == self.KEY_CHECKIN:
                self.booking_state[self.KEY_CHECKIN] = None
                self.booking_state[self.KEY_CHECKOUT] = None
                self.booking_state[self.KEY_SELECTED_ROOM] = None
            elif field == self.KEY_CHECKOUT:
                self.booking_state[self.KEY_CHECKOUT] = None
                self.booking_state[self.KEY_SELECTED_ROOM] = None
            elif field == self.KEY_ROOM_CONDITION:
                self.booking_state[self.KEY_ROOM_CONDITION] = None
                self.booking_state[self.KEY_AVAILABLE_ROOMS] = []
                self.booking_state[self.KEY_SELECTED_ROOM] = None
            elif field == self.KEY_GUESTS:
                self.booking_state[self.KEY_GUESTS] = None
                self.booking_state[self.KEY_AVAILABLE_ROOMS] = []
                self.booking_state[self.KEY_SELECTED_ROOM] = None
            elif field == self.KEY_SELECTED_ROOM:
                self.booking_state[self.KEY_SELECTED_ROOM] = None
                return self.format_room_list(self.booking_state[self.KEY_AVAILABLE_ROOMS])

            return prompt

        return (
            "⚠️ Invalid option. Please select what you want to change:\n"
            "1. Check-in Date\n"
            "2. Check-out Date\n"
            "3. Room Condition (AC/Non-AC)\n"
            "4. Number of Guests\n"
            "5. Selected Room"
        )

    def _handle_checkin(self, text: str):
        parsed, reason = DateValidator.parse_date_verbose(text)

        if reason == "none":
            return (
                "Sure! 😊\n"
                "When would you like to **check-in**?\n"
                "(Please choose a date within the next 30 days.)"
            )

        if reason == "past":
            return (
                "⚠️ The date you entered is in the past.\n"
                "Please choose a future date within the next 30 days."
            )

        if reason == "too_far":
            return (
                f"⚠️ Sorry! We only accept bookings within the next 30 days.\n\n"
                f"The date you entered (**{text}**) is too far ahead.\n"
                "Please select an earlier date."
            )

        if parsed:
            self.booking_state[self.KEY_CHECKIN] = parsed
            
            # If modifying check-in, validate existing check-out
            if self.booking_state[self.KEY_MODIFYING_FIELD] == self.KEY_CHECKIN:
                checkout_date = self.booking_state.get(self.KEY_CHECKOUT)
                
                if checkout_date:
                    ci = datetime.strptime(parsed, "%Y-%m-%d").date()
                    co = datetime.strptime(checkout_date, "%Y-%m-%d").date()
                    
                    # If check-out is now invalid, reset it and ask for new date
                    if co <= ci:
                        self.booking_state[self.KEY_CHECKOUT] = None
                        self.booking_state[self.KEY_MODIFYING_FIELD] = self.KEY_CHECKOUT
                        return (
                            f"✅ Check-in updated to **{parsed}**.\n\n"
                            "⚠️ Your previous check-out date is now invalid.\n"
                            "Please enter a new **check-out date**:"
                        )
                
                self.booking_state[self.KEY_MODIFYING_FIELD] = None
                return self.summary()
            
            return "Perfect! When is your **check-out date**? 📅"

        return (
            "⚠️ I couldn't understand that date.\n"
            "Please enter a valid check-in date within the next 30 days."
        )

    def _handle_checkout(self, text: str):
        parsed, reason = DateValidator.parse_date_verbose(text)
        checkin_date = self.booking_state[self.KEY_CHECKIN]
        ci = datetime.strptime(checkin_date, "%Y-%m-%d").date()

        if reason == "none":
            return (
                "⚠️ I couldn't understand that check-out date.\n"
                "Please enter a date within **7 days after your check-in date**."
            )

        if parsed:
            co = datetime.strptime(parsed, "%Y-%m-%d").date()

            if co <= ci:
                return (
                    f"⚠️ The check-out date you entered (**{text}**) is before your check-in date.\n"
                    "Please enter a valid check-out date."
                )

            max_allowed = ci + timedelta(days=7)

            if co > max_allowed:
                return (
                    f"⚠️ The check-out date you entered (**{text}**) is too far.\n"
                    "You can stay **up to 7 days** from your check-in date.\n\n"
                    f"Valid check-out range: **{ci} to {max_allowed}**.\n"
                    "Please enter a date within this range."
                )

            self.booking_state[self.KEY_CHECKOUT] = parsed
            
            # If modifying check-out, return to summary
            if self.booking_state[self.KEY_MODIFYING_FIELD] == self.KEY_CHECKOUT:
                self.booking_state[self.KEY_MODIFYING_FIELD] = None
                return self.summary()
            return "Would you like an **AC or Non-AC** room? ❄️🔥\n1. AC\n2. Non-AC"

        return "⚠️ Please enter a valid check-out date within 7 days after check-in."

    def _handle_room_condition(self, text: str):
        cond = self.extract_room_condition(text.lower())
        if cond:
            self.booking_state[self.KEY_ROOM_CONDITION] = cond
            
            # If modifying room condition, fetch rooms and return to summary
            if self.booking_state[self.KEY_MODIFYING_FIELD] == self.KEY_ROOM_CONDITION:
                guests = self.booking_state[self.KEY_GUESTS]
                rooms = self.get_available_rooms(guests, cond)
                self.booking_state[self.KEY_AVAILABLE_ROOMS] = rooms
                
                if not rooms:
                    return (
                        f"❌ Sorry, no **{cond}** rooms are available "
                        f"for **{guests} guests**.\n"
                        "Would you like to try different options?"
                    )
                
                # Auto-select first room if only one available, otherwise ask user to select
                if len(rooms) == 1:
                    self.booking_state[self.KEY_SELECTED_ROOM] = rooms[0]
                    self.booking_state[self.KEY_MODIFYING_FIELD] = None
                    return self.summary()
                else:
                    self.booking_state[self.KEY_MODIFYING_FIELD] = self.KEY_SELECTED_ROOM
                    return self.format_room_list(rooms)
            return "How many **guests** will be staying? 👨‍👩‍👧"
        return f"⚠️ Sorry, '**{text}**' is not a valid option.\nPlease select:\n1. AC\n2. Non-AC"

    def _handle_guest_count(self, text: str):
        guests = self.extract_guests(text)
        if guests:
            self.booking_state[self.KEY_GUESTS] = guests
            
            rooms = self.get_available_rooms(guests, self.booking_state[self.KEY_ROOM_CONDITION])
            self.booking_state[self.KEY_AVAILABLE_ROOMS] = rooms
            
            if not rooms:
                self.booking_state[self.KEY_WAITING_OVERFLOW] = True
                return (
                    f"❌ Sorry, no **{self.booking_state[self.KEY_ROOM_CONDITION]}** rooms are available "
                    f"for **{guests} guests**.\n\n"
                    "Please select an option:\n"
                    "1. Enter a different guest count 🔢\n"
                    "2. Close booking flow ❌"
                )
            
            # If modifying guests, handle room selection
            if self.booking_state[self.KEY_MODIFYING_FIELD] == self.KEY_GUESTS:
                if len(rooms) == 1:
                    self.booking_state[self.KEY_SELECTED_ROOM] = rooms[0]
                    self.booking_state[self.KEY_MODIFYING_FIELD] = None
                    return self.summary()
                else:
                    self.booking_state[self.KEY_MODIFYING_FIELD] = self.KEY_SELECTED_ROOM
                    return self.format_room_list(rooms)

            return self.format_room_list(rooms)

        return "❌ Please enter a valid **number of guests**."

    def _handle_room_selection(self, text: str):
        rooms = self.booking_state[self.KEY_AVAILABLE_ROOMS]
        count = len(rooms)

        if text.isdigit():
            idx = int(text) - 1
            
            if 0 <= idx < count:
                self.booking_state[self.KEY_SELECTED_ROOM] = rooms[idx]
                
                # If modifying room selection, return to summary
                if self.booking_state[self.KEY_MODIFYING_FIELD] == self.KEY_SELECTED_ROOM:
                    self.booking_state[self.KEY_MODIFYING_FIELD] = None
                return self.summary()
        
        return (
            f"⚠️ Invalid selection. Please choose a room number between **1 and {count}**.\n"
            "(e.g., reply '1' for the first room)"
        )

    def _handle_confirmation(self, text: str):
        if text == "1": # Confirm
            self.completed = True
            
            # Save Booking to Database
            try:
                current_user = self.auth_service.current_user
                user_id = str(current_user.get("_id")) if current_user else None
                
                # Retrieve selected room details
                room = self.booking_state[self.KEY_SELECTED_ROOM]
                
                # Prepare dates
                checkin_str = self.booking_state[self.KEY_CHECKIN]
                checkout_str = self.booking_state[self.KEY_CHECKOUT]
                checkin_date = datetime.strptime(checkin_str, "%Y-%m-%d")
                checkout_date = datetime.strptime(checkout_str, "%Y-%m-%d")
                
                # Calculate total price
                num_nights = (checkout_date.date() - checkin_date.date()).days
                price_per_night = room.get('price', 0)
                total_price = num_nights * price_per_night

                booking_data = {
                    "userId": user_id,
                    "room": room.get("_id"),
                    "roomNo": room.get("roomNo"),
                    "checkInDate": checkin_date,
                    "checkOutDate": checkout_date,
                    "noOfPerson": self.booking_state[self.KEY_GUESTS],
                    "totalPrice": total_price,
                    "pricePerNight": price_per_night,
                    "roomType": room.get("roomType"),
                    "status": "PENDING"
                }
                
                booking_id = BookingModel.create_booking(booking_data)
                print(f"Booking saved with ID: {booking_id}")
                
            except Exception as e:
                print(f"Error saving booking: {e}")
                # Optionally handle error (e.g., notify user), but we proceed to email for now

            # Send Confirmation Email
            from services.email_service import EmailService
            recipient = "anjanatinush2001@gmail.com"
            email_sent = EmailService.send_confirmation_email(recipient, self.booking_state)
            
            msg = "🎉 **Booking Confirmed!**\nThank you for choosing our hotel. We look forward to hosting you! 😊"
            if email_sent:
                msg += f"\n\n📧 A confirmation email has been sent to **{recipient}**."
            else:
                msg += "\n\n⚠️ (Note: Email sending failed. Please check server logs.)"
                
            return msg
        
        if text == "2": # Change Details
            self.booking_state[self.KEY_MODIFICATION_MODE] = True
            return (
                "What would you like to change?\n"
                "1. Check-in Date\n"
                "2. Check-out Date\n"
                "3. Room Condition (AC/Non-AC)\n"
                "4. Number of Guests\n"
                "5. Selected Room"
            )

        return self.summary()

    # ===============================
    # HELPERS
    # ===============================
    def extract_guests(self, text):
        date_patterns = [
            r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b",
            r"\b20\d{2}[-/]\d{1,2}\b",
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",
        ]
        for p in date_patterns:
            if re.search(p, text):
                return None

        if text.isdigit():
            return int(text) if int(text) >= 1 else None

        words = {
            "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10
        }

        if text.lower() in words:
            return words[text.lower()]

        match = re.search(r"\b(\d+)\b", text)
        if match:
            return int(match.group(1))

        return None

    def extract_room_condition(self, text):
        if "1" in text: return self.CHOICE_AC
        if "2" in text: return self.CHOICE_NON_AC
        
        if "non ac" in text or "no ac" in text:
            return self.CHOICE_NON_AC
        if "ac" in text:
            return self.CHOICE_AC
        return None

    def format_room_list(self, rooms):
        msg = f"📌 **Available {self.booking_state[self.KEY_ROOM_CONDITION]} Rooms:**\n\n"
        for i, room in enumerate(rooms, 1):
            msg += f"**{i}. Room {room.get('roomNo')}**\n"
            msg += f"   - Capacity: {room.get('noOfPerson')} Guests\n"
            msg += f"   - Price: LKR {room.get('price', 'N/A')}\n"
            
            images = room.get('images', [])
            if images and isinstance(images, list) and len(images) > 0:
                msg += f"   - Image: {images[0]}\n"
            
            msg += "\n"
        
        msg += "👉 Please reply with the **Room Number** you want to book (e.g., 1)."
        return msg

    # ===============================
    # SUMMARY
    # ===============================
    def summary(self):
        s = self.booking_state
        room = s[self.KEY_SELECTED_ROOM]
        
        if not room:
            return "⚠️ Error: No room selected."

        # Calculate number of nights
        checkin_date = datetime.strptime(s[self.KEY_CHECKIN], "%Y-%m-%d").date()
        checkout_date = datetime.strptime(s[self.KEY_CHECKOUT], "%Y-%m-%d").date()
        num_nights = (checkout_date - checkin_date).days
        
        # Calculate total bill
        room_price = room.get('price', 0)
        total_bill = num_nights * room_price

        return (
            "✨ **Your Booking Summary**\n"
            f"- Check-in: {s[self.KEY_CHECKIN]}\n"
            f"- Check-out: {s[self.KEY_CHECKOUT]}\n"
            f"- Number of Nights: {num_nights}\n"
            f"- Guests: {s[self.KEY_GUESTS]}\n"
            f"- Room Condition: {s[self.KEY_ROOM_CONDITION]}\n"
            "----------------------------------\n"
            f"🏠 **Selected Room: {room.get('roomNo')}**\n"
            f"- Type: {room.get('roomType')}\n"
            f"- Capacity: {room.get('noOfPerson')} Guests\n"
            f"- Price per Night: LKR {room_price}\n"
            f"- **Total Bill: LKR {total_bill}**\n"
            "\n"
            "**Please select an option:**\n"
            "1. **Confirm Booking** ✅\n"
            "2. **Change Details** ✏️"
        )
