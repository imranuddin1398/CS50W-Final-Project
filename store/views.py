from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, Category, Review, UserProfile
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def category(request):
    categoryFromForm = None
    category = None

    if request.method == "POST":
        categoryFromForm = request.POST.get('category', '')
        return redirect(f"{request.path}?category={categoryFromForm}")

    categoryFromForm = request.GET.get('category', '')
    if categoryFromForm:
        category = Category.objects.get(name=categoryFromForm)
    
    activeProduct = Product.objects.all()
    
    if category:
        activeProduct = activeProduct.filter(category=category)
    
    # Apply pagination
    paginator = Paginator(activeProduct, 4)  # Show 1 product per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    allCategories = Category.objects.all()

    return render(request, "store/category.html", {
        "page_obj": page_obj,
        "categories": allCategories,
        "selected_category": categoryFromForm,  # Pass the selected category
    })




def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    return render(request, 'store/login.html')

def user_logout(request):
    logout(request)
    return redirect('product_list')

def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    return render(request, 'store/profile.html', {'profile_user': user_profile})

def product_list(request):
    categories = Category.objects.all()
    selected_category = None
    products = Product.objects.all()

    # Get the category filter from the request
    category_filter = request.GET.get('category')
    query = request.GET.get('q')
    
    if category_filter:
        if category_filter.isdigit():  # Check if it's an ID
            selected_category = Category.objects.filter(id=category_filter).first()
        else:  # Assume it's a name
            selected_category = Category.objects.filter(name=category_filter).first()
        
        if selected_category:
            products = products.filter(category=selected_category)
    
    if query:
        products = products.filter(name__icontains=query)
    
    paginator = Paginator(products, 4)  # Show 4 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
    })
    
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    productData = Product.objects.get(pk=pk)
    allReviews = Review.objects.filter(product=productData)
    return render(request, 'store/product_detail.html', {'product': product, 'allReviews': allReviews})

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order = Order.objects.create(user=request.user, product=product, quantity=1)
    return redirect('cart')

@login_required
def cart(request):
    orders = Order.objects.filter(user=request.user, status='pending')
    total = sum(order.product.price * order.quantity for order in orders)
    return render(request, 'store/cart.html', {'orders': orders, 'total': total})

@login_required
def remove_from_cart(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order.delete()
    return redirect('cart')

@login_required
def update_cart(request):
    if request.method == 'POST':
        orders = Order.objects.filter(user=request.user)
        for order in orders:
            quantity = request.POST.get(f'quantity_{order.pk}')
            if quantity:
                try:
                    order.quantity = int(quantity)
                    order.save()
                except ValueError:
                    pass  # Handle invalid input if needed
    return redirect('cart')

@login_required
def checkout(request):
    orders = Order.objects.filter(user=request.user, status='pending')
    total = sum(order.product.price * order.quantity for order in orders)
    
    # Optionally: create a new order record or handle order creation here
    
    # Clear the cart after checkout
    # orders.delete()
    
    return render(request, 'store/checkout.html', {'orders': orders, 'total': total})

def addReview(request, id):
    currentUser = request.user
    productData = Product.objects.get(pk=id)
    message = request.POST['newReview']
    
    newReview = Review(
        author = currentUser,
        product = productData,
        message = message
    )
    newReview.save()
    return HttpResponseRedirect(reverse("product_detail", args=(id, )))

@login_required
def complete_purchase(request):
    if request.method == "POST":
        user = request.user
        payment_method = request.POST.get('payment_method')
        orders = Order.objects.filter(user=user, status='pending')
        total = sum(order.product.price * order.quantity for order in orders)

        if payment_method == 'wallet':
            if user.userprofile.wallet_balance >= total:
                user.userprofile.wallet_balance -= total
                user.userprofile.save()
                orders.update(status='completed', payment_method='wallet')
            else:
                return render(request, 'store/checkout.html', {'error': 'Insufficient wallet balance'})
        elif payment_method == 'cod':
            orders.update(status='completed', payment_method='cod')

        subject = 'Your Purchase Invoice'
        html_message = render_to_string('store/checkout_email.html', {'user': user, 'orders': orders, 'total': total})
        plain_message = strip_tags(html_message)
        from_email = 'no_reply@imizone.com'
        to_email = user.email

        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

        return render(request, 'store/checkout_confirmation.html')

    return redirect('checkout')

@login_required
def old_orders_view(request):
    user = request.user
    completed_orders = Order.objects.filter(user=user, status='completed').order_by('-created_at')

    paginator = Paginator(completed_orders, 2)  # Show 2 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/old_orders.html', {'page_obj': page_obj})