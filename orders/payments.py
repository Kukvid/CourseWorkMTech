from abc import ABC, abstractmethod
from django.core.exceptions import ValidationError


# Фабричный метод
class IPaymentProcessor(ABC):

    @abstractmethod
    def process_payment(self, order, cart_items):
        pass


class CashPaymentProcessor(IPaymentProcessor):
    def process_payment(self, order, cart_items):
        order.is_paid = False


class CardPaymentProcessor(IPaymentProcessor):
    def process_payment(self, order, cart_items):
        order.is_paid = True


class BonusPaymentProcessor(IPaymentProcessor):
    def process_payment(self, order, cart_items):
        user = order.user
        total_price = cart_items.total_price()

        if user.bonuses >= total_price:
            user.bonuses -= total_price
            user.save()
            order.is_paid = True
        else:
            raise ValidationError("Недостаточно бонусов для покупки")


class AbstractPaymentProcessFactory(ABC):
    @abstractmethod
    def get_payment_processor(self, payment_type):
        pass


class PaymentProcessorFactory(AbstractPaymentProcessFactory):
    def get_payment_processor(self, payment_type):
        if payment_type == "0":
            return CardPaymentProcessor()
        elif payment_type == "1":
            return CashPaymentProcessor()
        elif payment_type == "2":
            return BonusPaymentProcessor()
        else:
            raise ValidationError("Неизвестная ошибка, свяжитесь с нами по номеру:\n"
                                  "+79212688888")
