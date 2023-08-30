from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='celery-smartbase',
    version='0.3.5',
    packages=find_packages(),
    install_requires=[
        'Django~=3.2.11',
        'djangorestframework==3.13.1',
        'django-model-utils==3.1.2',
        'django-celery-results==2.4.0',
        'django-celery-beat==2.2.1',
        'kombu~=5.2.3',
        'celery~=5.2.3',
    ],
    description='An extension and improvement of the Celery package to avoid duplicate tasks and view pending tasks in Django.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/TonySchneider/celery-smartbase',
)
