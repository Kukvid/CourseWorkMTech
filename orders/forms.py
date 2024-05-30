import re

from django import forms


class CreateOrderForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField()
    requires_delivery = forms.ChoiceField(
        choices=[
            ("0", False),
            ("1", True),
        ],
    )
    delivery_address = forms.CharField(required=False)
    payment_type = forms.ChoiceField(
        choices=[
            ("0", 0),
            ("1", 1),
            ("2", 2)
        ],
    )

    # Проверка номера телефона
    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if data:
            if not data.isdigit():
                raise forms.ValidationError("Номер телефона должен содержать только цифры")

            pattern = re.compile(r'^\d{10}$')
            if not pattern.match(data):
                raise forms.ValidationError("Неверный формат номера")

        return data

    # Проверка адреса доставки
    def clean_delivery_address(self):
        delivery_address = self.cleaned_data["delivery_address"]

        is_requires_delivery = self.cleaned_data["requires_delivery"]

        if not delivery_address and is_requires_delivery == "1":
            raise forms.ValidationError("Для доставки требуется ввод адреса")

        return delivery_address
