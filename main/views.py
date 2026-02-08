from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Category, Profile
from cart.cart import Cart
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from payment.forms import  ShippingForm
from payment.models import ShippingAddress
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
import json


def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not searched:
            messages.error(request, ('That product does not exist. Please try again.'))
            return render(request, 'main/search.html')
        else:
            return render(request, 'main/search.html', {'searched': searched})
    else:
        return render(request, 'main/search.html', {})




def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()

            messages.success(request, ('Your Info has been updated successfully.'))
            return redirect('home')
        return render(request, 'main/update_info.html', {'form': form, 'shipping_form':shipping_form})
    else:
        messages.error(request, ('You must be logged in to update your profile.'))
        return redirect('home')



def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, ('Your password has been updated successfully.'))
                login(request, current_user)
                return redirect('update_password')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(user=current_user)
            return render(request, 'main/update_password.html', {'form': form})
    else:
        messages.error(request, ('You must be logged in to update your password.'))
        return redirect('home')





def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, ('Your profile has been updated successfully.'))
            return redirect('home')
        return render(request, 'main/update_user.html', {'user_form': user_form})
    else:
        messages.error(request, ('You must be logged in to update your profile.'))
        return redirect('home')

  




def category_summary(request):
    categories = Category.objects.filter()
    context = {
        'categories': categories,
    }        
    return render(request, 'main/category_summary.html', context)







def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    categories = Category.objects.all()
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }
    return render(request, 'main/category.html', context)



def product(request, pk):

    product = Product.objects.get(id=pk)
    context = {
        'product': product
    }
    return render(request, 'main/product.html', context)



def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'main/home.html', context)


def about(request):
    return render(request, 'main/about.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            current_user = Profile.objects.filter(user__id=request.user.id).first()
            saved_cart = current_user.old_cart
            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)

                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)



            messages.success(request, ('You have been logged in successfully.'))
            return redirect('home')
        else:
            messages.error(request, ('Invalid username or password. Please try again.'))
            return redirect('login')
    return render(request, 'main/login.html')

def logout_user(request):
    logout(request)
    messages.success(request, ('You have been logged out successfully.'))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    context = {'form': form}
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('Username created successfully. Please Fill Out Your User Info Below...'))
            return redirect('update_info')
        else:
            messages.success(request, ('Registration failed. Please correct the errors below.'))
            return redirect('register')
    else:
        return render(request, 'main/register.html', context)
    