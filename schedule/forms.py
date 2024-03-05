from django import forms
from django.utils.translation import gettext_lazy as _
from schedule.models import Event, Occurrence, Rule
import datetime
import time


class SpanForm(forms.ModelForm):

    start = forms.DateTimeField(label=_("start"),
                                widget=forms.SplitDateTimeWidget)
    end = forms.DateTimeField(label=_("end"),
                              widget=forms.SplitDateTimeWidget, help_text = _("The end time must be later than start time."))

    def clean_end(self):
        if self.cleaned_data['end'] <= self.cleaned_data['start']:
            raise forms.ValidationError(_("The end time must be later than start time."))
        return self.cleaned_data['end']


class EventForm(SpanForm):
    def __init__(self, hour24=False, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
    
    end_recurring_period = forms.DateTimeField(label=_("End recurring period"),
                                               help_text = _("This date is ignored for one time only events."), required=False)
    
    class Meta:
        model = Event
        exclude = ('creator', 'created_on', 'calendar')


class OccurrenceForm(SpanForm):

    class Meta:
        model = Occurrence
        exclude = ('original_start', 'original_end', 'event', 'cancelled')


class RuleForm(forms.ModelForm):
    params = forms.CharField(widget=forms.Textarea, required=False, help_text=_("Extra parameters to define this type of recursion. Should follow this format: rruleparam:value;otherparam:value."))

    def clean_params(self):
        params = self.cleaned_data["params"]
        try:
            Rule(params=params).get_params()
        except (ValueError, SyntaxError):
            raise forms.ValidationError(_("Params format looks invalid"))
        return self.cleaned_data["params"]
