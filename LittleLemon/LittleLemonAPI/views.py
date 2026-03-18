from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import MenuItem
from .serializers import MenuItemSerializer

# @api_view(['GET', 'POST'])
# def menu_items(request):
#     if request.method == 'GET':
#         items = MenuItem.objects.select_related('category').all()
#         serialized_items = MenuItemSerializer(items, many=True)
#         return Response(serialized_items.data)
    
#     # elif request.method == 'POST':
#     #     serialized_items = MenuItemSerializer(data=request.data)
#     #     serialized_items.is_valid(raise_exception=True)
#     #     serialized_items.save()
#     #     return Response(serialized_items.data, status=status.HTTP_201_CREATED)

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer