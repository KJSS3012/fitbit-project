# Backend – Initialization (FastAPI)

Standard guide to **set up and run** the backend.

---

## Prerequisites

* Python 3.10+
* Git

Check:

```bash
python --version
```

---

## Structure

```text
fitbit-back/
├── app/
├── tests/
├── .venv/
├── main.py
├── requirements.txt
└── README.md
```

---

## 1. Create virtual environment (first time only)

The venv is a **Python isolated environment** that allows you to install dependencies without affecting the global system.

To create this environment:

* Go to the `fitbit-project\fitbit-back` directory

* Run the command to create the `.venv`

### Commands

```bash
cd fitbit-back
python -m venv .venv
```

---

## 2. Activate virtual environment

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD)**

```cmd
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

After activation, you should see:

```text
(.venv)
```

This indicates that everything installed via pip will stay **inside the venv**, isolated from the global system.

---

## 3. Install dependencies

With the venv activated:

```bash
pip install -r requirements.txt
```

This will install all libraries listed in `requirements.txt`, for example:

```text
fastapi[standard]
```

---

## 4. Run the backend

Start the API server:

```bash
uvicorn main:app --reload
```

Expected output:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

## 5. API Documentation

* Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Daily workflow

```bash
cd fitbit-back
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```
