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

import os
import io
import zlib
import shutil
from PIL import Image
import multiprocessing

def extract_assets(in_folder, out_folder, save_dds=False):
    data_dir = os.path.join(in_folder, "data")
    shutil.copytree(data_dir, os.path.join(out_folder, "data"), dirs_exist_ok=True)

    with multiprocessing.Pool() as pool:
        for result in pool.starmap(extract_task, [
            ("2", "bitmap", data_dir, out_folder, save_dds),
            ("3", "bitmap", data_dir, out_folder, save_dds),
            ("2", "sprite", data_dir, out_folder, save_dds),
            ("3", "sprite", data_dir, out_folder, save_dds)
        ]):
            pass

def extract_task(scale, contains, data_dir, out_folder, save_dds):
    for filename in os.listdir(data_dir):
        if filename.lower().endswith(".pak") and "x" + scale in filename and contains in filename:
            full_name = os.path.join(data_dir, filename)
            __extract_pak(full_name, "", out_folder, save_dds)
    for filename in os.listdir(os.path.join(data_dir, 'LOC', list(os.listdir(os.path.join(data_dir, 'LOC')))[0])):
        if filename.lower().endswith(".pak") and "x" + scale in filename and contains in filename:
            lang = list(os.listdir(os.path.join(data_dir, 'LOC')))[0]
            full_name = os.path.join(data_dir, 'LOC', lang, filename)
            __extract_pak(full_name, lang, out_folder, save_dds)

def __extract_pak(file, lang, out_folder, save_dds):
    if os.path.isfile(os.path.join(out_folder, file + "-info.csv")):
        os.remove(os.path.join(out_folder, file + "-info.csv"))

    with open(file, 'rb') as f:
        f.read(4) # dummy
        info_offset = int.from_bytes(f.read(4), byteorder='little')
        f.seek(info_offset)
        files = int.from_bytes(f.read(4), byteorder='little')
        offset_name = f.tell()
        for i in range(files):
            f.seek(offset_name)
            name = f.read(8).split(b'\0', 1)[0].decode()
            f.read(12) # dummy
            offset = int.from_bytes(f.read(4), byteorder='little')
            dummy_size = int.from_bytes(f.read(4), byteorder='little')
            chunks = int.from_bytes(f.read(4), byteorder='little')
            zsize = int.from_bytes(f.read(4), byteorder='little')
            size = int.from_bytes(f.read(4), byteorder='little')
            chunk_zsize_arr = []
            for j in range(chunks):
                chunk_zsize = int.from_bytes(f.read(4), byteorder='little')
                chunk_zsize_arr.append(chunk_zsize)
            chunk_size_arr = []
            for j in range(chunks):
                chunk_size = int.from_bytes(f.read(4), byteorder='little')
                chunk_size_arr.append(chunk_size)
            offset_name = f.tell()

            f.seek(offset)
            image_config = f.read(dummy_size).decode()
            offset += dummy_size

            data = bytearray(b'')
            data_compressed = bytearray(b'')
            for j in range(chunks):
                f.seek(offset)
                if chunk_zsize_arr[j] == chunk_size_arr[j]:
                    data += bytearray(f.read(chunk_size))
                else:
                    data_compressed += bytearray(f.read(zsize))
                offset += chunk_zsize
            if len(data_compressed) != 0:
                to_decompress = data_compressed
                data_compressed = []
                while len(to_decompress) > 0:
                    dec = zlib.decompressobj()
                    try:
                        data_compressed.append(dec.decompress(to_decompress))
                        to_decompress = dec.unused_data
                    except:
                        break
                pass
            if len(data) < len(data_compressed):
                data = data_compressed
            else:
                data = [data]
            
            __extract_images(os.path.basename(file), name, image_config, data, lang, out_folder, save_dds)

def __extract_images(file, name, image_config, data, lang, out_folder, save_dds):
    img = [Image.open(io.BytesIO(x)) for x in data]
    for line in image_config.split('\r\n'):
        tmp = line.split(' ')
        if len(tmp) > 11:
            img_name = tmp[0]
            img_nr = int(tmp[1])
            img_val1 = int(tmp[2]) # x offset between hd and sd sprites
            img_val2 = int(tmp[3])
            img_val3 = int(tmp[4]) # y offset between hd and sd sprites
            img_val4 = int(tmp[5])
            img_x = int(tmp[6])
            img_y = int(tmp[7])
            img_width = int(tmp[8])
            img_height = int(tmp[9])
            img_rotation = int(tmp[10])
            img_has_shadow = int(tmp[11])

            img_crop = img[img_nr]
            img_crop = img_crop.crop((img_x, img_y, img_x+img_width, img_y+img_height))
            img_crop = img_crop.rotate(-90 * img_rotation, expand=True)

            img_shadow_crop = None
            if img_has_shadow == 1:
                img_shadow_nr = int(tmp[12])
                img_shadow_x = int(tmp[13])
                img_shadow_y = int(tmp[14])
                img_shadow_width = int(tmp[15])
                img_shadow_height = int(tmp[16])
                img_shadow_rotation = int(tmp[17])

                img_shadow_crop = img[img_shadow_nr]
                img_shadow_crop = img_shadow_crop.crop((img_shadow_x, img_shadow_y, img_shadow_x+img_shadow_width, img_shadow_y+img_shadow_height))
                img_shadow_crop = img_shadow_crop.rotate(-90 * img_shadow_rotation, expand=True)

            with open(os.path.join(out_folder, file + "-info.csv"), "a") as f:
                f.write("%s;%s;%s\r\n"%(file, name, line.replace(' ', ';')))

            if 'sprite' in file.lower():
                if not os.path.exists(os.path.join(out_folder, file, lang, name)): os.makedirs(os.path.join(out_folder, file, lang, name), exist_ok=True)
                img_crop.save(os.path.join(out_folder, file, lang, name, img_name + ".png"))
                
                if img_shadow_crop is not None:
                    img_shadow_crop.save(os.path.join(out_folder, file, lang, name, img_name + ".shadow.png"))
            else:
                if not os.path.exists(os.path.join(out_folder, file, lang)): os.makedirs(os.path.join(out_folder, file, lang), exist_ok=True)
                img_crop.save(os.path.join(out_folder, file, lang, img_name + ".png"))
                if img_shadow_crop is not None:
                    img_shadow_crop.save(os.path.join(out_folder, file, lang, img_name + ".shadow.png"))
    if save_dds:
        for i in range(len(img)):
            img[i].save(os.path.join(out_folder, file, lang, name + "." + str(i) + ".dds.png"))
            open(os.path.join(out_folder, file, lang, name + "." + str(i) + ".dds"), 'wb').write(data[i])
