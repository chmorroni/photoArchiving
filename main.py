
import datetime
import os
import piexif
from PIL import Image, ImageTk
import tkinter
from tkinter import filedialog


class DateEntry(tkinter.Frame):
    def __init__(self, master, frame_look={}, **look):
        args = dict(relief=tkinter.SUNKEN, border=1)
        args.update(frame_look)
        tkinter.Frame.__init__(self, master, **args)

        args = {'relief': tkinter.FLAT}
        args.update(look)

        self.entry_1 = tkinter.Entry(self, width=2, **args)
        self.label_1 = tkinter.Label(self, text='/', **args)
        self.entry_2 = tkinter.Entry(self, width=2, **args)
        self.label_2 = tkinter.Label(self, text='/', **args)
        self.entry_3 = tkinter.Entry(self, width=4, **args)

        self.entry_1.pack(side=tkinter.LEFT)
        self.label_1.pack(side=tkinter.LEFT)
        self.entry_2.pack(side=tkinter.LEFT)
        self.label_2.pack(side=tkinter.LEFT)
        self.entry_3.pack(side=tkinter.LEFT)

        self.entries = [self.entry_1, self.entry_2, self.entry_3]

        self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 2))
        self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))
        self.entry_3.bind('<KeyRelease>', lambda e: self._check(2, 4))

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, tkinter.END)
        entry.insert(0, cont[:-1])

    def _check(self, index, size):
        entry = self.entries[index]
        next_index = index + 1
        next_entry = self.entries[next_index] if next_index < len(self.entries) else None
        data = entry.get()

        if len(data) > size or not data.isdigit():
            self._backspace(entry)
        if len(data) >= size and next_entry:
            next_entry.focus()

    def get(self):
        return [e.get() for e in self.entries]


class Window:
    max_dim = 800

    def __init__(self, master):
        self.master = master
        
        self.master.title("Photo Editor")
        
        self.viewer = tkinter.Label(self.master, width=self.max_dim, height=self.max_dim)
        self.viewer.grid(row=0, column=0, columnspan=6, padx=10, pady=10)
        
        self.date_box = DateEntry(self.master)
        self.date_box.grid(row=1, column=2, padx=10)
        
        self.date_button = tkinter.Button(self.master, text="Set Date", width=10, height=1)
        self.date_button.grid(row=3, column=2, padx=10)
        
        self.old_date_label = tkinter.Label(self.master)
        self.old_date_label.grid(row=1, column=1)
        self.set_last_date( datetime.datetime(2019, 1, 1, 12) )
        
        self.old_date_button = tkinter.Button(self.master, text="Use Old Date", width=10, height=1)
        self.old_date_button.grid(row=3, column=1, padx=10)
        
        self.comment_box = tkinter.Entry(self.master, width=40)
        self.comment_box.grid(row=1, column=3, padx=10)
        
        self.comment_button = tkinter.Button(self.master, text="Add Comment", width=12, height=1)
        self.comment_button.grid(row=3, column=3, sticky=tkinter.E, padx=10)
        
        self.rotate_cw_button = tkinter.Button(self.master, text="Rotate CW", width=10, height=1)
        self.rotate_cw_button.grid(row=1, column=4, padx=10)
        
        self.rotate_ccw_button = tkinter.Button(self.master, text="Rotate CCW", width=10, height=1)
        self.rotate_ccw_button.grid(row=3, column=4, padx=10)
        
        self.left = tkinter.Frame(self.master, width=10)
        self.left.grid(row=1, column=0)
        
        self.right = tkinter.Frame(self.master, width=10)
        self.right.grid(row=1, column=5)
        
        self.blank_row_0 = tkinter.Frame(self.master, height=10)
        self.blank_row_0.grid(row=2, column=0)
        
        self.blank_row_1 = tkinter.Frame(self.master, height=10)
        self.blank_row_1.grid(row=4, column=0)
        
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=0)
        self.master.grid_columnconfigure(2, weight=0)
        self.master.grid_columnconfigure(3, weight=0)
        self.master.grid_columnconfigure(4, weight=0)
        self.master.grid_columnconfigure(5, weight=1)
        
    def update_image(self, path):
        self.current_image = Image.open(path)
        
        factor = self.max_dim / max(self.current_image.width, self.current_image.height)
        size = (int(self.current_image.width * factor), int(self.current_image.height * factor))
        image = ImageTk.PhotoImage( Image.open(path).resize(size) )
        self.viewer.configure(image=image)
        self.viewer.image = image
        
    def close_image(self):
        self.current_image.close()
    
    def set_last_date(self, date):
        self.last_date = date
        self.old_date_label.configure( text=self.last_date.strftime("%m/%d/%Y") )
        

class App:
    image_idx = 0

    def __init__(self, images, dir):
        self.images = images
        self.dir = dir
        
        self.application = tkinter.Tk()
        self.gui = Window(self.application)
        self.gui.update_image( self.build_path(self.dir, self.images[0]) )
        
        self.gui.date_button.configure(command=self.set_date_from_box)
        self.gui.old_date_button.configure(command=self.set_old_date)
        self.gui.rotate_cw_button.configure(command=self.rotate_image_cw)
        self.gui.rotate_ccw_button.configure(command=self.rotate_image_ccw)
        self.gui.comment_button.configure(command=self.add_comment)
        
        self.application.mainloop()
        
    def exit(self):
        self.application.quit()
        
    def build_path(self, dir, file):
        return os.path.join(dir, file)
    
    def next_image(self):
        self.gui.close_image()
        
        self.image_idx += 1
        if self.image_idx < len(self.images):
            self.gui.update_image( self.build_path(self.dir, self.images[self.image_idx]) )
        else:
            self.gui.master.quit()
            
    def rotate_image_cw(self):
        path = self.build_path(self.dir, self.images[self.image_idx])
        image = Image.open(path)
        image = image.rotate(-90, expand=1)
        image.save(path)
        self.gui.update_image(path)
            
    def rotate_image_ccw(self):
        path = self.build_path(self.dir, self.images[self.image_idx])
        image = Image.open(path)
        image = image.rotate(90, expand=1)
        image.save(path)
        self.gui.update_image(path)
    
    def set_date_from_box(self):
        try:
            date_str = self.gui.date_box.get()
            date = datetime.datetime(int(date_str[2]), int(date_str[0]), int(date_str[1]), 12)
            self.set_date(date)
        except:
            pass
        
    def set_old_date(self):
        self.set_date(self.gui.last_date)
        
    def set_date(self, date):
        old_path = self.build_path(self.dir, self.images[self.image_idx])
        new_jpg_path = os.path.join(self.dir, "jpgs", os.path.splitext(self.images[self.image_idx])[0] + ".jpg")
        new_tif_path = os.path.join(self.dir, "tifs", self.images[self.image_idx])
        
        self.next_image()
        self.gui.set_last_date(date)
        
        image = Image.open(old_path)
        image.save(new_jpg_path, format="JPEG", quality=100)
        
        metadata = piexif.load(new_jpg_path)
        metadata["Exif"] = { piexif.ExifIFD.DateTimeOriginal: date.strftime("%Y:%m:%d %H:%M:%S") }
        metadata_bytes = piexif.dump(metadata)
        piexif.insert(metadata_bytes, new_jpg_path)
        
        os.rename(old_path, new_tif_path)
    
    def add_comment(self):
        with open(os.path.join(self.dir, "log.csv"), "a") as file:
            out_line = self.images[self.image_idx] + "," + self.gui.comment_box.get() + "\n"
            file.write(out_line)
            self.gui.comment_box.delete(0, tkinter.END)


def get_files(dir, ext):
    files = []
    
    for file in os.listdir(dir):
        _, file_ext = os.path.splitext(file)
        if file_ext == ext:
            files.append(file)
            
    return files

if __name__ == "__main__":
    dir = "test"
    images = get_files(dir, ".tif")
    
    if not os.path.isdir( os.path.join(dir, "jpgs") ):
        os.mkdir( os.path.join(dir, "jpgs") )
    if not os.path.isdir( os.path.join(dir, "tifs") ):
        os.mkdir( os.path.join(dir, "tifs") )
        
    app = App(images, dir)
