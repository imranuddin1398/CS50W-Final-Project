from django.contrib import admin
from .models import Product, Category, Order, Review, UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_balance')
    search_fields = ('user__username', 'wallet_balance')
    list_editable = ('wallet_balance',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Review)
