from django import forms

class ChatForm(forms.Form):
    message = forms.CharField()
    widgets = {
        'message': forms.Textarea(attrs={'rows': 4, 'cols': 40})
    }


