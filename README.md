# 🚀 Rojgari Backend

Rojgari is a service marketplace platform that connects customers with skilled workers. This repository contains the backend implementation built with **Django** and **Django REST Framework (DRF)**, providing secure REST APIs for authentication, user management, and future service-related functionalities.

---

## ✨ Features

- 🔐 User Registration (Customer & Worker)
- 📱 OTP Verification
- 🔄 OTP Resend
- 🔑 JWT Authentication
- 👤 Customer & Worker Profiles
- 🛡️ Secure Password Hashing
- 📂 Profile Image Upload
- 📡 RESTful API Architecture
- 🏗️ Service Layer Architecture
- 🗄️ PostgreSQL Ready

---

## 🛠️ Tech Stack

- Python 3.12
- Django 6
- Django REST Framework
- PostgreSQL
- Simple JWT
- Pillow
- Django Environ
- Twilio (Production OTP Support)

---

## 📁 Project Structure

```text
Rojgari_Backend/
│
├── accounts/
│   ├── migrations/
│   ├── services/
│   ├── models.py
│   ├── serializers.py
│   ├── validators.py
│   ├── views.py
│   └── urls.py
│
├── rojgari_backend/
├── media/
├── requirements.txt
├── manage.py
└── README.md
```

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/SanjanaPaudel/Rojgari_Backend.git
cd Rojgari_Backend
```

### Check UV version

```bash
uv --version
```

### Sync the Project

```bash
uv sync
```

### Activate Virtual Environment (Optional)

**Windows**

```bash
.venv\Scripts\activate
```

**You can always use UV command at the beginnning to avoid this step**

### Create .env file

```bash
   copy .env.example .env
```

### Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run Development Server

```bash
python manage.py runserver
```

The backend will run at:

```
http://127.0.0.1:8000/
```

---

## 📡 Available APIs

| Method | Endpoint                | Description       |
| ------ | ----------------------- | ----------------- |
| POST   | `/api/auth/signup/`     | User Registration |
| POST   | `/api/auth/verify-otp/` | Verify OTP        |
| POST   | `/api/auth/resend-otp/` | Resend OTP        |

---

## 📋 Registration Flow

```text
Sign Up
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
```

---

## 🔐 Authentication

JWT Authentication is implemented using **Simple JWT**.

Protected APIs require:

```
Authorization: Bearer <access_token>
```

---

## 🚧 Current Progress

- ✅ User Registration
- ✅ OTP Verification
- ✅ OTP Resend
- ✅ Customer Registration
- ✅ Worker Registration
- ✅ Profile Creation
- ✅ Password Encryption
- ✅ JWT Configuration

---

## 📌 Upcoming Features

- Login
- Forgot Password
- Customer Dashboard
- Worker Dashboard
- Profile Management
- Service Categories
- Service Booking
- Reviews & Ratings
- Notifications
- Payment Integration

---

## 👨‍💻 Contributors

- **Sanjana Paudel**
- **Rojgari Development Team**

---

## 📄 License

This project is developed for educational and academic purposes.
