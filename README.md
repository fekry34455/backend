# Reddit Clone Django Backend API

Django REST API backend for Reddit Clone - replaces Firebase/Firestore with Django + PostgreSQL/SQLite3.

## Features

- ✅ Custom User model with JWT authentication
- ✅ Communities (create, join/leave, get details)
- ✅ Posts (create, delete, vote, list by community)
- ✅ Comments (create, delete, list by post)
- ✅ Post voting system (upvote/downvote)
- ✅ SQLite3 for development, easily migrates to RDS for production
- ✅ CORS enabled for Next.js frontend
- ✅ Django Admin panel for management

## Tech Stack

- Django 4.2.27
- Django REST Framework
- JWT Authentication (Simple JWT)
- SQLite3 (Development) / PostgreSQL (Production)
- Python 3.9+

## Setup

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend` directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### 4. Run Server

```bash
python manage.py runserver 8000
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/register/` | Register new user | No |
| POST | `/api/users/login/` | Login user | No |
| GET | `/api/users/profile/` | Get current user | Yes |
| POST | `/api/users/token/refresh/` | Refresh JWT token | No |

### Communities

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/communities/` | List all communities | No |
| POST | `/api/communities/` | Create community | Yes |
| GET | `/api/communities/<id>/` | Get community details | No |
| GET | `/api/communities/user/snippets/` | Get user's joined communities | Yes |
| POST | `/api/communities/<id>/join/` | Join community | Yes |
| POST | `/api/communities/<id>/leave/` | Leave community | Yes |

### Posts

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/posts/` | List posts (optional: ?community_id=x) | No |
| POST | `/api/posts/create/` | Create post | Yes |
| GET | `/api/posts/<id>/` | Get post details | No |
| DELETE | `/api/posts/<id>/` | Delete post | Yes (creator) |
| POST | `/api/posts/<id>/vote/` | Vote on post | Yes |
| GET | `/api/posts/votes/` | Get user votes (?community_id=x) | Yes |

### Comments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/comments/` | List comments (?post_id=x) | No |
| POST | `/api/comments/create/` | Create comment | Yes |
| DELETE | `/api/comments/<id>/delete/` | Delete comment | Yes (creator) |

## Request/Response Examples

### Register User

**Request:**
```json
POST /api/users/register/
{
  "email": "user@example.com",
  "username": "user123",
  "password": "securepass123",
  "password2": "securepass123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "display_name": "user123",
    "created_at": "2026-01-29T10:00:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Create Community

**Request:**
```json
POST /api/communities/
Authorization: Bearer <access_token>
{
  "id": "programming",
  "privacy_type": "public"
}
```

**Response:**
```json
{
  "id": "programming",
  "creator_id": "1",
  "privacy_type": "public",
  "number_of_members": 1,
  "image_url": null,
  "created_at": "2026-01-29T10:00:00Z"
}
```

### Create Post

**Request:**
```json
POST /api/posts/create/
Authorization: Bearer <access_token>
{
  "community_id": "programming",
  "title": "My First Post",
  "body": "This is the post content",
  "image_url": "https://example.com/image.jpg"
}
```

**Response:**
```json
{
  "id": 1,
  "community_id": "programming",
  "title": "My First Post",
  "body": "This is the post content",
  "creator_id": "1",
  "user_display_text": "user123",
  "vote_status": 0,
  "number_of_comments": 0,
  "created_at": "2026-01-29T10:00:00Z"
}
```

### Vote on Post

**Request:**
```json
POST /api/posts/1/vote/
Authorization: Bearer <access_token>
{
  "vote_value": 1  // 1 for upvote, -1 for downvote
}
```

**Response:**
```json
{
  "message": "Vote added",
  "vote_status": 1
}
```

## Migration from Firebase

This API replaces the following Firebase services:

- **Firebase Auth** → Django Custom User + JWT
- **Firestore Collections:**
  - `users` → User model
  - `communities` → Community model
  - `communitySnippets` → CommunityMember model
  - `posts` → Post model
  - `postVotes` → PostVote model
  - `comments` → Comment model

## Production Deployment (RDS)

To use PostgreSQL on AWS RDS in production:

1. Set `DATABASE_URL` environment variable:
```env
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
```

2. The app will automatically use PostgreSQL when `DATABASE_URL` is set.

## Admin Panel

Access the Django admin at `http://localhost:8000/admin/` using your superuser credentials.

## Development

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test
```

## License

MIT
