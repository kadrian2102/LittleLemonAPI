from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from .models import MenuItem
from rest_framework.views import APIView
from .serializers import MenuItemSerializer
from .permissions import IsManagerForUnsafeMethods
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes

# @api_view(['GET', 'POST'])
# def menu_items(request):
#     if request.method == 'GET':
#         items = MenuItem.objects.select_related('category').all()
#         serialized_items = MenuItemSerializer(items, many=True)
#         return Response(serialized_items.data)
    
#     elif request.method == 'POST':
#         serialized_items = MenuItemSerializer(data=request.data)
#         serialized_items.is_valid(raise_exception=True)
#         serialized_items.save()
#         return Response(serialized_items.data, status=status.HTTP_201_CREATED)

# GET all menu-items endpoint
class MenuItemsView(APIView):
    permission_classes = [IsManagerForUnsafeMethods]
    
    def get(self, request):
        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET single menu-items endpoint
class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsManagerForUnsafeMethods]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    