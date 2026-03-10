from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .models import MenuItem
from .serializers import MenuItemSerializer

@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        serialized_items = MenuItemSerializer(items, many=True)
        return Response(serialized_items.data)

