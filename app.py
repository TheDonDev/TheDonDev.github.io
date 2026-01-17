from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return "Backend is running!"

@app.route('/submit', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'error': 'Missing required fields'}), 400

    # Email Configuration
    sender_email = os.environ.get('MAIL_USERNAME')
    sender_password = os.environ.get('MAIL_PASSWORD')
    receiver_email = os.environ.get('MAIL_RECEIVER', sender_email)

    if not sender_email or not sender_password:
        print("Error: Environment variables MAIL_USERNAME or MAIL_PASSWORD are not set.")
        return jsonify({'error': 'Server configuration error: Missing email credentials'}), 500

    def send_async_email(user, pwd, msg_obj):
        """Background task to send email without blocking the server."""
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(user, pwd)
                server.send_message(msg_obj)
            print("Email sent successfully in background.")
        except Exception as e:
            print(f"Error sending email in background: {e}")

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"New Portfolio Contact from {name}"

        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        msg.attach(MIMEText(body, 'plain'))

        # Start a new thread to send the email
        email_thread = threading.Thread(target=send_async_email, args=(sender_email, sender_password, msg))
        email_thread.start()

        return jsonify({'message': 'Message received. Sending email...'}), 200
    except Exception as e:
        print(f"Error preparing email: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)