# 📝 Full-Stack Todo App

A modern, secure Task Management system. This project features a robust **FastAPI** backend with advanced authentication and a reactive **React** frontend.

## 🚀 Key Features

* **Secure Authentication:** Complete Auth flow using **JWT (JSON Web Tokens)** and **Refresh Tokens**.
* **User Management:** Separate logic for Administrators and regular Users.
* **Full CRUD:** Task management with persistent storage in **SQLite**.
* **Modern Tooling:** High-performance environment management with **uv**.
* **Fast Frontend:** Built with **Vite** for an optimized developer experience.

## 🛠️ Tech Stack

### Backend
* **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **Package Manager:** [uv](https://docs.astral.sh/uv/)
* **Security:** JWT (OAuth2 with Password flow & Refresh Tokens)
* **Database:** SQLite

### Frontend
* **Library:** [React](https://react.dev/)
* **Build Tool:** [Vite](https://vitejs.dev/)

---

## 💻 Getting Started

### 1. Backend Setup
The backend manages the database, JWT authentication, and API logic.

1. **Navigate to the backend folder:**
```bash
cd backend
```
2. **Sync dependencies and create environment:**
```bash
uv sync
```
3. **Start the FastAPI server:**
```bash
uv run uvicorn main:app --reload
```
🌐 API URL: http://127.0.0.1:8000

📑 Docs: http://127.0.0.1:8000/docs


## 🎨 Frontend Setup (React + Vite)
The frontend provides the user interface and connects to the API.

1. **Navigate to the frontend folder:**
```bash
cd frontend
```
2. **Install node packages:**
```bash
npm install
```
3. **Launch the development server:**
```bash
npm run dev
```
🚀 Frontend URL: http://localhost:5173


## 📖 API & Auth Logic
The backend includes specialized routers for:

* Auth: /auth/login and /auth/refresh endpoints.

* Users: Management of user profiles and roles.

* Todos: Protected endpoints that require a valid Bearer Token.


## 🚧 Status
The Backend is fully functional with Auth logic. The Frontend is currently under construction.



