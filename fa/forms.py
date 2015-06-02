from django import forms
from django.utils.safestring import mark_safe
from textwrap import dedent

import logging
logger = logging.getLogger(__name__)

class SearchForm(forms.Form):
    INITIAL_VALUES = {
        'perpage'           : '60',
        'order_by'          : 'date',
        'order_direction'   : 'desc',
        'range'             : 'all',
        'mode'              : 'extended',
        'rating'            : ['general', 'mature', 'adult'],
        'type'              : ['art', 'flash', 'photo', 'music', 'story', 'poetry'],
        'page'              : '1',
    }

    q = forms.CharField(
        label       = 'Search query',
        widget      = forms.TextInput(attrs={
            'placeholder'   : '@keywords kw1 kw2...',
            'class'         : 'search-input',
            'required'      : True,
        })
    )
    perpage = forms.ChoiceField(
        label       = 'Results per page',
        required    = False,
        initial     = INITIAL_VALUES['perpage'],
        choices     = (
            ('60', '60'),
            ('48', '48'),
            ('36', '36'),
            ('24', '24'),
        ),
    )
    order_by = forms.ChoiceField(
        label       = 'Order by',
        required    = False,
        initial     = INITIAL_VALUES['order_by'],
        choices     = (
            ('date', 'Date'),
            ('relevancy', 'Relevancy'),
            ('popularity', 'Popularity'),
        ),
    )
    order_direction = forms.ChoiceField(
        label       = 'Order direction',
        required    = False,
        initial     = INITIAL_VALUES['order_direction'],
        choices     = (
            ('desc' , 'Descending'),
            ('asc'  , 'Ascending'),
        ),
    )
    range = forms.ChoiceField(
        label       = 'Time range',
        required    = False,
        initial     = INITIAL_VALUES['range'],
        choices     = (
            ('all'  , 'All time'),
            ('month', 'A month'),
            ('week' , 'A week'),
            ('3days', 'Three days'),
            ('day'  , 'A day'),
        ),
    )
    mode = forms.ChoiceField(
        label       = 'Match mode',
        required    = False,
        initial     = INITIAL_VALUES['mode'],
        choices     = (
            ('extended', 'Extended'),
            ('any'  , 'Match any'),
            ('all'  , 'Match all'),
        ),
    )
    rating = forms.MultipleChoiceField(
        label       = 'Rating',
        widget      = forms.CheckboxSelectMultiple(attrs={
            'class' : 'filled-in',
        }),
        initial     = INITIAL_VALUES['rating'],
        choices     = (
            ('general'  , 'General'),
            ('mature'   , 'Mature'),
            ('adult'    , 'Adult'),
        ),
    )
    type = forms.MultipleChoiceField(
        label       = 'Type',
        widget      = forms.CheckboxSelectMultiple(attrs={
            'class' : 'filled-in',
        }),
        initial     = INITIAL_VALUES['type'],
        choices     = (
            ('art'      , 'Art'),
            ('flash'    , 'Flash'),
            ('photo'    , 'Photography'),
            ('music'    , 'Music'),
            ('story'    , 'Story'),
            ('poetry'   , 'Poetry'),
        ),
    )
    page = forms.IntegerField(
        widget      = forms.HiddenInput(),
        initial     = INITIAL_VALUES['page'],
        min_value   = 1,
    )

    def __init__(self, initial=None):
        if initial:
            initial = initial.copy()

            for key, value in self.INITIAL_VALUES.iteritems():
                if not key in initial:
                    if isinstance(value, list):
                        initial.setlist(key, value)
                    else:
                        initial[key] = value

        logger.debug(initial)
        super(SearchForm, self).__init__(initial)

    def args(self):
        cleaned_data = super(SearchForm, self).clean()
        args = []

        for field, field_data in cleaned_data.iteritems():
            if isinstance(field_data, list):
                field_data = ','.join(field_data)

            args.append('{}={}'.format(field, field_data))

        return '&'.join(args)

    def page_nav_urls(self):
        cleaned_data = super(SearchForm, self).clean()
        page = cleaned_data.pop('page')
        args = []

        for field, field_data in cleaned_data.iteritems():
            if isinstance(field_data, list):
                for item in field_data:
                    args.append('{}={}'.format(field, item))
            else:
                args.append('{}={}'.format(field, field_data))

        args = '&'.join(args)
        prev = '{}&page={}'.format(args, page-1) if page > 1 else False
        next = '{}&page={}'.format(args, page+1)

        return prev, next

