# Generated manually for auth cleanup

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_remove_user_created_at_remove_user_phone_number_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PasswordResetOTP",
        ),
    ]
