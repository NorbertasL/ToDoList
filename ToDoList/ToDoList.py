import tkinter as tk #GUI
from tkinter import Button, Toplevel, Listbox, messagebox
from types import MappingProxyType #MappingProxyType is a immutable dictionary
from typing import Callable # for hinting a fucntion as parameter
from datetime import datetime
import sqlite3# local database
import doctest

class ToDoEntry():
    def __init__(self, id:int, date:str, title: str, info:str = "", isDone:bool = False):
        '''
        Args:
            id(int): local db _ID
            date(str): entry creation date
            title(str)
            info(str): extra information
        '''
        self.__id: int = id
        self.__creation_date: str = date
        self.__title: str = title
        self.__info: str = info  
        self.__is_done: bool = isDone
        
    def get_id(self) -> int:
        '''
        Getter for id
        
        Returns:
            int: local databse id
        '''
        return self.__id
        
    def get_title(self) -> str:
        '''
        Getter for title
        
        Returns:
            str
        '''
        return self.__title
    
    def get_info(self) -> str:
        '''
        Getter for info
        
        Returns:
            str
        '''
        return self.__info
    
    def __str__(self) -> str:
        '''
        override to string method 
        using it for GUI display string
        
        Returns:
            str: title string , crossed out if is_done set to true
        '''
        temp:str = f"{self.__title}"
        if self.__is_done:
           temp ='\u0337'+ '\u0337'.join(temp)+'\u0337'
        return temp
        
    def is_done(self) -> bool:
        '''
        Getter for completed stated
        
        Returns:
            bool
        '''
        return self.__is_done
        
class DatabaseManager:
    '''
    Statsic class that manages the local database(SQLite) connection/querries
    '''
    DATABASE_PATH:str = "ToDoDatabase.db"
    MAIN_TABLE:str = "Entries"

    @classmethod
    def execure_sql_querry(cls, sql_statment:str, write_querry:bool = False, values:tuple = ()) -> tuple[bool, list]: # list | bool Python 3.10+ Hinting
        '''
        Connects to the local database and executes the querrrie
        
        Args:
           sql_statment(str): SQL Querrie
           write_querry(bool): set true if its a write function
           values(tuple): write function might have values that need to be passed it
           
        Returns:
            tuple(bool, list)
                bool: was the querrie sucsessful?
                list: get(non-write) querries return a list of rows
        '''
        successful: bool = False 
        return_list: list = []
        try:
            with sqlite3.connect(cls.DATABASE_PATH, timeout=0.5) as conn:#0.5s timout since it's local DB
                cursor = conn.cursor()
                successful = cursor.execute(sql_statment, values).rowcount > 0 #rowcount = affected rows
                if write_querry:
                    conn.commit()#commit is only needed for write querries
                    successful = True # No error so SQL querry was successful 
                else:
                    successful = True
                    return_list = cursor.fetchall() # fetchall is only needed if we are retiving data, write_querry == False
        except Exception as ex:
            print(ex)
        finally:
            return successful, return_list # using finally block to make sure something is always returned
        
    @classmethod
    def verify_db(cls) -> bool:
        '''
        Checks if database and table exists, if not it creates them
        
        Retruns:
            bool: connection good?
        '''
        main_table_sql:str = f'''CREATE TABLE IF NOT EXISTS {cls.MAIN_TABLE}(_ID INTEGER PRIMARY KEY NOT NULL,date TEXT NOT NULL, title TEXT NOT NULL,info TEXT,is_done BOOL NOT NULL);'''  
        return cls.execure_sql_querry(main_table_sql, True)[0] # only returning the state bool
    
    @classmethod
    def add_entry(cls, val: MappingProxyType) -> bool:
        '''
        Allows to add new entry to local db
        
        Args:
           val(MappingProxyType): immutable dic of keys(columbs in db) and values
           
        Returns:
            bool: entry sucsesfull
        '''

        #generates a INSERT querry with dic keys as keys for db columbs and values as ?. This allows me to pass values in @call and
        #has a built int querry sanitization to prevent SQL injections
        sql_querry:str = f"INSERT INTO {cls.MAIN_TABLE}({','.join(val.keys())}) VALUES({','.join('?'*len(val))})" 
        return cls.execure_sql_querry(sql_querry, True, tuple(val.values()))[0]
    
    @classmethod
    def delete_entry(cls, id:int) -> bool:
        '''
        Allows to remove entry to local db
        
        Args:
           id(int): local database id
           
        Returns:
            bool: delete sucsesfull
        '''
        
        sql_querry:str = f"DELETE FROM {cls.MAIN_TABLE} WHERE _ID={id};"
        return cls.execure_sql_querry(sql_querry, True)[0]
    
    @classmethod
    def get_entries(cls) -> tuple[bool, list]:
        '''
        Gets all the entires from the local database
        
        Returns:
            tuple(bool, list)
                bool: was the get sucsesfull
                list: list of rows
        '''
        sql_querry:str = f"SELECT * FROM {cls.MAIN_TABLE};"
        return cls.execure_sql_querry(sql_querry)
    
    @classmethod
    def change_done_status(cls, id: int, status: bool = True) -> bool:
        '''
        Changes the complete status of an entry
           
        Args:
            id(int): local database entry(row) id
            statsus(bool): new status of the entry
        '''
        sql_querry:str = f"UPDATE {cls.MAIN_TABLE} SET is_done={status} WHERE _ID={id};"
        return cls.execure_sql_querry(sql_querry, True)[0]
  
class ToDoLogic():
    
    def __init__(self, list_change_callback: Callable, error_callback: Callable):
        '''
        Args:
            list_change_callback(Callable): callback for GUI to update its display list
            error_callback(Callable): callback for GUI to display an error message
        '''
        self.__entry_list: list[ToDoEntry] = []
        self.__list_change_callback = list_change_callback
        self.__error_callback = error_callback # method callback that displays an error box with a custom message
        if not DatabaseManager.verify_db():
             self.__error_callback("Database Verification Issue")
           
          
    def get_entry_display_strings(self) -> tuple[str]:
        '''
        get a string list representation of entry_list objects
        
        Returns:
            tuple[str]: each elements represent a ToDoEntry Object
        '''
        return_list: list[str] = []
        for entry in self.__entry_list:
            return_list.append(str(entry))
        return tuple(return_list)
    
    def add_new_entry(self, val: MappingProxyType):
        '''
        Allows to add new ToDo entry
        
        Args:
           val(MappingProxyType): immutable dic of keys(columbs in db) and values
        '''  
    
        if not DatabaseManager.add_entry(val):
            self.__error_callback("Failed To Add Entry")
        self.update_entry_list()
        
        
    def remove_entry(self, index: int):
        '''
        Removes entry from ToDo based on the index in listbox
        
        Args:
            index(int): index in the list box
        '''
        if not DatabaseManager.delete_entry(self.__entry_list[index].get_id()):
            self.__error_callback("Failed To Remove Entry")
        self.update_entry_list()
        
    def change_entry_status(self, index: int, status: bool):
        '''
        Change complete status for ToDo entry
        
        Args:
            index(int): index of the entry in the listbox
            status(bool): new status for the entry
        '''
        if not DatabaseManager.change_done_status(self.__entry_list[index].get_id(), status):
            self.__error_callback("Failed To Update Entry")
        self.update_entry_list()
        
    def get_done_status(self, index: int) -> bool:
        '''
        returns the completeion statsu for the entry
        
        Args:
            index(int): index of the entry in listbox
        
        Returns:
            bool: staus of the entry(complete(True) or not(False))
        '''
        return self.__entry_list[index].is_done()

    def update_entry_list(self):
        '''
        Updates the entry_list of ToDoEntry objects 
        AND GUI display in the listbox
        '''

        self.__entry_list = [] #reseting it
        successful,  entries = DatabaseManager.get_entries()
        if not successful:
            self.__error_callback("Failed To Get Entry")
            return # not updating GUI
        
        for entry in entries:
             self.__entry_list.append(ToDoEntry(*entry))
        self.__list_change_callback()
        
class ToDoGUI(tk.Tk):   
    # Some default configs to be used in the GUI
    # Temorary solution. These setting should be in a config or xml file.
    DEFAULT_CONGIFS: MappingProxyType = MappingProxyType({
        "root_w": 400,
        "root_h": 500,
        "add_box_w": 200,
        "add_box_h": 100,
        "root_title": "ToDo List",
        "main_font" : ("Helvetica", 25),
        "main_colour": "#ffd900",
        "second_colour": "#FFCC00",
        "list_box_row_max": 10,# this should really be calculated based on root_h and front size
        }) 
    
    def __init__(self):
        super().__init__()#Tk parent class init
        
        self.__logic = ToDoLogic(self.reload_list, self.error_msgbox)

        self.__create_main_window()
        
        # Windows opens in the top left of screen.
        self.__offset_x = 0 
        self.__offset_y = 0
    
    def error_msgbox(self, msg:str, title:str = "Error!"):
        '''
        Easy way to display and error message in the GUI
        
        Args:
            msg(str): message to display in the error box
            title(srg): OPTIONAL Error Box Title DEFAULT = Error!
        '''
        messagebox.showerror(title, msg)
    def __create_main_window(self):
        def create_custom_title_bar():
            def move_window(event):#allows me to move window
                self.geometry('+%d+%d' % (event.x_root-self.__offset_x, event.y_root-self.__offset_y))
                
            def start_move(event):#calulates windows pos relative to mouse and not 0 0
                self.__offset_x = event.x
                self.__offset_y = event.y   
                
            self.overrideredirect(True)
            # Create a custom frame for the title bar
            title_bar = tk.Frame(self, bg=ToDoGUI.DEFAULT_CONGIFS["second_colour"], height=30)
            title_bar.pack(fill=tk.X)
            # Add a close button to exit the window
            close_button = tk.Button(title_bar, 
                                     text='X', 
                                     bg=ToDoGUI.DEFAULT_CONGIFS["second_colour"], 
                                     fg="black", 
                                     relief='flat',
                                     borderwidth=0,
                                     command=self.destroy)
            close_button.pack(side=tk.RIGHT)
            
            title_bar.bind("<ButtonPress-1>", start_move)
            title_bar.bind("<B1-Motion>", move_window)
            

        #Main windows setup/styling
        create_custom_title_bar()
        self.title(ToDoGUI.DEFAULT_CONGIFS["root_title"])
        self.geometry('%dx%d' % (ToDoGUI.DEFAULT_CONGIFS['root_w'], ToDoGUI.DEFAULT_CONGIFS['root_h'])) # parsing string into widthxheight string
        self.config(bg=ToDoGUI.DEFAULT_CONGIFS["main_colour"]) #RGB
        
        #self.__list_objects: list[ToDoEntry] = [ToDoEntry("TEST One"), ToDoEntry("TEST Two")]
        #self.__todo_list_items: tk.Variable = tk.Variable(value= self.__list_objects)
        self.__listbox: Listbox = Listbox(self)
        self.__listbox.configure(font=ToDoGUI.DEFAULT_CONGIFS["main_font"],
                                 bg = ToDoGUI.DEFAULT_CONGIFS["main_colour"],
                                 borderwidth=0, 
                                 highlightthickness=0,
                                 activestyle = "none", # removes selection undeline
                                 selectbackground = ToDoGUI.DEFAULT_CONGIFS["second_colour"],
                                 selectforeground = "black",
                                 ) 
        self.__listbox.bind('<Double-1>', self.__on_even_doubleclick)
        self.__listbox.bind('<Button-3>', self.__on_even_rightclick)
        self.__listbox.pack(fill=tk.X, padx=10)
       
        
        self.reload_list()
        
        
        
        #Add ToDo Item Button
        close_button = Button(self, 
                                     text='+', 
                                     font = (ToDoGUI.DEFAULT_CONGIFS["main_font"][0], 50),#just want the font, we using custom size
                                     bg=ToDoGUI.DEFAULT_CONGIFS["main_colour"], #makes it look transparent
                                     fg="green", 
                                     activebackground=ToDoGUI.DEFAULT_CONGIFS["main_colour"],#makes it look transparent when clicked
                                     relief='flat',
                                     borderwidth=0,
                                     command=self.__add_todo)
        close_button.pack()

        
    def __on_even_doubleclick(self, event:tk.Event):
        
        #prevents errors when clicking empty box
        if(len(self.__listbox.curselection()) == 0):
            return
        
        index:int = event.widget.curselection()[0] 
        if(self.__logic.get_done_status(index)):
            if messagebox.askyesno("Change", "Do you want to mark it as not done?"):
                self.__logic.change_entry_status(index, False)  
        else:
            self.__logic.change_entry_status(index, True)

 
        
    def __on_even_rightclick(self, event: tk.Event):
        self.__listbox.selection_clear(0,tk.END) # clears focus so we can only select one
        self.__listbox.selection_set(self.__listbox.nearest(event.y)) # selects the element
        #prvents errors when clicking empty box
        if(len(self.__listbox.curselection()) == 0):
            return
        index:int = self.__listbox.curselection()[0]
        self.__on_delete_entry(index)
        
        
    def __on_new_entry(self, entry: MappingProxyType):
        self.__logic.add_new_entry(entry)
        
    def __on_delete_entry(self, index: int):
        if messagebox.askyesno("", f"Are You sure you want to delete {self.__listbox.get(index)}?"):
            self.__logic.remove_entry(index)


    def reload_list(self):
        '''
        Reload the GUI ListBox display data
        Gets the data from ToDoLogic
        '''

        self.__listbox.delete(0, tk.END) #clears the list
        for entry in self.__logic.get_entry_display_strings():       
            self.__listbox.insert(tk.END, entry)
        
        #Figures out the size of the list_box
        list_box_size: int = self.__listbox.size()
        
        # Makig sure not to go over max size or the listbox pushes out the +(add) button out of view
        if list_box_size > ToDoGUI.DEFAULT_CONGIFS["list_box_row_max"]:
            list_box_size = ToDoGUI.DEFAULT_CONGIFS["list_box_row_max"]        
        self.__listbox.config(height = list_box_size)
      
    def __add_todo(self):
        def show_add_windows():
            def on_save():
                '''
                Called when we want to save the info the the add box
                '''
                if not 0 < len(title_var.get()) < 21:# making sure title is not too long
                    self.error_msgbox("Title lenght has to be between 1 and 20")
                    return
                self.__on_new_entry(MappingProxyType({"title": title_var.get(), #Getting text from box var
                                                      "info": info_var.get(), #Getting text from box var
                                                      "date": datetime.now(), #Time when the task was created
                                                      "is_done": False} #defaul ToDo is NOT done
                                                     )
                                    ) 
                add_task_widnow.destroy()#data submited so we are destoying the windows
             
                
            add_task_widnow: Toplevel = Toplevel(self)
            add_task_widnow.title("New ToDo!")
            
            #add task window and possitions it relative to root(main) window
            add_task_widnow.geometry('%dx%d+%d+%d' % (self.DEFAULT_CONGIFS["add_box_w"], 
                                                      self.DEFAULT_CONGIFS["add_box_h"], 
                                                      self.winfo_x() + self.DEFAULT_CONGIFS["root_w"] - (self.DEFAULT_CONGIFS["add_box_w"]*1.5), 
                                                      self.winfo_y() + self.DEFAULT_CONGIFS["root_h"]/2 - (self.DEFAULT_CONGIFS["add_box_h"])
                                                      )
                                     )
            
            add_task_widnow.attributes('-topmost', True)#make it alwasy on top
            #add_task_widnow.config(bg=ToDoGUI.DEFAULT_CONGIFS["main_colour"]) 
            
            # add_task_widnow.grab_set()#lock all other window interactions
            
            # #var to store the text in title
            # title_var: tk.StringVar = tk.StringVar(add_task_widnow)
            # title = tk.Entry(add_task_widnow, textvariable = title_var)
            # title.pack()
            
            # #var to store the text in info
            # info_var: tk.StringVar = tk.StringVar(add_task_widnow)
            # info = tk.Entry(add_task_widnow, textvariable = info_var)
            # info.pack()

            add_task_widnow.resizable(False, False) #making window NOT resizible W and H
            
            title_label = tk.Label(add_task_widnow, text="Title:")
            title_label.grid(row=0, column=0)

            #var to store the text in title
            title_var: tk.StringVar = tk.StringVar(add_task_widnow)
            title_entry = tk.Entry(add_task_widnow, textvariable = title_var, width=25)
            title_entry.grid(row=0, column=1)

            info_label = tk.Label(add_task_widnow, text="Info:")
            info_label.grid(row=1, column=0)

            #var to store the text in info
            info_var: tk.StringVar = tk.StringVar(add_task_widnow)
            info_text = tk.Entry(add_task_widnow, textvariable = info_var, width=25)
            info_text.grid(row=1, column=1)

            save_button = tk.Button(add_task_widnow, text="Save", command=on_save)
            save_button.grid(row=2, column=1)

            cancel_button = tk.Button(add_task_widnow, text="Cancel", command=add_task_widnow.destroy)
            cancel_button.grid(row=3, column=1)

            
            #Save and Cancel buttons are not used anywhere else, so dont need them in varibales
            # Button(add_task_widnow, 
            #        text = "Save", 
            #        command = on_save
            #        ).pack()
             

            # Button(add_task_widnow, 
            #        text = "Cancel",
            #        command = add_task_widnow.destroy
            #        ).pack()
  
        show_add_windows()#creates/displays the add window
        
        
    def start(self):
        self.__logic.update_entry_list()# gets the innitial list
        self.mainloop()
        
if __name__ == "__main__":
    ToDoGUI().start()