
from celery import shared_task
from django.core.cache import cache
from django.db import transaction as db_transaction # to avoid conflict with local transaction
from .models import Transaction, User

@shared_task
def process_transaction(transaction_id):
    try:
        # Get the transaction by its ID
        transaction = Transaction.objects.get(id=transaction_id)
        user = transaction.user
        # Validate the transaction (e.g., check if the user has enough balance)
        if transaction.transaction_type == 'BUY' and user.balance < transaction.transaction_price:
            transaction.status = "failed"
            transaction.save()
            raise ValueError("Insufficient balance for the transaction.")

        # Perform the transaction processing (e.g., deduct amount from user's balance)
        with db_transaction.atomic():
            if transaction.transaction_type == 'BUY':
                user.balance -= transaction.transaction_price
                
            elif transaction.transaction_type == 'SELL':
                user.balance += transaction.transaction_price

            user.save()
            transaction.status = 'completed'
            transaction.save()

        # delete the cache for user data
        cache_key = f"user_{user.username}"
        cache.delete(cache_key)
        
        return f"Transaction {transaction_id} processed successfully."

    except Exception as e:
        # Handle any errors during processing
        return f"Error processing transaction {transaction_id}: {str(e)}"
