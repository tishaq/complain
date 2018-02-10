# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.shortcuts import render, redirect, get_object_or_404

from complain.models import Govt_Agency_Access
from .models import Complain, Govt_Agency
import random
from .forms import UserForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


# Create your views here.
def complains_list(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        agency = request.POST['agency']
        message = request.POST['message']
        code = genCode()
        agncy = Govt_Agency.objects.get(name=agency)
        n_comp = Complain(code=code, subject=subject, govt_agency=agncy, message=message)
        n_comp.save()
        return redirect('/complain/' + str(code))

    govt_agency = Govt_Agency.objects.all()
    complains = Complain.objects.all()
    context = {
        'complains': complains,
        'agencies': govt_agency
    }
    return render(request, "index.html", context)


def check_status(request):
    if request.method == 'POST':
        code = request.POST['code']
        # return redirect('/complain/'+str(code))
        govt_agency = Govt_Agency.objects.all()
        if request.user.is_authenticated():
            if Govt_Agency_Access.objects.filter(user = request.user):
                #c = Complain.objects.filter(code=code).update(status='opened complain')
                complain = Complain.objects.filter(code=code)
                complain.status = "opened complain"
                complain.save()
        #complain = Complain.objects.get(code=code)
        #complain = get_object_or_404(Complain, code=code)
        error = []
        try:
            complain = Complain.objects.get(code=code)
        except Complain.DoesNotExist:
            complain = None
        context = {
            'complain': complain,
            'agencies': govt_agency
        }
        return render(request, "status.html", context)
    else:
        return redirect('/complain/')


def complains_status(request, pk):
    govt_agency = Govt_Agency.objects.all()
    if request.user.is_authenticated():
        if Govt_Agency_Access.objects.filter(user = request.user):
            Complain.objects.filter(code=pk).update(status='opened')
    complain = Complain.objects.get(code=pk)
    context = {
        'complain': complain,
        'agencies': govt_agency
    }
    return render(request, "status.html", context)


def genCode():
    rndm = random.randint(1, 1001) * 5

    cmpln = Complain.objects.filter(code=rndm).count()
    if cmpln > 0:
        genCode()
    else:
        return rndm


###agency
def register_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.save()
            authenticate(username=form_obj.username, password=form_obj.password)
            return HttpResponse('contact site admin for activation thank you for signing up')
    else:
        form = UserForm()
    # return render(request, 'register_user.html',{'form':form})
    return render(request, "agency/signup.html", {'form':form})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/agency/')
        else:
            return render(request, "agency/login.html", {'errors':['Your username or password is incorrect']})
    else:
        form = LoginForm()
    # return render(request, 'login.html',{'form':form})
    return redirect('/complain/')


def login_out(request):
    logout(request)
    return redirect('/agency/')

# agency list
def agency_complains_list(request):
    if request.user.is_authenticated():
        gov_access = Govt_Agency_Access.objects.filter(user = request.user)
        if gov_access:
            gov_access = Govt_Agency_Access.objects.get(user = request.user)
            gov = Govt_Agency.objects.get(id=gov_access.agency.id)
            complains = Complain.objects.filter(govt_agency=gov)
            context={"complains":complains,
                     "gov":gov}
            return render(request, "agency/index.html", context)
        else:
            logout(request)
            return render(request, "agency/login.html", {'errors':['Your username is not linked to any agency. Contact Site admin.']})
    else:
        return render(request, "agency/login.html")
