# Iftar Menu Planner

Advanced Programming 462 - Individual Project (Client Server)

- Author: Mohammed Abu Daqqa
- Student ID: 443046063
- GitHub: https://github.com/Mohammed132002/iftar_planner

## What the application does

The application helps a family plan the dishes of an iftar table. The user saves each dish with its
name, category and estimated cost. The window shows all dishes in a table, lets the user add, edit and
delete dishes, search by name, filter by category, and shows the **total estimated cost** of the menu
(the extra feature). Two more buttons make a text report (**Generate Report**) and print an invoice
(**Print Invoice**).

The Tkinter window never touches the database. It sends HTTP requests to Flask on port 5050, and Flask
checks the values, uses SQLite and replies with JSON.

```
Tkinter window (gui.py)  <->  Flask (app.py)  <->  SQLite (database.py, iftar.db)
        |
  client.py (urllib)
```

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Flask back end: routes, input checks, JSON replies |
| `database.py` | Class `DishDatabase`: all SQLite work and the table setup |
| `client.py` | Class `DishClient`: sends the HTTP requests with urllib and handles request errors |
| `gui.py` | Classes `DishApp` (main window) and `DishForm` (add and edit window), and the invoice that the Print Invoice button opens |
| `report.py` | Report helper: one thread writes the saved dishes to a text file |
| `requirements.txt` | Packages to install |

## Install

Requirements: Python 3.9 or newer (Tkinter comes with the standard Windows installer of Python).

Open PowerShell in the project folder and run:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If the command `python` is not recognised on your computer, write the full path of `python.exe`
instead, for example `& "C:\Users\HP\miniconda3\python.exe"`.

## Create the tables

The tables are created by `DishDatabase.create_tables()` with `CREATE TABLE IF NOT EXISTS`, so existing
records are kept. It runs automatically every time Flask starts. To create the database without
starting Flask:

```
python -c "from database import DishDatabase; DishDatabase()"
```

This creates the file `iftar.db` next to the programs.

## Start Flask

Start Flask first and leave this terminal open:

```
python app.py
```

Flask runs on `http://127.0.0.1:5050`.

## Start Tkinter

Open a second terminal in the same folder, activate the environment, then run:

```
python gui.py
```

The window connects to Flask by itself. The user only works in the window and never types a server
address. If Flask is stopped, the window shows an error. After Flask starts again, the user presses the
same button again (or **Refresh**) without restarting the window.

## Report helper

With Flask running, run in a terminal:

```
python report.py
```

The helper asks the route `GET /dishes` for the saved dishes, starts one `Thread` that writes them to
`iftar_report.txt` (UTF-8), waits with `join()` and prints whether the file was saved. A different file
name can be given: `python report.py my_report.txt`.

The same report can be made from the window with the **Generate Report** button. It reloads the dishes,
uses the same `write_report` function of `report.py` in a `Thread`, and shows the path of the file.

## Print the invoice

The **Print Invoice** button reloads the dishes from Flask, writes an invoice page (`iftar_invoice.html`,
UTF-8, in the temporary folder of the computer) with `save_invoice`, and opens it in the browser with
`open_invoice`. The print window of the browser opens by itself, so the user chooses a printer or
"Save as PDF". The code is in `gui.py` (`build_invoice`, `save_invoice`, `open_invoice` and
`DishApp.print_invoice`).

## Flask routes

| Method | Route | What it does | Replies |
| --- | --- | --- | --- |
| GET | `/dishes` | Returns all saved dishes as JSON (also used by the report helper) | 200 |
| GET | `/dishes/total` | Returns the total estimated cost (extra feature) | 200 |
| POST | `/dishes/add` | Checks `name`, `category`, `cost`, then saves a dish | 200, 400 |
| POST | `/dishes/edit` | Checks `id` and the fields, then changes that dish | 200, 400, 404 |
| POST | `/dishes/delete` | Checks `id`, then deletes that dish | 200, 400, 404 |

Allowed categories: Dates, Soup, Fried Snacks, Main dish, Salad, Dessert, Drink. Errors have the form
`{"ok": false, "error": "..."}`.

## Where each course topic appears

| Topic | Evidence in the project |
| --- | --- |
| Python and collections | Functions and conditions in `app.py` (`read_fields`, `read_id`). Loops in `gui.py` (`DishApp.apply_filters`, `build_invoice`) and `report.py` (`write_report`). Lists of records and dictionaries of named values: `DishDatabase.all_dishes` returns a list of dictionaries; `CATEGORIES` is a list. |
| Exceptions | `ServerError` and the `HTTPError`, `socket.timeout`, `URLError` handling in `DishClient.request` (`client.py`). `ValueError` in `read_fields` and `read_id` (`app.py`). `OSError` in `write_report` (`report.py`). |
| Classes | `DishDatabase` (`database.py`), `DishClient` and `ServerError` (`client.py`), `DishApp` and `DishForm` (`gui.py`). |
| SQLite | `DishDatabase` methods `create_tables`, `all_dishes`, `get_dish`, `add_dish`, `update_dish`, `delete_dish`, `total_cost`. They use `?` placeholders. Every method opens its own connection, saves with `with conn:` and closes it in `finally`. |
| Threads and files | `report.py`: `write_report` runs in a `Thread` started with `start()`. `main` waits with `join()`. The file is opened with `with open(..., encoding='utf-8')`. The **Generate Report** button (`DishApp.generate_report` in `gui.py`) uses the same function in a thread. `save_invoice` in `gui.py` also writes its file with `with open`. |
| Tkinter | `DishApp` in `gui.py`: a table (`Treeview`), a search box, a category filter, buttons, the total cost card, a confirmation box before deletion and a message line. `DishForm` in `gui.py`: labels, text boxes and a combobox for the name, category and cost. |
| Client and server | One request is explained below. |
| Flask | Routes, input checks and JSON replies in `app.py`. |

### One complete request: clicking Add

1. The user clicks **+ Add Dish**. `DishApp.add_dish` (`gui.py`) opens the form `DishForm`. The user fills the name, category and cost and clicks **Save**, and `DishForm.save` reads the three fields.
2. `DishClient.add` (`client.py`) calls `request('/dishes/add', values)`. `urlencode(...).encode('utf-8')` turns the values into bytes, and `urlopen(url, data=body, timeout=5)` sends a POST.
3. Flask runs `add_dish` (`app.py`). `read_fields` checks the values, then `DishDatabase.add_dish` inserts the row with an SQL placeholder.
4. Flask replies with JSON: `{"ok": true, "message": "Saved ...", "dish": {...}}`. For invalid input it replies with status 400, which makes `urlopen` raise `HTTPError`; `DishClient.request` reads the JSON of the error and raises `ServerError`.
5. The form closes and the window calls `refresh`, which reads the dishes and the total with GET requests, rebuilds the table and shows the message. If the form got an error, it shows the message in red and stays open.

## Test results

| # | Test | Result |
| --- | --- | --- |
| 1 | Add a dish (Harira, Soup, 7): message shown, row appears, total updated | Passed |
| 2 | View: the list loads when the window opens and when Refresh is pressed | Passed |
| 3 | Edit: select Kabsa, change the cost to 30, press Edit: only that dish changed | Passed |
| 4 | Delete: No keeps the dish, Yes deletes only that dish | Passed |
| 5 | Missing name, wrong category, non-numeric cost and negative cost: clear red message, nothing saved | Passed |
| 6 | Empty list: message "The list is empty" and total 0.00 SAR | Passed |
| 7 | Unknown record: delete a dish in one window, edit it in the second: "Dish not found" and the list reloads | Passed |
| 8 | Flask stopped: "Cannot reach the server"; after Flask starts again the same button works without restarting the window | Passed |
| 9 | Stop and start Flask and Tkinter: saved records and the total remain | Passed |
| 10 | Report helper with saved dishes: file saved and its text is correct | Passed |
| 11 | Report helper with Flask stopped: message "Report not saved" | Passed |
| 12 | Followed this README from a clean folder: install, start Flask, start Tkinter, report | Passed |

## Credits

- Python standard library, Flask and SQLite documentation.
- The code was written with the help of an AI assistant (Claude, by Anthropic), step by step. I ran and tested
  every part, and I can explain the code.
- No outside images or assets are used.
