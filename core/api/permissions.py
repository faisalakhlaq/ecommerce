from rest_framework.permissions import BasePermission

class IsOrderOwner(BasePermission):
    """Custome permission used for checking if this user
    has created the order"""
    message = 'View Order Summary not allowed.'
    def has_object_permission(self, request, view, object):
        return object.user == request.user

class BlocklistPermission(permissions.BasePermission):
    """
    Global permission check for blocked IPs.
    """

    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']
        blocked = Blocklist.objects.filter(ip_addr=ip_addr).exists()
        return not blocked