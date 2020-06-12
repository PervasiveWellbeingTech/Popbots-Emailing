from datetime import datetime
import pytz
from emailing_engine import send_qualtrics_email
from utils import return_logger
logger = return_logger()


send_qualtrics_email(receiver_email='lincolnt@stanford.edu',text_category='daily',survey_number=0,hashed_id=122,logger=logger)