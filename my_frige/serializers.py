from rest_framework import serializers
from my_frige.models import MyFrigeInside
from datetime import date, timedelta


class MyFrigeInsideSerializer(serializers.ModelSerializer):
    # state 필드 추가
    # 유효기간을 저장시 변경/업데이트도 변경

    class Meta:
        model = MyFrigeInside
        fields = "__all__"

    def create(self, validated_data):
        my_frige = MyFrigeInside.objects.create(**validated_data)
        if not my_frige.expiration_date:
            my_frige.expiration_date = my_frige.created_at.date() + timedelta(weeks=1) # +7일
        my_frige.save()
        return my_frige
    
