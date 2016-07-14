from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
	return HttpResponse("Hello World!")

def show(request, book_id):
	return HttpResponse(book_id)

def 
	
