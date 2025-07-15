from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Si besoin d'étendre l'utilisateur, exemple :
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, default='none')  # Par défaut : aucun accès

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# Signal pour créer automatiquement un UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)

class SchoolImage(models.Model):
    category_id = models.IntegerField(unique=True)  # ID Moodle de la catégorie principale (école)
    image = models.ImageField(upload_to='school_logos/')

    def __str__(self):
        return f"Logo pour catégorie {self.category_id}"
