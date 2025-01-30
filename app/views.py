from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.decorators import action
import json

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.dateparse import parse_datetime
from .serializers import UserSerializer, StockDataSerializer, TransactionSerializer
from .models import User, StockData, Transaction
from .tasks import process_transaction 

class UserViewSet(viewsets.ViewSet):
    lookup_field = 'username'
    
    def retrieve(self, request, username=None):
        """
        Retrieve user data, using cache if available.
        """
        cache_key = f"user_{username}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user)
            cache.set(cache_key, json.dumps(serializer.data), timeout=3600)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={201: UserSerializer(), 400: 'Bad Request'},
        operation_description="Create a new user with username and balance"
    )
    def create(self, request):
        """
        Create a new user.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class StockViewSet(viewsets.ViewSet):
    lookup_field = 'ticker'
    
    def list(self, request):
        """
        List all stocks, using cache if available.
        """
        cache_key = "all_stocks"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(json.loads(cached_data))
        
        stocks = StockData.objects.all()
        serializer = StockDataSerializer(stocks, many=True)
        cache.set(cache_key, json.dumps(serializer.data), timeout=3600)
        return Response(serializer.data)
    
    def retrieve(self, request, ticker=None):
        """
        Retrieve stock data, using cache if available.
        """
        cache_key = f"stock_{ticker}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(json.loads(cached_data))
        
        try:
            stock = StockData.objects.get(ticker=ticker)
            serializer = StockDataSerializer(stock)
            cache.set(cache_key, json.dumps(serializer.data), timeout=3600)
            return Response(serializer.data)
        except StockData.DoesNotExist:
            return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        request_body=StockDataSerializer,
        responses={201: StockDataSerializer()}
    )
    def create(self, request):
        """
        Create a new stock entry.
        """
        serializer = StockDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("all_stocks")  # Invalidate cache for all stocks
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class TransactionViewSet(viewsets.ViewSet):
    lookup_field = 'user_id'
    
    @swagger_auto_schema(
        request_body=TransactionSerializer,
        responses={201: TransactionSerializer()}
    )
    def create(self, request):
        """
        Create a new transaction.
        """
        required_fields = ["user", "ticker", "transaction_type", "transaction_volume"]
    
        for field in required_fields:
            if field not in request.data:
                return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = request.data.get("user")
        ticker = request.data.get("ticker")
        transaction_type = request.data.get("transaction_type")
        transaction_volume = int(request.data.get("transaction_volume"))
        
        try:
            user = User.objects.get(id=user_id)
            stock = StockData.objects.get(ticker=ticker)
            transaction_price = stock.close_price * transaction_volume
            
            transaction = Transaction.objects.create(
                user=user,
                ticker=ticker,
                transaction_type=transaction_type,
                transaction_volume=transaction_volume,
                transaction_price=transaction_price,
                status="pending"
            )

            process_transaction.delay(transaction.id)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except StockData.DoesNotExist:
            return Response({"error": "Stock not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def retrieve(self, request, user_id=None):
        """
        Retrieve transactions for a specific user.
        """
        transactions = Transaction.objects.filter(user_id=user_id)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'start_timestamp', openapi.IN_QUERY, 
                description="Start timestamp (ISO 8601 format)", 
                type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                'end_timestamp', openapi.IN_QUERY, 
                description="End timestamp (ISO 8601 format)", 
                type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={200: TransactionSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def transactions_by_date(self, request, user_id=None, start_timestamp=None, end_timestamp=None):
        """
        Filter transactions by date range.
        """
        start_timestamp = request.query_params.get("start_timestamp")
        end_timestamp = request.query_params.get("end_timestamp")
        
        if not start_timestamp or not end_timestamp:
            return Response(
                {"error": "Both start_timestamp and end_timestamp are required. Use ISO 8601 format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_datetime = parse_datetime(start_timestamp)
        end_datetime = parse_datetime(end_timestamp)
        
        if not start_datetime or not end_datetime:
            return Response({"error": "Invalid date format. Use ISO 8601."}, status=status.HTTP_400_BAD_REQUEST)

        transactions = Transaction.objects.filter(
            user_id=user_id, timestamp__range=[start_datetime, end_datetime]
        )
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
