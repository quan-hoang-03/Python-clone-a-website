from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from .models import Customer, Product,Cart
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q

def get_banner():
    return {
        'banners': [
            'app/images/banner/b1.jpg',
            'app/images/banner/b2.jpg', 
            'app/images/banner/b3.jpg',
            'app/images/banner/b4.jpg'
        ]
    }

def home(request):
    context = get_banner()
    return render(request, 'app/home.html', context)

def about(request):
    context = get_banner()
    return render(request, 'app/about.html', context)

def contact(request):
    context = get_banner()
    return render(request, 'app/contact.html', context)

class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
        return render(request,"app/category.html",locals())

class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())    

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
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
    
def address(request):
        # Lấy thông tin tài khoản người dùng đang login
        add = Customer.objects.filter(user = request.user)
        return render(request,"app/address.html",locals())

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
    
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect("/cart")

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

class checkout(View):
    def get(self,request):
        return render(request,"app/checkout.html", locals())

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