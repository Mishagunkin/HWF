from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login, logout
from . import models
from .forms import *
import logging
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder


logger = logging.getLogger('views')


class BookingListView(ListView):
    model = models.Booking
    template_name = 'booking_list.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(BookingListView, self).get_context_data(**kwargs)
        context['traveler'] = models.Traveler.objects.get(user=self.request.user)
        return context

    def get_queryset(self):
        try:
            trav = models.Traveler.objects.get(user=self.request.user)
            qs = models.Booking.objects.filter(user=trav)
        except:
            qs = None
        if qs is not None:
            qs = qs.order_by('-start_date')
        return qs

    @method_decorator(login_required(login_url='authorization'))
    def dispatch(self, request, *args, **kwargs):
        return super(BookingListView, self).dispatch(request, *args, **kwargs)

class SelfHotelListView(ListView):
    model = models.Hotel
    template_name = 'self_hotel_list.html'

    def get_context_data(self, **kwargs):
        context = super(SelfHotelListView, self).get_context_data(**kwargs)
        context['traveler'] = models.Traveler.objects.get(user=self.request.user)
        return context

    def get_queryset(self):
        try:
            qs = models.Hotel.objects.filter(owner=self.request.user)
            for q in qs:
                if len(q.description)>50:
                    q.description = q.description[:50]+'...'
        except:
            qs = None
        return qs

    @method_decorator(login_required(login_url='authorization'))
    def dispatch(self, request, *args, **kwargs):
        return super(SelfHotelListView, self).dispatch(request, *args, **kwargs)

class HotelListView(ListView):
    model = models.Hotel
    template_name = 'hotel_list.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(HotelListView, self).get_context_data(**kwargs)
        context['traveler'] = models.Traveler.objects.get(user=self.request.user)
        #context['booking_form'] = BookingForm()
        return context

    def get_queryset(self):
        qs = super(HotelListView, self).get_queryset()
        if qs is not None:
            for q in qs:
                if len(q.description)>50:
                    q.description = q.description[:50]+'...'
        return qs

    @method_decorator(login_required(login_url='authorization'))
    def dispatch(self, request, *args, **kwargs):
        return super(HotelListView, self).dispatch(request, *args, **kwargs)


@login_required(login_url='authorization')
def hotel_page(request, hotel):
    context = {}
    try:
        context['hotel'] = models.Hotel.objects.get(name=hotel)
        context['features'] = context['hotel'].features.all()
        context['booking_form'] = BookingForm()
        if len(context['features']) == 0:
            context['features'] = None
    except:
        context['hotel'] = None

    context['traveler'] = models.Traveler.objects.get(user=request.user)
    return render(request, 'hotel_page.html', context)


def authorization(request):
    if request.method == 'POST':
        form = AuthorizationForm(request.POST)

        is_val = form.is_valid()
        if is_val:
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            try:
                models.Traveler.objects.get(user=user)
            except:
                form.add_error('username',['Логин или пароль введены неверно'])
                is_val = False

        if is_val:
            login(request, user)
            try:
                return HttpResponseRedirect(request.GET['next'])
            except:
                return HttpResponseRedirect('/hw')
    else:
        form = AuthorizationForm()

    context = {'form':form}

    return render(request, 'authorization.html',context)


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        is_val = form.is_valid()

        if is_val:
            data = form.cleaned_data
            if data['password']!=data['password2']:
                is_val = False
                form.add_error('password2',['Пароли должны совпадать'])
            if models.User.objects.filter(username=data['username']).exists():
                form.add_error('username',['Пользователь с данным логином уже существует'])
                is_val = False
            if models.User.objects.filter(email=data['email']).exists():
                form.add_error('email',['Пользователь с данной электронной почтой уже зарегестрирован'])
                is_val = False

        if is_val:
            traveler = form.save(commit=False)
            traveler.user = models.User.objects.create_user(data['username'], data['email'], data['password'])
            traveler.save()

            return HttpResponseRedirect('/hw/authorization')
    else:
        form = RegistrationForm()

    context = {'form':form}

    return render(request, 'registration.html',context)


@login_required(login_url='authorization')
def hotel_registration(request):
    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST, request.FILES)
        is_val = form.is_valid()
        print('validation: {}'.format(is_val))
        if is_val:
            data = form.cleaned_data
            if models.Hotel.objects.filter(name=data['name']).exists():
                form.add_error('name',['Отель с таким названием уже зарегестрирован'])
                is_val = False
        if is_val:
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            form.save_m2m()
            return HttpResponseRedirect('/hw/hotel_list')
    else:
        form = HotelRegistrationForm()

    traveler = models.Traveler.objects.get(user=request.user)
    return render(request, 'hotel_registration.html', {'form':form, 'traveler':traveler})


@login_required(login_url='authorization')
def booking(request,hotel):
    traveler = models.Traveler.objects.get(user=request.user)
    inits = {'user':'{} {}'.format(traveler.last_name,traveler.first_name),
             'hotel':hotel,
             'price':5000}
    if request.method == "POST":
        form = BookingForm(request.POST, initial=inits)
        is_val = form.is_valid()
        if is_val:
            data = form.cleaned_data
            if not str.isnumeric(data['price']):
                form.add_error('price',['Цена указана некоректно'])
                is_val = False
            if data['start_date'] >= data['end_date']:
                form.add_error('end_date',['Введённая дата отбытия предшествует дате прибытия'])
                is_val = False
        if is_val:
            book = models.Booking()
            book.user = traveler
            book.hotel = models.Hotel.objects.get(name=data['hotel'])
            book.price = int(data['price'])
            book.start_date = data['start_date']
            book.end_date = data['end_date']
            book.save()
            return HttpResponseRedirect('/hw')
    else:
        form = BookingForm(initial=inits)

    return render(request, 'booking.html', {'form':form, 'traveler':traveler})


@login_required(login_url='authorization')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/hw')


@login_required(login_url='authorization')
def trav_settings(request):
    return HttpResponse("Такой странички пока нет")


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('authorization')
    else:
        return HttpResponseRedirect('book_list/1')


def ajax_book(request):
    if request.method == "POST":
        hotel = models.Hotel.objects.get(name=request.POST['hotel_name'])
        traveler = models.Traveler.objects.get(user=models.User.objects.get(email=request.POST['user_email']))
        start_date = datetime.date(int(request.POST['start_year']),int(request.POST['start_month']),int(request.POST['start_day']))
        end_date = datetime.date(int(request.POST['end_year']),int(request.POST['end_month']),int(request.POST['end_day']))
        price = int(request.POST['price'])

        book = models.Booking()
        book.user = traveler
        book.hotel = hotel
        book.price = price
        book.start_date = start_date
        book.end_date = end_date
        book.save()
        return HttpResponse('success')
        #return HttpResponse(datetime.(request.POST['start_date']))
        #return HttpResponse(forms.DateField(request.POST['start_date']))

def ajax_last_bookings(request):
    num = int(request.GET['page'])*5;

    hotel = models.Hotel.objects.get(name=request.GET['hotel_name'])
    traveler = models.Traveler.objects.get(user=models.User.objects.get(email=request.GET['user_email']))
    bookings = models.Booking.objects.filter(hotel=hotel, user=traveler).order_by('-booking_date').all()[num:num+5]
    if len(bookings) == 0:
        return HttpResponse('-')

    response =""
    if num == 0:
        response += "<thead><tr><th>Забронировано</th><th>Прибытие</th><th>Отбытие</th><th>Стоимость</th></tr></thead>"


    for b in bookings:
        response += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(b.booking_date.date(),b.start_date, b.end_date, b.price)

    return HttpResponse(response)
