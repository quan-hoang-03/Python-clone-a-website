from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from .models import Customer, Product,Cart,Wishlist
from .forms import CustomerRegistrationForm,CustomerProfileForm,PaymentForm
from django.contrib import messages
from django.db.models import Q
from .vnpay import vnpay
from datetime import datetime
import random
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


def get_banner():
    return {
        'banners': [
            # 'app/images/banner/b1.jpg',
            'app/images/banner/b2.jpg', 
            'app/images/banner/b3.jpg',
            'app/images/banner/b4.jpg'
        ]
    }

def home(request):
    totalitem = 0
    wishitem = 0
    
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    
    # Tạo context từ locals() và merge với banner
    context = locals()
    context.update(get_banner())
    
    return render(request, 'app/home.html', context)

def about(request):
    totalitem = 0
    wishitem = 0
    
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    
    context = locals()
    context.update(get_banner())
    
    return render(request, 'app/about.html', context)

def contact(request):
    totalitem = 0
    wishitem = 0
    
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    
    context = locals()
    context.update(get_banner())
    
    return render(request, 'app/contact.html', context)

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self, request, val):
        # Khởi tạo queryset ban đầu
        products = Product.objects.filter(category=val)
        
        # Lấy danh sách titles cho category này
        title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))

        # Xử lý tìm kiếm theo tên
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Xử lý tìm kiếm theo khoảng giá
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        if min_price:
            try:
                products = products.filter(discount_price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                products = products.filter(discount_price__lte=float(max_price))
            except ValueError:
                pass

        # Xử lý sắp xếp
        sort_by = request.GET.get('sort')
        if sort_by:
            if sort_by == 'price_asc':
                products = products.order_by('discount_price')
            elif sort_by == 'price_desc':
                products = products.order_by('-discount_price')
            elif sort_by == 'name_asc':
                products = products.order_by('title')
            elif sort_by == 'name_desc':
                products = products.order_by('-title')

        # Phân trang
        from django.core.paginator import Paginator
        paginator = Paginator(products, 8)  # Hiển thị 8 sản phẩm mỗi trang
        page_number = request.GET.get('page')
        product = paginator.get_page(page_number)

        context = {
            'product': product,
            'title': title,
            'current_category': val,
            'search_query': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by,
        }
        
        return render(request, "app/category.html", context)
    

@method_decorator(login_required,name='dispatch')
class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())    

@method_decorator(login_required,name='dispatch')
class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,"app/productdetail.html",locals())
    
    # đăng ký người dùng
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,"app/customerregistration.html",locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Đăng ký thành công")
        else:
            messages.warning(request,"Đăng ký thất bại")
        return render(request,"app/customerregistration.html",locals())
    

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,"app/profile.html",locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data["name"]
            locality = form.cleaned_data["locality"]
            city = form.cleaned_data["city"]
            mobile = form.cleaned_data["mobile"]
            state = form.cleaned_data["state"]
            zipcode = form.cleaned_data["zipcode"]
            
            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Lưu thông tin thành công")
        else :
            messages.warning(request,"Lưu thông tin thất bại")
        return render(request,"app/profile.html",locals())
    
@login_required
def address(request):
        # Lấy thông tin tài khoản người dùng đang login
        add = Customer.objects.filter(user = request.user)
        return render(request,"app/address.html",locals())

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,id):
        add = Customer.objects.get(id=id)
        form = CustomerProfileForm(instance=add)
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,id):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(id=id)
            locality = form.cleaned_data["locality"]
            city = form.cleaned_data["city"]
            mobile = form.cleaned_data["mobile"]
            state = form.cleaned_data["state"]
            zipcode = form.cleaned_data["zipcode"]
            add.save()
            messages.success(request,"Lưu thông tin thành công")
        else :
            messages.warning(request,"Lưu thông tin thất bại")
        return redirect("address")
    
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')

    if product_id:
        try:
            # Chỉ giữ lại phần số
            product_id = int(product_id.rstrip('/'))
            product = Product.objects.get(id=product_id)

            Cart(user=user, product=product).save()
            return redirect("/cart")

        except ValueError:
            return HttpResponse("Invalid product ID.", status=400)
        except Product.DoesNotExist:
            return HttpResponse("Product not found.", status=404)

    return HttpResponse("Product ID not provided.", status=400)


@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discount_price
        amount = amount + value
    # 40 là phí vận chuyển
    totalamount = amount + 40
    return render(request,"app/addtocart.html",locals())

@login_required
def show_wishlist(request):
    user = request.user
    totalitem = 0
    wishlist = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishlist = len(Wishlist.objects.filter(user=user))
    product = Wishlist.objects.filter(user=user)
    return render(request,"app/wishlist.html",locals())

@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0 
        for p in cart_items:
            value = p.quantity * p.product.discount_price
            famount = famount + value
        totalamount = famount + 40
        return render(request,"app/checkout.html", locals())

def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest() 
 
def payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            order_type = form.cleaned_data['order_type']
            order_id = form.cleaned_data['order_id']
            amount = form.cleaned_data['amount']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)

            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = amount * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            
            # Check language
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'

            # Check bank_code
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")
            return render(request, "app/payment.html", {"title": "Thanh toán", "form": form})  # Trả về form với thông tin lỗi
    else:
        form = PaymentForm()  # Tạo form mới cho GET request
        return render(request, "app/payment.html", {"title": "Thanh toán", "form": form})  # Trả về trang thanh toán với form

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str       

def  plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)& Q(user = request.user))
        c.quantity +=1
        c.save()
        user  = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discount_price
            amount = amount + value
            # 40 là phí vận chuyển
            totalamount = amount + 40
        data = {
            'quantity' : c.quantity,
            'amount' : amount,
            'totalamount' : totalamount,
        }
        return JsonResponse(data)

def  minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)& Q(user = request.user))
        c.quantity -=1
        c.save()
        user  = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discount_price
            amount = amount + value
            # 40 là phí vận chuyển
            totalamount = amount + 40
        data = {
            'quantity' : c.quantity,
            'amount' : amount,
            'totalamount' : totalamount,
        }
        return JsonResponse(data)

def  remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id)& Q(user = request.user))
        c.delete()
        user  = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discount_price
            amount = amount + value
            # 40 là phí vận chuyển
            totalamount = amount + 40
        data = {
            'amount' : amount,
            'totalamount' : totalamount,
        }
        return JsonResponse(data)
    
def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Đã thêm vào danh mục yêu thích'
        }
        return JsonResponse(data)
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Đã xóa khỏi danh mục yêu thích'
        }
        return JsonResponse(data)
    
@login_required
def search(request):
    query = request.GET['search']
    product = Product.objects.filter(Q(title_icontains=query))
    totalitem = 0
    wishitem = 0
    
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/search.html',locals())