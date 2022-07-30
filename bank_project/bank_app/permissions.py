# from rest_framework import permissions

# class isUserOrReadOnly(permissions.BasePermission):

#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.user == request.user
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user