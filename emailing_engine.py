# import the necessary components first
import os
import pytz
import codecs
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import urllib.parse


utc = pytz.timezone('UTC')
        


def send_qualtrics_email(receiver_email,text_category,survey_number,hashed_id,population,logger):

    send_datetime = urllib.parse.quote(datetime.now(utc).isoformat())
    hashed_id = urllib.parse.quote(hashed_id)

    # write the plain text part
    if text_category == 'daily':
        
        if population == 'test':
            subject = "Your Daily Chatbot Survey"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_aaWggWWTJZ5IYN7?snb={survey_number}&rdate={send_datetime}&hid={hashed_id}"
        else:
            subject = "Your Daily Stress Survey"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_aaWggWWTJZ5IYN7?snb={survey_number}&rdate={send_datetime}&hid={hashed_id}"

        f=codecs.open("email_views/daily.html", 'r')
        html = f.read().format(**locals())

    elif text_category=='weekly': # Verification needed

        
        if population == 'test':
            subject = "Your Weekly Chatbot Survey"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_elhTKO1aePDsqAl?snb={survey_number}&rdate={send_datetime}&hid={hashed_id}"
        else:
            subject = "Your Weekly Chatbot Survey"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_6gmpusDDaeCxfp3?snb={survey_number}&rdate={send_datetime}&hid={hashed_id}"
        f=codecs.open("email_views/weekly.html", 'r')
        html = f.read().format(**locals())
    
    elif text_category == 'final':
        
        if population == 'test':
            subject = "Post-Chatbot Study Survey"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_eJRT1I19FFCgDAh?rdate={send_datetime}&hid={hashed_id}" 
        else:
            
            subject = "Post Stress Study Survey"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_eJKGuZHsv1S7Uy1?rdate={send_datetime}&hid={hashed_id}"
        
        f=codecs.open('email_views/endStudy.html')
        html = f.read().format(**locals())

    elif text_category== 'unsubscribed':

        if population == 'test':
            subject = "Unsubscribed from Chatbot Study"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_eJRT1I19FFCgDAh?rdate={send_datetime}&hid={hashed_id}" 
        else:
            
            subject = "Unsubscribed from Stress Study"
            url = f"https://stanforduniversity.qualtrics.com/jfe/form/SV_eJKGuZHsv1S7Uy1?rdate={send_datetime}&hid={hashed_id}"        
        
        f=codecs.open("email_views/unsubscribed.html", 'r')
        html = f.read().format(**locals())
    else:
        raise Exception("No text category")


    send_email(receiver_email,html,subject)
    logger.info(f"Email for user {hashed_id} has been sucessfully sent at {datetime.now(utc)}")



def send_email(receiver_email,html,subject):

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
 
    part = MIMEText(html, "html")
    message.attach(part)

    # send the email
    with smtplib.SMTP_SSL(smtp_server, port,context=context) as server:
        server.login(login, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    
