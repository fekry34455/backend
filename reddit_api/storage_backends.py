"""
Custom storage backends for AWS S3
"""
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Storage backend for static files"""
    location = 'static'
    default_acl = None
    querystring_auth = False


class MediaStorage(S3Boto3Storage):
    """Storage backend for media files (user uploads)"""
    location = 'media'
    default_acl = None
    querystring_auth = False
    file_overwrite = False
