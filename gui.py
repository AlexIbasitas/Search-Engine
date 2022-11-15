# gui.py
from datetime import datetime
import tkinter as tk
import tkinter.ttk as ttk

from scipy.__config__ import show
from invertedIndex import invertedIndex

i = invertedIndex('./DEV', "docHash.json", "offsets.json", 55393)

window = tk.Tk()
window.title("Web Browser")
window.resizable(width=True, height=True)

# frame0 = tk.Frame()

frame1 = tk.Frame()

frame2 = tk.Frame()

frame3 = tk.Frame()

txt_response = tk.Text(window,
    height=20,
    width=115,
    # master=frame0
)
txt_response.pack(expand=True, fill='both')

lbl_web = ttk.Label(
    text="Enter a Query:",
    foreground="white",  # Set the text color to white
    background="black",  # Set the background color to black
    master=frame1
)
lbl_web.pack()


ent_query = tk.Entry(fg="black",
                     bg="white",
                     width=50,
                     master=frame2
)
ent_query.pack()
'''
Retrieving text with .get()
Deleting text with .delete()
Inserting text with .insert()
'''

btn_search = ttk.Button(
    text="Search",
    master=frame3
)
btn_search.pack()
'''
Make button use .get() to get the text and executre the query
'''

def handle_click(event):
    search(ent_query.get())

def search(query: str):
    query = query.strip().lower()
    if 'quit()' == query:
        window.destroy()
        return
    txt_response.delete('0.0', 'end')
    txt_response.insert('0.0',f'Processing query: {query}\n')
    start_time = datetime.now()
    response = i.handleCosineQuery(query)
    end_time = datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000

    

    showtext = ""

    if response == 'no files pertain to your search':
        txt_response.insert(response)
    else:
        for q, (v,s) in enumerate(response, 1): 
            showtext += f"{q}) {v}\t(score: {s})\n"
    showtext += f"Time: {execution_time}\n"
    showtext += f"Enter 'quit()' to leave"
    
    txt_response.insert('end',showtext)

btn_search.bind("<Button-1>", handle_click)




frame1.pack()
frame2.pack()
frame3.pack()
window.mainloop()
