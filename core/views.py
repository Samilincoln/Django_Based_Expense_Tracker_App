from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addbook_info, UserProfile
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
import datetime
from django.utils import timezone
from tablib import Dataset
from .resources import AddbookResources
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage



def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/index')
    return render(request, 'home/login.html')
    #return HttpResponse('This is Home')

def index(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addbook_info = Addbook_info.objects.all().order_by('Date')
        paginator = Paginator(addbook_info, 4)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_number)
        context = {
            'page_obj' : page_obj
        }
        return render(request, 'home/index.html', context)
    return redirect('home')

def register(request):
    return render(request,'home/register.html')
    #return HttpResponse('This is blog')
def password(request):
    return render(request,'home/password.html')

def charts(request):
    return render(request,'home/charts.html')
def search(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.GET['fromdate']
        todate = request.GET['todate']
        addbook = Addbook_info.objects.filter(user=user, Date__range=[fromdate,todate]).order_by('-Date')
        return render(request,'home/tables.html',{'addbook':addbook})
    return redirect('home')

def tables(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        addmoney = Addbook_info.objects.filter(user=user).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')

def addmoney(request):
    return render (request, 'home/addmoney.html')

def profile(request):
    if request.session.has_key('is_logged'):
        return render (request, 'home/profile.html')
    return redirect ('/home')

def profile_edit(request, id):
    if request.session.has_key('is_logged'):
        add = User.objects.get(id=id)
        return render(request, 'home/profile_edit.html', {'add':add})
    return redirect ('/home')

def profile_update(request,id):
    if request.session.has_key('is_logged'):
        if request.method == 'POST':
            user = User.objects.get(id=id)
            user.first_name = request.POST['fname']
            user.last_name = request.POST['lname']
            user.email = request.POST['email']
            user.userprofile.role = request.POST['role']
            user.userprofile.save()
            user.save()
        return redirect ('/profile')
    return redirect ('/home')

def handleSignup(request):
    if request.method == 'POST':
        uname = request.POST['uname']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        role = request.POST['role']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        profile = UserProfile()

        if request.method == 'POST':
            try:
                user_exists = User.objects.get(username =request.POST['uname'])
                messages.error(request, 'Username already taken, Try something else !!!')
                return redirect('/register')
            except User.DoesNotExist:
                if len(uname)>15:
                    messages.error(request, 'Username must be max 15 characters, Please try again')
                    return redirect('/register')
                
                if not uname.isalnum():
                    messages.errror(request, 'Username should only contain letters and numbers, Please try again')
                    return redirect('/register')
                
                if pass1 != pass2:
                    messages.error(request, 'Password do not match, Please try again')
                    return redirect('/register')
                
        user = User.objects.create_user(uname, email, pass1)
        user.first_name=fname
        user.last_name =lname
        user.email = email

        user.save()
        profile.user = user
        profile.save()
        messages.success(request,'Your account has been successfully created' )
        return redirect('/')
    else:
        return HttpResponse('404 - NOT FOUND')
    return redirect('/login')

def handlelogin(request):
    if request.method == 'POST':
        loginuname = request.POST["loginuname"]
        loginpassword1=request.POST["loginpassword1"]
        user = authenticate(username=loginuname, password=loginpassword1)
        if user is not None:
            dj_login(request, user)
            request.session['is_logged']= True
            user = request.user.id
            request.session['user_id'] = user
            messages.success(request, 'Successfully logged in')
            return redirect('/index')
        else:
            messages.error(request,'Invalid Credentials, Please try again ')
            return redirect('/')
    return HttpResponse('404 - NOT FOUND')

def handleLogout(request):
    del request.session['is_logged']
    del request.session['user_id']
    logout (request)
    messages.success(request, 'Successfully logged out')

def addmoney_submission(request):
    if request.session.has_key('is_logged'):
        if request.method == 'POST':
            user_id = request.session['user_id']
            user1 = User.objects.get(id=user_id)
            addbook_info1 = Addbook_info.objects.filter(user=user1).order_by('-Date')
            book_id = request.POST['book_id']
            title = request.POST["title"]
            subtitle = request.POST['subtitle']
            authors = request.POST['authors']
            publisher = request.POST['publisher']
            Date = request.POST["Date"]
            category = request.POST['category']
            distribution_expense = request.POST['distribution_expense']
        
            add = Addbook_info(user=user1, book_id=book_id, title=title, Date=Date, subtitle=subtitle,authors=authors,publisher=publisher,category=category,distribution_expense=distribution_expense)
            add.save()
            paginator = Paginator(addbook_info1, 4)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator, page_number)

            context = {
                'page_obj' : page_obj
            }
        return render(request, 'home/index.html', context)
    return redirect('/index')

def addmoney_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == 'POST':
            add = Addbook_info.objects.get(id=id)
            add.book_id = request.POST['book_id']
            add.title = request.POST["title"]
            add.subtitle = request.POST['subtitle']
            add.authors = request.POST['authors']
            add.publisher = request.POST['publisher']
            add.Date = request.POST['Date']
            add.category = request.POST['category']
            add.distribution_expense = request.POST['distribution_expense']
            add.save()
            return redirect('/index')
    return redirect('/home')

def import_excel(request):
    if request.method == 'POST':
        Addbook_info11 = AddbookResources
        dataset = Dataset
        new_book = request.FILES['myfile']
        data_import = dataset.load(new_book.read(), format='xls', in_stream=bytes)
        result = AddbookResources.import_data(dataset, dry_run=True)
        if not result.has_errors():
            AddbookResources.import_data(dataset, dry_run=False)
    return render(request, 'home/import_excel_db.html', {})

def import_excel_pandas(request):
    
    if request.method == 'POST' and request.FILES['myfile']:      
        myfile = request. FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)              
        empexceldata = pd.read_excel(filename)        
        dbframe = empexceldata
        for dbframe in dbframe.itertuples():
            obj = Addbook_info.objects.create(Empcode=dbframe.user,firstName=dbframe.book_id, middleName=dbframe.title,
                                            lastName=dbframe.subtitle, email=dbframe.authors, phoneNo=dbframe.publisher, address=dbframe.Date,
                                            gender=dbframe.category, DOB=dbframe.distribution_expense )           
            obj.save()
        return render(request, 'import_excel_db.html', {
            'uploaded_file_url': uploaded_file_url
        })   
    return render(request, 'import_excel_db.html',{})































































































































































'''def expense_edit(request, id):
    if request.session.has_key('is_logged'):
        addbook_info = Addbook_info.objects.get(id=id)
        user_id = request.session['user_id']
        user1 = User.objects.get(id=user_id)
        return render(request,'home.expense_edit.html', {'addbook_info': addbook_info})
    return redirect ('/home')

    
def expense_delete(request, id):
    if request.sessions.has_key('is_logged'):
        addbook_info = Addbook_info.objects.get(id=id)
        addbook_info.delete()
        return redirect('/index')
    return redirect('/home')

def expense_month(request):
    todays_date = datetime.date.today()
    one_month_ago = todays_date - datetime.timedelta(days=30)
    user_id = request.session['user_id']
    #user1 = User.objects.get(id=user_id)
    addbook = Addbook_info.objects.filter(Date_gte=one_month_ago,Date_lte=todays_date)
    finalrep = {}

def expense_week(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=7)
    #user_id = request.session["user_id"]
    #user1 = User.objects.get(id=user_id)
    addmoney = Addbook_info.objects.filter(Date__gte=one_week_ago,Date__lte=todays_date)
    finalrep ={}

def info_year(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=30*12)
    #user_id = request.session["user_id"]
    #user1 = User.objects.get(id=user_id)
    addbook = Addbook_info.objects.filter(Date__gte=one_week_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addbook_info):
        return addbook_info.Category
        Category_list = list(set(map(get_Category,addmoney)))


    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def check(request):
    if request.method == 'POST':
        user_exists = User.objects.filter(email=request.POST['email'])
        messages.error(request,"Email not registered, TRY AGAIN!!!")
        return redirect("/reset_password")
    
def info(request):
    return render(request,'home/info.html')

def weekly(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_week_ago = todays_date-datetime.timedelta(days=7)
        #user_id = request.session["user_id"]
        #user1 = User.objects.get(id=user_id)
        addbook_info = Addbook_info.objects.filter(Date__gte=one_week_ago,Date__lte=todays_date)
        sum = 0 
        for i in addbook_info:
            sum=sum+i.distribution_expense
        addbook_info.sum = sum
        sum1 = 0 
        for i in addbook_info:
            if i.add_book == 'Income':
                sum1 =sum1+i.quantity
        addbook_info.sum1 = sum1
        x= user1.userprofile.Savings+addbook_info.sum1 - addbook_info.sum
        y= user1.userprofile.Savings+addbook_info.sum1 - addbook_info.sum
        if x<0:
            messages.warning(request,'Your expenses exceeded your savings')
            x = 0
        if x>0:
            y = 0
        addbook_info.x = abs(x)
        addbook_info.y = abs(y)
    return render(request,'home/weekly.html',{'addmoney_info':addbook_info})



    def get_Category(addbook_info):
        return addbook_info.category
    Category_list = list(set(map(get_Category,addbook)))

    def get_expense_category_amount(category,distribution_expense):
        total = 0 
        filtered_by_category = addmoney.filter(category = category,distribution_expense="distribution_expense") 
        for item in filtered_by_category:
            total += item.distribution_expense
        return total

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)'''


'''def stats(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_month_ago = todays_date-datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addbook_info = Addbook_info.objects.filter(user = user1,Date__gte=one_month_ago,Date__lte=todays_date)
        sum = 0 
        for i in addbook_info:
            if i.add_book == 'Expense':
                sum=sum+i.quantity
        addbook_info.sum = sum
        sum1 = 0 
        for i in addbook_info:
            if i.add_money == 'Income':
                sum1 =sum1+i.quantity
        addbook_info.sum1 = sum1
        x= user1.userprofile.distribution_expense+addbook_info.sum1 - addbook_info.sum
        y= user1.userprofile.distribution_expense+addbook_info.sum1 - addbook_info.sum
        if x<0:
            messages.warning(request,'Your expenses exceeded your savings')
            x = 0
        if x>0:
            y = 0
        addbook_info.x = abs(x)
        addbook_info.y = abs(y)
        return render(request,'home/stats.html',{'addmoney':addbook_info})

def expense_week(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=7)
    user_id = request.session["user_id"]
    #user1 = User.objects.get(id=user_id)
    addmoney = Addbook_info.objects.filter(Date__gte=one_week_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addbook_info):
        return addbook_info.category
    Category_list = list(set(map(get_Category,addbook)))


    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)
    
def weekly(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_week_ago = todays_date-datetime.timedelta(days=7)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
        sum = 0 
        for i in addmoney_info:
            if i.add_money == 'Expense':
                sum=sum+i.quantity
        addmoney_info.sum = sum
        sum1 = 0 
        for i in addmoney_info:
            if i.add_money == 'Income':
                sum1 =sum1+i.quantity
        addmoney_info.sum1 = sum1
        x= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        y= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        if x<0:
            messages.warning(request,'Your expenses exceeded your savings')
            x = 0
        if x>0:
            y = 0
        addmoney_info.x = abs(x)
        addmoney_info.y = abs(y)
    return render(request,'home/weekly.html',{'addmoney_info':addmoney_info})

def check(request):
    if request.method == 'POST':
        user_exists = User.objects.filter(email=request.POST['email'])
        messages.error(request,"Email not registered, TRY AGAIN!!!")
        return redirect("/reset_password")

def info_year(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=30*12)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addmoney_info):
        return addmoney_info.Category
    Category_list = list(set(map(get_Category,addmoney)))


    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def info(request):
    return render(request,'home/info.html')'''





