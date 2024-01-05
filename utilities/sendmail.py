import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import utils
from config import get_config as read_config

config = read_config()


def send_email_via_smtp(msg):
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']
    smtp_username = config['smtp_username']
    smtp_password = config['smtp_password']
    smtp_security = config['smtp_security']

    try:
        # Create an SMTP connection
        if smtp_security.lower() == "ssl":
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Use TLS encryption

        # Login to the SMTP server (if authentication is required)
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", str(e))


def load_email_template(template_name, **kwargs):
    template_path = os.path.join('files/email_tpl/', template_name)
    with open(template_path, 'r') as file:
        template = file.read()

    kwargs['support_email'] = config['support_email']
    kwargs['network_name'] = config['network_name']
    kwargs['network_url'] = config['http_ip']
    kwargs['logo_url'] = config['network_logo']

    if config['email_location_support'].lower() == "true":
        country, region_name = utils.get_location(kwargs['ipaddress'])
        kwargs['ip_location_msg'] = f" (Location: {country}, {region_name})"
        print(f'Country: {country}, Region: {region_name}')
    else:
        kwargs['ip_location_msg'] = ""

    return template.format(**kwargs)


def send_username_email(to_email, username, ipaddress):
    subject = f"{config['network_name']}: Username Retrieval"
    body = load_email_template('username_retrieval.tpl', username = username, ipaddress = ipaddress[0])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['smtp_username']
    msg['To'] = to_email

    # Attach the HTML version of the body
    part = MIMEText(body, 'html')
    msg.attach(part)

    send_email_via_smtp(msg)


def send_reset_password_email(to_email, verification_code, question, ipaddress, username):
    subject = f"{config['network_name']}: Password Reset Request"
    body = load_email_template('password_reset_request.tpl', verification_code = verification_code, question = question, ipaddress = ipaddress[0], username = username)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['smtp_username']
    msg['To'] = to_email

    # Attach the HTML version of the body
    part = MIMEText(body, 'html')
    msg.attach(part)

    send_email_via_smtp(msg)


def send_verification_email(to_email, verification_token, ipaddress, username):
    subject = f"{config['network_name']}: Account Verification"
    body = load_email_template('account_verification.tpl', verification_code = verification_token, ipaddress = ipaddress[0], username = username)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['smtp_username']
    msg['To'] = to_email

    # Attach the HTML version of the body
    part = MIMEText(body, 'html')
    msg.attach(part)

    send_email_via_smtp(msg)


def send_new_user_email(to_email, ipaddress, username):
    subject = f"Welcome to {config['network_name']}!"
    body = load_email_template('new_user_welcome.tpl', ipaddress = ipaddress[0], username = username)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['smtp_username']
    msg['To'] = to_email

    # Attach the HTML version of the body
    part = MIMEText(body, 'html')
    msg.attach(part)

    send_email_via_smtp(msg)


def send_password_changed_email(to_email, ipaddress, username):
    subject = f"{config['network_name']}: Password Change Notice"
    body = load_email_template('password_changed.tpl', ipaddress = ipaddress[0], username = username)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = config['smtp_username']
    msg['To'] = to_email

    # Attach the HTML version of the body
    part = MIMEText(body, 'html')
    msg.attach(part)

    send_email_via_smtp(msg)


if __name__ == "__main__":
    send_new_user_email(sys.argv[1], sys.argv[2], sys.argv[3])