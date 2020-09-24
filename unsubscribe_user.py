#   Copyright 2020 Stanford University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
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

