# Stock Trading API - README

## 📌 Overview
This project is a **Stock Trading API** built using **Django REST Framework (DRF)** with **Celery** for asynchronous transaction processing and **Redis** for caching user data. The API allows users to:
- Register accounts and manage their balance
- Retrieve stock data
- Execute buy/sell transactions with automated processing
- View transaction history
- Monitor Celery tasks using **Flower**

## 🚀 Features
- **User Management**: Create users and retrieve user details.
- **Stock Data Management**: Fetch stock data by ticker.
- **Transaction Processing**: Handle buy/sell transactions with balance validation.
- **Caching**: Uses Redis to optimize performance.
- **Asynchronous Processing**: Uses Celery for background transaction handling.
- **Task Monitoring**: Uses **Flower** for tracking Celery tasks.
- **Swagger API Documentation**: Auto-generated API docs with `drf-yasg`.

---
## 🛠️ Setup Guide

### 1️⃣ **Clone the Repository**
```sh
git clone https://github.com/your-repo/stock-trading-api.git
cd stock-trading-api
```

### 2️⃣ **Set Up the Environment Variables**
Create a `.env` file in the root directory:
```ini
# Database Configuration
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_PORT=5432  # Change if needed

# Redis & Celery Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# API Keys and External Services
OPENAI_API_KEY=your_openai_api_key
MONGODB_URL=mongodb://your_mongo_url
DB_NAME=your_db_name
COLLECTION_NAME=your_collection_name
MODEL_NAME=your_model_name
```

### 3️⃣ **Run the Project with Docker**
Ensure you have Docker installed, then start the services:

```sh
docker-compose up --build -d
```
This will:
✅ Build the Django API  
✅ Set up PostgreSQL, Redis, Celery, and Flower  
✅ Run migrations  

### 4️⃣ **Apply Migrations & Create Superuser**
```sh
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 5️⃣ **Run Celery Worker (Optional)**
To process transactions asynchronously:
```sh
docker-compose exec web celery -A stockflow worker --loglevel=info
```

### 6️⃣ **Monitor Celery Tasks with Flower**
To view the **Celery task dashboard**, go to:
```sh
http://localhost:5555
```
You can use **Flower** to:
- See active and completed tasks
- Monitor task execution time
- Restart failed tasks

To start Flower manually, run:
```sh
docker-compose exec web celery -A stockflow flower
```

---
## 📡 API Endpoints

### 🔹 User API
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/users/` | Create a new user |
| `GET` | `/users/{username}/` | Retrieve user details |

### 🔹 Stock Data API
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/stocks/` | List all stocks |
| `GET` | `/stocks/{ticker}/` | Retrieve stock details |
| `POST` | `/stocks/` | Create a new stock entry |

### 🔹 Transaction API
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/transactions/` | Execute a new buy/sell transaction |
| `GET` | `/transactions/{user_id}/` | Retrieve a user's transactions |
| `GET` | `/transactions/{user_id}/{start_timestamp}/{end_timestamp}/` | Filter transactions by date |

### 🔹 Swagger API Docs
To view the interactive API documentation:
```sh
http://localhost:8000/swagger/
```

---
## 🏗️ Data Models

### 1️⃣ **User Model**
```python
class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2️⃣ **StockData Model**
```python
class StockData(models.Model):
    ticker = models.CharField(max_length=10)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()
    timestamp = models.DateTimeField()
```

### 3️⃣ **Transaction Model**
```python
class Transaction(models.Model):
    TRANSACTION_TYPES = [('BUY', 'Buy'), ('SELL', 'Sell')]
    TRANSACTION_STATUSES = [('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    transaction_volume = models.IntegerField()
    transaction_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUSES, default='pending')
```

---
## 🛠️ Assumptions
1. **Users have a starting balance** that allows transactions.
2. **Stock prices are pre-populated** and are retrieved from a database.
3. **Transactions require validation**, ensuring the user has sufficient funds.
4. **Celery is required** for asynchronous processing of transactions.
5. **Redis is used** to cache frequently accessed data.
6. **Flower is used** to monitor Celery tasks.

---

### 🎯 **Next Steps**
- Implement **real-time stock price updates** using WebSockets.
- Add **authentication (JWT)** for user security.
- Enable **trading limits** to prevent risky transactions.

---

Now, this README includes:
✅ **Flower integration**  
✅ **Correct `docker-compose` setup with `--build`**  
✅ **A clean, professional layout**  
