from .models import Inventory

def get_inventory_queryset_for_user(user):
    if user.role == 'admin':
        return Inventory.objects.all()
    if not user.store:
        return Inventory.objects.none()
    return Inventory.objects.filter(store=user.store)