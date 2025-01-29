from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem, OrderItem, Order
# Create your views here.

@api_view(['GET'])
def sample_data(request):
    data = {"message": "Hello from Django"}
    return Response(data)



@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        return JsonResponse({'message': 'User registered successfully'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            # Fetch the user_id after successful login
            user_id = user.id
            return JsonResponse({'message': 'Login successful', 'user_id': user_id})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def logout_user(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})


def get_user_by_id(request, user_id):
    try:
        # Retrieve user by user_id
        user = User.objects.get(id=user_id)
        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    



@csrf_exempt  # Disable CSRF for testing (Use proper authentication in production)
def add_to_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)  # Parse JSON data from frontend
        user_id = data.get("userId")  # Get user ID from frontend
        product_id = data.get("productId")

        user = get_object_or_404(User, id=user_id)
        product = get_object_or_404(Product, id=product_id)

        # Get or create a cart for the user
        cart, _ = Cart.objects.get_or_create(user=user)

        # Get or create a cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += 1  # Increment quantity
        cart_item.save()

        return JsonResponse({"message": "Product added to cart", "cartItem": cart_item.quantity}, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)


def cart_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    cart = Cart.objects.filter(user=user).first()  # Get the user's cart
    items = cart.items.all() if cart else []
    
    cart_data = [
        {
            "productId": item.product.id,
            "productName": item.product.name,
            "quantity": item.quantity,
            "totalPrice": item.total_price
        }
        for item in items
    ]

    return JsonResponse({"cartItems": cart_data, "totalPrice": cart.total_price if cart else 0})


@csrf_exempt
def place_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get("userId")

        user = get_object_or_404(User, id=user_id)
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return JsonResponse({"error": "Cart is empty"}, status=400)

        # Create an order
        order = Order.objects.create(user=user, total_price=cart.total_price)

        # Add cart items to the order
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.total_price,
            )

        # Clear the cart
        cart.items.all().delete()

        return JsonResponse({"message": "Order placed successfully", "orderId": order.id}, status=201)

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def add_product(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Extract the fields from the JSON data
        category_1 = data.get("category_1", "")
        category_2 = data.get("category_2", "")
        category_3 = data.get("category_3", "")
        title = data.get("title", "")
        product_rating = data.get("product_rating", 0)
        selling_price = data.get("selling_price", 0.0)
        mrp = data.get("mrp", 0.0)
        seller_name = data.get("seller_name", "")
        seller_rating = data.get("seller_rating", 0)
        description = data.get("description", "")
        highlights = data.get("highlights", "")
        image_links = data.get("image_links", "")

        # Validate required fields
        if not title or not selling_price or not product_rating:
            return JsonResponse({"error": "Title, selling price, and product rating are required"}, status=400)

        # Create the product object
        product = Product.objects.create(
            category_1=category_1,
            category_2=category_2,
            category_3=category_3,
            title=title,
            product_rating=product_rating,
            selling_price=selling_price,
            mrp=mrp,
            seller_name=seller_name,
            seller_rating=seller_rating,
            description=description,
            highlights=highlights,
            image_links=image_links
        )

        # Return a success response with the product ID and image URL (if image exists)
        return JsonResponse(
            {
                "message": "Product added successfully",
                "productId": product.id,
                "image_links": product.image_links,
            },
            status=201,
        )

    # If the request method is not POST, return an error
    return JsonResponse({"error": "Invalid request"}, status=400)