# Python code to illustrate Sending mail with attachments
# from your Gmail account

# libraries to be imported
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config.config_reader import ConfigReader


class SendEmail():
    def __init__(self):
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        self.fromaddr = self.configuration['EMAIL_FROM']
        self.pwd_from = self.configuration['PWD_FROM']


    def send_covid_data(self, toaddr):
        # open the file to be sent
        self.covid_files = ["Covid_FAQ.pdf", "Covid_Precaution.pdf"]
        self.msg = MIMEMultipart()
        # storing the subject
        self.msg['Subject'] = "Covid19 Faqs and Precautions"
        # self.fromaddr = self.email_from
        self.s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        self.s.starttls()

        # Authentication
        self.s.login(self.fromaddr, self.pwd_from)
        # storing the senders email address
        self.msg['From'] = self.fromaddr

        # storing the receivers email address
        self.msg['To'] = toaddr

        # string to store the body of the mail
        body = "Hi\n\nThanks for contacting. Please read attached information for Covid.\nGet Covid19 latest data by ChatBot or click on this link https://covid19-flask-lui.herokuapp.com/demographic-covid-data to see demographic covid data.\n\nStay Healthy!"

        # attach the body with the msg instance
        try:
            self.msg.attach(MIMEText(body, 'plain'))
            for file_name in self.covid_files:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open('covid_email/' + file_name, "rb").read())
                # attachment = open("Path of the file", "rb")

                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment', filename=file_name)
                self.msg.attach(part)

            # Converts the Multipart msg into a string
            text = self.msg.as_string()
            # sending the mail
            self.s.sendmail(self.fromaddr, toaddr, text)
            print("Email Sent!")
            # terminating the session
            self.s.quit()
        except Exception as e:
            print(e)
            print("Email not sent. Some issue has come")
