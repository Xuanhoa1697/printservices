from setuptools import setup

setup(
    name="print_service",
    version="1.0.0",
    packages=["app"],
    include_package_data=True,
    install_requires=[
        "flask",
        "python-escpos",
        "Pillow"
    ],
    entry_points={
        'console_scripts': [
            'print_service=app.main:main',
        ],
    },
)