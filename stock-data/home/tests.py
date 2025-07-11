from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .views import get_market_trends

ClientUser = get_user_model()

class ClientUserModelTest(TestCase):
    def test_create_user(self):
        user = ClientUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('test123'))

    def test_email_unique(self):
        ClientUser.objects.create_user(
            username='user1',
            email='unique@example.com',
            password='test123'
        )
        with self.assertRaises(Exception):
            ClientUser.objects.create_user(
                username='user2',
                email='unique@example.com',
                password='test123'
            )

    def test_get_full_name(self):
        user = ClientUser.objects.create_user(
            username='testuser',
            email='test2@example.com',
            first_name='Juan',
            last_name='Pérez',
            password='test123'
        )
        self.assertEqual(user.get_full_name(), 'Juan Pérez')

class GetMarketTrendsTest(TestCase):
    @patch('home.views.requests.get')
    def test_get_market_trends_success(self, mock_get):
        # Respuesta existosa
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'mostActiveStock': [{'symbol': 'AAPL', 'price': 150}]
        }
        data = get_market_trends()
        self.assertIn('most_active', data)
        self.assertEqual(data['most_active'][0]['symbol'], 'AAPL')

    @patch('home.views.requests.get')
    def test_get_market_trends_api_error(self, mock_get):
        # Error
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {}
        data = get_market_trends()
        self.assertEqual(data['most_active'], [])
