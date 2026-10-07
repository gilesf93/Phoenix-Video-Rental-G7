from django.conf import settings
from django.db import models
from django.utils import timezone


class Rental(models.Model):
    class RentalStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        RETURNED = "returned", "Returned"
        OVERDUE = "overdue", "Overdue"

    customer = models.ForeignKey(
        "accounts.CustomerProfile",
        on_delete=models.PROTECT,
        related_name="rentals",
    )
    movie_copy = models.ForeignKey(
        "catalog.MovieCopy",
        on_delete=models.PROTECT,
        related_name="rentals",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_rentals",
    )
    rental_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RentalStatus.choices,
        default=RentalStatus.ACTIVE,
        db_index=True,
    )

    class Meta:
        ordering = ["-rental_date"]

    @property
    def is_overdue(self):
        return (
            self.return_date is None
            and self.due_date < timezone.localdate()
        )

    def __str__(self):
        return f"Rental {self.pk} - {self.movie_copy}"


class PaymentRecord(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CREDIT_CARD = "credit_card", "Credit Card"
        DEBIT_CARD = "debit_card", "Debit Card"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    rental = models.ForeignKey(
        Rental,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Payment {self.pk} - ${self.amount}"