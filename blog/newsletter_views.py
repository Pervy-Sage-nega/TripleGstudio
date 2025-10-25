"""
Newsletter subscription views for the Triple G Blog System
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .newsletter import NewsletterSubscriber, NewsletterCampaign, NewsletterAnalytics
from .models import BlogPost
import json


def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            email = data.get('email', '').strip().lower()
            name = data.get('name', '').strip()
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email address is required.'
                })
            
            # Check if already subscribed
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'is_active': True,
                    'is_confirmed': False
                }
            )
            
            if not created:
                if subscriber.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'You are already subscribed to our newsletter.'
                    })
                else:
                    # Reactivate subscription
                    subscriber.is_active = True
                    subscriber.unsubscribed_date = None
                    subscriber.save()
            
            # Send confirmation email
            send_confirmation_email(subscriber, request)
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for subscribing! Please check your email to confirm your subscription.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again later.'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def newsletter_confirm(request, token):
    """Confirm newsletter subscription"""
    try:
        subscriber = get_object_or_404(NewsletterSubscriber, confirmation_token=token)
        
        if subscriber.is_confirmed:
            messages.info(request, 'Your subscription is already confirmed.')
        else:
            subscriber.confirm_subscription()
            send_welcome_email(subscriber, request)
            messages.success(request, 'Thank you! Your newsletter subscription has been confirmed.')
        
        return redirect('blog:blog_list')
        
    except Exception as e:
        messages.error(request, 'Invalid confirmation link.')
        return redirect('blog:blog_list')


def newsletter_unsubscribe(request, token):
    """Unsubscribe from newsletter"""
    try:
        subscriber = get_object_or_404(NewsletterSubscriber, confirmation_token=token)
        
        if request.method == 'POST':
            subscriber.unsubscribe()
            messages.success(request, 'You have been successfully unsubscribed from our newsletter.')
            return redirect('blog:blog_list')
        
        return render(request, 'blog/newsletter_unsubscribe.html', {
            'subscriber': subscriber
        })
        
    except Exception as e:
        messages.error(request, 'Invalid unsubscribe link.')
        return redirect('blog:blog_list')


@csrf_exempt
def newsletter_track_open(request, campaign_id, subscriber_id):
    """Track email opens"""
    try:
        campaign = get_object_or_404(NewsletterCampaign, id=campaign_id)
        subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
        
        # Record analytics
        NewsletterAnalytics.objects.create(
            subscriber=subscriber,
            campaign=campaign,
            action_type='open',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update counters
        campaign.total_opened += 1
        campaign.save()
        
        subscriber.open_count += 1
        subscriber.last_opened = timezone.now()
        subscriber.save()
        
        # Return 1x1 transparent pixel
        response = HttpResponse(
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3B',
            content_type='image/gif'
        )
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
        
    except Exception as e:
        # Return empty response even on error
        return HttpResponse(status=204)


def newsletter_track_click(request, campaign_id, subscriber_id):
    """Track link clicks"""
    try:
        campaign = get_object_or_404(NewsletterCampaign, id=campaign_id)
        subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
        redirect_url = request.GET.get('url', '/')
        
        # Record analytics
        NewsletterAnalytics.objects.create(
            subscriber=subscriber,
            campaign=campaign,
            action_type='click',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update counters
        campaign.total_clicked += 1
        campaign.save()
        
        subscriber.click_count += 1
        subscriber.save()
        
        return redirect(redirect_url)
        
    except Exception as e:
        return redirect('/')


def send_confirmation_email(subscriber, request):
    """Send confirmation email to subscriber"""
    try:
        confirmation_url = request.build_absolute_uri(
            f'/blog/newsletter/confirm/{subscriber.confirmation_token}/'
        )
        
        context = {
            'subscriber': subscriber,
            'confirmation_url': confirmation_url,
            'site_name': 'Triple G BuildHub'
        }
        
        html_message = render_to_string('blog/emails/newsletter_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Confirm your newsletter subscription - Triple G BuildHub',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=False,
        )
        
    except Exception as e:
        print(f"Error sending confirmation email: {e}")


def send_welcome_email(subscriber, request):
    """Send welcome email after confirmation"""
    try:
        unsubscribe_url = request.build_absolute_uri(
            f'/blog/newsletter/unsubscribe/{subscriber.confirmation_token}/'
        )
        blog_url = request.build_absolute_uri('/blog/')
        
        context = {
            'subscriber': subscriber,
            'unsubscribe_url': unsubscribe_url,
            'blog_url': blog_url,
            'site_name': 'Triple G BuildHub'
        }
        
        html_message = render_to_string('blog/emails/newsletter_welcome.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Welcome to Triple G BuildHub Newsletter!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=False,
        )
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")


def send_newsletter_campaign(campaign):
    """Send newsletter campaign to all active subscribers"""
    try:
        print(f"DEBUG NEWSLETTER: Starting campaign send for: {campaign.title}")
        # Get active, confirmed subscribers based on campaign type
        subscribers = NewsletterSubscriber.objects.filter(
            is_active=True,
            is_confirmed=True
        )
        print(f"DEBUG NEWSLETTER: Found {subscribers.count()} active confirmed subscribers")
        
        # Filter by preferences
        if campaign.campaign_type == 'weekly_digest':
            subscribers = subscribers.filter(weekly_digest=True)
        elif campaign.campaign_type == 'new_post':
            subscribers = subscribers.filter(new_posts=True)
        elif campaign.campaign_type == 'featured_post':
            subscribers = subscribers.filter(featured_posts=True)
        
        print(f"DEBUG NEWSLETTER: After filtering by type '{campaign.campaign_type}': {subscribers.count()} subscribers")
        
        sent_count = 0
        
        for subscriber in subscribers:
            try:
                # Build absolute URLs using settings
                from django.conf import settings
                site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                
                # Generate tracking URLs
                open_tracking_url = f'{site_url}/blog/newsletter/track/open/{campaign.id}/{subscriber.id}/'
                click_tracking_url = f'{site_url}/blog/newsletter/track/click/{campaign.id}/{subscriber.id}/'
                unsubscribe_url = f'{site_url}/blog/newsletter/unsubscribe/{subscriber.confirmation_token}/'
                blog_post_url = f'{site_url}{campaign.blog_post.get_absolute_url()}' if campaign.blog_post else f'{site_url}/blog/'
                
                context = {
                    'subscriber': subscriber,
                    'campaign': campaign,
                    'open_tracking_url': open_tracking_url,
                    'click_tracking_url': click_tracking_url,
                    'unsubscribe_url': unsubscribe_url,
                    'blog_post_url': blog_post_url,
                    'site_url': site_url,
                    'site_name': 'Triple G BuildHub'
                }
                
                html_message = render_to_string('blog/emails/newsletter_template.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=campaign.subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                sent_count += 1
                print(f"DEBUG NEWSLETTER: Successfully sent to {subscriber.email}")
                
            except Exception as e:
                print(f"ERROR NEWSLETTER: Failed sending to {subscriber.email}: {e}")
                continue
        
        # Update campaign status
        campaign.status = 'sent'
        campaign.sent_date = timezone.now()
        campaign.total_sent = sent_count
        campaign.save()
        
        print(f"DEBUG NEWSLETTER: Campaign completed. Total sent: {sent_count}")
        return sent_count
        
    except Exception as e:
        print(f"Error sending campaign: {e}")
        return 0


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_new_post_campaign(blog_post):
    """Create a campaign for new blog post"""
    try:
        campaign = NewsletterCampaign.objects.create(
            title=f'New Post: {blog_post.title}',
            subject=f'New Article: {blog_post.title} - Triple G BuildHub',
            content=f'Check out our latest article: {blog_post.title}',
            campaign_type='new_post',
            blog_post=blog_post,
            status='draft'
        )
        
        return campaign
        
    except Exception as e:
        print(f"Error creating new post campaign: {e}")
        return None
