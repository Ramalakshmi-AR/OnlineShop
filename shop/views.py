# shop/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt

# Home page and search/filter
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')
    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category__id=category)
    return render(request, 'shop/home.html', {'products': products, 'categories': categories})

# Product detail
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product_detail.html', {'product': product})

# Cart page (simple session cart)
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

def cart(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    for id, qty in cart.items():
        p = Product.objects.get(id=id)
        products.append({'product': p, 'qty': qty})
        total += p.price * qty
    return render(request, 'shop/cart.html', {'products': products, 'total': total})

# Razorpay payment
def checkout(request):
    cart = request.session.get('cart', {})
    total = sum(Product.objects.get(id=id).price * qty for id, qty in cart.items())
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({'amount': int(total*100), 'currency': 'INR', 'payment_capture': 1})
    return render(request, 'shop/checkout.html', {'payment': payment, 'total': total, 'razorpay_key': settings.RAZORPAY_KEY_ID})




@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Store or print for debugging
        print("Payment ID:", razorpay_payment_id)
        print("Order ID:", razorpay_order_id)
        print("Signature:", razorpay_signature)

        # After success → clear cart
        if 'cart' in request.session:
            del request.session['cart']

        return render(request, "shop/payment_success.html", {
            "payment_id": razorpay_payment_id
        })

    return render(request, "shop/payment_failed.html")

def products_page(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "shop/products.html", {
        "products": products,
        "categories": categories
    })



def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    return render(request, 'shop/contact.html')

def login(request):
    return render(request, 'shop/login.html')
