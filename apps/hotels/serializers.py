from rest_framework import serializers
from apps.users.models import User
from .models import Hotel

class HotelOwnerRegistrationSerializer(serializers.Serializer):
    # password = serializers.CharField(write_only=True)
    hotel = serializers.DictField()
    owner = serializers.DictField()

    def create(self, validated_data):
        hotel_data = validated_data["hotel"]
        owner_data = validated_data["owner"]

        owner = User.objects.create_user(
            username=owner_data["email"],
            email=owner_data["email"],
            password=validated_data["password"],
            role="OWNER",
            is_staff=True
        )

        hotel = Hotel.objects.create(owner=owner, **hotel_data)

        # user = User.objects.create_user(
        #     username=owner_data["username"],
        #     email=owner_data["email"],
        #     password=validated_data["password"],
        #     role="OWNER",
        #     hotel=hotel,
        #     is_staff=True
        # )
        owner.hotel = hotel # type: ignore
        owner.save(update_fields=["hotel"])

        return hotel