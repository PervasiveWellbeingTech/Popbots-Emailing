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

import pandas as pd
import datetime
import pytz

utc = pytz.timezone('UTC')


numdays = 120
now = datetime.datetime.now(utc)
date_list_past = [(now - datetime.timedelta(days=x)).date() for x in range(30)]
date_list = date_list_past  + [(now + datetime.timedelta(days=x)).date() for x in range(numdays)]
participant_df = pd.DataFrame(columns=date_list)

participant_df.columns = pd.to_datetime(participant_df.columns).sort_values()

participant_df.to_csv('./data/participant_df.csv')
