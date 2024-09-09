from rest_framework.serializers import ModelSerializer
from .models import OrderState, UserOrder


class OrderStateSerializer(ModelSerializer):
    class Meta:
        model = OrderState
        fields = ["product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderStateSerializer(many=True, allow_empty=False, write_only=True)

    def create(self, validated_data):
        order_items_fields = validated_data.pop('products')
        order = UserOrder.objects.create(**validated_data)
        order_items = [OrderState(order=order, price=fields['product'].price, **fields)
                       for fields in order_items_fields]
        OrderState.objects.bulk_create(order_items)
        return order

    class Meta:
        model = UserOrder
        fields = ["id", "firstname", "lastname", "address", "phonenumber", "products"]
