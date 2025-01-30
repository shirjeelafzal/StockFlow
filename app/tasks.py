from celery import shared_task
from django.core.cache import cache
from django.db import transaction as db_transaction  # to avoid conflict with local transaction
from .models import Transaction, User

@shared_task
def process_transaction(transaction_id):
    """
    Process a transaction by updating the user's balance.
    
    Args:
        transaction_id (int): The ID of the transaction to be processed.
        
    Returns:
        str: Success or error message.
    """
    try:
        # get the transaction by its ID
        transaction = Transaction.objects.get(id=transaction_id)
        user = transaction.user
        
        # validate the transaction (check if the user has enough balance for a buy transaction)
        if transaction.transaction_type == 'BUY' and user.balance < transaction.transaction_price:
            transaction.status = "failed"
            transaction.save()
            raise ValueError("Insufficient balance for the transaction.")

        # perform the transaction processing inside an atomic block for data consistency
        with db_transaction.atomic():
            if transaction.transaction_type == 'BUY':
                user.balance -= transaction.transaction_price  # deduct amount for buy transaction
                
            elif transaction.transaction_type == 'SELL':
                user.balance += transaction.transaction_price  # add amount for sell transaction

            user.save()
            transaction.status = 'completed'
            transaction.save()

        # delete the cache for user data to ensure updated balance is fetched next time
        cache_key = f"user_{user.username}"
        cache.delete(cache_key)
        
        return f"Transaction {transaction_id} processed successfully."

    except Exception as e:
        # handle any errors during processing and return error message
        return f"Error processing transaction {transaction_id}: {str(e)}"
