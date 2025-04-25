"""FORMS"""
from django import forms
from fundraisings.models import Fundraising

class UpdateFundraisingForm(forms.ModelForm):
    """
    Form for updating a Fundraising instance.
    """
    class Meta:
        """
        Meta class for UpdateFundraisingForm.
        """
        model = Fundraising
        fields = ('title', 'description', 'main_image', 'needed_sum', 'end_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required appropriately
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['needed_sum'].required = True
        self.fields['end_date'].required = True
        # main_image can be optional during update
        self.fields['main_image'].required = False
