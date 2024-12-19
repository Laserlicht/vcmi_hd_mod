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
from tkinter import messagebox
import os
import multiprocessing
import tempfile

TEST = False

def main():
    if TEST:
        input_path = "/tmp/test/Heroes of Might & Magic III - HD Edition"
        temp_path = "/tmp/test/tmp"
        output_path = "/tmp/test/out"

        extract_assets(input_path, temp_path)
        create_mod(temp_path, output_path)
    else:
        messagebox.showinfo("showinfo", "Please select the installation folder for Heroes of Might & Magic III - HD Edition.")
        input_path = askdirectory()
        if not isinstance(input_path, str) or not os.path.exists(os.path.join(input_path, "HOMM3 2.0.exe")):
            messagebox.showinfo("showerror", "Heroes of Might & Magic III - HD Edition folder not found!")
            return
        messagebox.showinfo("showinfo", "Please select the output folder for the created mod.") 
        output_path = askdirectory()
        if not isinstance(output_path, str):
            messagebox.showinfo("showerror", "No output folder selected!")
            return
        
        messagebox.showinfo("showinfo", "The conversion process will start after pressing OK. It will run in the background and may take some time (~1 hour). Please be patient. You will be notified upon completion.") 
        
        temp_path = tempfile.TemporaryDirectory()
        extract_assets(input_path, temp_path.name)
        create_mod(temp_path.name, output_path)
        try:
            temp_path.cleanup()
        except:
            pass

        messagebox.showinfo("showinfo", "The conversion process is complete. Please copy the folder in the output directory to the mod directory of VCMI.")         

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
