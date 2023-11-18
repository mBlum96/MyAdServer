# Generated by Django 4.2.7 on 2023-11-17 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad_api', '0002_alter_ad_id_alter_ad_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='landing_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='reward',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='target_country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='target_gender',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='ad',
            name='weight',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
