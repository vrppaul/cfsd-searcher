from django import forms


class SearchForm(forms.Form):
    search_input = forms.CharField(
        max_length=255,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "type here..."}),
    )
