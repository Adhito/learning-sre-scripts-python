import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import pytz
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'  # For Gmail
SMTP_PORT = 587
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_password'
RECIPIENT_EMAIL = 'recipient_email@gmail.com'
AWS_REGION = 'us-east-1'  # Change as per your SES region

# CPU usage threshold
CPU_THRESHOLD = 80

# Monitoring interval (in seconds)
MONITOR_INTERVAL = 1

# Log file configuration
jakarta_tz = pytz.timezone('Asia/Jakarta')
current_date = datetime.now(jakarta_tz).strftime('%d_%m_%Y')
LOG_FILE = f'cpu_usage_log_{current_date}.txt'

# Function to log messages to file
def log_message(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f'{message}\n')

# Function to send email alert (SMTP)
def send_email_alert(cpu_usage):
    subject = 'CPU Usage Alert!'
    body = f'Warning: CPU usage is at {cpu_usage}%.'

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
            log_message(f'Alert sent to {RECIPIENT_EMAIL}')
            print(f'Alert sent to {RECIPIENT_EMAIL}')
    except Exception as e:
        log_message(f'Failed to send email: {e}')
        print(f'Failed to send email: {e}')



# Monitoring loop
while True:
    cpu_usage = psutil.cpu_percent(interval=MONITOR_INTERVAL)
    timestamp = datetime.now(jakarta_tz).strftime('%Y-%m-%d %H:%M:%S')
    log_message(f'[{timestamp}] Current CPU Usage: {cpu_usage}%')
    print(f'[{timestamp}] Current CPU Usage: {cpu_usage}%')

    if cpu_usage > CPU_THRESHOLD:
        send_email_alert(cpu_usage)  # Existing SMTP function
        send_email_alert_ses(cpu_usage)  # New SES function

    time.sleep(MONITOR_INTERVAL)  # Check every MONITOR_INTERVAL seconds
