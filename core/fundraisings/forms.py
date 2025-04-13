from django import forms
from fundraisings.models import Fundraising, Category

class UpdateFundraisingForm(forms.ModelForm):
    class Meta:
        model = Fundraising
        fields = ('title', 'description', 'main_image', 'needed_sum', 'end_date', 'link_for_money')
        # start_date removed from fields
