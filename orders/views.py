from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse 
from cart.models import CartItem, Cart
from cart.views import _cart_id
from orders.forms import OrderForm
import datetime
from store.models import Products
from orders.models import Order, Payment, OrderProduct
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import razorpay
# from ishop.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from django.conf import settings
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.


@login_required(login_url='signin')
def checkout_address(request, total=0, quantity=0):

    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (18 * total/100)  # give the tax percentage here
    grand_total = total + tax

    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'checkout_address.html', context)




@login_required(login_url='signin')
def checkout_review(request, total=0):

    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
    tax = (18 * total/100)  # give the tax percentage here instead of 2
    grand_total = total + tax
    context = {
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # to generate order number
            yr = int(datetime.date.today().strftime('%y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'checkout_review.html', context)
    else:
        return render(request, 'checkout_review.html', context)




def cod(request):
    return




def payments(request):
    # if request.method == 'POST':
    body = json.loads(request.body)
    # print(body)

    # store transactions details inside Payment model   
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    #move the cart items to order product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True 
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        #reduce the quantity from stock
        product = Products.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    #clear the cart
    CartItem.objects.filter(user=request.user).delete()

    #send order received mail to customer
    # mail_subject = 'Thank you for your order.'
    # message = render_to_string('order_received.html', {
    #     'user': request.user,
    #     'order': order,
    # })
    # to_email = request.user.email
    # send_email = EmailMessage(mail_subject, message, to=[to_email])
    # send_email.send()

    #send order number and transaction id back to sendData method via jsonresponse
    data = {
        'order_number': order.order_number,
        'transID':payment.payment_id,
    }
    return JsonResponse(data)

    # return render(request, 'success.html')




def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number = order_number, is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price*i.quantity

        payment = Payment.objects.get(payment_id=transID)
         
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number':order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'order_complete.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store')