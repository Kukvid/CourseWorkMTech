from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from cart.models import Cart

from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem
from users.models import User
from .payments import PaymentProcessorFactory


@login_required
def create_order(request):
    initial = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    if request.user.is_authenticated:
        initial["phone_number"] = request.user.phone_number

    if request.method == 'POST':
        form = CreateOrderForm(data=request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = request.user
                    cart_items = Cart.objects.filter(user=user)

                    if cart_items.exists():
                        # Создать заказ
                        order = Order.objects.create(
                            user=user,
                            phone_number=form.cleaned_data['phone_number'],
                            requires_delivery=form.cleaned_data['requires_delivery'],
                            delivery_address=form.cleaned_data['delivery_address'],
                            payment_type=form.cleaned_data['payment_type'],
                        )

                        # Создать заказанные товары
                        for cart_item in cart_items:
                            product = cart_item.product
                            name = cart_item.product.name
                            price = cart_item.product.sell_price()
                            quantity = cart_item.quantity

                            if product.quantity < quantity:
                                raise ValidationError(f'Недостаточное количество товара {name} на складе\
                                                       \nВ наличии - {product.quantity} шт.')

                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                name=name,
                                price=price,
                                quantity=quantity,
                            )
                            product.quantity -= quantity
                            product.save()

                        # Обработка платежа
                        payment_processor = PaymentProcessorFactory().get_payment_processor(order.payment_type)
                        payment_processor.process_payment(order, cart_items)
                        order.save()

                        # Очистить корзину пользователя после создания заказа
                        cart_items.delete()

                        messages.success(request, 'Заказ оформлен!')
                        return redirect('user:profile')
                    else:
                        initial["is_cart"] = False
            except ValidationError as e:
                messages.warning(request, str(e.message))
                return HttpResponseRedirect(reverse("orders:create_order"))

    else:

        form = CreateOrderForm(initial=initial)

    context = {
        'title': 'MTech - Оформление заказа',
        'form': form,
        "order": True,
    }
    if request.user.is_authenticated:
        current_user_bonuses = User.objects.get(username=request.user.username).bonuses
        context["bonuses"] = current_user_bonuses

    return render(request, 'orders/create_order.html', context=context)
