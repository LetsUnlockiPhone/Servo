# -*- coding: utf-8 -*-

from rest_framework import serializers

from servo.models import (User, Device, Order, Note,
                          ServiceOrderItem, Customer,)


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    devices = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-device_detail'
    )
    orders = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-order_detail'
    )

    class Meta:
        model = Customer
        fields = ('name', 'fullname', 'phone', 'email',
                  'street_address', 'zip_code', 'city',
                  'country', 'devices', 'orders',)

class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = (
            'sn',
            'imei',
            'unlocked',
            'purchased_on',
            'purchase_country',
            'description',
            'warranty_status',
            'contract_end_date',
            'image_url',
            'fmip_active',
            'parts_and_labor_covered',
            'configuration',
            'applied_activation_policy',
            'next_tether_policy',
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email',)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'subject', 'body', 'code', 'sender',
                  'recipient', 'created_at', 'labels',)


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status_name',)


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='api-user_detail'
    )
    notes = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-note_detail'
    )
    products = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api-order_items'
    )
    class Meta:
        model = Order
        fields = ('created_at', 'status', 'notes', 'products', 'user',)


class ServiceOrderItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceOrderItem
