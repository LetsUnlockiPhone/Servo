# -*- coding: utf-8 -*-
# Copyright (c) 2013, First Party Software
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.

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
