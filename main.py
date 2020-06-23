import os
import traceback
import pickle
import datetime
import pytz
import qualtrics
import pandas
from time import sleep


from emailing_engine import send_qualtrics_email
from utils import return_logger,save_object, read_object
from hashing_engine import encrypt,decrypt

logger = return_logger()
utc = pytz.timezone('UTC')


participants = {}

participant_df = pandas.read_csv('data/participant_df.csv')


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

    self.unsubscribe = False
    self.unsubscribe_dt = None
    self.unsubscribe_email_sent = False
    self.unsubscribe_email_dt = None


  def send_email(self,text_category,survey_number):
    
    receiver_email = decrypt(self.hashed_email)
    hashed_id = self.hashed_subject_id.decode("utf-8")

    attempts = 0
    
    while True:
      attempts+=1
      try:
        send_qualtrics_email(receiver_email,text_category,survey_number,hashed_id,logger)
                
        return
      
      except BaseException as error:
        if attempts <= 3:

          sleep_for = 2 ** (attempts - 1)      
          logger.error(f"Error while trying to send an email for user {self.hashed_subject_id.decode('utf-8')} attempt number {attempts} error is {error}")
          sleep(sleep_for)
          continue

        else:
          raise



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

    esID = encrypt(response['id'])

    if esID not in list(participants.keys()):

      enrollment_date = datetime.datetime.strptime(response['EndDate'],"%Y-%m-%d %H:%M:%S")
      participants[esID] = PARTICIPANT(enrollment_date,esID,encrypt(response['Q21']),response['INATZ'])
      participant_df.loc[esID.decode("utf-8"),enrollment_date.date()] = "ENROLLED" 


    else:
      participant = participants[esID]
      participants[esID] = PARTICIPANT(participant.enrollment_date,participant.hashed_subject_id,participant.hashed_email,participant.time_zone)
      refreshed_participant = participants[esID]

      refreshed_participant.last_daily_date = participant.last_daily_date
      refreshed_participant.last_weekly_date = participant.last_weekly_date
      refreshed_participant.nb_sent_daily = participant.nb_sent_daily
      refreshed_participant.nb_sent_weekly = participant.nb_sent_weekly
      
      refreshed_participant.unsubscribe = getattr(participant, "unsubscribe", False)
      refreshed_participant.unsubscribe_dt = getattr(participant, "unsubscribe_dt", None)
      refreshed_participant.unsubscribe_email_sent = getattr(participant, "unsubscribe_email_sent", False)
      refreshed_participant.unsubscribe_email_dt = getattr(participant, "unsubscribe_email_dt", None)
 

      participant_df.loc[esID.decode("utf-8"),participant.enrollment_date.date()] = "ENROLLED"

       
      # updating the participant object, in case (in the code) we actually update the participant object. 

  save_object(participants,DATA_PATH)

  if os.path.exists(TEMP_QUALTRICS_DATA):
    os.remove(TEMP_QUALTRICS_DATA)
  else:
    logger.error("Cannot delete qualtrics data because the file does not exits")

  return participants



if __name__ == "__main__":


  STUDY_DURATION_DAYS = 28
  DATA_PATH = "data/participants.pkl"
  TEMP_QUALTRICS_DATA = "qualtrics_survey/PopBots June 2020- Pre-Study Survey.csv"

  participants = fetch_update_participants() # initializes the participants
  last_participant_update = datetime.datetime.now()
  logger.info(f"Running the weekly and daily emailing system")
  while True:

    sleep(10)
    
    try:

      #1 retrieve all new possible users

      if (datetime.datetime.now() - last_participant_update).seconds > 1200:
        logger.info('Participants dict updated and saved')
        participants = fetch_update_participants()
        last_participant_update = datetime.datetime.now()
      else:
        pass

      for participant in participants.values():

        try:
          tz = pytz.timezone(participant.time_zone)
          utc = pytz.timezone('UTC')
          
          nowUTC = datetime.datetime.now(utc)
          now_local = nowUTC.astimezone(tz)
          
          hsID = participant.hashed_subject_id
          
          if not participant.unsubscribe:
            
    
            now_local_20h = now_local.replace(hour=20, minute=0, second=0, microsecond=0)

            delta_to_8pm = now_local_20h - now_local
            time_to_weekly = datetime.timedelta(days=7) - (now_local_20h-participant.last_weekly_date.astimezone(tz))

            if delta_to_8pm.seconds % 37 ==0:
              logger.info(f'Local user time: {now_local} for user {hsID.decode("utf-8")} in time zone {tz}, delta to 8pm is {delta_to_8pm.seconds/3600:.2f},delta to weekly is {str(time_to_weekly)}, enrolled since {str(now_local - participant.enrollment_date.astimezone(tz))}')


            if delta_to_8pm < datetime.timedelta(hours=0): # if passed 20h Local time

              if (now_local - participant.enrollment_date.astimezone(tz)) > datetime.timedelta(days=STUDY_DURATION_DAYS):

                logger.info(f"Final email will be send now for participant {hsID}, participant unsubscribed")
                participant.send_final('final',None)
                participant.unsubscribe = True
                participant.unsubscribe_dt = nowUTC
                participant.unsubscribe_email_sent = True
                participant.unsubscribe_email_dt = nowUTC
                participant_df.loc[hsID.decode("utf-8"),str(nowUTC.date())] = "STUDY END"


              elif time_to_weekly < datetime.timedelta(minutes=1):
                logger.info(f"Weekly will be send now for participant {hsID}")

                participant.send_email('weekly',participant.nb_sent_weekly)
                participant.last_weekly_date = now_local_20h.astimezone(utc)
                participant.last_daily_date = now_local_20h.astimezone(utc) # we are bypassing the daily                
                participant_df.loc[hsID.decode("utf-8"),str(nowUTC.date())] = "WEEKLY "+ str(participant.nb_sent_weekly)
                participant.nb_sent_weekly +=1
              
              elif (now_local - participant.last_daily_date.astimezone(tz)) > datetime.timedelta(hours=24) and time_to_weekly > datetime.timedelta(hours=23): # if time is greater than yesterday
              
                logger.info(f"Daily will be send now for participant {hsID}")

                participant.send_email('daily',participant.nb_sent_daily)
                participant.last_daily_date = now_local_20h.astimezone(utc)
                participant_df.loc[hsID.decode("utf-8"),str(nowUTC.date())] = "DAILY "+ str(participant.nb_sent_daily)
                participant.nb_sent_daily +=1


          else: # this else occurs if the participant was unsubscribed from the study by the admin
            
            
            if not (now_local - participant.enrollment_date.astimezone(tz)) > datetime.timedelta(days=STUDY_DURATION_DAYS):
              if not participant.unsubscribe_email_sent:
                  
                  participant.send_final('unsubscribed',None)
                  participant.unsubscribe = True #
                  participant.unsubscribe_dt = nowUTC
                  participant.unsubscribe_email_sent = True
                  participant.unsubscribe_email_dt = nowUTC
                  participant_df.loc[hsID.decode("utf-8"),str(nowUTC.date())] = "UNSUBSCRIBED"
                  logger.info(f"Unsubscribed email will be send now for participant {hsID}, participant unsubscribed")

            if nowUTC.hour % 10 == 0 and nowUTC.minute % 31 == 0: # print 3 times a day 0h , 10h, 20h , 31 min is a co-prime integer 
              logger.info(f"Participant {hsID} is unsubscribed")

        except BaseException as error:
          logger.error(f"Error for participant {hsID} error is {error}")
          participant_df.loc[hsID.decode("utf-8"),str(nowUTC.date())] = "ERROR"
          


            
    except BaseException as error:
      
      error_traceback = error.__traceback__
      logger.error(str(error) + str(''.join(traceback.format_tb(error_traceback))))
    
    finally:

      save_object(participants,DATA_PATH)
      participant_df.to_csv('./data/participant_df.csv', index = False)




    

    
    