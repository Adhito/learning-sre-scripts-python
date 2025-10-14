import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import datetime
import pytz
import boto3
from botocore.exceptions import BotoCoreError, ClientError

## Configuration For Simple SMTP Email with Gmail
SMTP_SERVER = 'smtp.gmail.com'  
SMTP_PORT = 587
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_password'
RECIPIENT_EMAIL = 'recipient_email@gmail.com'

## Configuration For AWS SES Region
AWS_REGION = 'us-east-1' 

## Parameters For CPU usage threshold
CPU_THRESHOLD = 80

## Parameters For Monitoring interval (in seconds)
MONITOR_INTERVAL = 1


## Function to log messages to file
jakarta_tz = pytz.timezone('Asia/Jakarta')
current_date = datetime.now(jakarta_tz).strftime('%d_%m_%Y')
LOG_FILE = f'cpu_usage_log_{current_date}.txt'

def log_message(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f'{message}\n')


## Function to send email alert (SMTP)
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


## Function to send email alert using Amazon SES
def send_email_alert_ses(cpu_usage):
    subject = 'CPU Usage Alert via SES!'
    body = f'Warning: CPU usage is at {cpu_usage}%.'

    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.seMONITOR_INTERVALnd_email(
            Source=EMAIL_ADDRESS,
            Destination={
                'ToAddresses': [RECIPIENT_EMAIL]
            },
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body}
                }
            }
        )
        log_message(f'SES Alert sent to {RECIPIENT_EMAIL}, Message ID: {response["MessageId"]}')
        print(f'SES Alert sent to {RECIPIENT_EMAIL}, Message ID: {response["MessageId"]}')
    except (BotoCoreError, ClientError) as e:
        log_message(f'Failed to send SES email: {e}')
        print(f'Failed to send SES email: {e}')


while True:
    cpu_usage = psutil.cpu_percent(interval=MONITOR_INTERVAL)
    timestamp = datetime.now(jakarta_tz).strftime('%Y-%m-%d %H:%M:%S')
    log_message(f'[{timestamp}] Current CPU Usage: {cpu_usage}%')
    print(f'[{timestamp}] Current CPU Usage: {cpu_usage}%')

    if cpu_usage > CPU_THRESHOLD:
        send_email_alert(cpu_usage)     
        send_email_alert_ses(cpu_usage)  

    time.sleep(MONITOR_INTERVAL)  
