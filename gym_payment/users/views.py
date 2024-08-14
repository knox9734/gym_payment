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

def user_list(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(code__icontains=query) | Q(phone_number__icontains=query))
    else:
        users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users, 'query': query})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return HttpResponseRedirect(reverse('user_list'))

def add_payment(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        user = get_object_or_404(User, code=code)
        Payment.objects.create(user=user)
        return redirect('payment_list')
    else:
        return render(request, 'users/add_payment.html')

def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'users/payment_list.html', {'payments': payments})