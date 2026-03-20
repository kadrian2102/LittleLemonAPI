from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics, viewsets
from .models import MenuItem, Cart
from rest_framework.views import APIView
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer
from .permissions import IsManagerForUnsafeMethods
# from rest_framework.permissions import IsManagerForUnsafeMethods
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

class ManagerUsersView(APIView):
    """
    Endpoint para gestionar usuarios del grupo Manager
    
    GET /api/groups/manager/users/ - Lista todos los managers
    POST /api/groups/manager/users/ - Agrega un usuario al grupo Manager
    """
    permission_classes = [IsManagerForUnsafeMethods]
    
    def get(self, request):
        # Verificar permisos - solo managers pueden ver esta información
        if not request.user.groups.filter(name='Manager').exists():
            return Response(
                {"detail": "No tienes permiso para ver esta información"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el grupo Manager
        try:
            manager_group = Group.objects.get(name='Manager')
        except Group.DoesNotExist:
            return Response(
                {"detail": "El grupo Manager no existe"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todos los usuarios del grupo
        users = manager_group.user_set.all()
        
        # Serializar los usuarios
        serializer = UserSerializer(users, many=True)
        
        return Response({
            "group": "Manager",
            "total_users": users.count(),
            "users": serializer.data
        })
    
    def post(self, request):
        """
        Agrega un usuario al grupo Manager
        Payload esperado: {"user_id": 123} o {"username": "nombre_usuario"}
        """
        # Verificar permisos - solo managers pueden agregar nuevos managers
        if not request.user.groups.filter(name='Manager').exists():
            return Response(
                {"detail": "No tienes permiso para agregar usuarios al grupo Manager"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener el grupo Manager
        try:
            manager_group = Group.objects.get(name='Manager')
        except Group.DoesNotExist:
            return Response(
                {"detail": "El grupo Manager no existe"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Buscar el usuario a agregar (por ID o username)
        user = None
        if 'user_id' in request.data:
            try:
                user = User.objects.get(id=request.data['user_id'])
            except User.DoesNotExist:
                return Response(
                    {"detail": f"No existe usuario con ID {request.data['user_id']}"},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif 'username' in request.data:
            try:
                user = User.objects.get(username=request.data['username'])
            except User.DoesNotExist:
                return Response(
                    {"detail": f"No existe usuario con username '{request.data['username']}'"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {"detail": "Debes proporcionar 'user_id' o 'username'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya es manager
        if user.groups.filter(name='Manager').exists():
            return Response(
                {"detail": f"El usuario {user.username} ya pertenece al grupo Manager"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Agregar usuario al grupo
        user.groups.add(manager_group)
        
        # Respuesta exitosa
        serializer = UserSerializer(user)
        return Response({
            "detail": f"Usuario {user.username} agregado al grupo Manager exitosamente",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)


class ManagerUserDetailView(APIView):
    """
    Endpoint para operaciones con un usuario específico del grupo Manager
    DELETE /api/groups/manager/users/<int:pk>/ - Elimina un usuario del grupo
    """
    permission_classes = [IsManagerForUnsafeMethods]
    
    def delete(self, request, pk):
        """
        Elimina un usuario del grupo Manager por su ID
        """
        # Verificar permisos - solo managers pueden eliminar managers
        if not request.user.groups.filter(name='Manager').exists():
            return Response(
                {"detail": "No tienes permiso para eliminar usuarios del grupo Manager"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Buscar el usuario
        user = get_object_or_404(User, pk=pk)
        
        # Verificar si el usuario es manager
        if not user.groups.filter(name='Manager').exists():
            return Response(
                {"detail": f"El usuario {user.username} no pertenece al grupo Manager"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Evitar que un manager se elimine a sí mismo (opcional)
        if user.pk == request.user.id:
            return Response(
                {"detail": "No puedes eliminarte a ti mismo del grupo Manager"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener el grupo Manager
        try:
            manager_group = Group.objects.get(name='Manager')
        except Group.DoesNotExist:
            return Response(
                {"detail": "El grupo Manager no existe"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Eliminar usuario del grupo
        user.groups.remove(manager_group)
        
        return Response({
            "detail": f"Usuario {user.username} eliminado del grupo Manager exitosamente",
            "user": {
                "id": user.pk,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)
    
class CartView(APIView):
    """
    Endpoint para gestionar el carrito de compras del usuario autenticado
    
    GET /api/cart/menu-items/ - Ver items del carrito
    POST /api/cart/menu-items/ - Agregar item al carrito
    DELETE /api/cart/menu-items/ - Vaciar el carrito
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET: Retorna todos los items en el carrito del usuario autenticado
        """
        cart_items = Cart.objects.filter(user=request.user).select_related('menuitem')
        serializer = CartSerializer(cart_items, many=True, context={'request': request})
        
        # Calcular el total del carrito
        total = sum(item.price for item in cart_items)
        
        return Response({
            'user': request.user.username,
            'cart_items': serializer.data,
            'total_items': cart_items.count(),
            'total_price': total
        })
    
    def post(self, request):
        """
        POST: Agrega un item al carrito
        Payload esperado: {"menuitem_id": 1, "quantity": 2}
        """
        # Validar que se proporcionen los campos necesarios
        if 'menuitem_id' not in request.data:
            return Response(
                {"detail": "El campo 'menuitem_id' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el menuitem existe
        menuitem_id = request.data['menuitem_id']
        menuitem = get_object_or_404(MenuItem, pk=menuitem_id)
        
        # Obtener cantidad (por defecto 1)
        quantity = request.data.get('quantity', 1)
        if quantity < 1:
            return Response(
                {"detail": "La cantidad debe ser al menos 1"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar si el item ya existe en el carrito
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menuitem,
            defaults={
                'quantity': quantity,
                'unit_price': menuitem.price,
                'price': quantity * menuitem.price
            }
        )
        
        # Si ya existía, actualizar la cantidad
        if not created:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
            message = f"Cantidad actualizada. Ahora tienes {cart_item.quantity} unidades de {menuitem.title}"
        else:
            message = f"{menuitem.title} agregado al carrito"
        
        serializer = CartSerializer(cart_item, context={'request': request})
        
        return Response({
            'detail': message,
            'cart_item': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        """
        DELETE: Elimina todos los items del carrito del usuario autenticado
        """
        # Verificar si el carrito está vacío
        cart_items = Cart.objects.filter(user=request.user)
        items_count = cart_items.count()
        
        if items_count == 0:
            return Response({
                'detail': 'El carrito ya está vacío'
            }, status=status.HTTP_200_OK)
        
        # Eliminar todos los items
        cart_items.delete()
        
        return Response({
            'detail': f'Se eliminaron {items_count} items del carrito'
        }, status=status.HTTP_200_OK)
