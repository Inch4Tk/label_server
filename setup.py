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
        "marshmallow-sqlalchemy",
        "tensorflow"
    ],
)