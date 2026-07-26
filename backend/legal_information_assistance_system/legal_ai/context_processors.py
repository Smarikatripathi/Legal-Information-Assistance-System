"""Context processors for admin panel."""

from legal_information_assistance_system.legal_ai.models import AdminNotification


def notification_context(request):
    """Add notification context to templates."""
    if request.user.is_authenticated and request.user.is_staff:
        unread_count = AdminNotification.objects.filter(status="unread").count()
        high_priority_count = AdminNotification.objects.filter(
            status="unread", severity__in=["high", "critical"]
        ).count()
        recent_notifications = AdminNotification.objects.filter(
            status="unread"
        ).order_by("-created_at")[:5]
        
        return {
            "unread_notification_count": unread_count,
            "high_priority_notification_count": high_priority_count,
            "recent_notifications": recent_notifications,
        }
    return {
        "unread_notification_count": 0,
        "high_priority_notification_count": 0,
        "recent_notifications": [],
    }
