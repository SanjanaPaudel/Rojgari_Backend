from django.contrib.auth import authenticate, login, logout
from ninja import Router
from ninja.security import django_auth

from accounts.api.schemas import ErrorSchema, LoginInput, RegisterInput, UserOut
from accounts.models import Customer, User, Worker

router = Router()


@router.post("/register", response={201: UserOut, 400: ErrorSchema})
def register(request, data: RegisterInput):
    """
    Register a new user and auto-create the selected profile (customer/worker).
    """
    if User.objects.filter(username=data.username).exists():
        return 400, {"message": "Username already exists"}
    if User.objects.filter(email=data.email).exists():
        return 400, {"message": "Email already exists"}
    if data.role not in ["customer", "worker"]:
        return 400, {"message": "Role must be 'customer' or 'worker'"}

    user = User.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        phone_number=data.phone_number,
        role=data.role,
    )

    if data.role == "customer":
        Customer.objects.create(user=user)
    elif data.role == "worker":
        Worker.objects.create(user=user)

    return 201, user


@router.post("/login", response={200: UserOut, 401: ErrorSchema})
def login_user(request, data: LoginInput):
    """
    Authenticate user and start session.
    """
    user = authenticate(username=data.username, password=data.password)
    if user is not None:
        login(request, user)
        return 200, user
    return 401, {"message": "Invalid username or password"}


@router.post("/logout", auth=django_auth, response={204: None})
def logout_user(request):
    """
    Destroy current user session.
    """
    logout(request)
    return 204, None


@router.get("/me", auth=django_auth, response=UserOut)
def get_me(request):
    """
    Retrieve authenticated user account details.
    """
    return request.user
