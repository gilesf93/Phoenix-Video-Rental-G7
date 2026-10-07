from django.db import migrations


def create_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")

    Group.objects.get_or_create(name="Admin")
    Group.objects.get_or_create(name="Employee")
    Group.objects.get_or_create(name="Customer")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_roles,
            migrations.RunPython.noop,
        ),
    ]
