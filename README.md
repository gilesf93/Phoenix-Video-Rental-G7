# Phoenix Video Rental

Phoenix Video Rental is a Django web application developed by Group 7 for the CSC289 Programming Capstone. The system will manage movies, inventory, customer accounts, rentals, returns, and payment records.

## Team Members

- Francis Giles — Project Manager and Rental/Database Developer
- Matthew Robert Hall — Backend and Authentication Developer
- Yuki Fukushima — Frontend and Inventory Developer
- Ethan Wen Shelley — Customer Features and Testing Developer

## Technology

- Python 3.13.3
- Django 6.1.1
- PostgreSQL (planned database)
- Django templates
- Bootstrap

## Project Applications

- `accounts` — Authentication, user roles, and customer accounts
- `catalog` — Movies, genres, searching, and inventory
- `rentals` — Rentals, returns, payments, and rental history
- `core` — Shared pages and site-level functionality

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/gilesf93/Phoenix-Video-Rental-G7.git
cd Phoenix-Video-Rental-G7
```

### 2. Create a virtual environment

```bash
py -m venv .venv
```

### 3. Activate the virtual environment

Git Bash:

```bash
source .venv/Scripts/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install the required packages

```bash
python -m pip install -r requirements.txt
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a web browser.

Stop the server by pressing `Ctrl+C` in the terminal.

## Development Workflow

1. Update the local `main` branch.
2. Create a separate feature branch for the assigned task.
3. Develop and test the changes locally.
4. Commit and push the feature branch to GitHub.
5. Create a pull request for team review.
6. Merge changes only after approval.