import pytz,datetime

from utils import return_logger

logger = return_logger()

tz = pytz.timezone('America/Los_Angeles')
        
nowUTC = datetime.datetime.now()
now_local = nowUTC.astimezone(tz)

now_local_20h = now_local.replace(hour=9, minute=0, second=0, microsecond=0)

delta_to_8pm = now_local_20h - now_local

logger.info(f'Local user time: {now_local} in time zone {tz}, delta to 8pm is {delta_to_8pm.seconds/3600:.2f}')


logger.info(f'{delta_to_8pm < datetime.timedelta(hours=0)}')


        