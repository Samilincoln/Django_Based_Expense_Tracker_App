from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

SELECT_CATEGORY_CHOICES = [
    ("Business Analytics","Business Analytics"),
    ("deep learning","deep learning"),
    ("data science","data science"),
    ("maths","maths"),
    ("Data ethics","Data ethics"),
    ("NLP","NLP"),
    ("python","python"),
    ("R Studio","R Studio"),
    ("SQL","SQL"),
    ("visualization","visualization"),
    ("statistics","statistics"),
    ("Other","Others"),
]

ADD_EXPENSE_CHOICES = [
    ("Expense","Expense"),
    ("Income","Income"),
]

PROFESSION_CHOICES = [
    ("Employee","Employee"),
    ("Business","Business"),
    ("Student","Student"),
    ("Other","Other"),
    
]

class Addbook_info(models.Model):
    user = models.ForeignKey(User,default=1, on_delete=models.CASCADE)
    book_id = models.CharField(('name'), max_length=50, null=False, blank=False)
    title = models.CharField(max_length=225)
    subtitle = models.CharField(max_length=225)
    authors = models.CharField(max_length=225)
    publisher = models.CharField(max_length=225)
    Date = models.DateField(default= now, verbose_name='published_date')
    category = models.CharField(max_length= 30, choices = SELECT_CATEGORY_CHOICES, default='Others')
    distribution_expense = models.DecimalField(max_digits=4, decimal_places=2)

class Meta:

    db_table:'addbook'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length= 10, choices=PROFESSION_CHOICES)
    image = models.ImageField(upload_to='profile_image', blank=True)

    def __str__(self):

        return self.user.username
    
