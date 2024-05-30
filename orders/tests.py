from products.models import Products, Categories
from django.test import TestCase
from orders.models import Order, OrderItem
from users.models import User
from orders.payments import PaymentProcessorFactory, ValidationError
from cart.models import Cart


# Тесты для моделей заказа
class OrderModelTest(TestCase):
    # Метод setUp выполняется перед каждым тестом
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='12345')

    # Тест для проверки создания заказа
    def test_order_creation(self):
        # Создаем заказ с тестовыми данными
        order = Order.objects.create(
            user=self.user,
            phone_number='1234567890',
            requires_delivery=True,
            delivery_address='ул. Примерная, дом 1',
            payment_type=0,
        )
        # Проверяем, что данные заказа сохранены корректно
        self.assertEqual(order.phone_number, '1234567890')
        self.assertTrue(order.requires_delivery)
        self.assertEqual(order.delivery_address, 'ул. Примерная, дом 1')
        self.assertEqual(order.payment_type, 0)
        self.assertFalse(order.is_paid)
        self.assertEqual(order.status, 'В обработке')

    # Тест для проверки строкового представления заказа
    def test_order_str(self):
        # Создаем заказ с тестовыми данными
        order = Order.objects.create(
            user=self.user,
            phone_number='1234567890',
            requires_delivery=True,
            delivery_address='ул. Примерная, дом 1',
            payment_type=0,
        )
        # Проверяем, что строковое представление заказа корректно
        self.assertEqual(str(order), f"Заказ № {order.pk} | Покупатель {self.user.first_name} {self.user.last_name}")


# Тесты для процесса оплаты
class ProcessPaymentTest(TestCase):
    # Метод setUp выполняется перед каждым тестом
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Создаем тестовый продукт и категорию
        self.product = Products.objects.create(
            name="test",
            category=Categories.objects.create(name="test"),
            price=10
        )
        # Создаем тестовый заказ
        self.order = Order.objects.create(
            user=self.user,
            phone_number='1234567890',
            requires_delivery=True,
            delivery_address='ул. Примерная, дом 1',
            payment_type='2',
        )
        # Добавляем тестовый продукт в заказ
        self.order_item = OrderItem.objects.create(
            order=self.order,
            name=self.product.name,
            price=self.product.price,
            product=self.product,
            quantity=1
        )

    # Тест для проверки оплаты картой
    def test_card_payment(self):
        # Получаем процессор оплаты для карт
        processor = PaymentProcessorFactory().get_payment_processor("0")
        # Обрабатываем оплату
        processor.process_payment(self.order, Cart.objects.filter(user=self.user))
        self.order.save()
        # Проверяем, что заказ помечен как оплаченный
        self.assertTrue(self.order.is_paid)

    # Тест для проверки оплаты бонусами
    def test_bonus_payment(self):
        # Устанавливаем количество бонусов у пользователя
        self.user.bonuses = 1000
        self.user.save()
        # Получаем процессор оплаты для бонусов
        processor = PaymentProcessorFactory().get_payment_processor("2")
        # Обрабатываем оплату
        processor.process_payment(self.order, Cart.objects.filter(user=self.user))
        self.user.refresh_from_db()
        # Проверяем, что заказ помечен как оплаченный и бонусы списаны корректно
        self.assertTrue(self.order.is_paid)
        self.assertEqual(self.user.bonuses, 1000 - Cart.objects.filter(user=self.user).total_price())
