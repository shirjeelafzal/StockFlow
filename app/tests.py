from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from app.tasks import process_transaction
from .models import User, StockData, Transaction

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a test user
        self.user = User.objects.create(username='testuser', balance=10000.00)
        
        # Create a test stock
        self.stock = StockData.objects.create(
            ticker='AAPL', open_price=150.00, close_price=155.00,
            high=160.00, low=145.00, volume=1000, timestamp='2025-01-01T10:00:00Z'
        )
        
    def test_create_user(self):
        response = self.client.post('/api/users/', {'username': 'newuser', 'balance': 5000.00})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
    
    def test_get_user(self):
        response = self.client.get(f'/api/users/{self.user.username}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
    
    def test_create_stock(self):
        data = {
            'ticker': 'GOOGL',
            'open_price': 2800.00,
            'close_price': 2825.00,
            'high': 2850.00,
            'low': 2780.00,
            'volume': 500,
            'timestamp': '2025-01-01T12:00:00Z'
        }
        response = self.client.post('/api/stocks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ticker'], 'GOOGL')
    
    def test_get_stock(self):
        response = self.client.get(f'/api/stocks/{self.stock.ticker}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ticker'], self.stock.ticker)
    
    def test_create_transaction_insufficient_balance(self):
        data = {
            'user': self.user.id,
            'ticker': 'AAPL',
            'transaction_type': 'BUY',
            'transaction_volume': 1000
        }
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # call the celery task
        transaction_id = response.data['id']
        process_transaction(transaction_id) 
        transaction = Transaction.objects.get(id=transaction_id)
        self.assertEqual(transaction.status, 'failed')

    def test_create_transaction_success(self):
        data = {
            'user': self.user.id,
            'ticker': 'AAPL',
            'transaction_type': 'BUY',
            'transaction_volume': 1
        }
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_transactions(self):
        Transaction.objects.create(user=self.user, ticker='AAPL', transaction_type='BUY', transaction_volume=10, transaction_price=1500.00, status='completed')
        response = self.client.get(f'/api/transactions/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_transactions_by_date(self):
        Transaction.objects.create(user=self.user, ticker='AAPL', transaction_type='BUY', transaction_volume=10, transaction_price=1500.00, status='completed', timestamp='2025-01-01T10:00:00Z')
        response = self.client.get(f'/api/transactions/{self.user.id}/?start_timestamp=2025-01-01T00:00:00Z&end_timestamp=2025-01-02T00:00:00Z')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
