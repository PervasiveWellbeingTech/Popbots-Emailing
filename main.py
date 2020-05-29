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


daily_survey_time = time(20,00,00)


participants = {}


from threading import Timer


class PARTICIPANT:
  
  def __init__(self,enrollment_date,hashed_subject_id,hashed_email):
    
    self.enrollment_date = enrollment_date
    self.hashed_subject_id = hashed_subject_id
    self.hashed_email = hashed_email
    self.last_daily_date = None
    self.last_weekly_date = None
    self.nb_sent_daily = 0

  def send_daily(self):
    receiver_email = decrypt(self.hashed_email)
    text_category = 'daily'
    survey_number = self.nb_sent_daily
    hashed_id = self.hashed_subject_id

    attempts = 0
    
    while True:
      attempts+=1
      try:
        send_qualtrics_email(receiver_email,text_category,survey_number,hashed_id)
        
        self.last_daily_date = datetime.now()
        self.nb_sent_daily +=1
        return
      
      except BaseException as error:
        if attempts <= 3:
          sleep_for = 2 ** (attempts - 1)      
              
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

  
  logger = return_logger()

  if os.path.exist(DATA_PATH):
    participants = read_object(DATA_PATH)
  else:
    participants = {}
  
  qualtrics.main(logger) #fetching the surveys from qualtrics

  surveys = pandas.read_csv(TEMP_QUALTRICS_DATA)
  surveys = surveys.loc[2:] # only take data from row 2 
  surveys = surveys[surveys['Finished']=='1'] # only consider surveys which are completed

  for index,response in surveys.iterrows():

    if encrypt(response['id']) not in list(participants.keys()):

      enrollment_date = datetime.strptime(response['EndDate'],"%Y-%m-%d %H:%M:%S")
      participants[encrypt(response['id'])] = PARTICIPANT(enrollment_date,encrypt(response['id']),encrypt(response['Q21']))

  save_object(participants,DATA_PATH)

  if os.path.exist(TEMP_QUALTRICS_DATA):
    os.remove(TEMP_QUALTRICS_DATA)
  else:
    logger.error("Cannot delete qualtrics data because the file does not exits")

  return participants



if __name__ == "__main__":

  DATA_PATH = "data/participants.pkl"
  TEMP_QUALTRICS_DATA = "qualtrics_survey/PopBots June 2020- Pre-Study Survey.csv"

  participants = fetch_update_participants() # initializes the participants
  
  while True:

    sleep(5)

    try:

      #1 retrieve all new possible users

      if datetime.time.time() - last_participant_update > 1200:
        logger.info('Participants dict updated and saved')
        participants = fetch_update_participants()
        last_participant_update = datetime.time.time()
      else:
        pass

      for participant in participants.values():
        now = datetime.datetime.now()

        if (now.replace(hour=20, minute=0, second=0, microsecond=0) - datetime.datetime.now()) < datetime.timedelta(hours=0): # if passed 20h UTC

          if (datetime.datetime.now() - participant.last_daily_date) > datetime.timedelta(hours=20): # if time is greater than yesterday

            participant.send_daily()

            

        




      

    except BaseException as error:
      
      error_traceback = error.__traceback__
      logger.error(str(error) + str(''.join(traceback.format_tb(error_traceback))))
    
    finally:

      save_object(participants)



    

    
    