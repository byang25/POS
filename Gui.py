#POS System Prototype
import tkinter as tk
from tkinter import ttk
from time import strftime
import sqlite3
width = 1200
height = 700

#Point of Sale alternates between two frames, Register and Edit Inventory
class Point_of_Sale(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #container is where frames are stacked on top of each other
        #which will be raised when we want them to be visible
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frame = {}
        for page in (Register, Edit_inventory):
            frame = page(container,self)
            self.frame[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Register)
    def show_frame(self, page_name):
        frame = self.frame[page_name]
        frame.tkraise()

#Register is similar to a cash register where you can add items and checkout items
#You can see prices and enter items by their sku
class Register(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        frame_search = tk.Frame(self,width =400, height =100)
        frame_search.grid(row=0, column = 0, sticky="ew")
        frame_search.grid_propagate(0)

        frame_total = tk.Frame(self, width=400, height=150)
        frame_total.grid(row=0, column = 2, sticky="ew")
        frame_total.grid_rowconfigure(0, weight=1)
        frame_total.grid_rowconfigure(1, weight=1)
        frame_total.grid_rowconfigure(2, weight=1)
        frame_total.grid_columnconfigure(0, weight=1)
        frame_total.grid_columnconfigure(1, weight=1)

        frame_tree = tk.Frame(self,width =800, height =400)
        frame_tree.grid(row=1, column = 0, columnspan = 2, sticky ="nsew")

        frame_options = tk.Frame(self, width = 400, height = 400)
        frame_options.grid(row = 1, column = 2, sticky = "ns")
        frame_options.grid_rowconfigure(0, weight=1)
        frame_options.grid_rowconfigure(1, weight=1)
        frame_options.grid_columnconfigure(0, weight=1)
        frame_options.grid_columnconfigure(1, weight=1)
        #frame_options.grid_propagate(0)

        frame_num_item = tk.Frame(self , width = 400, height = 150)
        frame_num_item.grid(row = 2, column = 0)
        frame_num_item.grid_propagate(0)

        frame_alter = tk.Frame(self, width = 400, height = 150)
        frame_alter.grid(row = 2, column = 1)

        frame_clk = tk.Frame(self, width = 400, height = 150)
        frame_clk.grid(row = 2, column = 2)

        #Setting up upper left frame which contains search sku search function
        sku_label = tk.Label(frame_search, font = "10", text="SKU:")
        sku_label.grid(row=0, column = 0)
        self.searchr = tk.Entry(frame_search, width = 25)
        self.searchr.bind("<Return>", lambda event: self.search(controller))
        self.searchr.grid(row=0, column= 1)
        self.button_searchr = tk.Button(frame_search, text="Search", command=lambda: self.search(controller))
        self.button_searchr.grid(row=0, column=2)

        #Setting up middle right frame where you have option buttons
        button_special_item = tk.Button(frame_options, text="Add item",
                                        width = 15, height = 5, font= 12, command=lambda: self.add_item(controller))
        button_special_item.grid(row=0, column=0, sticky = "NSEW")
        button_edit_inventory = tk.Button(frame_options, text="Edit Inventory", width = 15, height = 5, font= 12,
                                           command=lambda: controller.show_frame(Edit_inventory))
        button_edit_inventory.grid(row=0, column=1, sticky = "NSEW")
        self.check_out = tk.Button(frame_options, text="Check Out", width = 31, height = 5, font= 12, command=self.clear_all)
        self.check_out.grid(row=1, column=0, columnspan=2, sticky = "NSEW")

        #Setting up clock display
        self.clock = tk.Label(frame_clk, width = 20, height = 1, font = 10, background = '#41C9B3',foreground = 'white')
        self.clock.grid(row=1,column=0)
        self.date = tk.Label(frame_clk, width = 20, height = 1, font = 10, background = '#41C9B3',foreground = 'white')
        self.date.grid(row=0,column=0)
        self.time_date()

        #Setting up list which displays items
        self.tree = ttk.Treeview(frame_tree, columns = ("Quantity", "Size", "Price"))
        self.tree.heading('#0', text="Name", anchor ="w")
        self.tree.heading('#1', text="Size", anchor ="w")
        self.tree.heading('#2', text="Quantity", anchor ="w")
        self.tree.heading('#3', text="Price", anchor ="w")
        self.tree.column('#0', width=300, anchor ="w")
        self.tree.column('#1', width=180, anchor ="w")
        self.tree.column('#2', width=120, anchor ="w")
        self.tree.column('#3', width=180, anchor ="w")
        self.tree.pack(side = "left", fill="both")
        self.scroll_bar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.scroll_bar.pack(side ="left", fill='y')
        self.tree.configure(yscrollcommand=self.scroll_bar.set)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 18), background = "#C3A825")
        style.configure("Treeview",rowheight= 40, font=(None, 15))

        #Setting up upper right frame which contains prices of items with tax
        self.price = tk.Label(frame_total,font = 50, bg = "blue", foreground = 'white',text = "Subtotal:")
        self.price.grid(row = 0,column = 0, sticky ="w")
        self.tax = tk.Label(frame_total, font = 50, bg = "blue", foreground = 'white', text = "Tax:")
        self.tax.grid(row = 2,column = 0, sticky ="w")
        self.total_price = tk.Label(frame_total, font = 50, bg = "blue", foreground = 'white', text = "Total:")
        self.total_price.grid(row = 4,column = 0, sticky ="w")
        self.price_val = tk.Label(frame_total, font = 50, bg = "blue", foreground = 'white', text="$0.00")
        self.price_val.grid(row=0, column=1, sticky ="e")
        self.tax_val = tk.Label(frame_total, font = 50, bg = "blue", foreground = 'white', text="$0.00")
        self.tax_val.grid(row=2, column=1, sticky ="e")
        self.total_price_val = tk.Label(frame_total, font = 50, bg = "blue", foreground = 'white', text="$0.00")
        self.total_price_val.grid(row=4, column=1, sticky ="e")

        #setting up lower left frame which will show total # of items
        self.total_items = tk.Label(frame_num_item, font = 10, text="Total Number Of Items: ")
        self.total_items.grid(row=0, column=0)
        self.total_items_val = tk.Label(frame_num_item, font = 10, text="0")
        self.total_items_val.grid(row=0, column=1)

        #setting up center bottom frame which increase/decreases quantity and deletes items
        self.delete_selected = tk.Button(frame_alter, text="Delete Item", width = 11, height = 5, font= 10,command=self.delete_item)
        self.delete_selected.grid(row=0, column=0)
        self.quantity_increase = tk.Button(frame_alter, text="+",  width = 11, height = 5, font=20, command=self.qup)
        self.quantity_decrease = tk.Button(frame_alter, text="-",  width = 11, height = 5, font=20, command=self.qdown)
        self.quantity_increase.grid(row =0, column = 1)
        self.quantity_decrease.grid(row=0, column=2)
        self.get_sum()

    #function searches database for sku, if not found ask you if you want to add item
    def search(self,controller, event=None):
        database = sqlite3.connect('items.db')
        c = database.cursor()
        c.execute('SELECT * FROM t WHERE item_sku=?', (self.searchr.get(),))
        rows = c.fetchall()
        database.close()

        if rows:
            row = rows[0]
            if self.tree.exists(row[0]):
                self.tree.item(row[0], values =(row[3],self.tree.item(row[0])["values"][1]+1 ,row[2]))
            else:
                self.tree.insert('', 'end', row[0], text=row[1],values=(row[3], 1, row[2]))
                self.tree.selection_set(row[0])
        else:
            self.new_item(controller)
        self.searchr.delete(0, 'end')
        self.tree.yview_moveto(1)
        self.get_sum()

    #Looping clock display
    def time_date(self):
        date_string = strftime("%A: %m-%d-%Y")
        self.date.config(text=date_string)
        clock_string = strftime('%I:%M:%S %p')
        self.clock.config(text=clock_string)
        self.clock.after(1000, self.time_date)
        #self.searchr.focus()

    #Deletes selected item
    def delete_item(self):
        self.tree.delete(self.tree.selection()[0])
        self.get_sum()

    #Clears tree and updates database based on items bought
    def clear_all(self):
        database = sqlite3.connect('items.db')
        c = database.cursor()
        entries = self.tree.get_children()
        for i in entries:
            c.execute('UPDATE t SET inventory = inventory - ? WHERE item_sku = ?', (self.tree.item(i)["values"][1],i))
            self.tree.delete(i)
            database.commit()
        self.get_sum()
        database.close()

    #Calculates sum of all items and taxes
    def get_sum(self):
        entries = self.tree.get_children()
        total = 0
        num_items = 0
        for i in entries:
            total = total + self.tree.item(i)["values"][2]*self.tree.item(i)["values"][1]
            num_items = num_items + self.tree.item(i)["values"][1]
        tax = round(total *.0875, 2)
        total_cost = total + tax
        self.price_val.config(text = "$%.2f" %total)
        self.tax_val.config(text="$%.2f" %float(tax))
        self.total_price_val.config(text="$%.2f" %float(total_cost))
        self.total_items_val.config(text="%s" %num_items)

    #Add a custom item with price to list
    def add_item(self, controller):
        popup_add = tk.Toplevel()
        popup_label = tk.Label(popup_add, text = "Price: ")
        popup_label.grid(row=0, column = 1)
        popup_entry = tk.Entry(popup_add)
        popup_entry.focus()
        popup_entry.bind("<Return>",lambda event: [self.submit_button(popup_entry), popup_add.destroy()])
        popup_entry.grid(row = 0, column =2)
        popup_confirm = tk.Button(popup_add, text="Okay", command=lambda: [self.submit_button(popup_entry), popup_add.destroy(), controller.show_frame[Edit_inventory]])
        popup_confirm.grid(row=2, column=1)

    #Part of Add_item
    def submit_button(self,popup_entry, event=None):
        x = self.tree.insert('', 'end', text="Special item",values=(750, 1, popup_entry.get()))
        self.tree.selection_set(x)
        self.get_sum()

    #Creates popup that asks you if you want to add item
    def new_item(self, controller):
        popup_new = tk.Toplevel()
        popup_label = tk.Label(popup_new, text="Add New Item?")
        popup_label.grid(row=0, column=1)
        popup_yes = tk.Button(popup_new, text="Yes",command=lambda: [popup_new.destroy(), controller.show_frame(Edit_inventory)])
        popup_no = tk.Button(popup_new, text="No", command=lambda: [popup_new.destroy()])
        popup_yes.grid(row=1, column=1)
        popup_no.grid(row=1, column=2)

    #Button that increases selection quantity by 1
    def qup(self):
        self.tree.item(self.tree.selection()[0],
                       values=(self.tree.item(self.tree.selection()[0]).get("values")[0],
                               self.tree.item(self.tree.selection()[0]).get("values")[1]+1,
                               self.tree.item(self.tree.selection()[0]).get("values")[2]))
        self.get_sum()

    #button that decreases selection quantity by 1
    def qdown(self):
        if self.tree.item(self.tree.selection()[0]).get("values")[1] == 1:
            self.delete_item()
        else:
            self.tree.item(self.tree.selection()[0],
                           values=(self.tree.item(self.tree.selection()[0]).get("values")[0],
                                   self.tree.item(self.tree.selection()[0]).get("values")[1] - 1,
                                   self.tree.item(self.tree.selection()[0]).get("values")[2]))
        self.get_sum()

#Frame that allows you to see the current database as well as edit it
class Edit_inventory(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        frame_data = tk.Frame(self, width=1200, height=100)
        frame_tree = tk.Frame(self, bg="red", width=600, height=500)
        frame_scroll = tk.Frame(self, bg="blue", width=50, height=500)
        frame_buttons = tk.Frame(self, bg="yellow", width=1200, height=100)

        frame_data.grid(row=0, column=0, columnspan = 2, sticky="ew")
        frame_tree.grid(row=1, column=0, sticky="nse")
        frame_scroll.grid(row=1, column=1, sticky="wns")
        frame_buttons.grid(row=2, column=0, columnspan = 2,sticky="ew")

        self.item_sku = tk.Entry(frame_data)
        self.item_name = tk.Entry(frame_data)
        self.item_size = tk.Entry(frame_data)
        self.item_inventory = tk.Entry(frame_data)
        self.item_price = tk.Entry(frame_data, width=15)

        self.sku_label = tk.Label(frame_data, text = "Sku:")
        self.name_label = tk.Label(frame_data, text="Name:")
        self.price_label = tk.Label(frame_data, text="Price:")
        self.size_label = tk.Label(frame_data, text="Size:")
        self.inventory_label = tk.Label(frame_data, text="Inventory:")

        self.sku_label.pack(side="left", anchor="n")
        self.item_sku.pack(side="left", anchor="n")
        self.name_label.pack(side="left", anchor = "n")
        self.item_name.pack(side = "left", anchor = "n")
        self.size_label.pack(side="left", anchor="n")
        self.item_size.pack(side="left", anchor = "n")
        self.inventory_label.pack(side="left", anchor = "n")
        self.item_inventory.pack(side ="left", anchor = "n")
        self.price_label.pack(side="left", anchor="n")
        self.item_price.pack(side="left", anchor="n")

        self.tree = ttk.Treeview(frame_tree, columns=("Name","Quantity", "Size", "Price"))
        self.tree.heading('#0', text="Sku", anchor="w")
        self.tree.heading('#1', text="Name", anchor="w")
        self.tree.heading('#2', text="Size", anchor="w")
        self.tree.heading('#3', text="Quantity", anchor="w")
        self.tree.heading('#4', text="Price", anchor="w")
        self.tree.column('#0', anchor="w")
        self.tree.column('#1', anchor="w")
        self.tree.column('#2', anchor="w")
        self.tree.column('#3', anchor="w")
        self.tree.column('#4', anchor="w")
        self.tree.pack(side="left", fill="both")
        self.scroll_bar = ttk.Scrollbar(frame_scroll, orient="vertical", command=self.tree.yview)
        self.scroll_bar.pack(side="left", fill='y')
        self.tree.configure(yscrollcommand=self.scroll_bar.set)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=(None, 18), background="#C3A825")
        style.configure("Treeview", rowheight=40, font=(None, 15))
        self.tree_setup()

        self.button_register = ttk.Button(frame_buttons, text="Cancel", width = 10, command=lambda: controller.show_frame(Register))
        self.button_delete = ttk.Button(frame_buttons, text="Delete item", command=self.delete_item)
        self.button_save = ttk.Button(frame_buttons, text="Add item", command=self.submit_item)
        self.button_update = ttk.Button(frame_buttons, text="Save Changes", command=self.update_item)
        self.button_select = ttk.Button(frame_buttons, text="Select", command= self.button_selection)

        self.button_select.pack()
        self.button_save.pack()
        self.button_delete.pack()
        self.button_update.pack()
        self.button_register.pack()

    #function that updates the tree to current database values
    def tree_setup(self):
        entries = self.tree.get_children()
        for i in entries:
            self.tree.delete(i)
        database = sqlite3.connect('items.db')
        c = database.cursor()
        c.execute('SELECT * FROM t')
        rows = c.fetchall()
        database.close()
        for row in rows:
            self.tree.insert('', 'end', row[0], text=row[0], values=(row[1],row[3], row[4], row[2]))

    #When pressed, displays information of selection in the entry fields
    def button_selection(self):
        self.item_sku.delete(0,tk.END)
        self.item_name.delete(0, tk.END)
        self.item_price.delete(0, tk.END)
        self.item_size.delete(0, tk.END)
        self.item_inventory.delete(0, tk.END)
        self.item_sku.insert(0, self.tree.item(self.tree.selection()[0]).get("text"))
        self.item_name.insert(0, self.tree.item(self.tree.selection()[0]).get("values")[0])
        self.item_price.insert(0, self.tree.item(self.tree.selection()[0]).get("values")[3])
        self.item_size.insert(0, self.tree.item(self.tree.selection()[0]).get("values")[1])
        self.item_inventory.insert(0, self.tree.item(self.tree.selection()[0]).get("values")[2])

    #inserts new item to database
    def submit_item(self):
        isku = self.item_sku.get()
        iname = self.item_name.get()
        iprice = self.item_price.get()
        isize = self.item_size.get()
        iinventory = self.item_inventory.get()
        database = sqlite3.connect('items.db')
        c = database.cursor()
        c.execute("INSERT INTO t (item_sku, item_name, item_price, item_size, inventory) VALUES (?, ?, ?, ?, ?)", (isku, iname, iprice, isize, iinventory))
        database.commit()
        database.close()
        self.pop_msg("Item added")
        self.tree_setup()

    #updates items of database
    def update_item(self):
        iskuu = self.tree.selection()[0]
        inameu = self.item_name.get()
        ipriceu = self.item_price.get()
        isizeu = self.item_size.get()
        iinventoryu = self.item_inventory.get()
        database = sqlite3.connect('items.db')
        c = database.cursor()
        c.execute('UPDATE t SET item_name = ? WHERE item_sku = ?', (inameu,iskuu))
        c.execute('UPDATE t SET item_price = ? WHERE item_sku = ?', (ipriceu, iskuu))
        c.execute('UPDATE t SET item_size = ? WHERE item_sku = ?', (isizeu, iskuu))
        c.execute('UPDATE t SET inventory = ? WHERE item_sku = ?', (iinventoryu, iskuu))
        database.commit()
        database.close()
        self.pop_msg("Item Updated")
        self.tree_setup()

    #deletes item from database
    def delete_item(self):
        iskuu = self.tree.selection()[0]
        database = sqlite3.connect('items.db')
        c = database.cursor()
        c.execute('DELETE FROM t WHERE item_sku = ?', (iskuu,))
        database.commit()
        database.close()
        self.pop_msg("Item Deleted")
        self.tree_setup()

    #generic popup message
    def pop_msg(self, text_info):
        popup = tk.Toplevel()
        label = tk.Label(popup, text=text_info,font = ('calibri', 10, 'bold'))
        label.pack()
        destroy_button = tk.Button(popup, text="Okay", command=lambda: [popup.destroy()])
        destroy_button.pack()

app = Point_of_Sale()
#centralize the window
window_width = app.winfo_screenwidth()
window_height = app.winfo_screenheight()
x = (window_width/2) - (width/2)
y = (window_height/2) - (height/2)
app.geometry('%dx%d+%d+%d' % (width, height, x, y))
app.mainloop()

#Create table to sqllite from csv files
'''
#c.execute("""CREATE TABLE addresses (
#        item_sku integer,
#        item_name text,
#        item_price real,
#        item_size real
#        inventory integer
#        )""")
c.execute("CREATE TABLE t (item_sku, "
          "item_name, "
          "item_price, "
          "item_size, "
          "inventory);")

with open('testcsv.csv','rt')
    to_db = [(i['item_sku'], 
              i['item_name'], 
              i['item_price'], 
              i['item_size'], 
              i['inventory']) for i in dr]
c.executemany("INSERT INTO t (item_sku, item_name, item_price, item_size, inventory) VALUES (?, ?, ?, ?, ?);", to_db)
database.commit()
'''
#Note this code only works with a database with the above specifications