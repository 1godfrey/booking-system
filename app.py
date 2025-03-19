from flask import Flask, request, jsonify, render_template
import sqlite3
import datetime
import smtplib, os
from email.mime.text import MIMEText
from twilio.rest import Client

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  email TEXT,
                  phone TEXT,
                  service TEXT,
                  date TEXT,
                  time TEXT)''')
    conn.commit()
    conn.close()

# Send email function
def send_email(to_email, subject, body):
    sender_email = os.getenv('EMAIL_USER')
    sender_password = os.getenv('EMAIL_PASSWORD')
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as email:
        print(f"Failed to send email: {email}")

# !!!!!!!!!!!  DEFINE THE ENV VARIABLES !!!!!!!!!!!!!!!!!!!!!!!!!

# Send SMS function (using Twilio)
def send_sms(to_phone, message):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to_phone
        )
        print(f"SMS sent to {to_phone}: {message.sid}")
    except Exception as esms:
        print(f"Failed to send email: {esms}")

# Booking route
@app.route('/book', methods=['POST'])
def book_appointment():
    data = request.json
    name = data['name']
    email = data['email']
    phone = data['phone']
    service = data['service']
    date = data['date']
    time = data['time']

    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("INSERT INTO bookings (name, email, phone, service, date, time) VALUES (?, ?, ?, ?, ?, ?)",
              (name, email, phone, service, date, time))
    conn.commit()
    conn.close()

    # Send confirmation email
    email_body = f"Hi {name}, your appointment for {service} on {date} at {time} is confirmed!"
    send_email(email, "Appointment Confirmation", email_body)

    # Send confirmation SMS
    sms_body = f"Hi {name}, your appointment for {service} on {date} at {time} is confirmed!"
    send_sms(phone, sms_body)

    return jsonify({"message": "Booking confirmed!"})

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()  # Initialize the database
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT or default to 5000
    app.run(host='0.0.0.0', port=port)  # Bind to the correct port