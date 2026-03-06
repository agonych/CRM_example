# Quick Start Guide

Follow these steps to run the CRM project from scratch.

## Backend Setup (Django)

### Step 1: Navigate to backend directory
```bash
cd backend
```

### Step 2: Create and activate virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin role
```bash
python manage.py create_admin_role
```

### Step 6: Create a superuser (follow prompts)
```bash
python manage.py createsuperuser
```
You'll be prompted for:
- Email address
- First name
- Last name
- Password

### Step 7: (Optional) Seed sample data
```bash
python manage.py seed_data
```
This creates sample groups, client statuses, task types, users, clients, and tasks for testing.

### Step 8: Start the backend server
```bash
python manage.py runserver
```

The backend will be running at `http://localhost:8000`

---

## Frontend Setup (React)

### Step 1: Open a new terminal and navigate to frontend directory
```bash
cd frontend
```

### Step 2: Install dependencies
```bash
npm install
```

### Step 3: Start the development server
```bash
npm run dev
```

The frontend will be running at `http://localhost:3000`

---

## Access the Application

1. **Frontend**: Open `http://localhost:3000` in your browser
2. **Backend API**: `http://localhost:8000/api/`
3. **Django Admin**: `http://localhost:8000/admin/` (use your superuser credentials)

---

## Login

Use the superuser email and password you created in Step 6 to log in to the frontend.

---

## Troubleshooting

### Backend issues:
- **Port 8000 already in use**: Change port with `python manage.py runserver 8001`
- **Migration errors**: Delete `db.sqlite3` and run migrations again
- **Module not found**: Make sure virtual environment is activated

### Frontend issues:
- **Port 3000 already in use**: Vite will automatically use the next available port
- **API connection errors**: Make sure backend is running on port 8000
- **Proxy errors**: Check `vite.config.js` proxy settings

### If proxy doesn't work:
Create a `.env` file in the `frontend` directory:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```
