from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .forms import UserRegistrationForm
from .models import User,Payment
from django.http import HttpResponseRedirect
from django.urls import reverse
import barcode
from barcode.writer import ImageWriter
from PIL import Image,ImageDraw, ImageFont
import os
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime
from datetime import timedelta
from django.http import Http404
import time as arduinoTime
import serial
from django.contrib.auth.decorators import login_required, user_passes_test

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)
def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)  
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone_number=form.cleaned_data['phone_number'],
                height=form.cleaned_data['height'],
                weight=form.cleaned_data['weight'],
                code=generate_user_code()
            )
            user.save()
            print(user.code)
            barcode_path = generate_barcode(user.code,user.first_name)
            print(barcode_path)
            return redirect('user_list')  # Replace 'success_url' with your success URL
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def generate_user_code():
    last_user = User.objects.order_by('id').last()
    if not last_user:
        return 'DF-0001'
    last_code = last_user.code
    last_number = int(last_code.split('-')[1])
    new_number = last_number + 1
    new_code = f'DF-{new_number:04d}'
    return new_code

def generate_barcode(code,firstname):
    if not os.path.exists('barcodes'):
        os.makedirs('barcodes')
    EAN = barcode.get_barcode_class('code128')
    if EAN is None:
        raise ValueError("Barcode class 'code128' not found.")
    ean = EAN(code, writer=ImageWriter())
    
    # Save the barcode to a temporary file in the 'barcodes' directory
    temp_file = os.path.join('barcodes', f'{code}')
    barcode_image_path = ean.save(temp_file)
    print(barcode_image_path)
    # If a firstname is provided, append it to the barcode image
    if firstname:
        # Load the barcode image
        barcode_image = Image.open(barcode_image_path)
        draw = ImageDraw.Draw(barcode_image)
        
        # Set font (you might need to specify the full path to a font file)
        try:
            font = ImageFont.truetype("arial.ttf", 20)  # You can adjust the font size as needed
        except IOError:
            font = ImageFont.load_default()  # Use default font if arial.ttf is not available

        # Calculate position to center the text
        text_bbox = draw.textbbox((0, 0), firstname, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_position = ((barcode_image.width - text_width) // 2, barcode_image.height - text_height - 10)
        
        # Add the text to the image
        draw.text(text_position, firstname, font=font, fill="black")
        
        # Save the modified image
        barcode_image.save(barcode_image_path)
    
    print(barcode_image_path)
    return barcode_image_path

@login_required
@user_passes_test(is_admin)
def user_list(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(code__icontains=query) | Q(phone_number__icontains=query))
    else:
        users = User.objects.all()
    
    paginator = Paginator(users, 15)  # Show 15 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/user_list.html', {'page_obj': page_obj, 'query': query})

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return HttpResponseRedirect(reverse('user_list'))

@login_required
@user_passes_test(is_admin)
def add_payment(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        user = get_object_or_404(User, code=code)
        payment = Payment.objects.filter(user=user).order_by('-expiration_date').first()
        if payment:
            payment.expiration_date = calculate_expiration_date()
            payment.payment_date = datetime.now().date()
            payment.save()
        else:
            Payment.objects.create(user=user)
        return redirect('payment_list')
    else:
        return render(request, 'users/add_payment.html')

def calculate_expiration_date():
    # Calculate the expiration date based on your logic
    # For example, you can add a fixed number of days to the current date
    expiration_date = datetime.now().date() + timedelta(days=30)
    return expiration_date

@login_required
@user_passes_test(is_admin)
def payment_list(request):
    # Get search query from GET parameters
    search_query = request.GET.get('search', '')

    # Filter payments based on search query
    if search_query:
        payments = Payment.objects.filter(Q(user__code__icontains=search_query))
    else:
        payments = Payment.objects.all()

    # Paginate the filtered payments
    paginator = Paginator(payments, 15)  # Show 15 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/payment_list.html', {'page_obj': page_obj, 'search_query': search_query})

def check_payment_status(request):
    if request.method == 'POST':
        code = request.POST.get('code')  # Use POST.get() for POST data
        user = None
        payment_status = None
        error_message = None
        remaining_days = None

        if code:
            try:
                user = get_object_or_404(User, code=code)
                payment = Payment.objects.filter(user=user).order_by('-expiration_date').first()
                if payment:
                    if payment.expiration_date < datetime.now().date():
                        payment_status = 'Expired'
                        door_open('0')
                        return render(request, 'users/payment_expired.html')
                    else:
                        remaining_days = (payment.expiration_date - datetime.now().date()).days
                        payment_status = 'Active'
                        door_open('1')
                        return render(request, 'users/welcome.html', {
                            'remaining_days': remaining_days,
                        })
                else:
                    payment_status = 'No payment details found'
                    
            except Http404:
                error_message = 'User not found'
        
        return render(request, 'users/user_error.html', {
            'user': user,
            'payment_status': payment_status,
            'code': code,
            'error_message': error_message,
            'remaining_days': remaining_days
        })
    
    # Handle GET requests by rendering the form
    return render(request, 'users/check_payment_status.html')

def write_read(x):
    
    arduino.write(bytes(x, 'utf-8'))
    arduinoTime.sleep(0.05)
    data = arduino.readline()
    return data

def blink_led():
    arduino.write(b'1')  # Sending '1' to the Arduino to trigger the LED blink
    arduinoTime.sleep(0.05)
    data = arduino.readline()
    return data

def door_open(value):
    blinking_done = False

    while not blinking_done:
        random_value = '2'  # Change this to any random value other than '1'
        response = write_read(random_value)
        arduinoTime.sleep(1)
        random_value = '2'  # Change this to any random value other than '1'
        response = write_read(random_value)
        arduinoTime.sleep(1)
        print("Sent random value:", random_value)

        num = value
        arduinoTime.sleep(1)
        if num == '1':
            response = blink_led()
            print("door opening:", response)
            blinking_done = True
        elif num == '0':
            response = write_read('0')
            print("not paid alarm:", response)
            blinking_done = True
        else:
            print("Invalid input. Only '1' or '0' triggers the LED action.")

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'users/login.html'  # Specify the path to your login template
    redirect_authenticated_user = True  # Redirect already authenticated users

def welcome(request):

    return render (request, 'users/home.html')