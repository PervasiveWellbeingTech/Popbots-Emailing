from utils import return_logger
import traceback
import pickle
import datetime
from time import sleep
import pytz
import qualtrics
import pandas

from emailing_engine import send_qualtrics_email
import os

from hashing_engine import encrypt,decrypt

logger = return_logger()
utc = pytz.timezone('UTC')


participants = {}


from threading import Timer


class PARTICIPANT:
  
  def __init__(self,enrollment_date,hashed_subject_id,hashed_email,time_zone):
    
    self.enrollment_date = enrollment_date
    self.hashed_subject_id = hashed_subject_id
    self.hashed_email = hashed_email
    self.time_zone = time_zone
    self.last_daily_date = enrollment_date.replace(hour=20, minute=0, second=0, microsecond=0) # pretending it was sent the first day at 8pm
    self.last_weekly_date = enrollment_date.replace(hour=20, minute=0, second=0, microsecond=0) # pretending it was sent the first day at 8pm
    
    self.nb_sent_daily = 0
    self.nb_sent_weekly = 0



  def send_daily(self):
    receiver_email = decrypt(self.hashed_email)
    text_category = 'daily'
    survey_number = self.nb_sent_daily
    hashed_id = self.hashed_subject_id.decode("utf-8")

    attempts = 0
    
    while True:
      attempts+=1
      try:
        send_qualtrics_email(receiver_email,text_category,survey_number,hashed_id,logger)
        
        self.last_daily_date = datetime.datetime.now(utc)
        self.nb_sent_daily +=1
        return
      
      except BaseException as error:
        if attempts <= 3:
          sleep_for = 2 ** (attempts - 1)      
          logger.error(f"Error while trying to send an email for user {self.hashed_subject_id.decode('utf-8')} attempt number {attempts} error is {error}")
          sleep(sleep_for)
          continue
        else:
          raise
    
  def send_weekly(self):
    receiver_email = decrypt(self.hashed_email)
    text_category = 'weekly'
    survey_number = self.nb_sent_weekly
    hashed_id = self.hashed_subject_id.decode("utf-8")

    attempts = 0
    
    while True:
      attempts+=1
      try:
        send_qualtrics_email(receiver_email,text_category,survey_number,hashed_id,logger)
        
        self.last_weekly_date = datetime.datetime.now(utc)
        self.nb_sent_weekly +=1
        return
      
      except BaseException as error:
        if attempts <= 3:
          sleep_for = 2 ** (attempts - 1)      
          logger.error(f"Error while trying to send an email for user {self.hashed_subject_id.decode('utf-8')} attempt number {attempts} error is {error}")
          sleep(sleep_for)
          continue
        else:
          raise




def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def read_object(filename):
  
  with open(filename, 'rb') as input:
    return pickle.load(input)


def fetch_update_participants():

  

  if os.path.exists(DATA_PATH):
    participants = read_object(DATA_PATH)
  else:
    participants = {}
  
  qualtrics.main(logger) #fetching the surveys from qualtrics

  surveys = pandas.read_csv(TEMP_QUALTRICS_DATA)
  surveys = surveys.loc[2:] # only take data from row 2 
  surveys = surveys[surveys['Finished']=='1'] # only consider surveys which are completed

  for index,response in surveys.iterrows():

    if encrypt(response['id']) not in list(participants.keys()):

      enrollment_date = datetime.datetime.strptime(response['EndDate'],"%Y-%m-%d %H:%M:%S")
      participants[encrypt(response['id'])] = PARTICIPANT(enrollment_date,encrypt(response['id']),encrypt(response['Q21']),response['INATZ'])

  save_object(participants,DATA_PATH)

  if os.path.exists(TEMP_QUALTRICS_DATA):
    os.remove(TEMP_QUALTRICS_DATA)
  else:
    logger.error("Cannot delete qualtrics data because the file does not exits")

  return participants



if __name__ == "__main__":



  DATA_PATH = "data/participants.pkl"
  TEMP_QUALTRICS_DATA = "qualtrics_survey/PopBots June 2020- Pre-Study Survey.csv"

  participants = fetch_update_participants() # initializes the participants
  last_participant_update = datetime.datetime.now()
  logger.info(f"Running the weekly and daily emailing system")
  while True:

    sleep(5)

    try:

      #1 retrieve all new possible users

      if (datetime.datetime.now() - last_participant_update).seconds > 1200:
        logger.info('Participants dict updated and saved')
        participants = fetch_update_participants()
        last_participant_update = datetime.datetime.now()
      else:
        pass

      for participant in participants.values():
        
        
        tz = pytz.timezone(participant.time_zone)
        utc = pytz.timezone('UTC')
        
        nowUTC = datetime.datetime.now(utc)
        now_local = nowUTC.astimezone(tz)

        now_local_20h = now_local.replace(hour=20, minute=0, second=0, microsecond=0)

        delta_to_8pm = now_local_20h - now_local
        time_to_weekly = now_local-participant.last_weekly_date.astimezone(tz)

        if delta_to_8pm.seconds % 21 ==0:
          logger.info(f'Local user time: {now_local} for user {participant.hashed_subject_id.decode("utf-8")} in time zone {tz}, delta to 8pm is {delta_to_8pm.seconds/3600:.2f},delta to weekly is {time_to_weekly.seconds/3600:.2f}')


        if delta_to_8pm < datetime.timedelta(hours=0): # if passed 20h Local time

          if (now_local - participant.last_daily_date.astimezone(tz)) > datetime.timedelta(hours=20): # if time is greater than yesterday
            logger.info(f"Daily will be send now for participant {decrypt(participant.hashed_email)}")

            participant.send_daily()
            participant.last_daily_date = datetime.datetime.now(utc)

          if now_local-participant.last_weekly_date.astimezone(tz) > datetime.timedelta(days=7):
            logger.info(f"Weekly will be send now for participant {decrypt(participant.hashed_email)}")

            participant.send_weekly()
            participant.last_weekly_date = datetime.datetime.now(utc)


    except BaseException as error:
      
      error_traceback = error.__traceback__
      logger.error(str(error) + str(''.join(traceback.format_tb(error_traceback))))
    
    finally:

      save_object(participants,DATA_PATH)



    

    
    