from django import forms
from django.utils.safestring import mark_safe
from textwrap import dedent

class SearchBooleanField(forms.BooleanField):
    def __init__(self, label, *args, **kwargs):
        kwargs['label']     = label
        kwargs['initial']   = True
        kwargs['required']  = False
        kwargs['label_suffix'] = ''
        kwargs['widget']    = forms.CheckboxInput(attrs={
            'class'         : 'filled-in',
        })
        super(SearchBooleanField, self).__init__(*args, **kwargs)

class SearchForm(forms.Form):
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
        initial     = '60',
        choices     = (
            ('60', '60'),
            ('48', '48'),
            ('36', '36'),
            ('24', '24'),
        ),
    )
    order_by = forms.ChoiceField(
        label       = 'Order by',
        initial     = 'date',
        choices     = (
            ('date', 'Date'),
            ('relevancy', 'Relevancy'),
            ('popularity', 'Popularity'),
        ),
    )
    order_direction = forms.ChoiceField(
        label       = 'Order direction',
        initial     = 'desc',
        choices     = (
            ('desc' , 'Descending'),
            ('asc'  , 'Ascending'),
        ),
    )
    range = forms.ChoiceField(
        label       = 'Time range',
        initial     = 'all',
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
        initial     = 'extended',
        choices     = (
            ('extended', 'Extended'),
            ('any'  , 'Match any'),
            ('all'  , 'Match all'),
        ),
    )

    ARGS = ('q', 'perpage', 'order_by', 'order_direction', 'range', 'mode')
    SUBM_RATINGS = ('general', 'mature', 'adult')
    SUBM_TYPES = ('art', 'flash', 'photo', 'music', 'story', 'poetry')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        for subm_rating in self.SUBM_RATINGS:
            self.fields['rating_' + subm_rating] = SearchBooleanField(
                subm_rating.capitalize()
            )
        for subm_type in self.SUBM_TYPES:
            self.fields['type_' + subm_type] = SearchBooleanField(
                subm_type.capitalize()
            )

    def args(self):
        cleaned_data = super(SearchForm, self).clean()
        args = '&'.join([
            '{}={}'.format(arg, cleaned_data.get(arg))
            for arg in self.ARGS
        ])

        ratings = ','.join([
            subm_rating
            for subm_rating in self.SUBM_RATINGS
            if cleaned_data.get('rating_' + subm_rating)
        ])
        args = args + '&rating=' + ratings if ratings else args

        types = ','.join([
            subm_type
            for subm_type in self.SUBM_TYPES
            if cleaned_data.get('type_' + subm_type)
        ])
        args = args + '&type=' + types if types else args

        return args
