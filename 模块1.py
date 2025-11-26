
import tkinter as tk, threading, time
from tkinter import ttk
root = tk.Tk(); root.withdraw()
w = tk.Toplevel(root); w.geometry('600x360'); ttk.Label(w, text='²âÊÔ´°¿Ú').pack(); txt = tk.Text(w); txt.pack(fill='both', expand=True)
w.deiconify(); w.lift(); w.attributes('-topmost', True)
def worker():
    for i in range(5):
        txt.configure(state='normal'); txt.insert('end', f'line {i}\\n'); txt.configure(state='disabled')
        time.sleep(0.6)
    w.after(500, w.destroy)
threading.Thread(target=worker, daemon=True).start()
# process events so window is responsive
while w.winfo_exists():
    root.update(); time.sleep(0.05)