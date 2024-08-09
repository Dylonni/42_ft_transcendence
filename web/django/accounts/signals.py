from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_super_user(sender, **kwargs):
	user_model = apps.get_model('accounts.CustomUser')
	profile_model = apps.get_model('profiles.Profile')
	for admin in ['acloos', 'daumis', 'psan']:
		if not user_model.objects.filter(username=f'42_{admin}').exists():
			user = user_model.objects.create_user(f'42_{admin}', f'{admin}@42.fr', f'42_{admin}', is_verified=True, is_active=True)
			profile_model.objects.create_from_user(user)