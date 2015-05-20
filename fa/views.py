from django.shortcuts import render
from fa import api
from datetime import datetime
import re

import logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'fa/index.html', {})

def user(request, name):
    try:
        context = api.get_profile_context(name)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    return render(request, 'fa/user.html', context)

def gallery(request, name, folder):
    if request.GET.get('page'):
        page = max(int(request.GET['page']), 1)
    else:
        page = 1

    try:
        context = api.get_gallery_context(name, folder, page)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    return render(request, 'fa/gallery.html', context)

def watch(request, name, watch_view):
    if request.GET.get('page'):
        page = max(int(request.GET['page']), 1)
    else:
        page = 1

    try:
        context = api.get_watch_context(name, watch_view, page)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    return render(request, 'fa/watch.html', context)

def journals(request, name):
    try:
        context = api.get_journals_context(name)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    return render(request, 'fa/journals.html', context)

def submission(request, sub_id):
    try:
        context = api.get_submission_context(sub_id)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    return render(request, 'fa/submission.html', context)

def journal(request, journ_id):
    try:
        context = api.get_journal_context(journ_id)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    return render(request, 'fa/journal.html', context)

def search(request):
    if request.GET.get('page'):
        page = max(int(request.GET['page']), 1)
    else:
        page = 1

    query = request.GET.get('q')

    try:
        context = api.get_search_context(query, page)
    except Exception as e:
        logger.exception(e)
        return render(request, 'fa/500.html', {'exception':e})

    return render(request, 'fa/search.html', context)

