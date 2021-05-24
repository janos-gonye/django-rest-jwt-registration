import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-rest-jwt-registration',
    author='János Gönye',
    author_email='janos.gonye@gmail.com',
    version='0.1.0',
    description='Django app for registration password reset, email - and password change with jwt tokens and email sending',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/janos-gonye/django-rest-jwt-registration',
    license='MIT',
    packages=['drjr'],
    classifiers=[
        'Development Status :: 3 - Alfa',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires=">=3.6",
    setup_requires = [
        'setuptools >= 38.3.0',
    ],
    install_requires=[
        'Django',
        'djangorestframework',
        'pyjwt',
    ],
)
