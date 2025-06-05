from setuptools import setup, find_packages

setup(
    name="iqraa",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.68.1",
        "uvicorn==0.15.0",
        "sqlalchemy==1.4.23",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.5",
        "pandas==1.3.3",
        "numpy==1.21.2",
        "scikit-learn==0.24.2",
        "scikit-surprise==1.1.1",
    ],
    extras_require={
        "dev": [
            "pytest==6.2.5",
            "pytest-cov==2.12.1",
            "httpx==0.19.0",
        ],
        "postgres": [
            "psycopg2-binary==2.9.1",
        ],
    },
) 