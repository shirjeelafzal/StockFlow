from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from app.tasks import process_transaction
from .models import User, StockData, Transaction

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()  # Initialize the API client for testing
        
        # Create a test user with a balance of 10,000.00
        self.user = User.objects.create(username='testuser', balance=10000.00)
        
        # Create a test stock with specific details
        self.stock = StockData.objects.create(
            ticker='AAPL', open_price=150.00, close_price=155.00,
            high=160.00, low=145.00, volume=1000, timestamp='2025-01-01T10:00:00Z'
        )
        
    def test_create_user(self):
        """
        Test creating a new user via the API.
        """
        response = self.client.post('/api/users/', {'username': 'newuser', 'balance': 5000.00})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Check if user is created
        self.assertEqual(response.data['username'], 'newuser')  # Verify the username
    
    def test_get_user(self):
        """
        Test retrieving user details via the API.
        """
        response = self.client.get(f'/api/users/{self.user.username}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Check successful retrieval
        self.assertEqual(response.data['username'], self.user.username)  # Verify the username
    
    def test_create_stock(self):
        """
        Test creating a new stock via the API.
        """
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Check if stock is created
        self.assertEqual(response.data['ticker'], 'GOOGL')  # Verify the ticker symbol
    
    def test_get_stock(self):
        """
        Test retrieving stock details via the API.
        """
        response = self.client.get(f'/api/stocks/{self.stock.ticker}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Check successful retrieval
        self.assertEqual(response.data['ticker'], self.stock.ticker)  # Verify the ticker symbol
    
    def test_create_transaction_insufficient_balance(self):
        """
        Test creating a transaction where the user has insufficient balance.
        """
        data = {
            'user': self.user.id,
            'ticker': 'AAPL',
            'transaction_type': 'BUY',
            'transaction_volume': 1000  # Trying to buy 1000 units
        }
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Check if transaction is created
        
        # Call the Celery task to process the transaction
        transaction_id = response.data['id']
        process_transaction(transaction_id)  # Simulate task for processing transaction
        transaction = Transaction.objects.get(id=transaction_id)
        self.assertEqual(transaction.status, 'failed')  # Check that the transaction failed due to insufficient funds

    def test_create_transaction_success(self):
        """
        Test creating a transaction with sufficient balance.
        """
        data = {
            'user': self.user.id,
            'ticker': 'AAPL',
            'transaction_type': 'BUY',
            'transaction_volume': 1  # Buying 1 unit
        }
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Check if transaction is created
    
    def test_get_transactions(self):
        """
        Test retrieving transactions via the API.
        """
        Transaction.objects.create(user=self.user, ticker='AAPL', transaction_type='BUY', transaction_volume=10, transaction_price=1500.00, status='completed')
        response = self.client.get(f'/api/transactions/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Check if transactions are retrieved
        self.assertEqual(len(response.data), 1)  # Verify only 1 transaction is returned
    
    def test_transactions_by_date(self):
        """
        Test filtering transactions by date range.
        """
        Transaction.objects.create(user=self.user, ticker='AAPL', transaction_type='BUY', transaction_volume=10, transaction_price=1500.00, status='completed', timestamp='2025-01-01T10:00:00Z')
        response = self.client.get(f'/api/transactions/{self.user.id}/?start_timestamp=2025-01-01T00:00:00Z&end_timestamp=2025-01-02T00:00:00Z')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Check if transactions are retrieved
        self.assertEqual(len(response.data), 1)  # Verify 1 transaction is returned within the date range
