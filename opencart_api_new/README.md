# OpenCart REST API

A FastAPI-based REST API for the OpenCart e-commerce platform.

## Features

- RESTful API for OpenCart database
- Product, Category, Customer, and Order management (CRUD operations)
- Automatic API documentation with Swagger UI
- User activity and enhanced tracking middleware
- Modular structure with Pydantic schemas and SQLAlchemy models

## Requirements

- Python 3.8+
- MySQL/MariaDB (existing OpenCart database)

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd opencart_api_new
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    Copy `.env` to your project root and update the values as needed:
    ```
    MYSQL_USER=your_user
    MYSQL_PASSWORD=your_password
    MYSQL_SERVER=your_server
    MYSQL_PORT=3306
    MYSQL_DB=your_db
    SECRET_KEY=your_secret_key
    ```

4. Run the API server:
    ```bash
    uvicorn app.main:app --reload
    ```

## Project Structure

```
opencart_api_new/
│   .env
│   README.md
│   requirements.txt
│   notes.txt
│
└───app/
    │   config.py
    │   database.py
    │   main.py
    │   utils.py
    │
    ├───middleware/
    │       enhanced_tracking.py
    │       tracking.py
    │
    ├───models/
    │       address.py
    │       analytics.py
    │       cart.py
    │       category.py
    │       ...
    │
    ├───routes/
    │       ...
    │
    ├───schemas/
    │       address.py
    │       category.py
    │       ...
    │
    └───utils/
            ...
```

## Usage

- Access the API documentation at: `http://localhost:8000/docs`
- The root endpoint `/` returns a welcome message and API version.

## Notes

- See [notes.txt](opencart_api_new/notes.txt) for additional setup instructions.
- Database models and schemas are located in the `app/models/` and `app/schemas/` directories.
- Middleware for enhanced tracking is in `app/middleware/enhanced_tracking.py`.

## License

MIT License