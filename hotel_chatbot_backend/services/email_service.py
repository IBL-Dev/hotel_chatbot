import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    
    @staticmethod
    def send_confirmation_email(to_email, booking_details):
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")

        if not sender_email or not sender_password:
            print("⚠️ Email credentials not found in .env. Skipping email.")
            return False

        subject = "🎉 Your Booking is Confirmed!"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #EDF6F9;
                }}
                .header {{
                    background: linear-gradient(135deg, #006D77 0%, #00565e 100%);
                    padding: 40px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    color: #ffffff;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    color: #83C5BE;
                    font-size: 16px;
                }}
                .content {{
                    padding: 40px 30px;
                    background-color: #ffffff;
                }}
                .greeting {{
                    color: #006D77;
                    font-size: 18px;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #333333;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .details-card {{
                    background-color: #EDF6F9;
                    border-left: 4px solid #006D77;
                    border-radius: 8px;
                    padding: 25px;
                    margin: 25px 0;
                }}
                .details-title {{
                    color: #006D77;
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                }}
                .detail-row {{
                    display: flex;
                    padding: 12px 0;
                    border-bottom: 1px solid #d1e7e5;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                .detail-label {{
                    font-weight: 600;
                    color: #006D77;
                    min-width: 140px;
                }}
                .detail-value {{
                    color: #333333;
                    flex: 1;
                }}
                .price-highlight {{
                    background-color: #006D77;
                    color: #ffffff;
                    padding: 15px 20px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 25px 0;
                }}
                .price-highlight .label {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-bottom: 5px;
                }}
                .price-highlight .amount {{
                    font-size: 32px;
                    font-weight: 700;
                }}
                .divider {{
                    height: 2px;
                    background: linear-gradient(to right, #83C5BE, #006D77, #83C5BE);
                    margin: 30px 0;
                    border-radius: 2px;
                }}
                .footer-message {{
                    background-color: #EDF6F9;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 30px;
                    text-align: center;
                }}
                .footer-message p {{
                    margin: 5px 0;
                    color: #006D77;
                    line-height: 1.6;
                }}
                .signature {{
                    margin-top: 30px;
                    color: #666666;
                }}
                .signature strong {{
                    color: #006D77;
                }}
                .footer {{
                    background-color: #006D77;
                    padding: 30px 20px;
                    text-align: center;
                    color: #83C5BE;
                    font-size: 14px;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                @media only screen and (max-width: 600px) {{
                    .content {{
                        padding: 30px 20px;
                    }}
                    .details-card {{
                        padding: 20px;
                    }}
                    .detail-row {{
                        flex-direction: column;
                    }}
                    .detail-label {{
                        margin-bottom: 5px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="header">
                    <h1>🎉 Booking Confirmed!</h1>
                    <p>Your reservation has been successfully processed</p>
                </div>

                <!-- Content -->
                <div class="content">
                    <div class="greeting">Dear Valued Guest,</div>
                    
                    <div class="message">
                        Thank you for choosing our hotel! We're delighted to confirm your reservation. 
                        Your comfort and satisfaction are our top priorities, and we look forward to 
                        providing you with an exceptional stay.
                    </div>

                    <!-- Booking Details -->
                    <div class="details-card">
                        <div class="details-title">📋 Reservation Details</div>
                        
                        <div class="detail-row">
                            <div class="detail-label">📅 Check-in Date:</div>
                            <div class="detail-value">{booking_details.get('checkin', 'N/A')}</div>
                        </div>
                        
                        <div class="detail-row">
                            <div class="detail-label">📅 Check-out Date:</div>
                            <div class="detail-value">{booking_details.get('checkout', 'N/A')}</div>
                        </div>
                        
                        <div class="detail-row">
                            <div class="detail-label">👥 Number of Guests:</div>
                            <div class="detail-value">{booking_details.get('guests', 'N/A')}</div>
                        </div>
                        
                        <div class="detail-row">
                            <div class="detail-label">🛏️ Room Type:</div>
                            <div class="detail-value">{booking_details.get('room_condition', 'N/A')}</div>
                        </div>
                        
                        <div class="detail-row">
                            <div class="detail-label">🚪 Room Number:</div>
                            <div class="detail-value">#{booking_details.get('selected_room', {}).get('roomNo', 'N/A')}</div>
                        </div>
                    </div>

                    <!-- Price Highlight -->
                    <div class="price-highlight">
                        <div class="label">Total Amount</div>
                        <div class="amount">${booking_details.get('selected_room', {}).get('price', 'N/A')}</div>
                    </div>

                    <div class="divider"></div>

                    <!-- Footer Message -->
                    <div class="footer-message">
                        <p><strong>📍 Check-in time:</strong> 3:00 PM | <strong>Check-out time:</strong> 11:00 AM</p>
                        <p>Need to make changes? Contact us anytime!</p>
                    </div>

                    <div class="signature">
                        <p>Warm regards,</p>
                        <p><strong>The Hotel Team</strong></p>
                        <p style="color: #83C5BE; margin-top: 5px;">Creating memorable experiences, one stay at a time</p>
                    </div>
                </div>

                <!-- Footer -->
                <div class="footer">
                    <p><strong>Questions?</strong> We're here to help!</p>
                    <p>Email: info@hotel.com | Phone: (123) 456-7890</p>
                    <p style="margin-top: 15px; font-size: 12px;">© 2024 Hotel. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            # Connect to Gmail's SMTP server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, to_email, msg.as_string())
            print(f"✅ Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False