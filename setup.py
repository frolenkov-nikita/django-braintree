#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test


setup(
    name='django-braintree',
    version='0.1',
    author='Sumit Chachra',
    author_email='chachra@tivix.com',
    url='http://github.com/tivix/django-braintree',
    description = 'An easy way to integrate with Braintree Payment Solutions from Django.',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django>=1.2.3',
        'South==0.7.2',
        'braintree>=2.10.0',
        'django_common==0.1'
    ],
    dependency_links=["git://github.com/Tivix/django-common.git@91e23cd5e0e8b420e8d4#egg=django_common-0.1"],
    # test_suite = 'django_braintree.tests',
    include_package_data=True,
    # cmdclass={},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
