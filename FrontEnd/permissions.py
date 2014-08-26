from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user

class IsUser(permissions.BasePermission):
    """
    Only allows user to view data if they are the same user
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsCompanies(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.ExtUser.Company == obj.Company

class IsAuthenticated(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated()