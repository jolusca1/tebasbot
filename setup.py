from setuptools import setup, find_packages

setup(
    name="tebasbot",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        'discord.py',
        'python-dotenv',
        'pymongo',
        'motor',
        'google-generativeai',
        'steam'
    ],
    python_requires='>=3.8'
)