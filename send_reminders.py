import sqlite3, os
from datetime import datetime, timedelta
from twilio.rest import Client

# Database connection
conn = sqlite3.connect('bookings.db')
c = conn.cursor()

# Get tomorrow's appointments
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
c.execute("SELECT name, phone, service, time FROM bookings WHERE date = ?", (tomorrow,))
appointments = c.fetchall()

# Send SMS reminders
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

for name, phone, service, time in appointments:
    message = f"Hi {name}, this is a reminder for your {service} appointment tomorrow at {time}."
    client.messages.create(
        body=message,
        from_= os.getenv('TWILIO_PHONE_NUMBER'),
        to=phone
    )

conn.close()