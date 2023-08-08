# calorie_calculator/setup.py
from setuptools import setup, find_packages

setup(
    name='calorie_calculator',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here if any
    ],
    entry_points={
        'console_scripts': [
            'calculate_calories = calorie_calculator.daily_calorie:main',
        ],
    },
)
