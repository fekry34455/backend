"""
Health check and utility views for Kubernetes
"""
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError


def readiness_check(request):
    """
    Readiness probe for Kubernetes
    Checks database connection - returns 200 if ready to serve traffic
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({
            "status": "ready",
            "database": "connected"
        }, status=200)
    except OperationalError:
        return JsonResponse({
            "status": "not_ready",
            "database": "disconnected"
        }, status=503)


def liveness_check(request):
    """
    Liveness check endpoint for Kubernetes
    Returns 200 OK if the application is running
    """
    return JsonResponse({
        "status": "alive",
        "service": "reddit-api"
    }, status=200)
