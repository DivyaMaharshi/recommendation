from django.conf.urls import url

from . import views

urlpatterns = [
		url(r'^set_user/$', views.set_user, name='set_user'),
    url(r'^$', views.index, name='index'),
    url(r'^(?P<book_id>[0-9]+)/$', views.show, name='show'),
    url(r'^affinity_score/$', views.books_affinity_score, name='books_affinity_score'),
    url(r'^alpha_purchase_score/$', views.alpha_product_bought_score, name='alpha_product_bought_score'),
    url(r'^gamma_product_rating_score/$', views.gamma_product_rating_score, name='gamma_product_rating_score'),
    url(r'^product_click_score/$', views.product_click_score, name='product_click_score'),
    url(r'^(?P<book_id>[0-9]+)/buy$', views.buy_now, name='buy_now'),
    url(r'^(?P<book_id>[0-9]+)/rating$', views.product_rating, name='product_rating'),
]
