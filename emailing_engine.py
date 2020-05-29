# import the necessary components first
import os
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_qualtrics_email(receiver_email,text_category,survey_number,hashed_id):
    # write the plain text part
    if text_category == 'daily':
        subject = "Your Daily Chatbot Survey"

        text = f"""\
        Dear participant,
        
        Thank you for your continued participation in our chatbot study. Please complete today’s daily survey: 
        https://stanforduniversity.qualtrics.com/jfe/form/SV_aaWggWWTJZ5IYN7?snb={survey_number}&rdate={datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}&hid={hashed_id}
        
        For any questions or concerns please contact:
        Nick Tantivasadakarn nantanic@stanford.edu Phone: 323-613-9774
        Marco Mora marcom3@stanford.edu Phone: 619-636-7636

        For participant’s rights questions, contact the Administrative Panel on Human Subjects in Medical Research via 1-866-680-2906

        Pervasive Wellbeing Technology Lab
        Stanford University School of Medicine
        3155 Porter Drive
        Palo Alto CA 94304 USA

        """
    else:
        raise Exception("No text category")


    send_email(receiver_email,text,subject)



def send_email(receiver_email,text,subject):

    port = 465 
    smtp_server = "smtp.gmail.com"
    login = os.environ['GMAIL_ADDRESS']
    password = os.environ['GMAIL_PASSWORD']
    sender_email = os.environ['GMAIL_ADDRESS']

    #receiver_email
    context = ssl.create_default_context()


    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message['Subject'] = subject


    # convert both parts to MIMEText objects and add them to the MIMEMultipart message
    part1 = MIMEText(text, "plain")
    message.attach(part1)
    # send the email
    with smtplib.SMTP_SSL(smtp_server, port,context=context) as server:
        server.login(login, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    print('Sent')

