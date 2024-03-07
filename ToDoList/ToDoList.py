
import tkinter as tk
from tkinter import Toplevel, messagebox
from types import MappingProxyType
from typing import Callable
from datetime import datetime

class ToDoEntry():
    def __init__(self, title: str, info:str = ""):
        self.__is_done = False
        self.__title: str = title
        self.__info: str = info 
        self.__creation_date: datetime = datetime.now()
        
    def get_title(self) -> str:
        return self.__title
    
    def get_info(self) -> str:
        return self.__info
    
    def __str__(self) -> str:
        temp:str = f"{self.__creation_date.hour:02d}:{self.__creation_date.minute:02d} {self.__title}"
        if self.__is_done:
           temp = '\u0336'.join(temp)
        return temp
    
    def mark_done(self):
        self.__is_done = True
        

class ToDoLogic():
    
    def __init__(self, list_change_callback: Callable):
        self.__entry_list: list[ToDoEntry] = []
        self.__list_change_callback = list_change_callback
    
    def get_entry_display_strings(self) -> tuple[str]:
        return_list: list[str] = []
        for entry in self.__entry_list:
            return_list.append(str(entry))
        return tuple(return_list)
    
    def add_new_entry(self, val: MappingProxyType):
        self.__entry_list.append(ToDoEntry(val["title"]))
        self.__list_change_callback()
        
    def remove_entry(self, index: int):
        del(self.__entry_list[index])
        self.__list_change_callback()
        
    def mark_entry_done(self, index: int):
        self.__entry_list[index].mark_done()
        self.__list_change_callback()
        

class ToDoGUI(tk.Tk):    
    DEFAULT_CONGIFS: MappingProxyType = MappingProxyType({
        "root_w": 400,
        "root_h": 800,
        "root_title": "ToDo List",
        })
    
    def __init__(self):
        super().__init__()
        self.__logic = ToDoLogic(self.reload_list)

        #self.__root: tk.Tk  = tk.Tk()
        self.__create_main_window()
  
    
    def __create_main_window(self):
        #Main windows setup/styling
        self.title(ToDoGUI.DEFAULT_CONGIFS["root_title"])
        self.geometry(f"{ToDoGUI.DEFAULT_CONGIFS['root_w']}x{ToDoGUI.DEFAULT_CONGIFS['root_h']}")
       
        
        #self.__list_objects: list[ToDoEntry] = [ToDoEntry("TEST One"), ToDoEntry("TEST Two")]
        #self.__todo_list_items: tk.Variable = tk.Variable(value= self.__list_objects)
        self.__listbox: tk.Listbox = tk.Listbox(self)
        self.__listbox.configure(font=('Helvetica', 12))
        self.__listbox.bind('<Double-1>', self.__on_even_doubleclick)
        self.__listbox.bind('<Button-3>', self.__on_even_rightclick)
        self.__listbox.pack()
       
        
        self.reload_list()
        
        
        
        #Add ToDo Item Button
        tk.Button(
            self, 
            text = "Add", 
            command = self.__add_todo
            ).pack()
        
    def __on_even_doubleclick(self, event:tk.Event):
        
        #prvents errors when clicking empty box
        if(len(self.__listbox.curselection()) == 0):
            return
        
        index:int = event.widget.curselection()[0]
        self.__logic.mark_entry_done(index)

 
        
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
        #self.__listbox.destroy()
        self.__listbox.delete(0, tk.END)
        self.__listbox.insert(tk.END, *self.__logic.get_entry_display_strings())
        self.__listbox.config(height = self.__listbox.size())
        #self.__todo_list_items.set(self.__list_objects)
        #self.__listbox.configure(height = len(self.__list_objects))
        
    def __add_todo(self):
        def show_add_windows():
            def on_save():
                self.__on_new_entry(MappingProxyType({"title": title_var.get(), 
                                                      "info": info_var.get()}
                                                     )
                                    ) 
                add_task_widnow.destroy()
                
            add_task_widnow: Toplevel = Toplevel(self)
            add_task_widnow.title("New ToDo!")
            
            #TODO
            add_task_widnow.geometry('%dx%d+%d+%d' % (100, 200, self.winfo_pointerx()-100/2, self.winfo_pointery()-50))
            
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
                                   command = add_task_widnow.destroy
                        )
            btn_cancel.pack()
            
        
        show_add_windows()
        
        
    def start(self):
        self.mainloop()
        


if __name__ == "__main__":
    ToDoGUI().start()