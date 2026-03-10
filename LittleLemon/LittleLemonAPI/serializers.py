from rest_framework import serializers
from .models import MenuItem, Category
import bleach

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    def validate_title(self, value):
        return bleach.clean(value)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'category_id']
        # extra_kwargs = {
        #     'price': {'min_value', 1},
        # }