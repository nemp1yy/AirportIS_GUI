Certainly! Here’s an improved and more visually appealing README for your project, written in English:

---

# ✈️ AirportIS_GUI

A modern graphical application for managing an airport’s flight database, built with Python and PyQt6.  
The entire workflow is available through a user-friendly graphical interface.

---

## 🚀 Features

- **View Flight Table**  
  Instantly see all scheduled flights in a sortable, filterable table.
- **Add & Remove Flights**  
  Easily add new flight records or remove outdated ones with a click.
- **Advanced Search**  
  Find flights using flexible queries in a dedicated search window.
- **Column Sorting**  
  Quickly organize data by any parameter.
- **Reset Search**  
  Return to the full dataset with a single click.

---

## 🛠️ Technologies Used

- **Python 3**
- **PyQt6** (GUI framework)
- **SQLite** (database, via QtSql)
- **Qt Designer** (.ui files for interface design)

---

## ⚡ Installation & Launch

1. **Clone the repository:**
    ```bash
    git clone https://github.com/nemp1yy/AirportIS_GUI.git
    cd AirportIS_GUI
    ```

2. **Install the required dependencies:**
    ```bash
    pip install PyQt6
    ```

3. **Run the application:**
    ```bash
    python main.py
    ```

---

## 📁 Project Structure

```
AirportIS_GUI/
│
├── main.py                # Entry point: launches the application
│
├── gui/                   # GUI modules
│   ├── MainWindow.py      # Main window (table view & controls)
│   ├── SearchWindow.py    # Search dialog window
│   └── design/            # Qt Designer .ui files
│
└── data/                  # Database files (e.g., data.db)
```

---

## 💡 Notes

- **Full GUI:** All operations are performed via a graphical interface—no command line required.
- **Database:** Ensure that a valid database file exists in the `data/` folder before running the app.
- **Auto-Loading:** The application automatically loads and displays the flight table on startup.

---

## 👤 Author

**[nemp1yy](https://github.com/nemp1yy)**
