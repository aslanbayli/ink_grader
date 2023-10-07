from django import forms

class UploadFileForm(forms.Form):
    quiz_file = forms.FileField(required=False)
    answer_key_file = forms.FileField(required=False)

    student_answers = forms.ImageField()