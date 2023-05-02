from django import forms

class BuscadorCasetas(forms.Form):
    titulo = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Título caseta'})
    )