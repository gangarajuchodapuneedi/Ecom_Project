'''
note:
    > in template folder we have registration folder, where the same should be given for it and even files within it has to be given a same name.
    > it will be used for built-in django action for login, password, change, ect.
    > path for account related activity, which has default login, logout and others is 
         path('accounts/', include('django.contrib.auth.urls')), and it takes the name = (the file name in registration folder)
    '''
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string

# used for filter of price
from django.db.models import Max, Min, Sum, Avg

from django.shortcuts import render, redirect, reverse,get_object_or_404

from core.models import *
from core.models import Product, Sub_category  
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail

from django.views import generic

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# cart imports
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from django.core.mail import EmailMultiAlternatives

from django.views.decorators.csrf import csrf_exempt
import razorpay , json
import datetime
from django.views.decorators.cache import never_cache




# Create your views here.
def base(request):
    return render(request, "base.html")

@never_cache 
def home(request):
    slider = Slider.objects.all().order_by("-id")[0:3]
    banner_area = Banner_area.objects.all().order_by("-id")[0:3]
    main_category = Main_category.objects.all()
    product = Product.objects.filter(section__name = "Top Deals of The Day")

    cart = request.session.get("cart", {})
    cart_total_amount = 0

    for product_id, item in cart.items():
        cart_total_amount += float(item.get("price", 0)) * int(item.get("quantity", 1))

    cart_count = len(cart)
    
    context = {"slider" : slider, "banner_area" : banner_area, "main_category" : main_category, 
               "product" : product, "cart_total_amount": cart_total_amount,"cart_count": cart_count,}
    
    return render(request, "main/home.html", context)

def Product_detail(request, slug):
    product = Product.objects.filter(slug = slug)
    review = Review.objects.filter(product__slug = slug).order_by("-created_at")
    review_count = Review.objects.filter(product__slug = slug).count()
    if product.exists():
        product = Product.objects.get(slug = slug)
    else:
        return redirect("404")
        
    page_no = request.GET.get('page')
    page_nk = Paginator(review, 5)
    try:
        review = page_nk.page(page_no)
    except PageNotAnInteger:
        review = page_nk.page(1)
    except EmptyPage:
        review = page_nk.page(page_nk.num_pages)
    context = {"product" : product,"review":review, "review_count":review_count}
    return render(request, "product/product_detail.html", context)

def review(request, id):
    
    if request.method == "POST":
        
        product = Product.objects.get(id = id)
        user = request.user
        review = Review.objects.create(
            user = user,
            product = product,
            comment = request.POST.get("comment"),
            rate = request.POST.get("rate")
        )
    return redirect("product_detail", slug=product.slug)

def error404(request):
    return render(request, "errors/404.html")

# def my_account(request):
#     return render(request, "account/my_account.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if User.objects.filter(username = username).exists():
            messages.error(request, "Username already exists ")
            return redirect("login") # here "login" is present in path('accounts/', include('django.contrib.auth.urls')) and it goes to login.html
        
        if User.objects.filter(email = email).exists():
            messages.error(request, "Email id already exists!!! ")
            return redirect("login")
        
        user = User(username = username, email = email)
        user.set_password(password)
        user.save()
        msg = "Dear {}, \nThank you for registering on VK Market. Enjoy shoping \n\n\nRegards,\nNK Market Team".format(user)
        send_mail("Confirm Your Registration on VK Market", msg,"gangaraju122333@gmail.com",[user.email])
        return redirect("login")
    

def Login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Email and Password are Invalid")
            return redirect("login")
  
            
@login_required(login_url = '/accounts/login/')
def profile(request):
    return render(request, "profile/profile.html")
        
@login_required(login_url = '/accounts/login/')
def profile_update(request):
    if request.method =="POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_id = request.user.id
        user = User.objects.get(id=user_id)

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        
        if password != None and password != "":
            user.set_password(password)
        user.save()
        messages.success(request, "Profile Updated Sucessfully !")
        return redirect('profile')

def about(request):
    return render(request, "main/about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact = Contact_us(name = name,email = email,subject = subject,message = message)
        
        subject = subject
        message = message + ", sent by \n" + email
        email_form = settings.EMAIL_HOST_USER
        try:
            send_mail(subject, message, email_form,["gangaraju122333@gmail.com"])
            contact.save()
            return redirect("home")
        except:
            return redirect("contact")
        
    return render(request, "main/contact.html")

def product(request):
    
    category = Category.objects.all()
    subcategory_id = request.GET.get("subcategory")
    product = Product.objects.all()
    if subcategory_id:
        product = product.filter(subcategory_id=subcategory_id)  # Filter by subcategory
    color = Color.objects.all()
    brand = Brand.objects.all()
    # filter by price
    min_price = Product.objects.all().aggregate(Min('price'))
    max_price = Product.objects.all().aggregate(Max('price'))
    # print(min_price)
    # print(max_price)

    FilterPrice = request.GET.get('FilterPrice')
    ColorID = request.GET.get("colorID")
    
    ATOZ = request.GET.get('ATOZ')
    ZTOA = request.GET.get('ZTOA')
    PRICE_LOWTOHIGH = request.GET.get('PRICE_LOWTOHIGH')
    PRICE_HIGHTOLOW= request.GET.get('PRICE_HIGHTOLOW')
    
    if FilterPrice:
        Int_FilterPrice = int(FilterPrice)
        product = Product.objects.filter(price__lte = Int_FilterPrice)
    
    elif ColorID:
        product = Product.objects.filter(color= ColorID)
        # if ~product.exists():
        #     product = Product.objects.all()
    
    elif ATOZ:
        product = Product.objects.all().order_by('product_name')
    elif ZTOA:
        product = Product.objects.all().order_by('-product_name')
    elif PRICE_LOWTOHIGH:
        product = Product.objects.all().order_by('price')
    elif PRICE_HIGHTOLOW:
        product = Product.objects.all().order_by('-price')
    else:
        product = Product.objects.all()
    
    page_no = request.GET.get('page')
    page_nk = Paginator(product, 8)
    try:
        product = page_nk.page(page_no)
    except PageNotAnInteger:
        product = page_nk.page(1)
    except EmptyPage:
        product = page_nk.page(page_nk.num_pages)
        
    context = {"category": category, "product" : product, 'min_price':min_price, 'max_price':max_price,'FilterPrice':FilterPrice,"color" : color, "brand" : brand,}
    return render(request, "product/product.html", context)


def filter_data(request,subcategory_id=None):
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    subcategories = request.GET.getlist('subcategory[]') 

    if subcategory_id and str(subcategory_id) not in subcategories:
        subcategories.append(str(subcategory_id))
        print(f"After Appending: {subcategories}")

    
    print(f"Received Filters - Categories: {categories}, Brands: {brands}, Subcategories: {subcategories}")

    allProducts = Product.objects.all().order_by('-id')

    if categories:
        allProducts = allProducts.filter(Categories_id__in=categories).distinct() # here in Categories__id__in=categories, Categories is the field the name in Product model and categories is this ->(categories = request.GET.getlist('category[]')) 

    if brands:
        allProducts = allProducts.filter(brand_id__in=brands).distinct() # here in brand__id__in = brands, brand is the field the name in Product model and brands is this ->(brands = request.GET.getlist('brand[]')) 

    if subcategories:
        allProducts = allProducts.filter(subcategory_id__in=subcategories).distinct()  # Filter by subcategory

    print("Subcategories Filter:", subcategories)
    print(f"Filtered Products: {list(allProducts.values('id', 'product_name'))}")
    print("Selected Subcategories:", subcategories)

    print('Context Data:', {'product': allProducts})
    html = render_to_string('ajax/product.html', {'product': allProducts})
    return JsonResponse({'data': html})
    # return render(request, 'ajax/product.html', {'product': allProducts})
    



@never_cache
def subcategory_products(request, subcategory_id):
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    subcategories = request.GET.getlist('subcategory[]')

    # Add the subcategory_id to subcategories list if not already present
    if str(subcategory_id) not in subcategories:
        subcategories.append(str(subcategory_id))

    print(f"Received Filters - Categories: {categories}, Brands: {brands}, Subcategories: {subcategories}")

    products = Product.objects.all().order_by('-id')

    if categories:
        products = products.filter(Categories_id__in=categories).distinct()

    if brands:
        products = products.filter(brand_id__in=brands).distinct()

    if subcategories:
        products = products.filter(subcategory_id__in=subcategories).distinct()

    subcategory = get_object_or_404(Sub_category, id=subcategory_id)
    cart = request.session.get("cart", {})
    cart_total_amount = 0
    for product_id, item in cart.items():
        cart_total_amount += float(item.get("price", 0)) * int(item.get("quantity", 1))
    cart_count = len(cart)

    context = {
        'subcategory': subcategory,
        'products': products,
        'cart_total_amount': cart_total_amount,
        'cart_count': cart_count,
    }
    print('Context Data:', {'products': products})
    return render(request, 'product/subcategory_product.html', context)






@login_required(login_url="/accounts/login/")
def cart_add(request, id):
    cart = Cart(request)
    # product = Product.objects.get(id=id)
    # cart.add(product=product)
    
    product = get_object_or_404(Product, id=id)

     # Calculate discounted price
    if product.Discount > 0:
        discounted_price = product.price - (product.price * (product.Discount / 100))
    else:
        discounted_price = product.price

    # Round the price for consistency
    discounted_price = round(discounted_price, 2)

    # Add item to cart with discounted price
    cart.add_item(product, extra_data={"discounted_price": discounted_price})
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_clear(request, id):
    cart = Cart(request)
    # product = Product.objects.get(id=id)
    cart.remove(id)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add_item(product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement_item(product)
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/accounts/login/")
@never_cache
def cart_detail(request):
    cart = request.session.get("cart",{})
     # Add product_id explicitly
    cart_items = []
    cart_total_amount = 0
    packing_cost=0
    tax=0

    for product_id, item in cart.items():
        item["product_id"] = product_id  # Ensure product_id exists
        cart_items.append(item)
        # **Calculate Total Amount (Fix)**
        cart_total_amount += float(item.get("price", 0)) * int(item.get("quantity", 1)) # Multiplying price by quantity
        packing_cost = sum(i['packing_cost'] for i in cart.values() if i)
        tax = sum(i['tax'] for i in cart.values() if i)
    # print(packing_cost, tax)
    # print(cart)
    print("Cart Items in View:", cart_items)  # Debugging: Check if quantity exists
    # Ensure cart valu  es are dictionaries, not integers
    packing_cost = sum(i.get("packing_cost", 0) for i in cart.values() if isinstance(i, dict))
    tax = sum(i.get("tax", 0) for i in cart.values() if isinstance(i, dict))


    # Check if the cart is empty -> Reset Coupon Discount
    if not cart:  
        request.session.pop('coupon_discount', None)
        request.session.pop('original_coupon_code', None)
        request.session.modified = True

    
    coupon = None
    valid_coupon = None
    invalid_coupon = None
    coupon_discount = request.session.get('coupon_discount', 0)
    if request.method == "GET":
        coupon_code=request.GET.get("coupon_code")
        
        
        if coupon_code:
            try:
                coupon=Coupon_code.objects.get(code=coupon_code)
                
                valid_coupon = " Applicable on Current Order !"
                discount_percentage = coupon.discount  # Get the discount p
                discount_amount = (cart_total_amount * discount_percentage) / 100
                request.session['coupon_discount'] = discount_amount  # Store in session
                request.session['original_coupon_code'] = coupon_code  # Store coupon code in session
                request.session.modified = True 
            except Coupon_code.DoesNotExist:
                invalid_coupon = "Invalid Coupon Code !"
                request.session.pop('coupon_discount', None)  # Remove old discount if invalid
                request.session.pop('original_coupon_code', None)
                request.session.modified = True
    
    context = {"cart_items":cart_items,"cart_total_amount": cart_total_amount,"packing_cost": packing_cost, "tax": tax, "coupon":coupon, "valid_coupon": valid_coupon, "invalid_coupon" : invalid_coupon,}
    return render(request, 'cart/cart.html', context)

def CHECKOUT(request):
    order_id = None
    payment=None
    coupon_discount = float(request.session.get('coupon_discount', 0))  # Get discount from session
    applied_coupon_code = request.session.get('original_coupon_code', "No Coupon Applied")
    
   
    if request.method == "GET":
        total = request.GET.get('total','0')
       


        try:
            total_price = float(total)
        except ValueError:
            total_price = 0  # Default to 0 if conversion fails

        amount = int(total_price * 100)  # Convert to paisa for Razorpay

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            payment = client.order.create(dict(amount=amount, currency ="INR", payment_capture="1"))
            order_id = payment['id']
        except razorpay.errors.BadRequestError as e:
            print("Razorpay Error:", e)
            payment = None  # Handle failed payment case

    
        
    cart = request.session.get('cart',{})
    
    total_price = sum(i.get('price', 0) * i.get('quantity', 1) for i in cart.values())
    packing_cost = sum(i.get('packing_cost', 0) for i in cart.values() if isinstance(i, dict))
    tax = sum(i.get('tax', 0) for i in cart.values() if isinstance(i, dict))
    
    tax_and_packing_cost = (packing_cost + tax)
    if coupon_discount > total_price:
        coupon_discount = total_price
    # Apply discount correctly
    # discount_amount = (total_price * coupon_discount) / 100 
    total_price_after_discount = total_price - coupon_discount

    delivery_charges = 0 if total_price > 500 else 120 
    order_total = total_price_after_discount + packing_cost + tax + delivery_charges  

    # print(f"Cart Subtotal: {total_price}")  # Debugging
    # print(f"Coupon Code Applied: {applied_coupon_code}")  # Debugging
    # print(f"Coupon Discount Applied: {coupon_discount}")  # Debugging
    # print(f"Final Order Total: {order_total}")  # Debugging


    context = {'tax_and_packing_cost': tax_and_packing_cost, 'coupon_discount': coupon_discount,'order_total': order_total,"delivery_charges":delivery_charges, "tax":tax, "packing_cost":packing_cost,'total': total_price_after_discount, "order_id":order_id,"payment":payment}
    
    return render(request, "checkout/checkout.html", context)


def search(request):
    query = request.GET.get('query') 
    product = Product.objects.filter(product_name__icontains = query) 
    context = {"product":product,}   
    return render(request, "product/search.html",context)


def placeorder(request):
    if request.method == "POST":
        uid = request.session.get('_auth_user_id')
        user = User.objects.get(id = uid)
        
        cart = request.session.get('cart',{})
         # Debug: Print request.POST data
        print("POST Data:", request.POST)

          # Check if cart is empty
        if not cart:
            messages.error(request, "Your cart is empty! Add items before placing an order.")
            return redirect("cart_detail") 

        payment_method = request.POST.get('payment_method')
        print("Selected Payment Method:", payment_method)  # Debugging line

         # Ensure a valid payment method is selected
        if payment_method not in ["razorpay", "paypal", "cod"]:
            messages.error(request, "Invalid payment method selected. Please try again.")
            return redirect("checkout")  
        
           
           # Collect user details from POST request
        try:
            order_details = {
                "user": user,
                "firstname": request.POST.get('firstname'),
                "lastname": request.POST.get('lastname'),
                "country": request.POST.get('country'),
                "address": request.POST.get('address'),
                "city": request.POST.get('city'),
                "state": request.POST.get('state'),
                "postalcode": int(request.POST.get('postalcode')),
                "phone": int(request.POST.get('phone')),
                "email": request.POST.get('email'),
                "additional_info": request.POST.get('message'),
                "payment_id": request.POST.get('order_id', None),  # Only for Razorpay
                "amount": int(float(request.POST.get('amount', 0))),
                "paid": payment_method in ["razorpay", "paypal"],  # Mark as paid if online payment
            }

        
            # Create order
            order = Order.objects.create(**order_details)
            print("Order created successfully:", order)
        
        except Exception as e:
            print("Error creating order:", e)
            messages.error(request, "There was an issue placing your order. Please try again.")
            return redirect("checkout")


        # Save cart items to OrderItem model
        try:
            for key, item in cart.items():
                price = int(float(item["price"]))
                quantity = int(item["quantity"])
                total = price * quantity
                Order_item.objects.create(
                    user=user, order=order, product=item["product_name"],
                    image=item["featured_image"], quantity=quantity,
                    price=price, total=total
                )
                print(f"Saved Order Item: {item['product_name']} x {quantity}")
        except Exception as e:
            print("Error saving order item:", e)
            messages.error(request, "There was an issue saving your order items. Please try again.")
            return redirect("checkout")
        

        
        try:
            subject = "🛒 Order Confirmation - VK Mart"

            payment_status = (
                f"<b>✅ Amount Paid:</b> ₹{order.amount}"
                if order.paid else
                f"<b>💰 Amount Due:</b> ₹{order.amount} (Cash on Delivery)"
            )

            delivery_date = "Tue, March 25, 2025"  # You can dynamically calculate this

            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <p>Hi <b>{order.firstname}</b>,</p>

                <p>Your order has been successfully placed.</p>

                <p><b>Order placed on:</b> {order.date.strftime('%b %d, %Y')}</p>
                <p><b>Order ID:</b> {order.id}</p>

                <hr style="border: 1px solid #ddd;">

                <p><b>🛍️ Items Ordered:</b></p>
                <ul>
                    {"".join([f"<li>{item.product} - ₹{item.price} (Qty: {item.quantity})</li>" for item in order.items.all()])}
                </ul>`

                <p><b>📅 Delivery by:</b> {delivery_date}</p>
                <p>{payment_status}</p>

                <p><b>🚚 Delivery Address:</b></p>
                <p>{order.firstname} {order.lastname}<br>
                {order.address}, {order.city}, {order.state} - {order.postalcode}<br>
                <b>Phone:</b> {order.phone}</p>

                <a href="https://vkmart.com/manage-order/{order.id}" 
                style="background-color: #007bff; color: #fff; padding: 10px 15px; text-decoration: none; border-radius: 5px;">
                📦 Manage Your Order
                </a>

                <p>We will notify you once your order is packed/shipped.</p>

                <hr style="border: 1px solid #ddd;">

                <p>Thank you for shopping with <b>VK Mart</b>!</p>

                <p style="font-size: 12px; color: #888;">For any queries, contact our 24x7 support: 
                <a href="mailto:support@vkmart.com">support@vkmart.com</a></p>
            </body>
            </html>
            """

            msg = EmailMultiAlternatives(subject, "", "gangaraju122333@gmail.com", [order.email])
            msg.attach_alternative(html_message, "text/html")
            msg.send()

            print("✅ Order confirmation email sent successfully.")

        except Exception as e:
            print("❌ Error sending email:", e)

         # Clear cart after order placement
        request.session["cart"] = {}
        
        context = {"order_id": order.payment_id, "total_cost": order.amount, "phone": order.phone, "user": user, "email": order.email, "payment": payment_method}

       # Redirect based on payment method
        if payment_method == "razorpay":
            messages.success(request, "Order placed successfully with Razorpay!")
            return render(request, 'cart/success.html', context)
        elif payment_method == "paypal":
            messages.info(request, "Redirecting to PayPal for payment...")
            return render(request, 'cart/paypal_redirect.html', context)
        elif payment_method == "cod":
            messages.success(request, "Order placed successfully with Cash on Delivery (COD)!")
            return render(request, 'cart/success.html')

    messages.error(request, "Invalid payment method selected. Please try again.")
    return redirect("checkout")  # Redirect only if no valid payment is selected
       

 

 
@csrf_exempt    
def success(request):
    try:
        if request.method == "POST":
            a = request.POST
        
            order_id = ""
            for key,val in a.items():
                if key == "razorpay_order_id":
                    order_id = val
                    break
        
            user = Order.objects.filter(payment_id = order_id).first()
            
            print(user)
            user.paid = True
            user.save()
            
            msg = "your order will be recieved shortly. \n Thank you and continue shoping"
            send_mail("payment successful", msg,"gangaraju1333@gmail.com",[user.email])
    except:
        return redirect("not_success")          
        
    return render(request, 'cart/success.html')


def not_success(request):
    return render(request, "cart/not_sucess.html")

@login_required(login_url="/accounts/login/") 
def your_order(request):
    uid = request.session.get('_auth_user_id')
    user = User.objects.get(id = uid)
    # order = Order.objects.filter(user = user,paid = True)
    orders = Order.objects.filter(user=user).order_by('-date') 
    order_items = Order_item.objects.filter(order__in=orders)
    # page_no = request.GET.get('page')
    # page_nk = Paginator(order_item, 10)
    # try:
    #     order_item = page_nk.page(page_no)
    # except PageNotAnInteger:
    #     order_item = page_nk.page(1)
    # except EmptyPage:
    #     order_item = page_nk.page(page_nk.num_pages)
    cart = request.session.get("cart", {})
    cart_total_amount = 0
    for product_id, item in cart.items():
        cart_total_amount += float(item.get("price", 0)) * int(item.get("quantity", 1))
    cart_count = len(cart)
    
    context = {"order_items":order_items,"orders": orders ,"cart_total_amount":cart_total_amount,"cart_count":cart_count,}
    return render(request, 'cart/your_order.html', context)



def faqs(request):
    return render(request, "faqs/faqs.html")


from django.utils.decorators import method_decorator


@method_decorator(login_required, name='get')
class WishlistView(generic.View):
    
    def get(self, *args, **kwargs):
        wish_items = Wishlist.objects.filter(user = self.request.user)
        page_no = self.request.GET.get('page')
        page_nk = Paginator(wish_items, 10)
        try:
            wish_items = page_nk.page(page_no)
        except PageNotAnInteger:
            wish_items = page_nk.page(1)
        except EmptyPage:
            wish_items = page_nk.page(page_nk.num_pages)
        context = {"wish_items":wish_items}
    
        return render(self.request, "wishlist/wishlist.html", context)

@csrf_exempt  
@login_required(login_url="/accounts/login/")    
def add_wishlist(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        prod = Product.objects.get(id = product_id)
        try:
            wish_item = Wishlist.objects.get(user = request.user, product = prod)
            if wish_item:
                return redirect("wishlist")
        except:
            Wishlist.objects.create(user = request.user, product = prod)
            
        finally:
            return HttpResponseRedirect(reverse("wishlist"))

@login_required(login_url="/accounts/login/")        
def delete_wishlist(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        Wishlist.objects.filter(id = item_id).delete()
        
        return HttpResponseRedirect(reverse("wishlist"))
        
@login_required(login_url="/accounts/login/")
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.paid:
        messages.error(request, "You cannot cancel a paid order.")
    else:
        order.canceled = True  # Update the canceled status
        order.save()
        messages.success(request, "Your order has been canceled successfully.")

    return redirect('your_order')  # Redirect back to the orders page

