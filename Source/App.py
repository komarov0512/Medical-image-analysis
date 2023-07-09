import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
import tkinter as tk
from tkinter import filedialog
from gray import ImageAnaliz
from tkinter import ttk
import tkinter.messagebox as mb

# Initialize Tkinter
root = tk.Tk()
root.state('zoomed')


# Function for close app
def quit_me():
    root.quit()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", quit_me)


# Create class ImageAnaliz
imgAnaliz = ImageAnaliz()

# Initialize Matplotlib Figure
fig, axs = plt.subplots(nrows=1, ncols=2)
ax = plt.gca()
fig.suptitle("Загрузите изображение")
im1 = axs[0].imshow(np.arange(24).reshape((6, 4))[..., ::-1])
im2 = axs[1].imshow(np.arange(24).reshape((6, 4)), "gray")


# Function for upload image
def upload_file():
    # Allowed types of file
    f_types = [('Image Files', ('*png', '*jpg', '*jpeg'))]
    # Get File Name
    filename = tk.filedialog.askopenfilename(filetypes=f_types)
    # Loading Image
    imgAnaliz.set_image(filename)
    # First Call Matplotlib Figure
    change(60)


# Function for refresh plots in App
def change(value):
    # Call function getThreshold from class ImageAnaliz
    img, th, title = imgAnaliz.getThreshold(round(float(value)))
    # Set title on the plots
    fig.suptitle(title)
    # Set images on the plots
    im1.set_data(img[..., ::-1])
    im2.set_data(th)
    # Refresh canvas
    canvas.draw()


# Function for get areas and counters
def bt_getAreas():
    imgAnaliz.mainFunc(float(en1.get()), float(en2.get()))
    msg = "Программа выполнена.\nВся информация успешно сохранена!\nВы можете найти её в папке с программой."
    mb.showinfo("Уведомление", msg)


# -------------STYLE
s = ttk.Style()
s.configure("Frame.TFrame", background='#90c0e0')

# -----------WIDGETS
# Create Canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=0, sticky='NSWE')

# Create Slider Frame
scaleframe = ttk.Frame(root, height=100, style='Frame.TFrame')
scaleframe.grid(row=1, column=0, sticky='NSWE')

# Create Slider
val = tk.IntVar(value=60)
scale = tk.Scale(scaleframe, orient=tk.HORIZONTAL, length=640, from_=1, to=255,
                 command=change, variable=val, background='#90c0e0')
scale.pack()

# Right Vertical Frame
verticalframe = ttk.Frame(root, width=200, style='Frame.TFrame')
verticalframe.grid(row=0, column=1, rowspan=2, sticky="NWSE")

# Button open file
btnOpen = ttk.Button(verticalframe, width=20, text="Открыть файл", command=upload_file)
btnOpen.pack(padx=10, pady=10)

lbInf1 = ttk.Label(verticalframe, width=21, text="Введите Global Thresh:")
lbInf1.pack(padx=10, pady=5)

lb1 = ttk.Label(verticalframe, width=21, text="Введите обл. язв (V)")
lb1.pack(padx=10, pady=5)
en1 = ttk.Entry(verticalframe, width=21)
en1.pack(padx=10, pady=5)

lb2 = ttk.Label(verticalframe, width=21, text="Введите обл. корич (V)")
lb2.pack(padx=10, pady=5)
en2 = ttk.Entry(verticalframe, width=21)
en2.pack(padx=10, pady=5)

# Button get area
btn = ttk.Button(verticalframe, width=20, text="Выполнить", command=bt_getAreas)
btn.pack(padx=10, pady=5)

# --------GRID-CONFIG
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# ----RUN-APPLICATION
canvas.draw()
root.mainloop()
