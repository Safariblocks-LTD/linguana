from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import os


def verify_firebase_token(token):
    if not settings.FIREBASE_ENABLED:
        raise ValueError("Firebase authentication is not enabled")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, auth
        
        if not firebase_admin._apps:
            if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
        
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except ImportError:
        raise ValueError("Firebase Admin SDK not installed. Install with: pip install firebase-admin")
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {str(e)}")


def send_magic_link_email(email, token):
    magic_link = f"{settings.CORS_ALLOWED_ORIGINS[0]}/auth/magic-link?token={token}"
    
    subject = "Your Linguana Magic Link"
    message = f"Click the link below to sign in to Linguana:\n\n{magic_link}\n\nThis link will expire in 15 minutes."
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #40C4C4; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">Linguana</h1>
            </div>
            <div style="padding: 30px; background-color: #f9f9f9;">
                <h2>Sign in to Linguana</h2>
                <p>Click the button below to sign in to your account:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{magic_link}" 
                       style="background-color: #40C4C4; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Sign In
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 15 minutes. If you didn't request this, please ignore this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@linguana.com',
            [email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send magic link email: {str(e)}")
        raise


def award_badge(user, badge_type):
    from .models import Badge, UserBadge
    
    try:
        badge = Badge.objects.get(badge_type=badge_type)
        user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
        
        if created:
            user.add_points(badge.points_reward)
            return True
    except Badge.DoesNotExist:
        pass
    
    return False


def check_and_award_badges(user):
    if user.total_contributions == 1:
        award_badge(user, 'first_contribution')
    
    if user.total_contributions >= 100:
        award_badge(user, 'contributor_100')
    
    if user.total_validations >= 100:
        award_badge(user, 'validator_100')
    
    if user.streak_days >= 7:
        award_badge(user, 'streak_7')
    
    if user.streak_days >= 30:
        award_badge(user, 'streak_30')
    
    if user.total_earnings_usdc >= 10:
        award_badge(user, 'earnings_10')
    
    if user.total_earnings_usdc >= 100:
        award_badge(user, 'earnings_100')
