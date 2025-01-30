# StockFlow

This is a **Django Rest Framework (DRF)** API for a stock trading application. It allows users to create accounts, fetch stock data, and execute transactions (buy/sell). Transactions are processed asynchronously using **Celery** and **Redis**.

## Features
- **User Management**: Create and retrieve users with account balances.
- **Stock Data**: Retrieve stock information.
- **Transaction Processing**: Buy and sell stocks with automatic balance updates.
- **Caching**: Uses Redis to cache frequently accessed data.
- **Asynchronous Processing**: Transactions are handled using Celery tasks.
- **Swagger API Documentation** available at `/docs/`.

## Technology Stack
| Technology | Purpose |
|------------|---------|
| **Django Rest Framework (DRF)** | Backend framework for API development |
| **PostgreSQL** | Database for storing user and stock data |
| **Celery** | Handles asynchronous transaction processing |
| **Redis** | Used for caching and as Celery message broker |

## Architecture Overview
### **Django & DRF** (Backend & API Layer)
Django REST Framework serves as the main backend framework, exposing RESTful APIs for user, stock, and transaction management. It provides authentication, serialization, and request handling.

### **PostgreSQL** (Database Layer)
Stores user data, stock prices, and transaction history. The transactions are processed atomically to maintain consistency.

### **Redis** (Caching & Message Broker)
- **Caching**: Frequently accessed data (e.g., user profiles, stock prices) are stored in Redis for quick retrieval.
- **Celery Broker**: Celery tasks use Redis to queue and manage transaction processing asynchronously.

### **Celery** (Background Task Processing)
Handles transaction execution in the background to avoid blocking API requests. Ensures that transactions do not impact the API's responsiveness.

---

## Installation & Setup
### Prerequisites
- **Docker & Docker Compose** (to containerize and run the application)

### Steps
1. **Clone the repository:**
   ```sh
   git clone https://github.com/shirjeelafzal/StockFlow.git
   cd StockFlow
   ```
2. **Setup Environment Variables:**
   - Copy `.env.sample` to `.env` and update values:
     ```sh
     cp .env.sample .env
     ```
3. **Run the Application with Docker Compose:**
   ```sh
   docker-compose up --build
   ```
   This will start **PostgreSQL, Redis, Django, and Celery** in separate containers.

---

## Running Tests
Tests will run automatically when the Docker container starts, as specified in the **Dockerfile**:
```dockerfile
CMD ["sh", "-c", "python manage.py migrate && python manage.py test && python manage.py runserver 0.0.0.0:8000"]
```
There is no need to manually run tests.

---

## API Endpoints
### **Users**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/api/users/` | Create a new user |
| `GET` | `/api/users/{username}/` | Retrieve user details |

### **Stocks**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/api/stocks/` | Add stock data |
| `GET` | `/api/stocks/{ticker}/` | Retrieve stock information |

### **Transactions**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/api/transactions/` | Execute a transaction |
| `GET` | `/api/transactions/{user_id}/` | Get transactions for a user |
| `GET` | `/api/transactions/{user_id}/?start_timestamp=...&end_timestamp=...` | Filter transactions by date range |

---

### **Docker Deployment**
```sh
docker-compose up --build
```
This will start Django, PostgreSQL, Redis, and Celery in separate containers.

