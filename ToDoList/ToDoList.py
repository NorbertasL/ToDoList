import tkinter as tk
from tkinter import Toplevel, messagebox
from typing import Callable

class ToDoEntry():
    def __init__(self, title: str, info:str = ""):
        
        self.__title: str = title
        self.__info: str = info 
        
    def get_title(self) -> str:
        return self.__title
    
    def get_info(self) -> str:
        return self.__info
    
    def __str__(self) -> str:
        return self.__title

class ToDoLogic():
   
    def on_new_item(self):
        print("New Item Logic")

class ToDoGUI(tk.Tk):    
    __DEFAULT_CONGIF: dict = {
        "root_title": "ToDo List",
        "root_size": "400x600"
        }
    
    def __init__(self):
        super().__init__()
        self.__logic = ToDoLogic()

        #self.__root: tk.Tk  = tk.Tk()
        self.__create_main_window()
  
    
    def __create_main_window(self):
        #Main windows setup/styling
        self.title(ToDoGUI.__DEFAULT_CONGIF["root_title"])
        self.geometry(ToDoGUI.__DEFAULT_CONGIF["root_size"])
        
        self.__list_objects: list[ToDoEntry] = [ToDoEntry("TEST One"), ToDoEntry("TEST Two")]
        self.__todo_list_items: tk.Variable = tk.Variable(value= self.__list_objects)
        self.__listbox: tk.Listbox = tk.Listbox(
            self,
            height = 20,
            listvariable=self.__todo_list_items
            )
        
        self.__listbox.bind('<Double-1>', self.__on_even_doubleclick)
        self.__listbox.bind('<Button-3>', self.__on_even_rightclick)
        self.__listbox.pack()
        
        
        
        #Add ToDo Item Button
        tk.Button(
            self, 
            text = "Add", 
            command = self.__add_todo
            ).pack()
        
    def __on_even_doubleclick(self, event:tk.Event):
        index:int = event.widget.curselection()[0]
        print(f"Double Click on Event Index:{index} Object:{self.__list_objects[index]}")
        
    def __on_even_rightclick(self, event: tk.Event):
        self.__listbox.selection_clear(0,tk.END) # clears focus so we can only select one
        self.__listbox.selection_set(self.__listbox.nearest(event.y)) # selects the element
        index:int = self.__listbox.curselection()[0]
        print(f"Right Click on Event Index:{index} Object:{self.__list_objects[index]}")
        
        
    def __on_new_entry(self, entry: ToDoEntry):
        self.__list_objects.append(entry)
        self.__todo_list_items.set(self.__list_objects)
        
    def __add_todo(self):
        def show_add_windows(on_new_entry: Callable):
            def on_save():
                on_new_entry(ToDoEntry(title_var.get(), info_var.get())) 
                add_task_widnow.destroy()
                
            add_task_widnow: Toplevel = Toplevel(self)
            add_task_widnow.title("New ToDo!")
            
            add_task_widnow.attributes('-topmost', True)#make it alwasy on top
            
            add_task_widnow.grab_set()#lock all othe window interactions
            
            title_var: tk.StringVar = tk.StringVar(add_task_widnow)
            title = tk.Entry(add_task_widnow, textvariable = title_var)
            
            title.insert(0, "Title")
            title.pack()
            
            info_var: tk.StringVar = tk.StringVar(add_task_widnow)
            info = tk.Entry(add_task_widnow, textvariable = info_var)
            info.insert(0, "Extra Info!")
            info.pack()
            
            btn_save = tk.Button(add_task_widnow, 
                                 text = "Save", 
                                 command = on_save 
                                 
                        )
            btn_save.pack()            

            btn_cancel = tk.Button(add_task_widnow, 
                                   text = "Cancel",
                                   command = lambda: add_task_widnow.destroy()
                        )
            btn_cancel.pack()
            
        
        show_add_windows(self.__on_new_entry)
        
        
        self.__logic.on_new_item()
        
    def start(self):
        self.mainloop()
        


if __name__ == "__main__":
    ToDoGUI().start()