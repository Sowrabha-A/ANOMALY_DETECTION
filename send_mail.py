import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_email(sender_email, app_password, recipient_email, subject, body, image_path):
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the body to the MIME message
    message.attach(MIMEText(body, 'plain'))

    # Attach the image file
    with open(image_path, 'rb') as attachment:
        image_mime = MIMEImage(attachment.read(), name="anomaly_detected.jpg")
    message.attach(image_mime)

    # Create SMTP session
    server = smtplib.SMTP('smtp.gmail.com', 587)  # Using Gmail SMTP server
    server.starttls()  # Start TLS for security
    server.login(sender_email, app_password)  # Log in to your email account

    # Send the message via the server
    server.sendmail(sender_email, recipient_email, message.as_string())
    print("Email sent successfully!")

    # Terminate the SMTP session
    server.quit()
