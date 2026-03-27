# Django Retail Management Backend

A Django + Django REST Framework backend system for managing products, stores, and inventory with real-world business logic and reporting features.

---

## Features

### Core Functionality
- Manage **Products**, **Stores**, and **Inventory**
- Full CRUD APIs using Django REST Framework
- Proper relationships between models

### Business Logic
- Inventory updates instead of duplicate entries
- Automatic quantity merging for same product-store pair
- Prevents over-selling (stock cannot go below 0)

### Reporting & Insights
- Low stock detection (`/low_stock/`)
- Out-of-stock items (`/out_of_stock/`)
- Total stock per product
- Total stock per store
- Dashboard summary endpoint

### API Features
- Filtering and ordering support
- Query parameters (e.g. threshold, ordering)
- Clean and consistent JSON responses

---

## Tech Stack

- Python
- Django
- Django REST Framework (DRF)
- SQLite (default)

---

## Project Structure


retail_project/
│
├── inventory/
│ ├── models.py
│ ├── views.py
│ ├── serializers.py
│ ├── urls.py
│ └── templates/
│
├── retail_project/
│ ├── settings.py
│ ├── urls.py
│
├── manage.py
├── requirements.txt
└── README.md


---

## ⚙️ Setup Instructions

### 1. Clone the repo

git clone https://github.com/YOUR_USERNAME/django-retail-backend.git

cd django-retail-backend


### 2. Create virtual environment

python -m venv venv
venv\Scripts\activate # Windows


### 3. Install dependencies

pip install -r requirements.txt


### 4. Run migrations

python manage.py migrate


### 5. Run server

python manage.py runserver


---

##  API Endpoints

### Products
- `GET /api/products/`
- `POST /api/products/`

### Stores
- `GET /api/stores/`
- `POST /api/stores/`

### Inventory
- `GET /api/inventory/`
- `POST /api/inventory/`

---

### Reporting Endpoints

#### Low Stock

GET /api/inventory/low_stock/?threshold=5


#### Out of Stock

GET /api/inventory/out_of_stock/


#### Total by Product

GET /api/inventory/total_by_product/?ordering=-total_quantity


#### Total by Store

GET /api/inventory/total_by_store/?ordering=-total_quantity


#### Dashboard Summary

GET /api/dashboard/summary/
GET /api/dashboard/summary/?threshold=5


---

## Key Concepts Implemented

- RESTful API design
- Model relationships (ForeignKey, unique constraints)
- Business logic in ViewSets
- Aggregation using Django ORM (`Sum`, `annotate`)
- Query optimization (`select_related`)
- Custom endpoints using `@action`

---

## Future Improvements

- Authentication & permissions
- Pagination
- Frontend integration (React / Next.js)
- Deployment (Render / AWS)

---

##  Author

**Jason Samuel Das**

---
