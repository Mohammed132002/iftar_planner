import tkinter as tk
from tkinter import messagebox, ttk

from client import DishClient, ServerError

CATEGORIES = ['Soup', 'Salad', 'Main dish', 'Dessert', 'Drink']


class DishApp:
    """The window of the Iftar menu planner."""

    def __init__(self, root):
        self.root = root
        self.client = DishClient()
        self.selected_id = None
        root.title('Iftar Menu Planner')

        # the labels and the input fields
        tk.Label(root, text='Name').grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.name_box = tk.Entry(root, width=30)
        self.name_box.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        tk.Label(root, text='Category').grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.category_box = ttk.Combobox(root, values=CATEGORIES, state='readonly', width=27)
        self.category_box.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        tk.Label(root, text='Cost (SAR)').grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.cost_box = tk.Entry(root, width=30)
        self.cost_box.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        # the buttons
        buttons = tk.Frame(root)
        buttons.grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(buttons, text='Add', width=9, command=self.add_dish).grid(row=0, column=0, padx=4)
        tk.Button(buttons, text='Edit', width=9, command=self.edit_dish).grid(row=0, column=1, padx=4)
        tk.Button(buttons, text='Delete', width=9, command=self.delete_dish).grid(row=0, column=2, padx=4)
        tk.Button(buttons, text='Clear', width=9, command=self.clear_fields).grid(row=0, column=3, padx=4)
        tk.Button(buttons, text='Refresh', width=9, command=self.refresh).grid(row=0, column=4, padx=4)

        # the table of the dishes
        columns = ('id', 'name', 'category', 'cost')
        self.table = ttk.Treeview(root, columns=columns, show='headings', height=10)
        for column, title, width in [('id', 'ID', 50), ('name', 'Name', 190),
                                     ('category', 'Category', 110), ('cost', 'Cost (SAR)', 90)]:
            self.table.heading(column, text=title)
            self.table.column(column, width=width)
        self.table.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        self.table.bind('<<TreeviewSelect>>', self.on_select)

        # the extra feature: the total estimated cost
        self.total_label = tk.Label(root, text='Total estimated cost: 0.00 SAR',
                                    font=('Segoe UI', 11, 'bold'))
        self.total_label.grid(row=5, column=0, columnspan=2, pady=5)

        # one line for the success and error messages
        self.status = tk.Label(root, text='', wraplength=440)
        self.status.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 10))

        # the window connects to Flask by itself when it opens
        self.refresh()

    # ----- messages -----

    def show_ok(self, message):
        self.status.config(text=message, fg='green')

    def show_error(self, message):
        self.status.config(text=message, fg='red')

    # ----- helpers -----

    def clear_fields(self):
        # empty the three fields and forget the selected dish
        self.name_box.delete(0, 'end')
        self.cost_box.delete(0, 'end')
        self.category_box.set('')
        self.table.selection_remove(self.table.selection())
        self.selected_id = None

    def read_fields(self):
        # the raw text of the fields, Flask checks it
        return self.name_box.get(), self.category_box.get(), self.cost_box.get()

    def refresh(self):
        # ask Flask for the dishes and the total, True when it worked
        try:
            dishes = self.client.list_dishes()
            total = self.client.total()
        except ServerError as error:
            self.show_error(str(error))
            return False

        # rebuild the table
        self.clear_fields()
        for row in self.table.get_children():
            self.table.delete(row)
        for dish in dishes:
            cost = '%.2f' % dish['cost']
            self.table.insert('', 'end', values=(dish['id'], dish['name'], dish['category'], cost))

        self.total_label.config(text='Total estimated cost: %.2f SAR' % total)
        if len(dishes) == 0:
            self.show_ok('The list is empty. Add the first dish.')
        else:
            self.show_ok('Loaded ' + str(len(dishes)) + ' dishes.')
        return True

    def on_select(self, event):
        # copy the selected row into the fields
        selection = self.table.selection()
        if not selection:
            return
        dish_id, name, category, cost = self.table.item(selection[0], 'values')
        self.selected_id = int(dish_id)
        self.name_box.delete(0, 'end')
        self.name_box.insert(0, name)
        self.category_box.set(category)
        self.cost_box.delete(0, 'end')
        self.cost_box.insert(0, cost)

    # ----- the three actions -----

    def add_dish(self):
        name, category, cost = self.read_fields()
        try:
            result = self.client.add(name, category, cost)
        except ServerError as error:
            self.show_error(str(error))
            return
        if self.refresh():
            self.show_ok(result['message'])

    def edit_dish(self):
        if self.selected_id is None:
            self.show_error('Select a dish from the table first.')
            return
        name, category, cost = self.read_fields()
        try:
            result = self.client.edit(self.selected_id, name, category, cost)
        except ServerError as error:
            self.show_error(str(error))
            # an unknown dish means the list is old, so reload it
            if str(error) == 'Dish not found.':
                self.refresh()
                self.show_error('Dish not found. It was deleted, the list is reloaded.')
            return
        if self.refresh():
            self.show_ok(result['message'])

    def delete_dish(self):
        if self.selected_id is None:
            self.show_error('Select a dish from the table first.')
            return
        name = self.name_box.get()
        if not messagebox.askyesno('Delete', 'Delete ' + name + '?'):
            return
        try:
            result = self.client.delete(self.selected_id)
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
