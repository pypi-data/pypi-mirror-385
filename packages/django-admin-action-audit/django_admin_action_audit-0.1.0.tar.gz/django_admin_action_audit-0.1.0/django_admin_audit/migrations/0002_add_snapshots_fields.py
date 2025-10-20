from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_admin_audit", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminauditlog",
            name="after_snapshot",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="adminauditlog",
            name="before_snapshot",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="adminauditlog",
            name="can_revert",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="adminauditlog",
            name="snapshot_schema_version",
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
