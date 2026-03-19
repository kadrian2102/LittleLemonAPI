from rest_framework import permissions

class IsManagerForUnsafeMethods(permissions.BasePermission):
    """
    Permiso personalizado:
    - Manager: puede usar cualquier metodo (GET, PUT, POST, PATCH, DELETE)
    - Crew y Customer: solo puede utilizar metodos seguros (GET)
    """

    def has_permission(self, request, view):
        # El usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.groups.filter(name='Manager').exists()