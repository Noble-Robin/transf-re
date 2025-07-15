from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('caplogy_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.IntegerField(unique=True)),
                ('image', models.ImageField(upload_to='school_logos/')),
            ],
        ),
    ]
