# Dayflow

A modern employee attendance management system built with Streamlit and MongoDB. Track attendance, manage leave requests, and provide dashboards for admins and employees.

## Features

- **User Authentication**: Secure login for admins and employees
- **Admin Dashboard**: Manage employees, view attendance reports, approve leave requests
- **Employee Dashboard**: Mark attendance, submit leave requests, view personal records
- **Database Integration**: MongoDB for data storage with connection testing
- **Responsive UI**: Built with Streamlit for easy web access

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KRISH-0201/Dayflow.git
   cd Dayflow
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv env
   env\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirement.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env` (if exists) or create `.env`
   - Add your MongoDB URI:
     ```
     MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
     ```

5. **Initialize the database** (optional):
   ```bash
   python init_db.py
   ```

## Usage

1. **Test database connection**:
   ```bash
   python test_db.py
   ```

2. **Run the application**:
   ```bash
   streamlit run app.py
   ```

3. Open your browser to `http://localhost:8501` and log in.

## Project Structure

```
Dayflow/
├── app.py                 # Main Streamlit application
├── auth.py                # Authentication logic
├── database.py            # MongoDB connection and operations
├── init_db.py             # Database initialization
├── test_db.py             # Database connection test
├── requirement.txt        # Python dependencies
├── .env                   # Environment variables (not committed)
└── pages/
    ├── admin_dashboard.py     # Admin interface
    ├── employee_dashboard.py  # Employee interface
    └── login.py               # Login page
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature-name`
5. Create a Pull Request

## License

This project is licensed under the MIT License.</content>
<parameter name="filePath">d:\pyhon_projects\Dayflow\README.md