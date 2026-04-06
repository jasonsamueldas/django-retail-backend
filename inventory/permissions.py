from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' and request.user.is_authenticated

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'manager' and request.user.is_authenticated
    
class IsAssignedToStore(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.store is not None and request.user.is_authenticated
    
class IsAdminOrManagerWithStore(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role == 'admin':
            return True
        if user.role == 'manager' and user.store:
            return True
        return False
    
class IsSameStore(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.store:
            return True  # admin

        return obj.store == user.store