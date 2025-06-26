# 📚 Quiz Backend API

This is a Flask-based REST API backend for a quiz application. It handles questions, participations, user authentication, and database management.

---

## 🛠️ Features

- JWT-based admin login  
- Full CRUD for quiz questions  
- Submit and score quiz participations  
- Secure routes for administrative actions  
- Rebuild/reset database endpoint  
- CORS enabled for frontend (localhost:3000)

---

## 🗂️ Project Structure

```
.
├── app.py                     # Main Flask app
├── models/
│   └── question_model.py      # Data model 
    └── answer_model.py        # Data model 
├── services/
│   ├── question_service.py    # Business logic for questions
│   ├── rebuild_service.py     # DB reset logic
├── jwt_utils.py               # JWT handling
├── requirements.txt           # Python dependencies
├── quiz-api.code-workspace    # Workspace and and default launch
```

---

## ⚙️ Getting Started

### ✅ Prerequisites

- Python 3.10+
- `virtualenv` or similar for managing Python environments

---

### 🚀 Setup Instructions

```bash
# Clone the repository
git clone <your-repo-url>
cd <quiz-api>

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the App

### VS Code Debug

This project includes a `quiz-api.code-workspace` to launch Flask in debug mode:

1. Open the project in **Visual Studio Code**
2. Go to **Run and Debug** (Ctrl+Shift+D)
3. Select `Python: Flask` and click ▶️ Run

---

## 🔐 Authentication

**Admin routes** are protected using a simple login system:

- Login via `POST /login` with JSON:
  ```json
  { "password": "admin_password" }
  ```
- You will receive a JWT token.
- Use this token in `Authorization` header for protected endpoints

---

## 📡 API Endpoints

### Public

| Method | Endpoint             | Description                          |
|--------|----------------------|--------------------------------------|
| GET    | `/quiz-info`         | Get basic quiz info                  |
| GET    | `/questions`         | Get all questions or by `?position=` |
| GET    | `/questions/<id>`    | Get question by ID                   |
| POST   | `/participations`    | Submit quiz answers                  |

### Admin (requires token)

| Method | Endpoint                              | Description               |
|--------|----------------------------------------|---------------------------|
| POST   | `/questions`                           | Create a question         |
| PUT    | `/questions/<id>`                      | Update a question         |
| DELETE | `/questions/<id>`                      | Delete by ID              |
| DELETE | `/questions/position?position=<n>`     | Delete by position        |
| DELETE | `/questions/all`                       | Delete all questions      |
| DELETE | `/participations/all`                  | Delete all participations |
| POST   | `/rebuild-db`                          | Reset the entire database |

---

## 🧪 Testing Tips

- Use [Postman](https://www.postman.com/) to test HTTP requests.
- Don’t forget to include the `Authorization` header for secured routes.

---

## 📝 Environment Variables

These are already configured in `launch.json`:

```json
"env": {
  "FLASK_APP": "app.py",
  "FLASK_DEBUG": "1",
  "FLASK_ENV": "development"
}
```

---

## ✅ Requirements

All dependencies are in `requirements.txt`. To update it:

```bash
pip freeze > requirements.txt
```
