from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from .models import MenuItem
from rest_framework.views import APIView
from .serializers import MenuItemSerializer, UserSerializer
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