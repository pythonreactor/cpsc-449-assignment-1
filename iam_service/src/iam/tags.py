from flask_openapi3 import Tag

superuser_tag = Tag(name='superuser', description='Superuser Endpoints')
iam_tag = Tag(name='iam', description='Identity and Access Management')
external_tag = Tag(name='external', description='Incoming API calls')
