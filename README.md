# Agile Web Development - CITS5505 Group 23 project

## 📝⏳ *ProcrastiNo* Overview  
*Feeling lazy? Always procrastinating your plans? NO, FOCUS! START NOW! 🫵*

Our project **ProcrastiNo** is a web application designed to provide a fully simulated environment for immersive studying and working.<br> It allows users to **set timer**, **plan tasks**, **track productivity**, and **visualize performance**. <br> Users are also allowed to **share their performance results**.

## 🎯 Key Features 
- User login, registration, and password reset
- Background theme settings
- Study/work session planning with personal timer
- Automatic productivity analysis and data visualization
- Share results with specific users
- Notification center for system message

## 👥 Team Members
| Name         | Student ID | GitHub Username   |
|--------------|------------|-------------------|
| Will Xu      | 22440804   | [@WhoIsWill38](https://github.com/WhoIsWill38)|
| Yehao Chen   | 23985897   | [@YehaoO-chen](https://github.com/YehaoO-chen)|
| Chloe W Wu   | 24019456   | [@Chloeiw](https://github.com/Chloeiw)        |
| Zong Zhang   | 24049392   | [@zongcooper](https://github.com/zongcooper)  |


## 🛠️ Applied Technologies and Libraries (*※TBD*)
- **Frontend**: `HTML` , `CSS` , `Javascript` , `JQuery` , `Bootstrap` , `AJAX`
- **Backend**: `Flask` 
- **Data Processing**: `SQLite`
- **Testing**: `unittest`, `pytest`, `selenium`

## 🚀 Getting Started

This section will guide you through setting up and running the project locally.

---

### ✅ Prerequisites

Make sure you have the following installed:

- [Python 3.8+](https://www.python.org/)
- [pip](https://pip.pypa.io/)
- Virtual environment tool: `venv` or `virtualenv` 

---

### 🔧 Installation

1. **Clone the repository**

```bash
git clone https://github.com/YehaoO-chen/AgileWebDevGroup23.git
cd AgileWebDevGroup23
```
2. **Create and activate a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```
3. **Install Dependency**
```bash
pip install -r requirements.txt
```

---

### ▶️ Running the App

**Start the run.py to initiate the project:**
```bash
flask run
```

**Or**
```bash
python run.py
```

**Open the address:**
```bash
 * Running on: http://127.0.0.1:5000
```



## 🔬 Running Test
Use the provided test runner script to execute tests:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only unit tests
python run_tests.py --selenium

# Generate test reports
python run_tests.py --report --coverage

# Optional flag to reduce console output.
python script.py --quiet

```