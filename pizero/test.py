import tkinter
import PIL
from PIL import Image, ImageDraw, ImageTk

window = tkinter.Tk()
im = PIL.Image.new(mode="RGB", size=(200, 200))
d = ImageDraw.Draw(im)
d.circle((50, 50), 50, fill="yellow")
i = ImageTk.PhotoImage(im)
label1 = tkinter.Label(image=i)
label1.image = i
# Position image
label1.pack()
window.mainloop()
