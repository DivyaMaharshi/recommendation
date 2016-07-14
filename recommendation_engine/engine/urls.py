from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<book_id>[0-9]+)/$', views.show, name='show'),
    url(r'^(?P<book_id>[0-9]+)/buy$', views.buy_now, name='buy_now'),
    url(r'^(?P<book_id>[0-9]+)/rating$', views.product_rating, name='product_rating'),
]