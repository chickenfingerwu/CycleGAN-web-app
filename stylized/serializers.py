from rest_framework import serializers
from .image_models import ImageInfo

class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(allow_empty_file=False, use_url=False)
    style = serializers.CharField(required=True, allow_blank=False, max_length=255)

    def create(self, validated_data):
        return ImageInfo.objects.create(**validated_data)
