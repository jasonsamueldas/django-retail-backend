#  Retail Management API (Django + DRF)

A production-style backend built using Django and Django REST Framework for managing products, stores, inventory, and transactions with secure, role-based access control.

---

##  Features

*  **JWT Authentication** (Login, Token Refresh)
*  **Role-Based Access Control**

  * Admin → Full access
  * Manager → Restricted to assigned store
*  **Store-Based Data Isolation** (Multi-tenant architecture)
*  **Transaction-Based Inventory System**

  * All stock updates via transactions (sale/restock)
  * Prevents negative stock & overselling
* **Analytics Endpoints**

  * Low stock
  * Out-of-stock
  * Aggregated summaries
*  **Pagination, Filtering & Search**
*  **Optimized Queries using select_related**
*  **Interactive API Docs (Swagger UI)**

---

##  Tech Stack

* **Backend:** Django, Django REST Framework
* **Authentication:** SimpleJWT
* **Documentation:** drf-yasg (Swagger/OpenAPI)
* **Database:** SQLite (default, easily switchable)

---

##  Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/jasonsamueldas/django-retail-backend.git
cd django-retail-backend
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4️. Run migrations

```bash
python manage.py migrate
```

### 5️. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 6️. Run server

```bash
python manage.py runserver
```

---

##  Authentication

### Get JWT Token

```http
POST /api/token/
```

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

### Use Token

```
Authorization: Bearer <your_access_token>
```

---

## 📖 API Documentation

Swagger UI available at:

```
http://127.0.0.1:8000/swagger/
```

Use the **Authorize button** to enter your JWT token.

---

##  Core Endpoints

### 🔹 Products

* `GET /api/products/`
* `POST /api/products/` (Admin only)

### 🔹 Stores

* `GET /api/stores/`

### 🔹 Inventory

* `GET /api/inventory/`
* `GET /api/inventory/low_stock/?threshold=10`
* `GET /api/inventory/out_of_stock/`
* `GET /api/inventory/total_by_product/`
* `GET /api/inventory/total_by_store/`

### 🔹 Transactions

* `POST /api/transactions/`
* `GET /api/transactions/`

### 🔹 User

* `GET /api/me/`

---

##  Key Design Decisions

* **Multi-Tenant Architecture:** Managers are restricted to their assigned store
* **Server-Side Ownership Enforcement:** Store/user fields are never trusted from client input
* **Transaction-Driven Inventory:** Prevents inconsistent stock states
* **Separation of Concerns:**

  * Permissions → Access control
  * Utils → Query logic
  * Views → Business logic

---

##  Testing

Run tests using:

```bash
python manage.py test
```

---

##  Future Improvements

* Unit & integration test expansion
* Docker deployment
* PostgreSQL integration
* CI/CD pipeline

---

##  Author

**Jason Samuel Das**

---
