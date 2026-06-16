# Tsaiwimon Project Structure

```
tsaiwimon/
│
├── README.md                    # Main project documentation
├── README_DEVELOPMENT.md        # Development guide
├── Tsaiwimon_FRD.md            # Functional Requirements Document
│
├── manage.py                   # Django management script
├── pyproject.toml              # uv and project configuration
├── requirements.txt            # Python dependencies
│
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
│
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
│
├── setup.sh                    # Setup script (Linux/Mac)
├── setup.bat                   # Setup script (Windows)
│
├── tsaiwimon/                  # Django project settings
│   ├── __init__.py
│   ├── settings.py             # Main settings
│   ├── urls.py                 # URL routing
│   ├── wsgi.py                 # WSGI application
│   ├── asgi.py                 # ASGI application
│
├── apps/                       # Django applications
│   ├── __init__.py
│   │
│   ├── core/                   # Base models and utilities
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py           # Base models, UserProfile
│   │   ├── serializers.py
│   │   └── admin.py
│   │
│   ├── ecommerce/              # E-Commerce System
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py           # Category, Product, Cart, Order, Review, Payment
│   │   ├── views.py            # ViewSets for e-commerce
│   │   ├── serializers.py      # DRF Serializers
│   │   ├── urls.py             # URL routing
│   │   ├── admin.py            # Django Admin
│   │   └── tests.py            # Unit tests
│   │
│   ├── warehouse/              # Warehouse Management System
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py           # Warehouse, Stock, PurchaseOrder, PickingList, etc
│   │   ├── views.py            # ViewSets for warehouse
│   │   ├── serializers.py      # DRF Serializers
│   │   ├── urls.py             # URL routing
│   │   ├── admin.py            # Django Admin
│   │   └── tests.py            # Unit tests
│   │
│   ├── marketing/              # Marketing System
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py           # Campaign, Coupon, EmailCampaign, LoyaltyPoints, etc
│   │   ├── views.py            # ViewSets for marketing
│   │   ├── serializers.py      # DRF Serializers
│   │   ├── urls.py             # URL routing
│   │   ├── admin.py            # Django Admin
│   │   └── tests.py            # Unit tests
│   │
│   └── logistics/              # Logistics System
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py           # Shipment, Return, DeliverySlot, ShippingReport, etc
│       ├── views.py            # ViewSets for logistics
│       ├── serializers.py      # DRF Serializers
│       ├── urls.py             # URL routing
│       ├── admin.py            # Django Admin
│       └── tests.py            # Unit tests
│
├── templates/                  # HTML templates
│   └── (template files)
│
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                      # User uploaded files
│
├── logs/                       # Application logs
│
├── mypy.ini                    # Type checking configuration
├── pytest.ini                  # Testing configuration
└── setup.cfg                   # Code quality configuration
```

## Models Overview

### Core App
- **UserProfile** - Extended user profile with address and contact info

### E-Commerce App
- **Category** - Product categories
- **Product** - Product information
- **ProductImage** - Additional product images
- **Cart** - Shopping cart
- **CartItem** - Items in cart
- **Order** - Customer orders
- **OrderItem** - Items in order
- **Review** - Product reviews
- **Payment** - Payment records

### Warehouse App
- **Warehouse** - Warehouse locations
- **StockLocation** - Storage positions
- **Stock** - Product stock per warehouse
- **StockHistory** - Stock change history
- **PurchaseOrder** - Supplier purchase orders
- **GoodsReceipt** - Received goods records
- **GoodsReceiptItem** - Items in receipt
- **PickingList** - Items to pick from warehouse
- **PickingItem** - Individual items in picking list
- **Parcel** - Packaged goods
- **QualityCheck** - Quality control records

### Marketing App
- **Campaign** - Marketing campaigns
- **Coupon** - Discount coupons
- **CouponUsage** - Coupon usage records
- **EmailCampaign** - Email marketing campaigns
- **EmailLog** - Email delivery logs
- **LoyaltyProgram** - Loyalty program configuration
- **MembershipTier** - Membership levels
- **LoyaltyPoints** - Customer loyalty points
- **PointsTransaction** - Points transaction history

### Logistics App
- **ShippingProvider** - Third-party shipping providers
- **Shipment** - Shipment records
- **ShipmentTracking** - Tracking history
- **Return** - Return requests
- **ReturnItem** - Items in return request
- **DeliverySlot** - Available delivery time slots
- **ShippingReport** - Daily shipping reports

## API Structure

All APIs follow REST principles:
- **GET** /api/v1/{app}/{resource}/ - List all
- **POST** /api/v1/{app}/{resource}/ - Create new
- **GET** /api/v1/{app}/{resource}/{id}/ - Retrieve one
- **PATCH** /api/v1/{app}/{resource}/{id}/ - Partial update
- **DELETE** /api/v1/{app}/{resource}/{id}/ - Delete

Custom actions available at:
- **GET/POST** /api/v1/{app}/{resource}/{id}/{action}/ - Custom action
- **GET/POST** /api/v1/{app}/{resource}/{action}/ - Collection action
