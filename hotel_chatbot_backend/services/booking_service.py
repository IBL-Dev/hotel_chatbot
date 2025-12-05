from services.base_service import BaseService
from utils.date_validator import DateValidator
from config.database import database
import re
from datetime import datetime, timedelta

class ServiceHandler(BaseService):

    def __init__(self):
        self.reset()
        self.completed = False

    def reset(self):
        self.booking_state = {
            "checkin": None,
            "checkout": None,
            "guests": None,
            "room_condition": None,
            "available_rooms": [],
            "selected_room": None,
            "modification_mode": False,
            "modifying_field": None,  # Track which field is being modified
            "waiting_for_guest_overflow_choice": False # Track if waiting for user choice after overflow
        }
        self.completed = False

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

        text = message.strip()

        # --------------------------------------
        # -1. GUEST OVERFLOW HANDLING
        # --------------------------------------
        if self.booking_state.get("waiting_for_guest_overflow_choice"):
            if text == "1":
                self.booking_state["guests"] = None
                self.booking_state["waiting_for_guest_overflow_choice"] = False
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

        # --------------------------------------
        # 0. MODIFICATION MODE
        # --------------------------------------
        if self.booking_state["modification_mode"]:
            if text == "1": # Check-in
                self.booking_state["checkin"] = None
                self.booking_state["checkout"] = None
                self.booking_state["selected_room"] = None
                self.booking_state["modification_mode"] = False
                self.booking_state["modifying_field"] = "checkin"
                return "Sure! When would you like to **check-in**? 📅"
            
            if text == "2": # Check-out
                self.booking_state["checkout"] = None
                self.booking_state["selected_room"] = None
                self.booking_state["modification_mode"] = False
                self.booking_state["modifying_field"] = "checkout"
                return "Okay! When is your new **check-out date**? 📅"
            
            if text == "3": # Room Condition
                self.booking_state["room_condition"] = None
                self.booking_state["available_rooms"] = []
                self.booking_state["selected_room"] = None
                self.booking_state["modification_mode"] = False
                self.booking_state["modifying_field"] = "room_condition"
                return "Would you like an **AC or Non-AC** room? ❄️🔥\n1. AC\n2. Non-AC"
            
            if text == "4": # Guests
                self.booking_state["guests"] = None
                self.booking_state["available_rooms"] = []
                self.booking_state["selected_room"] = None
                self.booking_state["modification_mode"] = False
                self.booking_state["modifying_field"] = "guests"
                return "How many **guests** will be staying? 👨‍👩‍👧"
            
            if text == "5": # Room Selection
                self.booking_state["selected_room"] = None
                self.booking_state["modification_mode"] = False
                self.booking_state["modifying_field"] = "room_selection"
                return self.format_room_list(self.booking_state["available_rooms"])

            return (
                "⚠️ Invalid option. Please select what you want to change:\n"
                "1. Check-in Date\n"
                "2. Check-out Date\n"
                "3. Room Condition (AC/Non-AC)\n"
                "4. Number of Guests\n"
                "5. Selected Room"
            )

        # --------------------------------------
        # 1. CHECK-IN DATE
        # --------------------------------------
        if self.booking_state["checkin"] is None:
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
                self.booking_state["checkin"] = parsed
                
                # If modifying check-in, validate existing check-out
                if self.booking_state["modifying_field"] == "checkin":
                    checkout_date = self.booking_state.get("checkout")
                    
                    if checkout_date:
                        ci = datetime.strptime(parsed, "%Y-%m-%d").date()
                        co = datetime.strptime(checkout_date, "%Y-%m-%d").date()
                        
                        # If check-out is now invalid, reset it and ask for new date
                        if co <= ci:
                            self.booking_state["checkout"] = None
                            self.booking_state["modifying_field"] = "checkout"
                            return (
                                f"✅ Check-in updated to **{parsed}**.\n\n"
                                "⚠️ Your previous check-out date is now invalid.\n"
                                "Please enter a new **check-out date**:"
                            )
                    
                    self.booking_state["modifying_field"] = None
                    return self.summary()
                
                return "Perfect! When is your **check-out date**? 📅"

            return (
                "⚠️ I couldn't understand that date.\n"
                "Please enter a valid check-in date within the next 30 days."
            )

        # --------------------------------------
        # 2. CHECK-OUT DATE
        # --------------------------------------
        if self.booking_state["checkout"] is None:
            parsed, reason = DateValidator.parse_date_verbose(text)
            checkin_date = self.booking_state["checkin"]
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

                self.booking_state["checkout"] = parsed
                
                # If modifying check-out, return to summary
                if self.booking_state["modifying_field"] == "checkout":
                    self.booking_state["modifying_field"] = None
                    return self.summary()
                return "Would you like an **AC or Non-AC** room? ❄️🔥\n1. AC\n2. Non-AC"

            return "⚠️ Please enter a valid check-out date within 7 days after check-in."

        # --------------------------------------
        # 3. ROOM CONDITION
        # --------------------------------------
        if self.booking_state["room_condition"] is None:
            cond = self.extract_room_condition(text.lower())
            if cond:
                self.booking_state["room_condition"] = cond
                
                # If modifying room condition, fetch rooms and return to summary
                if self.booking_state["modifying_field"] == "room_condition":
                    guests = self.booking_state["guests"]
                    rooms = self.get_available_rooms(guests, cond)
                    self.booking_state["available_rooms"] = rooms
                    
                    if not rooms:
                        return (
                            f"❌ Sorry, no **{cond}** rooms are available "
                            f"for **{guests} guests**.\n"
                            "Would you like to try different options?"
                        )
                    
                    # Auto-select first room if only one available, otherwise ask user to select
                    if len(rooms) == 1:
                        self.booking_state["selected_room"] = rooms[0]
                        self.booking_state["modifying_field"] = None
                        return self.summary()
                    else:
                        self.booking_state["modifying_field"] = "room_selection"
                        return self.format_room_list(rooms)
                return "How many **guests** will be staying? 👨‍👩‍👧"
            return f"⚠️ Sorry, '**{text}**' is not a valid option.\nPlease select:\n1. AC\n2. Non-AC"

        # --------------------------------------
        # 4. GUEST COUNT
        # --------------------------------------
        if self.booking_state["guests"] is None:
            guests = self.extract_guests(text)
            if guests:
                self.booking_state["guests"] = guests
                
                rooms = self.get_available_rooms(guests, self.booking_state["room_condition"])
                self.booking_state["available_rooms"] = rooms
                
                if not rooms:
                    self.booking_state["waiting_for_guest_overflow_choice"] = True
                    return (
                        f"❌ Sorry, no **{self.booking_state['room_condition']}** rooms are available "
                        f"for **{guests} guests**.\n\n"
                        "Please select an option:\n"
                        "1. Enter a different guest count 🔢\n"
                        "2. Close booking flow ❌"
                    )
                
                # If modifying guests, handle room selection
                if self.booking_state["modifying_field"] == "guests":
                    if len(rooms) == 1:
                        self.booking_state["selected_room"] = rooms[0]
                        self.booking_state["modifying_field"] = None
                        return self.summary()
                    else:
                        self.booking_state["modifying_field"] = "room_selection"
                        return self.format_room_list(rooms)

                return self.format_room_list(rooms)

            return "❌ Please enter a valid **number of guests**."

        # --------------------------------------
        # 5. ROOM SELECTION
        # --------------------------------------
        if self.booking_state["selected_room"] is None:
            rooms = self.booking_state["available_rooms"]
            count = len(rooms)

            if text.isdigit():
                idx = int(text) - 1
                
                if 0 <= idx < count:
                    self.booking_state["selected_room"] = rooms[idx]
                    
                    # If modifying room selection, return to summary
                    if self.booking_state["modifying_field"] == "room_selection":
                        self.booking_state["modifying_field"] = None
                    return self.summary()
            
            return (
                f"⚠️ Invalid selection. Please choose a room number between **1 and {count}**.\n"
                "(e.g., reply '1' for the first room)"
            )

        # --------------------------------------
        # 6. CONFIRMATION
        # --------------------------------------
        if text == "1": # Confirm
            self.completed = True
            
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
            self.booking_state["modification_mode"] = True
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
        if "1" in text: return "AC"
        if "2" in text: return "Non-AC"
        
        if "non ac" in text or "no ac" in text:
            return "Non-AC"
        if "ac" in text:
            return "AC"
        return None

    def format_room_list(self, rooms):
        msg = f"📌 **Available {self.booking_state['room_condition']} Rooms:**\n\n"
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
        room = s['selected_room']
        
        if not room:
            return "⚠️ Error: No room selected."

        # Calculate number of nights
        checkin_date = datetime.strptime(s['checkin'], "%Y-%m-%d").date()
        checkout_date = datetime.strptime(s['checkout'], "%Y-%m-%d").date()
        num_nights = (checkout_date - checkin_date).days
        
        # Calculate total bill
        room_price = room.get('price', 0)
        total_bill = num_nights * room_price

        return (
            "✨ **Your Booking Summary**\n"
            f"- Check-in: {s['checkin']}\n"
            f"- Check-out: {s['checkout']}\n"
            f"- Number of Nights: {num_nights}\n"
            f"- Guests: {s['guests']}\n"
            f"- Room Condition: {s['room_condition']}\n"
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
