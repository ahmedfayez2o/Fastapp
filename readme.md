# Iqraa - Book Management System Backend

## Project Overview
Iqraa is a comprehensive book management system built with Django REST Framework and PostgreSQL. The system provides features for managing books, user accounts, orders (borrowing/purchasing), reviews, and personalized book recommendations.

## Technology Stack
- **Framework**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Additional Features**: 
  - Sentiment Analysis for book reviews
  - Machine Learning-based book recommendations
  - CORS support for frontend integration
  - Docker containerization

## Project Structure
```
iqraa/
├── books/             # Book management
├── users/             # User authentication and profiles
├── orders/            # Book borrowing and purchasing
├── reviews/           # Book reviews and ratings
├── recommendations/   # ML-based book recommendations
└── iqraa/            # Project settings
```

## Features
1. **User Management**
   - User registration and authentication
   - Profile management
   - JWT-based authentication

2. **Book Management**
   - Book catalog with detailed information
   - Search and filter capabilities
   - Genre-based categorization

3. **Order System**
   - Book borrowing
   - Book purchasing
   - Order history tracking

4. **Review System**
   - Book ratings and reviews
   - Sentiment analysis of reviews
   - Recent and top-rated reviews

5. **Recommendation System**
   - Personalized book recommendations
   - Machine learning-based suggestions
   - Top-rated books recommendations

## API Endpoints

### Users API
- `GET/POST /api/users/` - List/Create users
- `GET/PUT/DELETE /api/users/{id}/` - Manage specific user
- `GET /api/users/me/` - Current user profile
- `POST /api/users/{id}/change_password/` - Change password

### Books API
- `GET/POST /api/books/` - List/Create books
- `GET/PUT/DELETE /api/books/{id}/` - Manage specific book
- `GET /api/books/genres/` - List book genres

### Orders API
- `GET/POST /api/orders/` - List/Create orders
- `GET/PUT/DELETE /api/orders/{id}/` - Manage specific order
- `POST /api/orders/{id}/borrow/` - Borrow book
- `POST /api/orders/{id}/purchase/` - Purchase book
- `POST /api/orders/{id}/return_book/` - Return book
- `GET /api/orders/borrowed/` - List borrowed books
- `GET /api/orders/purchased/` - List purchased books

### Reviews API
- `GET/POST /api/reviews/` - List/Create reviews
- `GET/PUT/DELETE /api/reviews/{id}/` - Manage specific review
- `GET /api/reviews/my_reviews/` - User's reviews
- `GET /api/reviews/recent/` - Recent reviews
- `GET /api/reviews/top_rated/` - Top-rated reviews
- `GET /api/reviews/{id}/sentiment/` - Review sentiment
- `GET /api/reviews/book_sentiments/` - Book review sentiments

### Recommendations API
- `GET /api/recommendations/` - List recommendations
- `POST /api/recommendations/generate/` - Generate recommendations
- `GET /api/recommendations/top_rated_books/` - Top-rated books

## Setup Instructions

1. **Using Docker (Recommended)**
   ```bash
   # Build and start the containers
   docker-compose up --build

   # The application will be available at http://localhost:8000
   ```

2. **Manual Setup (Alternative)**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   The following environment variables are configured in docker-compose.yml:
   ```
   DATABASE_URL=postgresql://postgres:postgres@db:5432/iqraa_db
   DJANGO_SETTINGS_MODULE=iqraa.settings
   ```

4. **Database Setup**
   - When using Docker, PostgreSQL is automatically configured
   - For manual setup, configure PostgreSQL according to the settings in docker-compose.yml

5. **Run Development Server (for manual setup)**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Dependencies
See `requirements.txt` for complete list:
- Django
- Django REST Framework
- psycopg2-binary
- django-cors-headers
- scikit-learn (for ML features)
- nltk (for sentiment analysis)
- And more...

## Security Features
- JWT Authentication
- Secure password handling
- CORS configuration
- SSL/TLS support in production
- XSS and CSRF protection

## API Documentation
For detailed API documentation, you can use Django REST Framework's built-in documentation interface at:
`http://localhost:8000/api/`

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
This project is licensed under the FCDS License.

# this is final gradution project backend #
all the steps to make this up will be in the this file

## Prerequisites

*   Python (version 3.8 or higher recommended)
*   pip (Python package manager)
*   Docker and Docker Compose (for running the PostgreSQL database)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repo-url> iqraa
    cd iqraa
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On Linux/Mac:
    # source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    Create a `.env` file in the project root (if it doesn't exist) and add the following (adjust values as needed):

    ```
    DJANGO_SECRET_KEY=your-secret-key-here
    DEBUG=True
    # Add other environment variables if required (e.g., database credentials if not using Docker)
    ```

5.  **Run Database Migrations:**

    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (optional, for admin access):**

    ```bash
    python manage.py createsuperuser
    ```

## Running the Development Server

```bash
python manage.py runserver
```

The development server will usually be available at `http://127.0.0.1:8000/`.

## Running the Database with Docker

This project uses Docker Compose to run a PostgreSQL database container.

1.  **Navigate to the `database` directory:**

    ```bash
    cd database
    ```

2.  **Start the PostgreSQL container:**

    ```bash
    docker-compose up -d
    ```

    This command builds (if necessary) and starts the `postgres` service defined in `database/docker-compose.yml` in detached mode (`-d`). It will create a container named `iqraa_db`.

3.  **Verify the container is running:**

    ```bash
    docker ps | grep iqraa_db
    ```

    You should see output indicating that the `iqraa_db` container is running and healthy.

4.  **Accessing the Database:**

    The PostgreSQL database is accessible from your Django application using the following settings (already configured in `iqraa/settings.py`):

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'iqraa_db',
            'USER': 'iqraa_user',
            'PASSWORD': 'iqraa_password',
            'HOST': '127.0.0.1', # Or 'localhost'
            'PORT': '5432',
        }
    }
    ```

    You can also connect to the database directly using a PostgreSQL client (like `psql`) using the credentials defined in the `docker-compose.yml` file (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`) and the host/port.

5.  **Stopping the Database Container:**

    To stop the running container, run the following command from the `database` directory:

    ```bash
    docker-compose down
    ```

    This will stop and remove the `iqraa_db` container. The data volume (`postgres_data`) will persist unless you explicitly remove it (e.g., using `docker volume rm iqraa_postgres_data`).

## Additional Notes

*   **Custom Book Form:** A custom HTML form for adding/editing books is available at `http://127.0.0.1:8000/books/add/` and `http://127.0.0.1:8000/books/<book_id>/edit/`.
*   **Django Admin:** The standard Django admin interface is available at `http://127.0.0.1:8000/admin/`.
*   **API Endpoints:** API endpoints are generally available under the `/api/` prefix (e.g., `/api/books/`).
