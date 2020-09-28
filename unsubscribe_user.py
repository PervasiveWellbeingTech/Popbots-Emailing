from utils import read_object,save_object
from main import PARTICIPANT
from hashing_engine import encrypt,decrypt
import datetime
import pytz

utc = pytz.timezone('UTC')

DATA_PATH = "data/participants.pkl"
participants = read_object(DATA_PATH)


user_email = input("Please enter the user email you want to delete: ")

users_hids = []
for participant in participants.values():
    
    if participant.hashed_email == encrypt(user_email) and participant.unsubscribe == False:
        users_hids.append(participant.hashed_subject_id)

string_hids = f"\n".join([x.decode("utf-8") for x in users_hids])
print(f'Found {len(users_hids)} ids subcribed with that email here is the list:\n{string_hids}')

user_to_unsubscribe = input("Type the item number of appearance corresponding to the sID /!\ start with 0, or type any letter to do thing: ")

if user_to_unsubscribe.isdigit():
    indice = int(user_to_unsubscribe)
    participants[users_hids[indice]].unsubscribe = True
    participants[users_hids[indice]].unsubscribe_dt = datetime.datetime.now(utc)
    print(f"User {users_hids[indice].decode('utf-8')} has been unsubscribed, once emailing is active, the user will receive an automatic unsubscription email")
else:
    print("Nothing done")

save_object(participants,DATA_PATH)

