from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^booking/(?P<hotel>[^/]+)', views.booking, name='booking'),
    url(r'^hotels/(?P<hotel>[^/]+)', views.hotel_page, name='hotel_page'),
    url(r'^self_hotel_list', views.SelfHotelListView.as_view(), name='self_hotel_list'),
    url(r'^hotel_list/$', views.HotelListView.as_view(), name='hotel_list'),
    url(r'^hotel_list/(?P<page>\d+)$', views.HotelListView.as_view(), name='hotel_list_page'),
    url(r'^hotel_registration', views.hotel_registration, name='hotel_registration'),
    url(r'^trav_settings', views.trav_settings, name='trav_settings'),
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^registration', views.registration, name='registration'),
    url(r'^authorization', views.authorization, name='authorization'),
    url(r'^book_list/$', views.BookingListView.as_view(), name='book_list'),
    url(r'^book_list/(?P<page>\d+)/$', views.BookingListView.as_view(), name='book_list_page'),
    url(r'^$', views.index, name='index')
]
ajax_functions = [
    url(r'^ajax/book/', views.ajax_book, name='ajax_book'),
    url(r'^ajax/last_bookings/', views.ajax_last_bookings, name='ajax_last_bookings'),
]

urlpatterns += ajax_functions
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

