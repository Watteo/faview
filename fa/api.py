from django.core.cache import cache
from django.conf import settings
from datetime import datetime
from file_serve import ServeStatic
from string import capwords
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

def fetch_data(api_key, extra_args=''):
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

def fetch_name(username):
    user_data = fetch_data('user/{}'.format(username))
    return user_data['name']

def fetch_first_image(username):
    gallery = fetch_data('user/{}/gallery'.format(username))

    if not gallery:
        return None

    subm_id     = gallery[0]
    subm_data   = fetch_data('submission/{}'.format(subm_id))
    subm_full   = replace_media_urls(subm_data['full'])
    file_ext    = re.sub(r'.*\.([a-z0-9]+)$', r'\1', subm_full.lower())

    if file_ext not in ('jpeg', 'jpg', 'png', 'gif', 'tif', 'tiff'):
        return None

    head_img = {
        'id'    : subm_id,
        'full'  : subm_full,
    }

    return head_img

def fetch_comments(comments_url, right_now=datetime.now(), sort_IDs=False):
    comments = fetch_data(comments_url)

    for comment in comments:
        comment['username']   = replace_username(comment['profile'])
        comment['text']       = replace_media_urls(comment['text'])
        comment['avatar']     = replace_media_urls(comment['avatar'])
        comment['delta']      = natural_delta(comment['posted_at'], right_now)

    if sort_IDs:
        comments.sort(key=lambda comment: int(comment['id']))

    return comments

def fetch_watch_list(username, watch_view, page, limit=None):
    try:
        watch_list = fetch_data(
            'user/{}/{}'.format(username, watch_view),
            '?page={}'.format(page) if page > 1 else '',
        )
    except:
        watch_list = []

    if limit and limit <= len(watch_list):
        watch_list = watch_list[0:limit]

    return [(user, user.lower().replace('_', '')) for user in watch_list]

def fetch_text(url):
    cache_key = 'txt:' + url
    data = cache.get(cache_key)

    if data is None:
        logger.debug('CACHE MISS: {}'.format(cache_key))
        file_server = ServeStatic(settings.MEDIA_ROOT+'data', 'http://d.facdn.net')
        real_url    = re.sub(settings.MEDIA_URL + 'data(/.*)', r'\1', url)
        text_file   = file_server.get_file(real_url)['fd']
        raw_data    = text_file.read()
        text_file.close()

        try:
            encoding = chardet.detect(raw_data)
            data = raw_data.decode(encoding['encoding'])
            data = data.replace('<hr>', '---')
            data = data.replace('<', '&lt;')
            data = data.replace('>', '&gt;')
            data = data.replace('\r\n', '<br>\n')
            data = data.replace('\n', '<br>\n')
            cache.set(cache_key, data, API_TIMEOUT)
        except Exception as e:
            logger.exception(e)
            data = ''
    else:
        logger.debug('CACHE HIT: {}'.format(cache_key))

    return data

def replace_username(profile_url):
    return USER_REGEX.sub(r'\1', profile_url)

def replace_media_urls(content):
    class MediaURLHandler(object):
        def __init__(self):
            pass

        def __call__(self, match):
            url_root    = match.group(2)
            url_path    = urllib2.quote(match.group(3).encode('utf-8'), '/:@')
            local_url   = MEDIA_PREFIX[url_root] + url_path

            if match.group(1) == 'http:':
                return local_url

            return match.group(1) + local_url + match.group(5)

    return MEDIA_REGEX.sub(MediaURLHandler(), content)

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

def get_profile_context(username):
    USER_PROFILE_LIST = (
        'full_name',
        'artist_type',
        'registered_since',
        'current_mood',
    )
    USER_STATS_LIST = (
        'pageviews',
        'submissions',
        'comments_received',
        'comments_given',
        'journals',
        'favorites',
    )

    user_data   = fetch_data('user/{}'.format(username))
    head_img    = fetch_first_image(username)
    shouts      = fetch_comments('user/{}/shouts'.format(username))
    watchers    = fetch_watch_list(username, 'watchers', 1, 24)
    watching    = fetch_watch_list(username, 'watching', 1, 24)

    user_profile    = [
        (capwords(key, '_').replace('_', ' '), user_data[key])
        for key in USER_PROFILE_LIST
    ]

    user_stats      = [
        (capwords(key, '_').replace('_', ' '), user_data[key])
        for key in USER_STATS_LIST
    ]

    context = {
        'name'      : fetch_name(username),
        'username'  : username,
        'user_url'  : user_data['profile'],
        'head_img'  : head_img,
        'profile'   : replace_media_urls(user_data['artist_profile']),
        'avatar'    : replace_media_urls(user_data['avatar']),
        'user_data' : user_profile,
        'user_stats': user_stats,
        'shouts'    : shouts,
        'watchers'  : watchers,
        'watching'  : watching,
    }

    return context

def get_gallery_context(username, folder, page=1):
    if page > 1:
        extra_args = '?full=1&page={}'.format(page)
    else:
        extra_args = '?full=1'

    user_folder     = fetch_data('user/{}/{}'.format(username, folder), extra_args)
    folder_size     = len(user_folder)
    previous_page   = (page - 1) if page > 1 and folder_size > 0 else False
    next_page       = (page + 1) if folder_size > 0 else False

    gallery = []

    for img in user_folder:
        if img['title'] == 'Submission has been deleted':
            continue

        img['thumbnail'] = replace_media_urls(img['thumbnail'])
        gallery.append(img)

    context = {
        'name'      : fetch_name(username),
        'username'  : username,
        'folder'    : folder,
        'gallery'   : gallery,
        'previous'  : previous_page,
        'next'      : next_page,
    }

    return context

def get_watch_context(username, watch_view, page=1):
    watch_list      = fetch_watch_list(username, watch_view, page)
    watch_count     = len(watch_list)
    previous_page   = (page - 1) if page != 1 and watch_count > 0 else False
    next_page       = (page + 1) if watch_count > 0 else False
    full_name       = fetch_name(username)

    if watch_view == 'watching':
        head = '{} is watching'.format(full_name)
    elif watch_view == 'watchers':
        head = '{}\'s watchers'.format(full_name)

    context = {
        'name'      : full_name,
        'username'  : username,
        'view'      : watch_view,
        'head'      : head,
        'watchs'    : watch_list,
        'previous'  : previous_page,
        'next'      : next_page,
    }

    return context

def get_journals_context(username):
    right_now   = datetime.now()
    journals    = fetch_data('user/{}/journals'.format(username), '?full=1')

    for journal in journals:
        journal['delta'] = natural_delta(journal['posted_at'], right_now)

    context = {
        'name'      : fetch_name(username),
        'username'  : username,
        'journals'  : journals,
    }

    return context

def get_submission_context(subm_id):
    STATS_ATTRIBUTE_LIST = (
        'category',
        'theme',
        'species',
        'gender',
        'favorites',
        'comments',
        'views',
        'rating',
        'resolution',
    )

    right_now       = datetime.now()
    subm_data       = fetch_data('submission/{}'.format(subm_id))
    subm_comments   = fetch_comments(
        'submission/{}/comments'.format(subm_id),
        right_now,
        True,
    )
    username        = replace_username(subm_data['profile'])

    subm_data['full']           = replace_media_urls(subm_data['full'])
    subm_data['download']       = subm_data['full']
    subm_data['delta']          = natural_delta(subm_data['posted_at'], right_now)
    subm_data['description']    = replace_media_urls(re.sub(
        r'^<a href="/user/[^/]+/"><img alt="[^"]+" src="[^"]+"></a>',
        r'',
        subm_data['description'],
    ))
    subm_data['stats']          = [
        (capwords(key, '_').replace('_', ' '), subm_data[key])
        for key in STATS_ATTRIBUTE_LIST
    ]

    file_ext = re.sub(r'.*\.([a-z0-9]+)$', r'\1', subm_data['full'].lower())

    if file_ext not in ('jpeg', 'jpg', 'png', 'gif', 'tif', 'tiff'):
        subm_data['full'] = replace_media_urls(subm_data['thumbnail'])

        if file_ext == 'txt':
            subm_data['text_content'] = fetch_text(subm_data['download'])
        elif file_ext == 'swf':
            subm_data['swf_resolution'] = subm_data['resolution'].split('x')
        elif file_ext in ('mp3', 'ogg'):
            subm_data['audio_type'] = 'mpeg' if file_ext == 'mp3' else 'ogg'

    context = {
        'name'      : fetch_name(username),
        'username'  : username,
        'sub_data'  : subm_data,
        'comments'  : subm_comments,
    }

    return context

def get_journal_context(journ_id):
    right_now       = datetime.now()
    journ_data      = fetch_data('journal/{}'.format(journ_id))
    journ_comments  = fetch_comments(
        'journal/{}/comments'.format(journ_id),
        right_now,
        True,
    )
    username        = replace_username(journ_data['profile'])

    journ_data['delta']         = natural_delta(journ_data['posted_at'], right_now)
    journ_data['description']   = replace_media_urls(journ_data['description'])

    context = {
        'name'      : fetch_name(username),
        'username'  : username,
        'journ_data': journ_data,
        'comments'  : journ_comments,
    }

    return context

def get_search_context(query, page=1):
    if not query:
        return {
            'query'     : '',
            'gallery'   : [],
            'previous'  : False,
            'next'      : False,
        }

    if page > 1:
        extra_args = '?q={}&full=1&page={}'.format(query, page)
    else:
        extra_args = '?q={}&full=1'.format(query)

    search_data     = fetch_data('search', extra_args)
    result_size     = len(search_data)
    previous_page   = (page - 1) if page != 1 and result_size > 0 else False
    next_page       = (page + 1) if result_size > 0 else False

    gallery = []

    for img in search_data:
        if img['title'] == 'Submission has been deleted':
            continue

        img['thumbnail'] = replace_media_urls(img['thumbnail'])
        gallery.append(img)

    context = {
        'query'     : query,
        'gallery'   : gallery,
        'previous'  : previous_page,
        'next'      : next_page,
    }

    return context

