from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
	return HttpResponse("Hello World!")

def show(request, book_id):
	# Update clicks table
	return HttpResponse(book_id)

def buy_now(request, book_id):
	# update 
	return HttpResponse(book_id)

def product_rating(request, book_id):

	return HttpResponse(book_id)

	
