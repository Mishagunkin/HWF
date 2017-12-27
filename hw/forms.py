from django import forms
from . import models


class AuthorizationForm(forms.Form):
    username = forms.CharField(min_length=5, label='Логин')
    password = forms.CharField(min_length=8,widget=forms.PasswordInput, label='Пароль')


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(min_length=5,label='Логин')
    password = forms.CharField(min_length=8,widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput, label='Повторите ввод')
    email = forms.EmailField(label='Email')
    last_name = forms.CharField(label='Фамилия')
    first_name = forms.CharField(label='Имя')
    photo = forms.FileField(label='Аватар', widget=forms.ClearableFileInput(attrs={'class':'ask-signup-avatar-input'}),required=False)

    class Meta:
        model = models.Traveler
        fields = ('username', 'password', 'password2', 'email', 'last_name', 'first_name', 'photo')


class HotelRegistrationForm(forms.ModelForm):
    name = forms.CharField(min_length=5, max_length=30, label='Название')
    adress = forms.CharField(min_length=1, max_length=30, label='Адрес')
    description = forms.CharField(min_length=1, max_length=255, label='Описание')
    photo = forms.FileField(label='Фотография', required=False)


    class Meta:
        model = models.Hotel
        fields = ('name', 'adress', 'description', 'photo', 'features')


class BookingForm(forms.Form):
    user = forms.CharField(disabled=True,label='Постоялец')
    hotel = forms.CharField(disabled=True, label='Отель')
    price = forms.CharField(disabled=True,label='Стоимость')
    start_date = forms.DateField(widget=forms.SelectDateWidget(), label='Дата прибытия')
    end_date = forms.DateField(widget=forms.SelectDateWidget(), label='Дата отбытия')
