from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from chatbot.models import ChatbotMessage

def contact_support(request):
    """Contact support page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if not all([name, email, subject, message]):
            messages.error(request, 'All fields are required.')
            return render(request, 'client/contact_support.html')
        
        try:
            # Save to database
            ChatbotMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            # Send email to support
            send_mail(
                f'Support Request: {subject}',
                f'From: {name} ({email})\n\nSubject: {subject}\n\nMessage:\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent successfully! We will get back to you shortly.')
            return redirect('accounts:contact_support')
            
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
    
    return render(request, 'client/contact_support.html')
