from builtins import str
import smtplib
from email.mime.text import MIMEText
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


def sendusername_email(to_email, username):
	subject = 'Stmserver Username Retrieval'
	body = 'Hello,\n\nYour username for Stmserver is: {}\n\nIf you did not request this information, please ignore ' \
		   'this email.\n\nBest regards,\nYour Stmserver Team'.format(username)

	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = config['admin_email']
	msg['To'] = to_email

	send_email_via_smtp(msg)


def send_reset_password_email(to_email, verification_code, question):
	subject = 'Password Reset Request'
	body = 'Hello,\n\nYou have requested a password reset for your account.\n\nVerification Code: ' + verification_code + '\nSecret Question: ' + question + '\n\nIf you did not request this reset, please ignore this email.\n\nBest regards,\nYour Stmserver Team'

	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = config['admin_email']
	msg['To'] = to_email

	send_email_via_smtp(msg)


def send_verification_email(to_email, verification_token):
	subject = 'Account Verification'
	body = 'Hello,\n\nThank you for registering with Stmserver. To verify your account, please use the following verification token:\n\nVerification Token: ' + verification_token + '\n\nIf you did not create an account, please ignore this email.\n\nBest regards,\nYour Stmserver Team'

	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = config['admin_email']
	msg['To'] = to_email

	send_email_via_smtp(msg)