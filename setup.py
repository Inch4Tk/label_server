from setuptools import find_packages, setup

setup(
    name="flask_label",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask==1.0.2",
        "flask-script",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-marshmallow",
        "marshmallow==3.0.0b9",
        "marshmallow-sqlalchemy==0.13.0",
        'tensorflow==1.10.0',
        'tensorflow-serving-api',
    ],
)