from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Users, Books, UserClickHistory, PurchaseHistory, UserBoughtHistory
from decimal import Decimal

# Create your views here.

def index(request):
	books = Books.objects.all()
	return render(request, 'engine/index.html', {'books': books})

def show(request, book_id):
	user_id = 1
	# Update user_click_history
	try:
		x = UserClickHistory.objects.get(user_id=user_id,book_id=book_id)
	except UserClickHistory.DoesNotExist:
		x = UserClickHistory.objects.create(user_id=user_id, book_id=book_id, clicks=0)
	x.clicks = x.clicks + 1
	x.save()

	book = Books.objects.get(pk=book_id)
	return render(request, 'engine/show.html',{'book': book})

def buy_now(request, book_id):
	user_id = 1
	# update purchase_history
	try:
		x = PurchaseHistory.objects.get(book_id=book_id)
	except PurchaseHistory.DoesNotExist:
		x = PurchaseHistory.objects.create(book_id=book_id, quantity=0, rating=0, rating_count=0)
	x.quantity = x.quantity + 1
	x.save()

	# update user_bought_history
	try:
		ub = UserBoughtHistory.objects.get(user_id=user_id, book_id=book_id)
	except UserBoughtHistory.DoesNotExist:
		ub = UserBoughtHistory.objects.create(book_id=book_id, user_id=user_id, is_bought=True)

	book = Books.objects.get(pk=book_id)
	return render(request, 'engine/rating.html', {'book': book, 'loop_times': range(1,6)})

def product_rating(request, book_id):
	user_id = 1
	rating = Decimal(request.POST["user_rating"])
	#update purchase_history
	x = PurchaseHistory.objects.get(book_id=book_id)
	x.rating = (x.rating*x.rating_count + rating)/(x.rating_count + 1)
	x.rating_count = x.rating_count + 1
	x.save()
	
	return HttpResponse("You rated this book " + str(rating) + " star")


	
