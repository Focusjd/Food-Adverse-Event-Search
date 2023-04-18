from django import forms

class SearchForm(forms.Form):
    GENDER_CHOICES = (
        ('', 'Any'),
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    age = forms.IntegerField(min_value=0, required=False)
    product_name = forms.CharField(max_length=200, required=False)
    reactions = forms.CharField(max_length=200, required=False)
