# Rojgari REST API Documentation 📖

This project uses **Django Ninja** for constructing REST APIs. One of its primary features is automatic, out-of-the-box generation of interactive OpenAPI documentation using Swagger UI.

---

## 🚀 Accessing Swagger UI Docs

When your development environment is running, Swagger UI is served automatically at:
* **Interactive Swagger UI**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
* **Raw OpenAPI 3.0 Schema (JSON)**: [http://localhost:8000/api/openapi.json](http://localhost:8000/api/openapi.json)

Navigate to the docs page in your browser to view inputs, outputs, query parameters, schemas, and live-execute API requests.

---

## 🔐 Authentication Model

The API employs Django's session-based authentication (`DjangoAuth` middleware).
1. **Session Establishment**: Log in via `POST /api/auth/login` to store session details in cookies.
2. **Authenticated Requests**: Subsequent requests will automatically pass the session cookie.
3. **Session Termination**: Call `POST /api/auth/logout` to clear the session cookie.

---

## 📁 API Endpoints Catalog

### 1. Authentication (`/api/auth/*`)
* **`POST /auth/register`**: Creates a new user account and automatically provisions either a [Customer](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L23) or [Worker](file:///Users/pablo/Development/Projects/Rojgari/accounts/models.py#L38) profile based on the selected role.
* **`POST /auth/login`**: Authenticates user credentials and starts session.
* **`POST /auth/logout`**: Logs the user out of the active session.
* **`GET /auth/me`**: Fetches basic account details of the authenticated user.

### 2. Service Categories (`/api/categories/*`)
* **`GET /categories`**: Lists all active categories (e.g., Plumbing, Electrical, Cleaning).

### 3. Worker Operations (`/api/workers/*`)
* **`POST /workers/join`**: Sets up a worker profile for the authenticated user.
* **`POST /workers/document`**: Submits verification documents for the worker profile.
* **`GET /workers/services`**: Lists services offered by the authenticated worker.
* **`POST /workers/services`**: Adds a new service category configuration (hourly rate, experience) for the worker.

### 4. Service Requests (`/api/requests/*`)
* **`GET /requests`**: Lists service requests. For Customers, returns their posted requests. For Workers, returns pending requests.
* **`POST /requests`**: Creates a new service request (Customer only).

### 5. Bookings (`/api/bookings/*`)
* **`POST /bookings/{request_id}/accept`**: Accepts a pending request and creates a booking (Worker only).
* **`PUT /bookings/{booking_id}/status`**: Modifies the execution status of an active booking (`started`, `completed`, `cancelled`).

### 6. Payments (`/api/payments/*`)
* **`POST /payments/checkout`**: Records payment details (transaction ref, method, amount) for a completed booking.

### 7. Reviews (`/api/reviews/*`)
* **`POST /reviews`**: Submits ratings and comments for a completed booking. Updates the target worker's avg rating automatically.

### 8. Notifications (`/api/notifications/*`)
* **`GET /notifications`**: Lists all in-app notifications for the user.
* **`POST /notifications/{notification_id}/read`**: Marks a notification as read.
