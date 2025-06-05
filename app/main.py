from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import users, books, reviews, recommendations, orders
from app.database import engine, Base
from app.core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Iqraa Library Management System",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(books.router, prefix=f"{settings.API_V1_STR}/books", tags=["books"])
app.include_router(reviews.router, prefix=f"{settings.API_V1_STR}/reviews", tags=["reviews"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["recommendations"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["orders"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Iqraa API"} 