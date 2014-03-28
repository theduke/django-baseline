import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-baseline',
    version = '0.2.0',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'Django >= 1.6',
        # Form helper.
        'django-crispy-forms >= 1.4',
        # Needed for address field.
        'django-countries >= 2.0',
    ],
    license = 'BSD License',
    description = 'Convenienve functionality for Django projects.',
    long_description = README,
    url = 'https://github.com/theduke/django-baseline',
    author = 'Christoph Herzog',
    author_email = 'chris@theduke.at',
    classifiers =[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ]
)
