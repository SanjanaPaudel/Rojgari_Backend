# Rojgari System Architecture & Design 🏗️

This document outlines the architectural components, database design, and caching flow of the Rojgari application. It is designed to help human developers quickly grasp how the parts connect and how to extend the codebase.

---

## 1. Component Topology

Rojgari is structured as a decoupled backend API service backed by high-performance data and caching systems.

```mermaid
graph TD
    Client[Web Browser / API Client] <-->|HTTP REST / Cookies| Django[Django App with Ninja]
    Django <-->|ORM / SQL| Postgres[(PostgreSQL DB)]
    Django <-->|Redis Protocol| Valkey[(Valkey Cache)]
```

* **Django Framework**: Serves as the web application server. We use [Django Ninja](https://django-ninja.rest-framework.com/) for building APIs with static type annotation and automatic Swagger documentation.
* **PostgreSQL**: The primary relational store. Handles user accounts, profiles, requests, bookings, payments, and reviews.
* **Valkey**: A high-performance, open-source caching server (wire-compatible with Redis). Used to cache database queries, sessions, and transient states.

---

## 2. Database Models (ER Diagram)

The database schema manages user accounts, distinct customer/worker profiles, service catalogs, requests, bookings, and tracking history.

```mermaid
erDiagram
    USER ||--|| CUSTOMER : "has profile"
    USER ||--|| WORKER : "has profile"
    WORKER ||--o{ WORKER_DOCUMENT : "submits"
    WORKER ||--o{ WORKER_SERVICE : "offers"
    SERVICE_CATEGORY ||--o{ WORKER_SERVICE : "categorizes"
    SERVICE_CATEGORY ||--o{ SERVICE_REQUEST : "requested for"
    CUSTOMER ||--o{ SERVICE_REQUEST : "places"
    SERVICE_REQUEST ||--o| BOOKING : "leads to"
    WORKER ||--o{ BOOKING : "accepts"
    BOOKING ||--o| PAYMENT : "has"
    BOOKING ||--o{ REVIEW : "receives"
    USER ||--o{ NOTIFICATION : "receives"
    WORKER ||--o{ WORKER_LOCATION_HISTORY : "tracked in"

    USER {
        uuid id PK
        string username
        string email
        string full_name
        string phone_number
        string role
        string profile_photo_url
        boolean is_active
        boolean is_verified
        datetime created_at
        datetime updated_at
    }

    CUSTOMER {
        uuid id PK
        uuid user_id FK
        string address
        float default_lat
        float default_lng
        datetime created_at
    }

    WORKER {
        uuid id PK
        uuid user_id FK
        text bio
        float avg_rating
        int total_jobs
        boolean is_available
        boolean is_approved
        float current_lat
        float current_lng
        text current_location
        string bank_account
        string wallet_number
        datetime approved_at
        datetime created_at
    }

    WORKER_DOCUMENT {
        uuid id PK
        uuid worker_id FK
        string document_type
        string file_url
        string verification_status
        text rejection_reason
        datetime submitted_at
        datetime reviewed_at
    }

    SERVICE_CATEGORY {
        uuid id PK
        string name
        text description
        string icon_url
        boolean is_active
        datetime created_at
    }

    WORKER_SERVICE {
        uuid id PK
        uuid worker_id FK
        uuid category_id FK
        int years_experience
        string skill_level
        decimal hourly_rate
        datetime created_at
    }

    SERVICE_REQUEST {
        uuid id PK
        uuid customer_id FK
        uuid category_id FK
        text description
        string status
        float customer_lat
        float customer_lng
        text customer_location
        string address
        datetime requested_at
        datetime expires_at
    }

    BOOKING {
        uuid id PK
        uuid request_id FK
        uuid worker_id FK
        string status
        decimal agreed_price
        datetime accepted_at
        datetime started_at
        datetime completed_at
        datetime cancelled_at
        text cancellation_reason
    }

    PAYMENT {
        uuid id PK
        uuid booking_id FK
        decimal amount
        string method
        string status
        string transaction_ref
        datetime paid_at
    }

    REVIEW {
        uuid id PK
        uuid booking_id FK
        uuid reviewer_id FK
        uuid reviewee_id FK
        int rating
        text comment
        datetime created_at
    }

    NOTIFICATION {
        uuid id PK
        uuid user_id FK
        string title
        text body
        string type
        boolean is_read
        uuid reference_id
        string reference_type
        datetime created_at
    }

    WORKER_LOCATION_HISTORY {
        uuid id PK
        uuid worker_id FK
        float lat
        float lng
        text location
        datetime recorded_at
    }
```

### Models Reference
* **accounts**:
  * [User](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L5): Extends Django's `AbstractUser` with UUID primary key.
  * [Customer](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L23) & [Worker](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L38): Profiles linked 1:1 to [User](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L5).
  * [WorkerDocument](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L67): Worker verification uploads.
* **services**:
  * [ServiceCategory](file:///Users/pablo/Development/Projects/Rojgari/services/models.py#L5): Catalog categories.
  * [WorkerService](file:///Users/pablo/Development/Projects/Rojgari/services/models.py#L20): Links workers to their offered categories.
  * [ServiceRequest](file:///Users/pablo/Development/Projects/Rojgari/services/models.py#L35): Posted by customers.
* **bookings**:
  * [Booking](file:///Users/pablo/Development/Projects/Rojgari/bookings/models.py#L5): Match request and worker.
  * [Review](file:///Users/pablo/Development/Projects/Rojgari/bookings/models.py#L23): Performance feedback.
  * [WorkerLocationHistory](file:///Users/pablo/Development/Projects/Rojgari/bookings/models.py#L39): GPS track trail.
* **payments**:
  * [Payment](file:///Users/pablo/Development/Projects/Rojgari/payments/models.py#L5): Transaction records.
* **notifications**:
  * [Notification](file:///Users/pablo/Development/Projects/Rojgari/notifications/models.py#L5): System alerts.

---

## 3. Core Technical Flow

### Authentication Pattern
Rojgari uses Django's built-in session-based authentication coupled with Django Ninja's `django_auth` middleware.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client / UI
    participant Django as Django Ninja
    participant DB as PostgreSQL
    participant Cache as Valkey (Sessions)

    Client->>Django: POST /api/auth/login (username/password)
    Django->>DB: Verify credentials
    DB-->>Django: Valid user
    Django->>Cache: Save session id & user context
    Django-->>Client: Set Cookie: sessionid=XYZ (HTTPOnly)
    
    Note over Client, Django: Subsequent requests automatically send Cookie
    Client->>Django: GET /api/auth/me
    Django->>Cache: Lookup sessionid XYZ
    Cache-->>Django: Found User details
    Django-->>Client: Response User Details (JSON)
```

1. **Registration**: [register](file:///Users/pablo/Development/Projects/Rojgari/accounts/api/auth.py#L10) creates a new `User` and automatically sets up a [Customer](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L23) or [Worker](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L38) profile based on the selected role.
2. **Login**: [login_user](file:///Users/pablo/Development/Projects/Rojgari/accounts/api/auth.py#L38) establishes a standard Django session.
3. **Session Cookie**: The client receives a secure, HTTP-only cookie. Django reads this cookie on subsequent requests using `django_auth` to populate `request.user`.

---

## 4. Development Standards & Style

* **Coding Style**: Follow PEP 8 guidelines. Type hint all view functions, endpoints, and helpers. Keep source format check compliant with Ruff.
* **API Versioning**: Endpoints are defined using Pydantic schemas (e.g. [UserOut](file:///Users/pablo/Development/Projects/Rojgari/accounts/api/schemas.py#L22)) for input validation and output serialization.
* **Test First**: Before adding any API modifications, write corresponding automated test cases in [accounts/tests.py](file:///Users/pablo/Development/Projects/Rojgari/accounts/tests.py).
