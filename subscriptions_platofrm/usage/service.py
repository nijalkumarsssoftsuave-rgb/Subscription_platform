from .models import APIUsage


def log_usage(user, endpoint, status_code, ip):

    APIUsage.objects.create(

        user=user,
        endpoint=endpoint,
        status_code=status_code,
        ip_address=ip
    )