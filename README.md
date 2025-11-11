# Python API User Fetcher

A Python script that fetches user data from the JSONPlaceholder API and displays it in a clean, readable format.

## 📋 Description

This script demonstrates:

- Making GET requests to public APIs
- Handling JSON data
- Error handling for API requests
- Data filtering and formatting
- Clean code structure with functions

## 🚀 Features

- Fetches user data from JSONPlaceholder API
- Displays user information (Name, Username, Email, City)
- **Bonus Feature**: Filters users by city names starting with 'S'
- Comprehensive error handling for network issues
- Clean, formatted output

## 📦 Requirements

- Python 3.6 or higher
- `requests` library

## 📁 Project Structure

```
python-api-task/
│
├── src/
│   ├── __init__.py
│   └── fetch_users.py      # Main script
│
├── tests/
│   ├── __init__.py
│   └── test_fetch_users.py # Unit tests (optional)
│
├── screenshots/
│   └── output_example.png  # Example output
│
├── venv/                   # Virtual environment (not committed)
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## 🛠️ Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/LakshyaVerma123kl/pythonapi.git
cd python-api-task
```

### Step 2: Create a Virtual Environment

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Usage

Run the script using:

```bash
python src/fetch_users.py
```

Or if you're in the src directory:

```bash
cd src
python fetch_users.py
```

## 📤 Expected Output

```
==================================================
USER DATA FETCHER
==================================================

Fetching data from API...

Successfully fetched 10 users.

==================================================
ALL USERS
==================================================

User 1:
Name: Leanne Graham
Username: Bret
Email: Sincere@april.biz
City: Gwenborough
------------------------
User 2:
Name: Ervin Howell
Username: Antonette
Email: Shanna@melissa.tv
City: Wisokyburgh
------------------------
...

==================================================
USERS FROM CITIES STARTING WITH 'S'
==================================================

User 1:
Name: Patricia Lebsack
Username: Karianne
Email: Julianne.OConner@kory.org
City: South Elvis
------------------------
```

## 🎯 Task Requirements Met

✅ Uses GET method to call the API  
✅ Fetches data from `https://jsonplaceholder.typicode.com/users`  
✅ Loops through each user  
✅ Displays Name, Username, Email, and City  
✅ Uses the `requests` library  
✅ **Bonus**: Filters users whose city starts with 'S'  
✅ **Bonus**: Handles API errors comprehensively

## 🔧 Error Handling

The script handles:

- Connection timeouts
- Network connection errors
- HTTP errors (4xx, 5xx status codes)
- JSON parsing errors
- Empty API responses
- Missing or malformed data fields

## 🧪 Running Tests (Optional)

```bash
python -m pytest tests/
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

Lakshya Verma - [GitHub Profile](https://github.com/LakshyaVerma123kl)

## 🙏 Acknowledgments

- [JSONPlaceholder](https://jsonplaceholder.typicode.com/) for providing the free API
- Task designed as a Python internship assessment
