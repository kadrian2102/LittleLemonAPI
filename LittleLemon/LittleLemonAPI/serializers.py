from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import MenuItem, Category
import bleach

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    featured = serializers.BooleanField()

    def validate_title(self, value):
        return bleach.clean(value)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'category', 'category_id', 'featured']
        
        extra_kwargs = {
            'price': {'min_value': 0},
            'title': {
                'validators': [
                    UniqueValidator(
                        queryset=MenuItem.objects.all()
                    )
                ]
            }
        }