import tkinter as tk
from idlelib.colorizer import ColorDelegator
from idlelib.percolator import Percolator

root = tk.Tk()
text = tk.Text(root)
text.pack()

# 应用语法高亮
p = Percolator(text)
d = ColorDelegator()
p.insertfilter(d)

root.mainloop()
