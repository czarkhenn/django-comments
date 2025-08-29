# Django Comments API

A Django REST Framework API backend for a blogging/comments system with Docker, PostgreSQL, and comprehensive testing using pytest. 

## Features

- **Django 5.2.5** with Django REST Framework 3.16.1
- **PostgreSQL** database with Docker
- **Docker & Docker Compose** for containerization
- **Environment variables** support with `.env` files
- **Comprehensive Makefile** for common tasks
- **pytest** with comprehensive API and model test coverage
- **REST API** with filtering, pagination, and authentication
- **Blogging system** with Author, Post, and Comment models

## Requirements

### System Requirements
- Docker and Docker Compose


## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/czarkhenn/django-comments.git
   cd django-comments
   ```

2. **Start the application**
   ```bash
   make start
   ```
   This will:
   - Copy `.env.example` to `.env`
   - Build Docker images
   - Start PostgreSQL and Django containers
   - Make the application available at http://localhost:8000

3. **Run initial migrations**
   ```bash
   make migrate
   ```

4. **Create a superuser**
   ```bash
   make superuser
   ```

## Makefile Commands

The project includes a comprehensive Makefile for common development tasks:

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make start` | Start the application with hot reload |
| `make stop` | Stop all containers |
| `make build` | Build Docker images |
| `make test` | Run test suite with pytest |
| `make restart` | Restart the application |
| `make makemigrations` | Create database migrations |
| `make migrate` | Apply database migrations |
| `make superuser` | Create Django superuser |
| `make shell` | Open Django shell |
| `make logs` | Show application logs |
| `make clean` | Clean up containers and volumes |

**Note:** All commands use `docker exec` to run inside the `django-comments-backend-1` container.


## Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
POSTGRES_DB=base_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Additional settings can be added as needed
```

## How to Run the App

### Using Docker (Recommended)

1. **Start the application:**
   ```bash
   make start
   ```

2. **Apply migrations:**
   ```bash
   make migrate
   ```

3. **Create a superuser (optional):**
   ```bash
   make superuser
   ```

4. **Access the application:**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

### Manual Setup (Alternative)

If you prefer to run without Docker:

1. **Install dependencies:**
   ```bash
   pip install -r requirements/local.txt
   ```

2. **Set up PostgreSQL database and update settings**

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

This is an API-only backend. All endpoints are under the `/api/` prefix.

### Base URL
```
http://localhost:8000/api/
```

### Authentication
- **Session Authentication**: For web-based clients
- **Basic Authentication**: For API clients
- **Mixed Authentication**: 
  - **Public Access**: Post listing and detail views (anonymous users can read posts)
  - **Authentication Required**: Post creation, editing, deletion (authenticated users only)
  - **Anonymous Comments**: Both authenticated and anonymous users can create comments

### Post Endpoints

#### 1. List All Posts
**GET** `/api/posts/`

Lists all active posts with pagination. **No authentication required.**

**Query Parameters:**
- `title` - Filter by title (case-insensitive partial match)
- `author_name` - Filter by author name (case-insensitive partial match)
- `published_date` - Filter by exact published date (YYYY-MM-DD format)
- `published_date_from` - Filter posts from date onwards (YYYY-MM-DD format)
- `published_date_to` - Filter posts up to date (YYYY-MM-DD format)
- `search` - Search across title and author name (partial match)
- `ordering` - Order by fields: `published_date`, `title`, `-published_date`, `-title`

**Response Fields:**
- `id` - Post ID
- `title` - Post title
- `content` - Post content
- `published_date` - Publication date
- `author_name` - Author's name
- `active` - Whether post is active

**Example:**
```bash
# Get all posts (no authentication required)
curl http://localhost:8000/api/posts/

# Filter by title
curl http://localhost:8000/api/posts/?title=django

# Filter by date range
curl http://localhost:8000/api/posts/?published_date_from=2024-01-01&published_date_to=2024-12-31

# Search and order
curl http://localhost:8000/api/posts/?search=tutorial&ordering=-published_date
```

#### 2. Post Detail
**GET** `/api/posts/{id}/`

Shows details of a specific post including nested comments. **No authentication required.**

**Response includes all post fields plus:**
- `comments` - Array of comments with `id`, `content`, `user`, `created`
- `author` - Full author object with nested user information
- `status` - Post status (draft/published)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Example:**
```bash
curl http://localhost:8000/api/posts/1/
```

#### 3. Create Post
**POST** `/api/posts/create/`

Creates a new post. **Requires authentication.**

**Required Fields:**
- `title` - Post title
- `content` - Post content
- `status` - Post status (`draft` or `published`)

**Example:**
```bash
curl -X POST http://localhost:8000/api/posts/create/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{
    "title": "My New Post",
    "content": "This is the content of my post.",
    "status": "published"
  }'
```

#### 4. Update Post
**PUT** `/api/posts/{id}/update/`

Updates an existing post. **Only the post owner can update.**

**Editable Fields:**
- `title` - Post title
- `content` - Post content
- `active` - Post active status

**Example:**
```bash
curl -X PUT http://localhost:8000/api/posts/1/update/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{
    "title": "Updated Title",
    "content": "Updated content.",
    "active": true
  }'
```

#### 5. Delete Post
**DELETE** `/api/posts/{id}/delete/`

Deletes a post. **Only the post owner can delete.**

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/posts/1/delete/ \
  -u username:password
```

### Comment Endpoints

#### 1. Create Comment
**POST** `/api/posts/comments/create/`

Creates a comment on a post. **Both authenticated and anonymous users can comment.**

**Required Fields:**
- `post` - Post ID to comment on
- `content` - Comment content

**Validation:**
- Comments can only be created on active posts

**Authentication:**
- **Authenticated users**: Comments will be associated with the user account
- **Anonymous users**: Comments will be created with `user=None`

**Examples:**

**Authenticated Comment:**
```bash
curl -X POST http://localhost:8000/api/posts/comments/create/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{
    "post": 1,
    "content": "Great post from authenticated user!"
  }'
```

**Anonymous Comment:**
```bash
curl -X POST http://localhost:8000/api/posts/comments/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "post": 1,
    "content": "Great post from anonymous user!"
  }'
```

### Error Responses

The API returns standard HTTP status codes:

- `200 OK` - Successful GET/PUT requests
- `201 Created` - Successful POST requests
- `204 No Content` - Successful DELETE requests
- `400 Bad Request` - Invalid data or validation errors
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found

**Error Response Format:**
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```


## Test Coverage

The project includes comprehensive test coverage using **pytest** with Django integration.

### Test Structure

**Test Files:**
- `posts/tests/test_api.py` - API endpoint tests (31 test methods)
- `posts/tests/test_models.py` - Model tests
- `conftest.py` - Shared test fixtures
- `pytest.ini` - Test configuration

### Test Configuration

**pytest.ini Configuration:**
- Django settings module: `base.settings`
- Test discovery patterns: `tests.py`, `test_*.py`, `*_tests.py`
- Options: `--reuse-db`, `--nomigrations`, `--disable-warnings`
- Custom markers: `slow`, `integration`, `unit`

### API Test Coverage

**Post API Tests (`TestPostListAPI`):**
- ✅ List shows only active posts (public access)
- ✅ Filtering by title, author name, published date range
- ✅ Search functionality across title and author name
- ✅ Combined filters and ordering
- ✅ Pagination support

**Post Detail Tests (`TestPostDetailAPI`):**
- ✅ Post detail with nested comments
- ✅ Full author object with nested user information
- ✅ Inactive posts return 404
- ✅ Proper handling of authors with/without users

**Post CRUD Tests:**
- ✅ Post creation by authenticated authors (`TestPostCreateAPI`)
- ✅ Post editing by owners only (`TestPostUpdateAPI`)
- ✅ Post deletion by owners only (`TestPostDeleteAPI`)
- ✅ Permission validation for all operations

**Comment Tests (`TestCommentCreateAPI`):**
- ✅ Comment creation by authenticated users
- ✅ Comment creation by anonymous users (user=None)
- ✅ Anonymous comment creation on posts succeeds
- ✅ Validation: comments only on active posts
- ✅ Proper user association

### Model Test Coverage

**Model Tests (`test_models.py`):**
- Model creation and validation
- Field constraints and relationships
- Model methods and properties
- Database cascade behaviors
- Admin functionality
- Query optimizations

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
docker exec django-comments-backend-1 pytest posts/tests/test_api.py -v

# Run specific test class
docker exec django-comments-backend-1 pytest posts/tests/test_api.py::TestPostListAPI -v

# Run with coverage
docker exec django-comments-backend-1 pytest --cov=posts --cov-report=html

# Run tests with markers
docker exec django-comments-backend-1 pytest -m "not slow"
```

### Test Fixtures

**Shared Fixtures (conftest.py):**
- `api_client` - DRF API client
- `user`, `author_user`, `another_user` - User instances
- `author` - Author instance
- `active_post`, `inactive_post` - Post instances
- `comment_on_active_post`, `anonymous_comment` - Comment instances

**Factory Support:**
- Uses `factory-boy` for creating test data
- Consistent test data generation
- Database isolation for each test

## Docker Services

The application runs using Docker Compose with the following services:

### Services Configuration

**backend** (Django Application):
- **Image**: Built from local Dockerfile
- **Port**: 8000 (mapped to host)
- **Command**: `python manage.py runserver 0.0.0.0:8000`
- **Volumes**: Hot reload support with local code mounting
- **Environment**: Loads from `.env` file
- **Dependencies**: Waits for database health check

**db** (PostgreSQL Database):
- **Image**: `postgres:15`
- **Port**: 5432 (mapped to host)
- **Environment**: Configurable via environment variables
- **Health Check**: `pg_isready` command
- **Volume**: Persistent data storage

### Container Names
- Backend: `django-comments-backend-1`
- Database: `django-comments-db-1`


### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs db

# Follow logs in real-time
make logs

# Access Django shell
make shell

# Access container bash
docker exec -it django-comments-backend-1 bash
```

## License

This project is licensed under the MIT License.
