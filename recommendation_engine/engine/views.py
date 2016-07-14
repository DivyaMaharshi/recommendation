from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
	return HttpResponse("Hello World!")

def show(request, book_id):
	# Update user_click_history
	return HttpResponse(book_id)

def buy_now(request, book_id):
	# update purchase_history and user_bought_history
	return HttpResponse(book_id)

def product_rating(request, book_id):
	#update purchase_history
	return HttpResponse(book_id)

	
