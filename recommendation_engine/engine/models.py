from django.db import models
from engine.models import *

# Create your models here.

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=70)
 
    class Meta:
        db_table  = "users"
        app_label = "engine"
        managed = True

    def __str__(self):
    	return self.name


class Books(models.Model):
    id = models.IntegerField(primary_key=True)
    name =  models.CharField(max_length=70)
  

    class Meta:
        db_table  = "books"
        app_label = "engine"
        managed = True

    def __str__(self):
    	return self.name


class UserClickHistory(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(Users)
	book = models.ForeignKey(Books)
	clicks =  models.IntegerField()
  

	class Meta:
		db_table  = "user_click_history"
		app_label = "engine"
		managed = True


class UserBoughtHistory(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.ForeignKey(Users)
	book = models.ForeignKey(Books)
	is_bought =  models.BooleanField()
  

	class Meta:
		db_table  = "user_bought_history"
		app_label = "engine"
		managed = True


class PurchaseHistory(models.Model):
	id = models.AutoField(primary_key=True)
	book = models.ForeignKey(Books)
	quantity = models.IntegerField()
	rating = models.DecimalField(decimal_places=2,max_digits=5)
	rating_count = models.IntegerField()
  

	class Meta:
		db_table  = "purchase_history"
		app_label = "engine"
		managed = True











        
        

