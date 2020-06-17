import pandas as pd
import datetime
import pytz

utc = pytz.timezone('UTC')


numdays = 120
now = datetime.datetime.now(utc)
date_list = [(now - datetime.timedelta(days=x)).date() for x in range(30)]
date_list = date_list  + [(now + datetime.timedelta(days=x)).date() for x in range(numdays)]
participant_df = pd.DataFrame(columns=date_list)

participant_df.columns = pd.to_datetime(participant_df.columns).sort_values()

participant_df.to_csv('./data/participant_df.csv')
