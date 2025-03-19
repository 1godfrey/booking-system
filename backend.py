from flask import Flask, request, jsonify, render_template
import sqlite3
import datetime
import smtplib
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
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())

# Send SMS function (using Twilio)
def send_sms(to_phone, message):
    account_sid = 'your_twilio_account_sid'
    auth_token = 'your_twilio_auth_token'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_='+your_twilio_phone_number',
        to=to_phone
    )

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
    init_db()
    app.run(debug=True)