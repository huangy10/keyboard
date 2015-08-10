from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import UserProfile
# Create your tests here.


class UserProfileTest(TestCase):

    def setUp(self):
        self.user = get_user_model()

    def test_user_profile_auto_create(self):
        """
        This test check if the profile is created automatically for the given user
        """
        self.assertIsNotNone(self.user.profile)
