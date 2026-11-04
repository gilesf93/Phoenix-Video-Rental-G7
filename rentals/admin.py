from django.contrib import admin

from .models import Rental, PaymentRecord

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "movie_copy", "rental_date", "due_date", "status")

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "rental", "amount", "payment_date", "payment_method", "payment_status")

    list_filter = ("payment_status", "payment_method")
    serch_fields = ("rental__id", "id")
    