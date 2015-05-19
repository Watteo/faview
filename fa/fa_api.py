from django.core.cache import cache
from django.conf import settings
from datetime import datetime
import chardet
import json
import logging
import re
import time
import urllib2

logger      = logging.getLogger(__name__)
API_URL     = settings.FAEXPORT_API_URL
API_TIMEOUT = settings.FAEXPORT_API_TIMEOUT
USER_AGENT  = 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'

USER_REGEX_STR = r'[-_.~`\[\]\w]+'
USER_REGEX  = re.compile(r'^http://www.furaffinity.net/user/({})/'.format(USER_REGEX_STR))
MEDIA_REGEX = re.compile(r'(^http:| src=")/(/[adt]\.facdn\.net|themes)(/.*?\.[a-zA-Z0-9]+)(#[^"]+)?($|")')

MEDIA_PREFIX = {
    '/a.facdn.net' : settings.MEDIA_URL + 'avatar',
    '/d.facdn.net' : settings.MEDIA_URL + 'data',
    '/t.facdn.net' : settings.MEDIA_URL + 'thumbnail',
    'themes'       : settings.MEDIA_URL + 'themes',
}

class RegexFetcher(object):
    def __init__(self):
        pass

    def __call__(self, match):
        url_root    = match.group(2)
        url_path    = urllib2.quote(match.group(3).encode('utf-8'), '/:@')
        local_url   = MEDIA_PREFIX[url_root] + url_path

        if match.group(1) == 'http:':
            return local_url
        else:
            return match.group(1) + local_url + match.group(5)

def api_fetch(api_key, extra_args=''):
    cache_key = api_key + extra_args
    data = cache.get(cache_key)

    if data is None:
        logger.debug('CACHE MISS: {}'.format(cache_key))
        request_url = '{}/{}.json{}'.format(API_URL, api_key, extra_args)
        request_url = urllib2.quote(request_url, ':/?&=')
        request_obj = urllib2.Request(request_url)
        request_obj.add_header('User-Agent', USER_AGENT)

        opener      = urllib2.build_opener()
        raw_data    = opener.open(request_obj).read()
        data        = json.loads(raw_data)

        cache.set(cache_key, data, API_TIMEOUT)
    else:
        logger.debug('CACHE HIT: {}'.format(cache_key))

    return data

def api_fetch_watchs(name, watch_view, page, limit=None):
    try:
        watchs = api_fetch(
            'user/{}/{}'.format(name, watch_view),
            '?page={}'.format(page) if page > 1 else '',
        )
    except:
        watchs = []

    if limit and limit <= len(watchs):
        watchs = watchs[0:limit]

    return [(user, user.lower().replace('_', '')) for user in watchs]

def txt_fetch(url):
    cache_key = 'txt:' + url
    data = cache.get(cache_key)

    if data is None:
        logger.debug('CACHE MISS: {}'.format(cache_key))
        local_path = re.sub(
            r'{}(.*)'.format(settings.MEDIA_URL),
            r'{}\1'.format(settings.MEDIA_ROOT),
            url,
        )

        with open(local_path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)

            try:
                data = raw_data.decode(encoding['encoding'])
                data = data.replace('<', '&lt;')
                data = data.replace('>', '&gt;')
                data = data.replace('\r\n', '<br>\n')
                data = data.replace('\n', '<br>\n')
            except Exception as e:
                logger.exception(e)
                data = ''

            cache.set(cache_key, data, API_TIMEOUT)
    else:
        logger.debug('CACHE HIT: {}'.format(cache_key))

    return data

def get_username(profile_url):
    return USER_REGEX.sub(r'\1', profile_url)

def auto_fetch_media(content):
    return MEDIA_REGEX.sub(RegexFetcher(), content)

def natural_delta(then_str, now_date):
    then_date = datetime.strptime(then_str, '%Y-%m-%dT%H:%M:%SZ')
    delta = now_date - then_date
    delta_seconds   = delta.seconds
    delta_minutes   = delta_seconds/(60)
    delta_hours     = delta_seconds/(60*60)
    delta_days      = delta.days
    delta_weeks     = delta_days/7
    delta_months    = delta_days/30
    delta_years     = delta_days/365
    str_delta = '{} {} ago'

    if delta_years:
        if delta_years == 1:
            return 'a year ago'
        else:
            return str_delta.format(delta_years, 'years')
    elif delta_months:
        if delta_months == 1:
            return 'a month ago'
        else:
            return str_delta.format(delta_months, 'months')
    elif delta_weeks:
        if delta_weeks == 1:
            return 'a week ago'
        else:
            return str_delta.format(delta_weeks, 'weeks')
    elif delta_days:
        if delta_days == 1:
            return 'a day ago'
        else:
            return str_delta.format(delta_days, 'days')
    elif delta_hours:
        if delta_hours == 1:
            return 'an hour ago'
        else:
            return str_delta.format(delta_hours, 'hours')
    elif delta_minutes:
        if delta_minutes == 1:
            return 'a minute ago'
        else:
            return str_delta.format(delta_minutes, 'minutes')

    return 'a few seconds ago'
