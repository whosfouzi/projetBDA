# 🎓 UMBB Exam Scheduler - Faculty of Sciences

Welcome to the **UMBB Exam Scheduler**! This portal handles exam planning, room assignments, and surveillance for 13,000 students.

## 🚀 Quick Start for Teammates

Follow these steps to get the application running on your local machine:

### 1. Project Setup
Clone the repository and create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
Install all required libraries:
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
You need a MySQL database running. 
1. Import the latest schema and data:
   - Use the file `optimisation_edt-2.sql`.
2. Configure **Streamlit Secrets**:
   - Create a folder named `.streamlit` in the root directory.
   - Create a file `secrets.toml` inside it:
   ```toml
   [mysql]
   host = "localhost"
   port = 3306
   user = "your_username"
   password = "your_password"
   database = "exam_scheduler" # or your target db name
   ```

### 4. Running the App
Start the Streamlit portal:
```bash
streamlit run app.py
```

## 🏗️ Project Architecture
- `app.py`: Main entry point and dynamic router.
- `backend/`: Core logic (Scheduler, Auth, DB connectors).
- `frontend/`: UI implementation (Sidebar, Dashboard, Timetables).
- `assets/`: Custom Academic UI styling.

## 🔑 Default Accounts
- **Admin**: `admin@univ.edu` / `admin`
- **Professors**: `nom_numero@univ.edu` (ex: `bouchenak_0`) / `password123`
- **Students**: `e12345@student.edu` / `password123`

---
*Note: If your database is empty, you can use the "Mode Récupération" button on the Login page to seed 13,000 students and 1,000 professors automatically.*
