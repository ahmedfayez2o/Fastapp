# Iqraa - Library Management System Backend

## Project Overview
Iqraa is a comprehensive library management system built with FastAPI and PostgreSQL. The system provides features for managing books, user accounts, orders (borrowing/purchasing), reviews, and personalized book recommendations using machine learning.

## Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Additional Features**: 
  - Sentiment Analysis for book reviews using Transformers
  - Machine Learning-based book recommendations using Implicit and scikit-learn
  - CORS support for frontend integration
  - Docker containerization support

## Project Structure
```
iqraa/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality (config, auth, etc.)
│   ├── crud/           # Database operations
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic models
│   └── services/       # Business logic and ML services
├── alembic/            # Database migrations
├── tests/              # Test files
└── requirements.txt    # Project dependencies
```

## Features
1. **User Management**
   - User registration and authentication
   - Profile management
   - JWT-based authentication with refresh tokens

2. **Book Management**
   - Book catalog with detailed information
   - Search and filter capabilities
   - Category-based organization
   - Stock management

3. **Order System**
   - Book borrowing with due dates
   - Book purchasing
   - Order history tracking
   - Transaction management

4. **Review System**
   - Book ratings and reviews
   - Sentiment analysis using RoBERTa model
   - Review statistics and analytics

5. **Recommendation System**
   - Hybrid recommendation engine (content-based + collaborative filtering)
   - Personalized book recommendations
   - Trending books
   - Similar books suggestions

## API Endpoints

### Users API
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - User login
- `GET /api/v1/users/me` - Current user profile
- `PUT /api/v1/users/me` - Update user profile
- `POST /api/v1/users/refresh-token` - Refresh JWT token

### Books API
- `GET /api/v1/books/` - List books with filtering
- `POST /api/v1/books/` - Create new book
- `GET /api/v1/books/{book_id}` - Get book details
- `PUT /api/v1/books/{book_id}` - Update book
- `DELETE /api/v1/books/{book_id}` - Delete book
- `GET /api/v1/books/categories/` - List book categories

### Orders API
- `GET /api/v1/orders/` - List orders
- `POST /api/v1/orders/borrow` - Borrow a book
- `POST /api/v1/orders/purchase` - Purchase a book
- `POST /api/v1/orders/{order_id}/return` - Return a book
- `GET /api/v1/orders/statistics` - Get order statistics

### Reviews API
- `GET /api/v1/reviews/` - List reviews
- `POST /api/v1/reviews/` - Create review
- `GET /api/v1/reviews/{review_id}` - Get review details
- `GET /api/v1/reviews/sentiment-analysis` - Get review sentiment statistics

### Recommendations API
- `GET /api/v1/recommendations/personalized` - Get personalized recommendations
- `GET /api/v1/recommendations/trending` - Get trending books
- `GET /api/v1/recommendations/similar/{book_id}` - Get similar books

## Setup Instructions

1. **Prerequisites**
   - Python 3.8 or higher
   - PostgreSQL 12 or higher
   - pip (Python package manager)
   - Docker and Docker Compose (optional)

2. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the project root with:
   ```
   # Database
   POSTGRES_DB=iqraa_db
   POSTGRES_USER=iqraa_user
   POSTGRES_PASSWORD=iqraa_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   
   # Security
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # API
   DEBUG=False
   API_V1_STR=/api/v1
   ```

4. **Database Setup**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

5. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation
FastAPI provides automatic API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Dependencies
Key dependencies (see `requirements.txt` for complete list):
- FastAPI and Uvicorn for the web framework
- SQLAlchemy and Alembic for database ORM and migrations
- Pydantic for data validation
- Python-jose and Passlib for authentication
- Transformers and PyTorch for sentiment analysis
- Implicit and scikit-learn for recommendations
- pytest and httpx for testing

## Development
1. **Code Style**
   - Black for code formatting
   - isort for import sorting
   - flake8 for linting

2. **Running Tests**
   ```bash
   pytest
   ```

3. **Database Migrations**
   ```bash
   # Create new migration
   alembic revision --autogenerate -m "description"
   
   # Apply migrations
   alembic upgrade head
   ```

## Security Features
- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- CORS middleware configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- Rate limiting (can be implemented as needed)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the FCDS License.

## Support
For support, please open an issue in the repository or contact the development team.
