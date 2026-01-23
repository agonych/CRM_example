# CRM System

A modular CRM system built with Django (backend) and React with Tailwind CSS (frontend).

## Features

- **User Management**: Custom user model with groups and roles
- **Permission System**: Role-based permissions with ownership types (self/group) and access levels (read/create/edit/manage/admin)
- **Client Management**: Full CRUD operations for client records
- **Modern UI**: React frontend with Tailwind CSS and responsive design

## Project Structure

```
CRM_Example/
├── backend/          # Django backend
│   ├── crm_project/  # Main Django project
│   ├── users/        # Users app (User, Group, Role models)
│   ├── clients/      # Clients app
│   └── requirements.txt
└── frontend/         # React frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── contexts/
    │   └── services/
    └── package.json
```

## Backend Setup

### Prerequisites
- Python 3.8+
- MySQL 5.7+ or 8.0+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the `backend` directory (copy from `.env.example`):
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=crm_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

6. Create the MySQL database:
```sql
CREATE DATABASE crm_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

7. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

8. Create a superuser:
```bash
python manage.py createsuperuser
```

9. Run the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

## Frontend Setup

### Prerequisites
- Node.js 16+ and npm

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/users/login/` - Login
- `POST /api/auth/users/register/` - Register new user
- `GET /api/auth/users/me/` - Get current user
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Users
- `GET /api/auth/users/` - List users
- `POST /api/auth/users/` - Create user
- `GET /api/auth/users/{id}/` - Get user
- `PATCH /api/auth/users/{id}/` - Update user
- `DELETE /api/auth/users/{id}/` - Delete user

### Groups
- `GET /api/auth/groups/` - List groups
- `POST /api/auth/groups/` - Create group
- `GET /api/auth/groups/{id}/` - Get group
- `PATCH /api/auth/groups/{id}/` - Update group
- `DELETE /api/auth/groups/{id}/` - Delete group

### Roles
- `GET /api/auth/roles/` - List roles
- `POST /api/auth/roles/` - Create role
- `GET /api/auth/roles/{id}/` - Get role
- `PATCH /api/auth/roles/{id}/` - Update role
- `DELETE /api/auth/roles/{id}/` - Delete role

### Clients
- `GET /api/clients/` - List clients
- `POST /api/clients/` - Create client
- `GET /api/clients/{id}/` - Get client
- `PATCH /api/clients/{id}/` - Update client
- `DELETE /api/clients/{id}/` - Delete client

## Permission System

The permission system works with:
- **Ownership Types**: `self` (objects assigned to user) or `group` (objects assigned to user's groups)
- **Access Levels**: `read`, `create`, `edit`, `manage`, `admin`
- **Modules**: Each module (like `clients`) can define its own permission requirements

Roles store permissions as JSON:
```json
{
  "clients": {
    "ownership": "group",
    "level": "edit",
    "special": []
  }
}
```

## Development

### Backend Development
- Admin panel: `http://localhost:8000/admin/`
- API root: `http://localhost:8000/api/`

### Frontend Development
- The frontend proxies API requests to `http://localhost:8000/api` via Vite proxy configuration

## Notes

- All models include timestamps: `created_at`, `last_access`, `last_edit`, `last_edited_by`
- JWT tokens are used for authentication
- CORS is configured to allow requests from `http://localhost:3000`
- The permission system is extensible - new modules can be added by extending the Role model's permissions JSON field
