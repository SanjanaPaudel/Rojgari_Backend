
````markdown
# 🚀 Rojgari Backend

Rojgari is a service marketplace platform that connects customers with skilled workers. This repository contains the backend implementation built with **Django** and **Django REST Framework (DRF)**, providing secure REST APIs for authentication, user management, and future service-related functionalities.

---

## ✨ Features

- 🔐 User Registration (Customer & Worker)
- 📱 OTP Verification (Development Mode - Terminal OTP)
- 🔄 OTP Resend
- 🔑 JWT Authentication
- 👤 Customer & Worker Profiles
- 🛡️ Password Hashing
- 📂 Image Upload Support
- 📡 RESTful API Architecture
- 🏗️ Service Layer Architecture
- 🗄️ PostgreSQL Ready
- 📖 Clean and Scalable Codebase

---

## 🛠️ Tech Stack

- Python 3.12+
- Django 6
- Django REST Framework
- PostgreSQL
- JWT Authentication (Simple JWT)
- Pillow
- Django Environ
- Twilio (Future Production OTP Support)

---

## 📁 Project Structure

```
Rojgari_Backend/
│
├── accounts/
│   ├── migrations/
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── otp_service.py
│   │   └── sms_service.py
│   ├── models.py
│   ├── serializers.py
│   ├── validators.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── rojgari_backend/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── media/
├── requirements.txt
├── manage.py
└── README.md
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/SanjanaPaudel/Rojgari_Backend.git

cd Rojgari_Backend
```

---

## Create Virtual Environment

Windows

```bash
python -m venv .venv
```

Activate

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your_secret_key

DEBUG=True

DATABASE_URL=postgres://username:password@localhost:5432/rojgari

TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone

CACHE_URL=redis://127.0.0.1:6379/1
```

---

## Apply Migrations

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## Run Server

```bash
python manage.py runserver
```

Backend will be available at

```
http://127.0.0.1:8000/
```

---

# 📡 Available APIs

## User Registration

```
POST /api/auth/signup/
```

Registers both Customer and Worker accounts.

---

## Verify OTP

```
POST /api/auth/verify-otp/
```

Verifies the OTP and completes account registration.

---

## Resend OTP

```
POST /api/auth/resend-otp/
```

Generates and sends a new OTP.

---

# 📋 Registration Flow

```
User
 │
 ▼
Click Sign Up
 │
 ▼
Choose Role
(Customer / Worker)
 │
 ▼
Registration Form
 │
 ▼
Generate OTP
 │
 ▼
Verify OTP
 │
 ▼
Account Created
 │
 ▼
Login
```

---

# 🏗️ Architecture

The backend follows a layered architecture.

```
Flutter App
      │
      ▼
REST API
      │
      ▼
Views
      │
      ▼
Serializers
      │
      ▼
Services
      │
      ▼
Models
      │
      ▼
Database
```

---

# 🔐 Authentication

JWT Authentication is implemented using Simple JWT.

Protected APIs require

```
Authorization: Bearer <access_token>
```

---

# 📂 Media Files

Uploaded images are stored inside

```
media/
```

---

# 📌 Current Progress

- ✅ Registration
- ✅ OTP Verification
- ✅ Resend OTP
- ✅ Customer Registration
- ✅ Worker Registration
- ✅ Profile Creation
- ✅ Password Encryption
- ✅ Image Upload
- ✅ JWT Configuration

---

# 🚧 Upcoming Features

- User Login
- Forgot Password
- Refresh Tokens
- Customer Dashboard
- Worker Dashboard
- Profile Update
- Service Categories
- Service Requests
- Worker Search
- Booking System
- Reviews & Ratings
- Notifications
- Payment Integration
- Admin Dashboard

---

# 👨‍💻 Development

Run system checks

```bash
python manage.py check
```

Create migrations

```bash
python manage.py makemigrations
```

Apply migrations

```bash
python manage.py migrate
```

---

# 🤝 Contributors

- **Sanjana Paudel**
- Rojgari Development Team

---

# 📄 License

This project is developed for educational and research purposes.

---

## ⭐ If you found this project helpful, don't forget to star the repository!
````

