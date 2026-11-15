import tkinter as tk
from tkinter import messagebox, ttk

from client import DishClient, ServerError

CATEGORIES = ['Soup', 'Salad', 'Main dish', 'Dessert', 'Drink']
ALL = 'All Categories'

# the colors and the font of the whole window
FONT = 'Segoe UI'
BG = '#F4F2EC'
INK = '#1F2A2E'
GRAY = '#6B7478'
CARD = '#FCF3CF'
TABLE_BG = '#FFF8DC'
HEADER = '#274C4B'
TEAL = '#3A7D7B'
RED = '#D6342B'
GREEN = '#2E7D32'

# the colors of the buttons
BTN_ADD = '#2F8F6B'
BTN_EDIT = '#3B82A0'
BTN_DELETE = '#C95151'
BTN_REFRESH = '#5B6B73'
BTN_CLEAR = '#D9902F'
BTN_CANCEL = '#8A9499'


def make_button(parent, text, color, command):
    # one flat colored button, the same style everywhere
    return tk.Button(parent, text=text, command=command, bg=color, fg='white',
                     activebackground=color, activeforeground='white',
                     relief='flat', bd=0, cursor='hand2',
                     font=(FONT, 9, 'bold'), padx=14, pady=7)


def make_entry(parent, width):
    # one flat input box with a thin border
    return tk.Entry(parent, width=width, relief='flat', bg=TABLE_BG, fg=INK,
                    font=(FONT, 10), highlightthickness=1,
                    highlightbackground='#D9CFA3', highlightcolor=TEAL)


class DishForm(tk.Toplevel):
    """The small window for adding a dish or editing one."""

    def __init__(self, app, dish=None):
        super().__init__(app.root)
        self.app = app
        self.dish = dish
        self.title('Edit Dish' if dish else 'Add Dish')
        self.configure(bg=BG)
        self.resizable(False, False)

        tk.Label(self, text='Edit Dish' if dish else 'Add Dish', bg=BG, fg=INK,
                 font=(FONT, 15, 'bold')).grid(row=0, column=0, columnspan=2,
                                               padx=24, pady=(18, 10), sticky='w')

        # the three fields
        tk.Label(self, text='Name', bg=BG, fg=GRAY, font=(FONT, 9, 'bold')).grid(
            row=1, column=0, padx=(24, 8), pady=6, sticky='e')
        self.name_box = make_entry(self, 30)
        self.name_box.grid(row=1, column=1, padx=(0, 24), pady=6, ipady=4)

        tk.Label(self, text='Category', bg=BG, fg=GRAY, font=(FONT, 9, 'bold')).grid(
            row=2, column=0, padx=(24, 8), pady=6, sticky='e')
        self.category_box = ttk.Combobox(self, values=CATEGORIES, state='readonly', width=28)
        self.category_box.grid(row=2, column=1, padx=(0, 24), pady=6, sticky='w')

        tk.Label(self, text='Cost (SAR)', bg=BG, fg=GRAY, font=(FONT, 9, 'bold')).grid(
            row=3, column=0, padx=(24, 8), pady=6, sticky='e')
        self.cost_box = make_entry(self, 30)
        self.cost_box.grid(row=3, column=1, padx=(0, 24), pady=6, ipady=4)

        # one line for the error messages of this window
        self.error_label = tk.Label(self, text='', bg=BG, fg=RED, wraplength=320,
                                    font=(FONT, 9))
        self.error_label.grid(row=4, column=0, columnspan=2, padx=24, pady=(4, 0))

        # the buttons
        buttons = tk.Frame(self, bg=BG)
        buttons.grid(row=5, column=0, columnspan=2, pady=(8, 18))
        make_button(buttons, 'Save', BTN_ADD, self.save).grid(row=0, column=0, padx=5)
        make_button(buttons, 'Cancel', BTN_CANCEL, self.destroy).grid(row=0, column=1, padx=5)

        # when editing, start with the values of the selected dish
        if dish:
            self.name_box.insert(0, dish['name'])
            self.category_box.set(dish['category'])
            self.cost_box.insert(0, '%.2f' % dish['cost'])

        # put the form in the middle of the main window
        self.update_idletasks()
        x = app.root.winfo_rootx() + (app.root.winfo_width() - self.winfo_width()) // 2
        y = app.root.winfo_rooty() + (app.root.winfo_height() - self.winfo_height()) // 3
        self.geometry('+%d+%d' % (x, y))

        # the form keeps the focus until it is closed
        self.bind('<Return>', lambda event: self.save())
        self.transient(app.root)
        self.grab_set()
        self.name_box.focus_set()

    def save(self):
        # the raw text of the fields, Flask checks it
        name = self.name_box.get()
        category = self.category_box.get()
        cost = self.cost_box.get()
        try:
            if self.dish is None:
                result = self.app.client.add(name, category, cost)
            else:
                result = self.app.client.edit(self.dish['id'], name, category, cost)
        except ServerError as error:
            message = str(error)
            if message == 'Dish not found.':
                # the dish was deleted somewhere else, so reload the list
                self.destroy()
                self.app.refresh()
                self.app.show_error('Dish not found. It was deleted, the list is reloaded.')
            else:
                self.error_label.config(text=message)
            return

        self.destroy()
        if self.app.refresh():
            self.app.show_ok(result['message'])


class DishApp:
    """The main window of the Iftar menu planner."""

    def __init__(self, root):
        self.root = root
        self.client = DishClient()
        self.dishes = []
        root.title('Iftar Menu Planner')
        root.geometry('900x620')
        root.minsize(900, 620)
        root.configure(bg=BG)

        # the table style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=TABLE_BG, fieldbackground=TABLE_BG,
                        foreground=INK, rowheight=28, borderwidth=0, font=(FONT, 10))
        style.map('Treeview', background=[('selected', TEAL)],
                  foreground=[('selected', 'white')])
        style.configure('Treeview.Heading', background=HEADER, foreground='white',
                        font=(FONT, 10, 'bold'), relief='flat', padding=6)
        style.map('Treeview.Heading', background=[('active', HEADER)])

        # the title
        title = tk.Frame(root, bg=BG)
        title.pack(fill='x', padx=26, pady=(18, 0))
        tk.Label(title, text='Iftar Menu Planner', bg=BG, fg=INK,
                 font=(FONT, 20, 'bold')).pack(anchor='w')
        tk.Label(title, text='Plan and manage the dishes of your iftar table', bg=BG,
                 fg=GRAY, font=(FONT, 10)).pack(anchor='w', pady=(2, 0))

        # the card with the numbers
        card = tk.Frame(root, bg=CARD)
        card.pack(fill='x', padx=26, pady=14)
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        tk.Label(card, text='TOTAL DISHES', bg=CARD, fg=INK, font=(FONT, 8)).grid(
            row=0, column=0, padx=18, pady=(12, 0), sticky='w')
        self.count_label = tk.Label(card, text='0', bg=CARD, fg=INK, font=(FONT, 22, 'bold'))
        self.count_label.grid(row=1, column=0, padx=18, pady=(0, 10), sticky='w')
        tk.Label(card, text='TOTAL ESTIMATED COST', bg=CARD, fg=INK, font=(FONT, 8)).grid(
            row=0, column=1, padx=18, pady=(12, 0), sticky='w')
        self.total_label = tk.Label(card, text='0.00 SAR', bg=CARD, fg=INK,
                                    font=(FONT, 22, 'bold'))
        self.total_label.grid(row=1, column=1, padx=18, pady=(0, 10), sticky='w')

        # the section title and the buttons
        bar = tk.Frame(root, bg=BG)
        bar.pack(fill='x', padx=26)
        tk.Label(bar, text='Dish Records', bg=BG, fg=INK, font=(FONT, 14, 'bold')).pack(
            side='left')
        buttons = tk.Frame(bar, bg=BG)
        buttons.pack(side='right')
        for text, color, command in [('+ Add Dish', BTN_ADD, self.add_dish),
                                     ('Edit', BTN_EDIT, self.edit_dish),
                                     ('Delete', BTN_DELETE, self.delete_dish),
                                     ('Refresh', BTN_REFRESH, self.refresh)]:
            make_button(buttons, text, color, command).pack(side='left', padx=(8, 0))

        # the filters
        filters = tk.Frame(root, bg=BG)
        filters.pack(fill='x', padx=26, pady=(12, 8))
        self.search_text = tk.StringVar()
        self.search_text.trace_add('write', lambda *args: self.apply_filters())
        self.search_box = make_entry(filters, 26)
        self.search_box.config(textvariable=self.search_text)
        self.search_box.pack(side='left', ipady=4)
        self.category_filter = ttk.Combobox(filters, values=[ALL] + CATEGORIES,
                                            state='readonly', width=16)
        self.category_filter.set(ALL)
        self.category_filter.bind('<<ComboboxSelected>>', lambda event: self.apply_filters())
        self.category_filter.pack(side='left', padx=10)
        make_button(filters, 'Clear Filters', BTN_CLEAR, self.clear_filters).pack(side='right')

        # the table of the dishes, with a scroll bar
        holder = tk.Frame(root, bg=BG)
        holder.pack(fill='both', expand=True, padx=26)
        columns = ('id', 'name', 'category', 'cost')
        self.table = ttk.Treeview(holder, columns=columns, show='headings',
                                  selectmode='browse')
        for column, name, width in [('id', 'ID', 60), ('name', 'Name', 330),
                                    ('category', 'Category', 200), ('cost', 'Cost (SAR)', 120)]:
            self.table.heading(column, text=name)
            self.table.column(column, width=width, anchor='center')
        scroll = ttk.Scrollbar(holder, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        # one line for the success and error messages
        self.status = tk.Label(root, text='', bg=BG, wraplength=840, font=(FONT, 10))
        self.status.pack(fill='x', padx=26, pady=(8, 12))

        # the window connects to Flask by itself when it opens
        self.refresh()

    # ----- messages -----

    def show_ok(self, message):
        self.status.config(text=message, fg=GREEN)

    def show_error(self, message):
        self.status.config(text=message, fg=RED)

    # ----- the table and the filters -----

    def refresh(self):
        # ask Flask for the dishes and the total, True when it worked
        try:
            self.dishes = self.client.list_dishes()
            total = self.client.total()
        except ServerError as error:
            self.show_error(str(error))
            return False

        self.count_label.config(text=str(len(self.dishes)))
        self.total_label.config(text='%.2f SAR' % total)
        self.apply_filters()
        if len(self.dishes) == 0:
            self.show_ok('The list is empty. Add the first dish.')
        else:
            self.show_ok('Loaded ' + str(len(self.dishes)) + ' dishes.')
        return True

    def apply_filters(self):
        # show only the dishes that match the search text and the category
        text = self.search_text.get().strip().lower()
        category = self.category_filter.get()

        for row in self.table.get_children():
            self.table.delete(row)
        shown = 0
        for dish in self.dishes:
            if text not in dish['name'].lower():
                continue
            if category != ALL and dish['category'] != category:
                continue
            cost = '%.2f' % dish['cost']
            self.table.insert('', 'end', values=(dish['id'], dish['name'], dish['category'], cost))
            shown = shown + 1

        if shown == 0 and len(self.dishes) > 0:
            self.show_ok('No dishes match the filters.')

    def clear_filters(self):
        self.search_text.set('')
        self.category_filter.set(ALL)
        self.apply_filters()

    def selected_dish(self):
        # the dish of the selected row as a dictionary, or None
        selection = self.table.selection()
        if not selection:
            self.show_error('Select a dish from the table first.')
            return None
        dish_id, name, category, cost = self.table.item(selection[0], 'values')
        return {'id': int(dish_id), 'name': name, 'category': category, 'cost': float(cost)}

    # ----- the buttons -----

    def add_dish(self):
        return DishForm(self)

    def edit_dish(self):
        dish = self.selected_dish()
        if dish is None:
            return None
        return DishForm(self, dish)

    def delete_dish(self):
        dish = self.selected_dish()
        if dish is None:
            return
        if not messagebox.askyesno('Delete', 'Delete ' + dish['name'] + '?'):
            return
        try:
            result = self.client.delete(dish['id'])
        except ServerError as error:
            self.show_error(str(error))
            if str(error) == 'Dish not found.':
                self.refresh()
                self.show_error('Dish not found. It was already deleted, the list is reloaded.')
            return
        if self.refresh():
            self.show_ok(result['message'])


if __name__ == '__main__':
    window = tk.Tk()
    DishApp(window)
    window.mainloop()
