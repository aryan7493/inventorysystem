services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-inventory_db}
      POSTGRES_USER: ${POSTGRES_USER:-inventory}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change-me}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-inventory} -d ${POSTGRES_DB:-inventory_db}"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build:
      context: ./backend
    environment:
      DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg://inventory:change-me@db:5432/inventory_db}
      BACKEND_CORS_ORIGINS: ${BACKEND_CORS_ORIGINS:-http://localhost:8080,http://127.0.0.1:8080,http://localhost:5173,http://127.0.0.1:5173}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://localhost:8000}
    ports:
      - "8080:80"
    depends_on:
      - backend

volumes:
  postgres_data:
