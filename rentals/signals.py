from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from catalog.models import MovieCopy

from .models import Rental


def sync_movie_copy_status(movie_copy_id):
    movie_copy = MovieCopy.objects.filter(pk=movie_copy_id).first()

    if movie_copy is None:
        return

    if movie_copy.status == MovieCopy.AvailabilityStatus.DAMAGED:
        return

    has_open_rental = (
        Rental.objects.filter(
            movie_copy_id=movie_copy_id,
            return_date__isnull=True,
        )
        .exclude(
            status=Rental.RentalStatus.RETURNED,
        )
        .exists()
    )

    if has_open_rental:
        new_status = MovieCopy.AvailabilityStatus.RENTED
    else:
        new_status = MovieCopy.AvailabilityStatus.AVAILABLE

    if movie_copy.status != new_status:
        MovieCopy.objects.filter(pk=movie_copy_id).update(status=new_status)


@receiver(post_save, sender=Rental)
def update_inventory_after_rental_save(
    sender,
    instance,
    **kwargs,
):
    sync_movie_copy_status(instance.movie_copy_id)


@receiver(post_delete, sender=Rental)
def update_inventory_after_rental_delete(
    sender,
    instance,
    **kwargs,
):
    sync_movie_copy_status(instance.movie_copy_id)
