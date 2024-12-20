#!/usr/bin/env python3
#
# MIT License
# 
# Copyright (c) 2024 Laserlicht
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from extract import extract_assets
from create_mod import create_mod
from tkinter.filedialog import askdirectory
from tkinter import messagebox, Label, Tk, HORIZONTAL, IntVar
from tkinter.ttk import Progressbar
import os
import multiprocessing
import tempfile
import threading
import time
from pathlib import Path

TEST = False
TITLE = "Heroes of Might & Magic III - HD Edition Mod Creator for VCMI"

class Progress(Tk):
    def __init__(self, destpaths):
        Tk.__init__(self)

        self.title(TITLE)
        self.resizable(0, 0)
        self.eval('tk::PlaceWindow . center')

        progress = IntVar()
        
        self.label = Label(self, text="HD Edition Mod is created... Please wait!")
        self.progress = Progressbar(self, orient=HORIZONTAL, length=200, maximum=1000, variable=progress)
        self.label.pack(pady=10, padx=10)
        self.progress.pack(pady=10, padx=10)

        def update(destpaths):
            try:
                while True:
                    max_size = 4_793_170_141 + 3_698_241_492
                    size = sum([sum(f.stat().st_size for f in Path(destpath).glob('**/*') if f.is_file()) for destpath in destpaths])
                    percent = size / max_size
                    progress.set(min(percent, 0.999999) * 1000)
                    time.sleep(5)
            except: pass
        threading.Thread(target=update, args=(destpaths,)).start()

def progresswindow(destpaths):
    app = Progress(destpaths)
    app.mainloop()
            
def main():
    if TEST:
        input_path = "/tmp/test/Heroes of Might & Magic III - HD Edition"
        temp_path = "/tmp/test/tmp"
        output_path = "/tmp/test/out"

        extract_assets(input_path, temp_path)
        create_mod(temp_path, output_path)
    else:
        messagebox.showinfo(TITLE, "Please select the installation folder of Heroes of Might & Magic III - HD Edition.")
        input_path = askdirectory()
        if not isinstance(input_path, str) or not os.path.exists(os.path.join(input_path, "HOMM3 2.0.exe")):
            messagebox.showinfo(TITLE, "Heroes of Might & Magic III - HD Edition folder not found!")
            return
        messagebox.showinfo(TITLE, "Please select the output folder for the created mod.") 
        output_path = askdirectory()
        if not isinstance(output_path, str):
            messagebox.showinfo(TITLE, "No output folder selected!")
            return
        
        messagebox.showinfo(TITLE, "The conversion process will start after pressing OK. It may take some time (~1 hour). Please be patient.") 

        temp_path = tempfile.TemporaryDirectory()

        p = multiprocessing.Process(target=progresswindow, args=([temp_path.name, os.path.join(output_path, "hd_version")],))
        p.start()

        extract_assets(input_path, temp_path.name)
        create_mod(temp_path.name, output_path)
        try:
            temp_path.cleanup()
        except:
            pass

        try:
            p.kill()
        except: pass

        messagebox.showinfo(TITLE, "The conversion process is complete. Please copy the folder in the output directory to the mod directory of VCMI.")         

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
