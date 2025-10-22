from os.path import basename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from odd_kernel.util.general import wait_some_time

MAX_MAIL_CONNECTION_RETRIES = 10

def send_mail(body, subject, from_addr, password, to_address, attached_file_names=None, max_mail_connection_retries=MAX_MAIL_CONNECTION_RETRIES):
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        # Read and attach file
        for attached_file_name in  attached_file_names:
            base_name = basename(attached_file_name)
            with open(attached_file_name, "rb") as file:
                part = MIMEApplication(file.read(),Name=base_name)
            part['Content-Disposition'] = f'attachment; filename="{base_name}"'
            msg.attach(part)
        
        for attempt in range(max_mail_connection_retries):
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.login(from_addr, password)
                text = msg.as_string()
                server.sendmail(from_addr, to_address, text)
                server.quit()
                break
            except smtplib.SMTPConnectError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                wait_some_time(5, 10)