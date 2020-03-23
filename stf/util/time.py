import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from datetime import datetime, timedelta
from stf.util import files
import stf

# Maxmimum difference between sysclock and webapi to allow
MAX_DIFF_SECONDS = 10

# should this be equal to a testset in length at least?
TIMESYNC_EXPIRE_TIME = timedelta(minutes=20)

# APIs:

# http://worldtimeapi.org/api/timezone/Zulu
# Returns
'''
{
    "week_number": 10,
    "utc_offset": "+00:00",
    "utc_datetime": "2020-03-06T22:44:42.526827+00:00",
    "unixtime": 1583534682,
    "timezone": "Zulu",
    "raw_offset": 0,
    "dst_until": null,
    "dst_offset": 0,
    "dst_from": null,
    "dst": false,
    "day_of_year": 66,
    "day_of_week": 5,
    "datetime": "2020-03-06T22:44:42.526827+00:00",
    "client_ip": "184.8.34.173",
    "abbreviation": "UTC"
}
'''

def get_time(url='http://worldtimeapi.org/api/timezone/Zulu'):
    '''
    this function should be run only once per runset...
    considering using a tmp file that contains maybe the timestamp?
    '''
    path = files.Path(files.join(stf.config.get_path('tmp'), 'timesync.stf.tmp'))
    try:
        file_stat = path.stat()
        # IMPORTANT: use system time for this and only this calculation)
        file_ctime = datetime.fromtimestamp(file_stat.st_ctime)
        if abs(datetime.now() - file_ctime) > TIMESYNC_EXPIRE_TIME:
            try:
                path.unlink()
            except Exception as e:
                stf.debug('Unable to unlink file ', path)
                stf.debug(f'Exception: {e}')
        else:
            # if file was written recently, all is well
            return 'verified'
    except FileNotFoundError:
        pass

    # my brain realizes now that if multiple tests are being run on site
    # we should cache a file and see if we've verified the time already
    # on this machine. maybe the file contains the verified timestamp
    # and if it's older than an hour we ignore and overwrite it with a fresh check

    response = urlopen(Request(url)).read()
    # check response.status_code ? retry? or try_repeat this fn if needed...
    timestamp = json.loads(response).get('unixtime')
    nowlocal = datetime.utcfromtimestamp(timestamp)
    if not path.exists():
        try:
            path.touch()
        except:
            # Missing parent directory, no write permission, file system full, etc.
            stf.debug(f'unable to touch file ', path)
            stf.debug(f'Exception: {e}')
    return nowlocal


def check_systime_accurate():
    now = datetime.utcnow()
    try:
        nowlocal = get_time()
    except (URLError, ValueError) as e:
        stf.debug(f'Exception: {e}')
        return None

    # shortcut in case we just checked
    if nowlocal == 'verified':
        stf.debug('Timesync verified by cached file')
        return True

    if not nowlocal:
        stf.debug('Unable to fetch time')
        '''unable to fetch time'''
        return False

    if abs(nowlocal - now).seconds > MAX_DIFF_SECONDS:
        return False
        #raise STFTimeError
        #raise Exception('Unable to verify time accuracy!')

    return True


# https://timezonedb.com/api
# Returns: nothing without an API key :(


def getTimeSlug(t=None):
    if not t:
        t = datetime.utcnow()  # XXX: move to util.time
    return t.strftime('%Y.%m.%d_%H%M%S')
