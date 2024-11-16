from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from .models import Customer, Product,Cart,Wishlist,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm,PaymentForm
from django.contrib import messages
from django.db.models import Q
from .vnpay import vnpay
from datetime import datetime
import random
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse


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
        # Định nghĩa mapping cho danh mục cha và con
        category_mapping = {
            'PA': {
                'name': 'Phòng ăn',
                'subcategories': {
                    'PA-BA': 'Bàn ăn',
                    'PA-GHE': 'Ghế ăn',
                    'PA-TU': 'Tủ trang trí'
                }
            }
        }

        # Xử lý đặc biệt cho danh mục phòng ăn và các danh mục con
        if val == 'PA':
            # Lấy subcategory từ request
            subcategory = request.GET.get('subcategory', '')
            if subcategory and subcategory in category_mapping['PA']['subcategories']:
                # Nếu có chọn subcategory thì chỉ lấy sản phẩm của subcategory đó
                products = Product.objects.filter(category=subcategory)
            else:
                # Nếu không có subcategory thì lấy tất cả
                products = Product.objects.filter(
                    Q(category='PA') |
                    Q(category='PA-BA') |
                    Q(category='PA-GHE') |
                    Q(category='PA-TU')
                )
        else:
            # Với các danh mục khác, giữ nguyên logic cũ
            products = Product.objects.filter(category=val)

        # Lấy danh sách titles cho category này
        title = products.values('title').annotate(total=Count('title'))

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

        # Lấy thông tin subcategories nếu đang ở category cha
        subcategories = []
        if val in category_mapping:
            subcategories = [(code, name) for code, name in category_mapping[val]['subcategories'].items()]

        # Phân trang
        from django.core.paginator import Paginator
        paginator = Paginator(products, 8)
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
            'subcategories': subcategories,  # Thêm danh sách subcategories vào context
            'selected_subcategory': request.GET.get('subcategory', '')  # Subcategory đang được chọn
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
     if request.method == 'POST':
            product_id = request.POST.get('prod_id')
            redirect_to_cart = request.POST.get('redirect_to_cart')  # Kiểm tra tham số này

            if product_id:
                try:
                    # Chỉ giữ lại phần số trong product_id
                    product_id = int(product_id.rstrip('/'))
                    product = Product.objects.get(id=product_id)

                    # Thêm sản phẩm vào giỏ hàng
                    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
                    if not created:
                        cart_item.quantity += 1
                        cart_item.save()

                    # Nếu "Mua ngay", chuyển hướng đến giỏ hàng
                    if redirect_to_cart == 'true':
                        return redirect('/cart')

                    # Nếu chỉ "Thêm vào giỏ hàng", không chuyển hướng, trả về trang hiện tại
                    return HttpResponse(status=204)  # Không làm gì thêm, chỉ trả về "No Content"

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
        return redirect(f'{reverse("payment")}?totalamount={totalamount}')

def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest() 
 
def payment(request):
    totalamount = request.GET.get('totalamount', 0)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Đảm bảo tính nhất quán của dữ liệu
                    # Lấy dữ liệu từ form
                    order_type = form.cleaned_data.get('order_type', 'billpayment')
                    order_id = form.cleaned_data['order_id']
                    amount = Decimal(form.cleaned_data['amount'].replace(',', ''))  # Chuyển đổi chuỗi sang số
                    order_desc = form.cleaned_data['order_desc']
                    bank_code = form.cleaned_data['bank_code']
                    language = form.cleaned_data['language']
                    ipaddr = get_client_ip(request)

                    # Tạo payment record
                    payment = Payment.objects.create(
                        user=request.user,
                        amount=amount,
                        order_id=order_id,
                        vnpay_payment_status='PENDING',
                        bank_code=bank_code,
                        order_desc=order_desc
                    )

                    # Lấy cart items và tạo OrderPlaced records
                    cart_items = Cart.objects.filter(user=request.user)
                    customer = Customer.objects.get(user=request.user)

                    for cart_item in cart_items:
                        OrderPlaced.objects.create(
                            user=request.user,
                            customer=customer,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            status='Pending',
                            payment=payment
                        )

                    # Cấu hình VNPay
                    vnp = vnpay()
                    vnp.requestData['vnp_Version'] = '2.1.0'
                    vnp.requestData['vnp_Command'] = 'pay'
                    vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
                    vnp.requestData['vnp_Amount'] = int(amount * 100)
                    vnp.requestData['vnp_CurrCode'] = 'VND'
                    vnp.requestData['vnp_TxnRef'] = order_id
                    vnp.requestData['vnp_OrderInfo'] = order_desc
                    vnp.requestData['vnp_OrderType'] = order_type
                    vnp.requestData['vnp_Locale'] = language
                    if bank_code:
                        vnp.requestData['vnp_BankCode'] = bank_code
                    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
                    vnp.requestData['vnp_IpAddr'] = ipaddr
                    vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL

                    # Xóa giỏ hàng
                    cart_items.delete()

                    # Tạo URL thanh toán VNPay
                    vnpay_payment_url = vnp.get_payment_url(
                        settings.VNPAY_PAYMENT_URL,
                        settings.VNPAY_HASH_SECRET_KEY
                    )

                    # Chuyển hướng đến trang thanh toán VNPay
                    return redirect('payment_success', order_id=order_id)

            except Customer.DoesNotExist:
                messages.error(request, "Không tìm thấy thông tin khách hàng!")
                return redirect('profile')
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {str(e)}")
                return render(request, "app/payment.html", {
                    "totalamount": totalamount,
                    "form": form
                })
    else:
        form = PaymentForm(initial={'amount': totalamount})
        return render(request, "app/payment.html", {
            "totalamount": totalamount,
            "form": form
        })
    
    # Đảm bảo trả về response ngay cả khi không vào điều kiện trên
    return render(request, "app/payment.html", {
        "totalamount": totalamount,
        "form": form
    })


def payment_return(request):
    if request.method == 'GET':
        # Các tham số trả về từ VNPay
        vnp_ResponseCode = request.GET.get('vnp_ResponseCode')
        vnp_TxnRef = request.GET.get('vnp_TxnRef')
        
        try:
            # Tìm payment record
            payment = Payment.objects.get(order_id=vnp_TxnRef)
            
            # Cập nhật trạng thái payment
            if vnp_ResponseCode == '00':
                payment.payment_status = 'COMPLETED'
                
                # Cập nhật trạng thái các đơn hàng liên quan
                OrderPlaced.objects.filter(payment=payment).update(status='Accepted')
                
                messages.success(request, "Thanh toán thành công!")
            else:
                payment.payment_status = 'FAILED'
                
                # Cập nhật trạng thái các đơn hàng liên quan
                OrderPlaced.objects.filter(payment=payment).update(status='Cancelled')
                
                messages.error(request, "Thanh toán thất bại!")
            
            payment.save()
            
            return redirect('orders')
            
        except Payment.DoesNotExist:
            messages.error(request, "Không tìm thấy thông tin thanh toán!")
            return redirect('home')
        
def payment_success(request, order_id):
    return render(request, 'app/payment_success.html', {
        'order_id': order_id
    })
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

def remove_cart(request):
     if request.method == 'GET':
         prod_id = request.GET['prod_id']

         try:
             # Lấy đối tượng Cart với sản phẩm và người dùng tương ứng
             cart_item = Cart.objects.get(product_id=prod_id, user=request.user)
             cart_item.delete()  # Xóa sản phẩm khỏi giỏ hàng

             # Tính toán lại tổng tiền trong giỏ hàng
             user = request.user
             cart = Cart.objects.filter(user=user)
             amount = 0
             for p in cart:
                 value = p.quantity * p.product.discount_price
                 amount += value

             # 40 là phí vận chuyển (nếu có)
             totalamount = amount + 40

             # Trả về dữ liệu dưới dạng JSON
             return JsonResponse({
                 'success': True,
                 'amount': amount,
                 'totalamount': totalamount
             })
         except Cart.DoesNotExist:
             return JsonResponse({
                 'success': False,
                 'message': 'Không tìm thấy sản phẩm trong giỏ hàng'
             })
    
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
    # Sử dụng get() để tránh lỗi MultiValueDictKeyError
    # Tìm kiếm tham số có tên 'search' trong request.GET
    # Nếu không tìm thấy, trả về chuỗi rỗng '' (giá trị mặc định)
    query = request.GET.get('search', '')
    # Kiểm tra xem có từ khóa tìm kiếm không
    if query:
        # Truy cập vào model Product  Lọc các sản phẩm theo điều kiện
        # title__icontains: Tìm kiếm không phân biệt hoa thường trong trường title
        products = Product.objects.filter(Q(title__icontains=query))
    else:
        # Trả về QuerySet rỗng khi không có từ khóa tìm kiếm tránh việc trả về None hoặc lỗi
        products = Product.objects.none()  # Trả về QuerySet rỗng nếu không có query

    context = {
        'query': query,# Từ khóa tìm kiếm
        'products': products# Kết quả tìm kiếm
    }

    return render(request, 'app/search.html', context)