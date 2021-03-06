from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from engine.header import *
from django.db import connection
import math
from .models import Users, Books, UserClickHistory, PurchaseHistory, UserBoughtHistory
from decimal import Decimal
import pdb

# Create your views here.

def set_user(request):
	user_id = request.POST.get("user_id")
	if user_id != None:
		response = redirect('index')
		response.set_cookie('user_id', user_id)
		return response
	else:
		users = Users.objects.all()
		return render(request, 'engine/select_user.html', {'users': users})

def index(request, user_id):
	user_id = int(user_id)
	user = Users.objects.get(pk=user_id)

	books = Books.objects.all()
	paginator = Paginator(books, 5)

	page = request.GET.get('page')
	try:
		books = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
 		books = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		books = paginator.page(paginator.num_pages)
	recommended_books, top_5_books = fn_calculation_for_each_book(request, user_id)
	
	return render(request, 'engine/index.html', {'books': books, 'recommended_books': top_5_books, 'user': user})

def bought(request, user_id):
	user_id = int(user_id)
	user = Users.objects.get(pk=user_id)

	books = Books.objects.all()
	paginator = Paginator(books, 5)

	page = request.GET.get('page')
	try:
		books = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
 		books = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		books = paginator.page(paginator.num_pages)

	books = []
	for bought_book in UserBoughtHistory.objects.filter(user_id=user_id):
		books.append(Books.objects.get(pk=bought_book.book_id))
	recommended_books, top_5_books = fn_calculation_for_each_book(request, user_id)
	return render(request, 'engine/bought.html',{'books':books, 'recommended_books': top_5_books, 'user':user})

def show(request, user_id, book_id):
	user_id = int(user_id)
	user = Users.objects.get(pk=user_id)
	# Update user_click_history
	try:
		x = UserClickHistory.objects.get(user_id=user_id,book_id=book_id)
	except UserClickHistory.DoesNotExist:
		x = UserClickHistory.objects.create(user_id=user_id, book_id=book_id, clicks=0)
	x.clicks = x.clicks + 1
	x.save()


	book = Books.objects.get(pk=book_id)
	recommended_books, top_5_books = fn_calculation_for_each_book(request, user_id)
	return render(request, 'engine/show.html',{'book': book, 'recommended_books': top_5_books, 'user': user})

def buy_now(request, user_id, book_id):
	user_id = int(user_id)
	user = Users.objects.get(pk=user_id)
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
	return render(request, 'engine/rating.html', {'book': book, 'loop_times': range(1,6), 'user': user})

def product_rating(request, user_id, book_id):
	user_id = int(user_id)
	user = Users.objects.get(pk=user_id)

	rating = Decimal(request.POST["user_rating"])
	#update purchase_history
	x = PurchaseHistory.objects.get(book_id=book_id)
	x.rating = (x.rating*x.rating_count + rating)/(x.rating_count + 1)
	x.rating_count = x.rating_count + 1
	x.save()
	
	return render(request, 'engine/rated.html',{'user':user, 'rating':rating})
	#return HttpResponse("You rated this book " + str(rating) + " star")


def sql_dictfetchall(sql_query):
        cursor = connection.cursor()
        cursor.execute(sql_query)
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def intersect(a, b):
    return list(set(a) & set(b))
	

def books_affinity_score(request):
    # books count
    affinity_dict = {}
    books_count=Books.objects.all()
    for booka in range(len(books_count)):
        affinity_dict[str(booka)] = {}
        for bookb in  range(booka+1, len(books_count)):
            user_list = Users.objects.values("id")
            booka_count_list =  [i['id'] for i in user_list]
            booka_count = UserBoughtHistory.objects.filter(book__id = booka).values("user_id")
            bookb_count = UserBoughtHistory.objects.filter(book__id = bookb).values("user_id")  
            booka_count_list =  [i['user_id'] for i in booka_count]
            bookb_count_list =  [i['user_id'] for i in bookb_count]
            
            yayb = len(intersect(booka_count_list, bookb_count_list))
            yanb = len([item for item in booka_count if item not in bookb_count])
            nayb = len([item for item in bookb_count if item not in booka_count])
            nanb = len([item for item in user_list if (item not in booka_count and item not in bookb_count)])
            
            temp1 = yayb*nanb - yanb*nayb
            temp2 = (yayb+yanb) * (nayb+nanb) * (yayb+nayb) * (yanb+nanb) 
            temp3 = math.sqrt(temp2) 
            temp4 = 0
            if temp3 !=0 :
                temp4 = temp1/temp3
         
            temp={}
            temp[str(bookb)] = temp4
            affinity_dict[str(booka)].update(temp)
            
    return affinity_dict


def alpha_product_bought_score(request):

    books_purchased_dict=[]
    books_purchased_dict_final={}
    # to consider all books
    books_list = Books.objects.values("id")
    books_list =  [i['id'] for i in books_list]
     
    #total purchased amount
    company_total_purchased_quantity = PurchaseHistory.objects.aggregate(total=Sum("quantity"))
    company_total_purchased_quantity = company_total_purchased_quantity['total']

    # each book purchased quantity
    total_purchase_bookwise = PurchaseHistory.objects.values("book").annotate(total_purchased=Sum("quantity")).order_by('book')
    books_keys_list = [i['book'] for i in total_purchase_bookwise ]
    total_purchase_bookwise  = list(total_purchase_bookwise)

    for book_id in books_list:
        if book_id not in books_keys_list :
            temp={}
            temp['book'] = book_id
            temp['total_purchased'] = 0 
            temp['total_normalised'] = 0
            total_purchase_bookwise.append(temp)

    
    for purchase_dict in  total_purchase_bookwise :
        if 'total_normalised' not in purchase_dict.keys():
            if company_total_purchased_quantity > 0 :
                purchase_dict['total_normalised'] = round(purchase_dict['total_purchased']/company_total_purchased_quantity,2)
                books_purchased_dict.append(purchase_dict)
        else: 
            books_purchased_dict.append(purchase_dict) 

    for i in books_purchased_dict:
        books_purchased_dict_final[str(i['book'])] = i
    
    return books_purchased_dict_final


def gamma_product_rating_score(request):
    
    books_ratings_dict = []
    books_ratins_dict_final = {}
    # to consider all books
    books_list = Books.objects.values("id")
    books_list =  [i['id'] for i in books_list]
    
    # each book purchased quantity
    books_ratings = PurchaseHistory.objects.values("book",'rating').order_by('book')
    books_keys_list = [i['book'] for i in books_ratings ]
    books_ratings  = list(books_ratings)

    for book_id in books_list:
        if book_id not in books_keys_list :
            temp={}
            temp['book'] = book_id
            temp['rating'] = 0 
            temp['normalised_rating'] = 0
            books_ratings.append(temp)
    
    for ratings_dict in  books_ratings :
        if 'normalised_rating' not in ratings_dict.keys():
                ratings_dict['normalised_rating'] = round(ratings_dict['rating']/5,2)
                books_ratings_dict.append(ratings_dict)
        else: 
            books_ratings_dict.append(ratings_dict)

    for i in books_ratings_dict:
        books_ratins_dict_final[str(i['book'])] = i

    return books_ratins_dict_final
   


def product_click_score(request):
    
    product_clicks_dict={}
    sql_query = "select u1.user_id,u1.book_id,u1.clicks,is_bought from  user_click_history u1 left outer join user_bought_history u2 on u1.user_id = u2.user_id and u1.book_id = u2.book_id and is_bought != 't' "
    clicked_butnotbought = sql_dictfetchall(sql_query)

    sql_query = "select user_id,sum(clicks) from user_click_history group by user_id order by user_id "
    productwise_totalclicks = sql_dictfetchall(sql_query)
    productwise_totalclicks = {str(i['user_id']):i['sum'] for i in productwise_totalclicks}
    
    
    for clicked_dict in clicked_butnotbought:
        clicked_dict['normalised_clicks'] = round(clicked_dict['clicks']/productwise_totalclicks[str(clicked_dict['user_id'])],3)
    
    for i in clicked_butnotbought:
        if str(i['user_id']) not in product_clicks_dict.keys():
            product_clicks_dict[str(i['user_id'])]={}
            product_clicks_dict[str(i['user_id'])][str(i['book_id'])]=i

        else:
            temp={}
            temp[str(i['book_id'])] = i
            product_clicks_dict[str(i['user_id'])].update(temp)

    return product_clicks_dict 


def fn_calculation_for_each_book(request, user_id):
    #function call
    fn_score={}
    affinity_dict = books_affinity_score(request)
    books_purchased_dict = alpha_product_bought_score(request)
    books_ratings_dict = gamma_product_rating_score(request)
    clicked_butnotbought = product_click_score(request)
    
    # all books list
    books_list = Books.objects.values("id")
    books_list =  [i['id'] for i in books_list]

    #books bought by that user_id
    user_bought_books_list = UserBoughtHistory.objects.filter(user=user_id).values('book')
    user_bought_books_list = [i['book'] for i in user_bought_books_list]

    for book_id in books_list:
        
        check_new_or_repeat = UserBoughtHistory.objects.filter(book=book_id,user=user_id).values('user_id')
        if len(check_new_or_repeat) == 0:
            # calculate alpha,gamma, beta
            alpha = books_purchased_dict[str(book_id)]['total_normalised']
            gamma = float(books_ratings_dict[str(book_id)]['normalised_rating'])
            if str(user_id) in clicked_butnotbought.keys():
                if str(book_id) in list(clicked_butnotbought[str(user_id)].keys()):
                    beta = clicked_butnotbought[str(user_id)][str(book_id)]['normalised_clicks']
                else : 
                    beta = 0
            else:
                beta = 0

            total = round(((.20*alpha) + (.20*gamma) + (.60*beta)),4)
            fn_score.update({str(book_id) :total})

        else :
            alpha = books_purchased_dict[str(book_id)]['total_normalised']
            gamma = float(books_ratings_dict[(str(book_id))]['normalised_rating'])
            if str(user_id) in clicked_butnotbought.keys():
                if str(book_id) in list(clicked_butnotbought[str(user_id)].keys()):
                    beta = clicked_butnotbought[str(user_id)][str(book_id)]['normalised_clicks']
                else : 
                    beta = 0
            else:
                beta = 0
            
            # PHI calculation 
            user_bought_books_list = UserBoughtHistory.objects.filter(user=user_id).values('book')
            user_bought_books_list =  [i['book'] for i in user_bought_books_list]
            
            #case 1 if book is in the user_bought_books_list
            affinity_list=[]
            if book_id in user_bought_books_list:
                phi = 0

            else:
                for already_bought in user_bought_books_list:
                    min_book_id = min(book_id,already_bought)
                    max_book_id = max(book_id,already_bought)

                    if str(min_book_id) in affinity_dict.keys():
                        if str(max_book_id) in affinity_dict[str(min_book_id)].keys(): 
                            phi = affinity_dict[str(min_book_id)][str(max_book_id)]
                            affinity_list.append(phi)
                        else :
                            phi = 0
                    else:
                        phi = 0 
            
            if len(affinity_list) > 0:
                average_phi = sum(affinity_list)/len(affinity_list)
            else:
                average_phi = 0
            
            total = round(((.20*alpha) + (.20*gamma) + (.40*beta) + (.20*average_phi)), 4)
            fn_score.update({str(book_id) :total})

            
    # check recommended books should not be in consideration 
    for i in user_bought_books_list :
    	if str(i) in fn_score.keys():
    	    fn_score.pop(str(i))

    final_fn_score_withbooks_names = select_top5_books(fn_score)
    return fn_score,final_fn_score_withbooks_names


def  select_top5_books(fn_score):
    
    final_books_dict=[]
    import operator 
    sorted_x = sorted(fn_score.items(), key=operator.itemgetter(1),reverse=True)
    sorted_x = sorted_x[:5]
    for i in sorted_x:
        temp={}
        book_name = Books.objects.filter(id=i[0]).values('id','name')
        final_books_dict.append({'book_id':book_name[0]['id'],'book_name':str(book_name[0]['name']), 'score': i[1]})
    
    final_books_dict.sort(lambda x,y : cmp(x['score'], y['score']), reverse=True)
    return final_books_dict

