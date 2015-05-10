from django.shortcuts import render
from string import capwords
from datetime import datetime
from fa.fa_api import api_fetch, api_fetch_watchs, txt_fetch, get_username, auto_fetch_media, natural_delta
import re

import logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'fa/index.html', {})

def user(request, name):
    USER_ATTRIBUTE_LIST = (
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

    try:
        api_user_data   = api_fetch('user/{}'.format(name))
        api_shouts      = api_fetch('user/{}/shouts'.format(name))
        api_watchers    = api_fetch_watchs(name, 'watchers', 24)
        api_watching    = api_fetch_watchs(name, 'watching', 24)
        api_gallery     = api_fetch('user/{}/gallery'.format(name))
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    right_now       = datetime.now()

    if api_user_data['full_name'] == 'Not Available...':
      api_user_data['full_name'] = name

    if api_gallery:
        try:
            api_sub_data = api_fetch('submission/{}'.format(api_gallery[0]))

            file_ext = re.sub(
                r'.*\.([a-zA-Z0-9]+)$',
                r'\1',
                api_sub_data['full']
            ).lower()

            if file_ext not in ('jpeg', 'jpg', 'png', 'gif', 'tif', 'tiff'):
                head_img = None
            else:
                head_img = {
                    'id'    : api_gallery[0],
                    'full'  : auto_fetch_media(api_sub_data['full']),
                }
        except Exception as e:
            logger.exception(e)
            head_img = None
    else:
        head_img = None

    user_data       = [
        (capwords(key, '_').replace('_', ' '), api_user_data.get(key))
        for key in USER_ATTRIBUTE_LIST
    ]

    user_stats      = [
        (capwords(key, '_').replace('_', ' '), api_user_data.get(key))
        for key in USER_STATS_LIST
    ]

    for shout in api_shouts:
        shout['avatar']     = auto_fetch_media(shout['avatar'])
        shout['username']   = get_username(shout['profile'])
        shout['delta']      = natural_delta(shout['posted_at'], right_now)
        shout['text']       = auto_fetch_media(shout['text'])

    context = {
        'name'      : api_user_data['full_name'],
        'username'  : name,
        'user_url'  : api_user_data['profile'],
        'head_img'  : head_img,
        'profile'   : auto_fetch_media(api_user_data['artist_profile']),
        'avatar'    : auto_fetch_media(api_user_data['avatar']),
        'user_data' : user_data,
        'user_stats': user_stats,
        'shouts'    : api_shouts,
        'watchers'  : api_watchers,
        'watching'  : api_watching,
    }

    return render(request, 'fa/user.html', context)

def gallery(request, name, folder):
    try:
        if request.GET.get('page'):
            page = max(int(request.GET['page']), 1)
            extra_args = '?full=1&page={}'.format(page)
        else:
            page = 1
            extra_args = '?full=1'

        api_user_data   = api_fetch('user/{}'.format(name))
        api_user_folder = api_fetch('user/{}/{}'.format(name,folder), extra_args)
        folder_size     = len(api_user_folder)
        previous_page   = (page - 1) if page != 1 and folder_size > 0 else False
        next_page       = (page + 1) if folder_size > 0 else False
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    if api_user_data['full_name'] == 'Not Available...':
      api_user_data['full_name'] = name

    gallery = []

    for img in api_user_folder:
        if img['title'] == 'Submission has been deleted':
            continue

        img['thumbnail'] = auto_fetch_media(img['thumbnail'])
        gallery.append(img)

    context = {
        'name'      : api_user_data['full_name'],
        'username'  : name,
        'folder'    : folder,
        'gallery'   : gallery,
        'previous'  : previous_page,
        'next'      : next_page,
    }

    return render(request, 'fa/gallery.html', context)

def watch(request, name, watch_view):
    try:
        api_user_data   = api_fetch('user/{}'.format(name))
        api_watchs      = api_fetch_watchs(name, watch_view)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    if api_user_data['full_name'] == 'Not Available...':
      api_user_data['full_name'] = name

    head = '{} is watching' if watch_view == 'watching' else '{}\'s watchers'

    context = {
        'name'      : api_user_data['full_name'],
        'username'  : name,
        'view'      : watch_view,
        'head'      : head.format(name),
        'watchs'    : api_watchs,
    }

    return render(request, 'fa/watch.html', context)

def journals(request, name):
    try:
        api_journals    = api_fetch('user/{}/journals'.format(name), '?full=1')
        api_user_data   = api_fetch('user/{}'.format(name))
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    if api_user_data['full_name'] == 'Not Available...':
      api_user_data['full_name'] = name

    right_now = datetime.now()

    for journal in api_journals:
        journal['delta'] = natural_delta(journal['posted_at'], right_now)

    context = {
        'name'      : api_user_data['full_name'],
        'username'  : name,
        'journals'  : api_journals,
    }

    return render(request, 'fa/journals.html', context)

def submission(request, sub_id):
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
        'keywords',
    )

    try:
        api_sub_comments    = api_fetch('submission/{}/comments'.format(sub_id))
        api_sub_data        = api_fetch('submission/{}'.format(sub_id))
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    right_now                   = datetime.now()
    api_sub_data['full']        = auto_fetch_media(api_sub_data['full'])
    api_sub_data['delta']       = natural_delta(
        api_sub_data['posted_at'],
        right_now,
    )
    api_sub_data['description'] = auto_fetch_media(re.sub(
        r'^<a href="/user/[^/]+/"><img alt="[^"]+" src="[^"]+"></a>',
        r'',
        api_sub_data['description'],
    ))
    api_sub_data['download']    = api_sub_data['full']
    api_sub_data['keywords']    = ', '.join(api_sub_data['keywords']) or '-'
    api_sub_data['stats']       = [
        (capwords(key, '_').replace('_', ' '), api_sub_data.get(key))
        for key in STATS_ATTRIBUTE_LIST
    ]

    file_ext = re.sub(r'.*\.([a-zA-Z0-9]+)$', r'\1', api_sub_data['full']).lower()

    if file_ext == 'txt':
        api_sub_data['text_content'] = txt_fetch(api_sub_data['full'])

    if file_ext in ('mp3', 'ogg'):
        api_sub_data['audio_content'] = api_sub_data['full']
        api_sub_data['audio_type'] = 'mpeg' if file_ext == 'mp3' else 'ogg'

    if file_ext not in ('jpeg', 'jpg', 'png', 'gif', 'tif', 'tiff'):
        api_sub_data['full'] = auto_fetch_media(api_sub_data['thumbnail'])

    for comment in api_sub_comments:
        comment['avatar']   = auto_fetch_media(comment['avatar'])
        comment['username'] = get_username(comment['profile'])
        comment['delta']    = natural_delta(comment['posted_at'], right_now)
        comment['text']     = auto_fetch_media(comment['text'])

    context = {
        'name'      : api_sub_data['name'],
        'username'  : get_username(api_sub_data['profile']),
        'sub_data'  : api_sub_data,
        'comments'  : api_sub_comments,
    }

    return render(request, 'fa/submission.html', context)

def journal(request, journ_id):
    try:
        api_journ_data      = api_fetch('journal/{}'.format(journ_id))
        api_journ_comments  = api_fetch('journal/{}/comments'.format(journ_id))
        user                = get_username(api_journ_data['profile'])
        api_user_data       = api_fetch('user/{}'.format(user))
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    if api_user_data['full_name'] == 'Not Available...':
      api_user_data['full_name'] = name

    right_now               = datetime.now()
    api_journ_data['delta'] = natural_delta(
        api_journ_data['posted_at'],
        right_now,
    )
    api_journ_data['description'] = auto_fetch_media(api_journ_data['description'])

    for comment in api_journ_comments:
        comment['avatar']   = auto_fetch_media(comment['avatar'])
        comment['username'] = get_username(comment['profile'])
        comment['delta']    = natural_delta(comment['posted_at'], right_now)
        comment['text']     = auto_fetch_media(comment['text'])

    context = {
        'name'      : api_user_data['full_name'],
        'username'  : user,
        'journ_data': api_journ_data,
        'comments'  : api_journ_comments,
    }

    return render(request, 'fa/journal.html', context)

