from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """
    A user model manager where email is the unique identifier
    for authentication instead of usernames.
    """

    def create_user(self, first_name, last_name, email, password=None, **kwargs):
        if not email:
            raise ValueError(_('Kindly enter an email address'))

        # force the email address entered to follow standard email address rule
        email = self.normalize_email(email)
        user = self.model(first_name=first_name, last_name=last_name, email=email, **kwargs)

        # hash the password
        user.set_password(password)
        user.save(using=self.db)

        from core.models import Wallet #to avoid circular imports
        Wallet.objects.create(user=user)
        
        return user

    # create admin user
    def create_superuser(self, first_name, last_name, email, password):
        """
        called create_user to create the user and added new property to the user as a superuser
        """
        user = self.create_user(first_name, last_name, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user 