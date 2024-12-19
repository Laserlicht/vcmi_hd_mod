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
import json
import zipfile
import pandas as pd
from PIL import Image, ImageFilter, ImageEnhance
import multiprocessing
from sd_lod_sprites_data import get_data
from helper import get_stroke

def create_mod(in_folder, out_folder):
    out_folder = os.path.join(out_folder, "hd_version")
    os.makedirs(out_folder, exist_ok=True)

    with multiprocessing.Pool() as pool:
        for result in pool.starmap(create_mod_task, [
            (in_folder, out_folder, "2"),
            (in_folder, out_folder, "3")
        ]):
            pass

def create_mod_task(in_folder, out_folder, scale):
    df = get_data()
    df_pak = None
    for filename in os.listdir(in_folder):
        if filename.endswith("-info.csv"):
            if df_pak is None:
                df_pak = pd.read_csv(os.path.join(in_folder, filename), sep=";", header=None, names=range(20))
            else:
                df_pak = pd.concat([df_pak, pd.read_csv(os.path.join(in_folder, filename), sep=";", header=None, names=range(20))])
    df_flag = pd.read_csv(os.path.join(in_folder, "data", "spriteFlagsInfo.txt"), sep=" ", names=range(20), header=None)

    # flag images
    flag_path = os.path.join(in_folder, "data", "flags")
    flag_img_tmp = {
        2: Image.open(os.path.join(flag_path, "flag_grey_x2.png")),
        3: Image.open(os.path.join(flag_path, "flag_grey.png"))
    }
    flag_img = [
        flag_img_tmp,
        {x:y.transpose(Image.FLIP_LEFT_RIGHT) for x, y in flag_img_tmp.items()}
    ]
    flag_img = [{x2:ImageEnhance.Brightness(y2).enhance(2.5) for x2, y2 in x.items()} for x in flag_img] #brighten flags

    lang = os.listdir(os.path.join(in_folder, "bitmap_DXT_loc_x" + scale + ".pak"))[0]

    out_folder_main = os.path.join(out_folder, "mods", "x" + scale)
    os.makedirs(out_folder_main, exist_ok=True)
    out_folder_translation = os.path.join(out_folder, "mods", "x" + scale + "_translation_" + lang.lower())
    os.makedirs(out_folder_translation, exist_ok=True)

    with open(os.path.join(out_folder, "mod.json"), "w") as f:
        f.write(create_mod_config())
    with open(os.path.join(out_folder_main, "mod.json"), "w") as f:
        f.write(create_main_mod_config(scale))
    with open(os.path.join(out_folder_translation, "mod.json"), "w") as f:
        f.write(create_lang_mod_config(scale, lang))

    for name, destination in { "bitmap_DXT_com_x" + scale + ".pak": out_folder_main, "bitmap_DXT_loc_x" + scale + ".pak": out_folder_translation }.items():
        with zipfile.ZipFile(os.path.join(destination, "content.zip"), mode="w", compression=zipfile.ZIP_STORED) as archive:
            path = os.path.join(in_folder, name, lang if "loc" in name else "")
            for file in os.listdir(path):
                handle_bitmaps(archive, path, file, scale)

    for name, destination in { "sprite_DXT_com_x" + scale + ".pak": out_folder_main, "sprite_DXT_loc_x" + scale + ".pak": out_folder_translation }.items():
        with zipfile.ZipFile(os.path.join(destination, "content.zip"), mode="a", compression=zipfile.ZIP_STORED) as archive:
            path = os.path.join(in_folder, name, lang if "loc" in name else "")

            grouped_df = df.groupby('defname')
            for name, group in grouped_df:
                folders = [x.upper() for x in os.listdir(path)]
                if name.upper() in folders:
                    folder = os.listdir(path)[folders.index(name.upper())]
                    handle_sprites(archive, path, folder, scale, group, df_pak[df_pak[1].str.upper() == folder.upper()], df_flag, flag_img)

def handle_bitmaps(archive, path, file, scale):
    name = os.path.splitext(file)[0]

    # Skip RoE specific files
    if name.upper() in [ "MAINMENU", "GAMSELBK", "GSELPOP1", "SCSELBCK", "LOADGAME", "NEWGAME", "LOADBAR" ]:
        return

    archive.writestr("data" + scale + "x/" + os.path.splitext(file)[0] + ".png", open(os.path.join(path, file), "rb").read())

def handle_sprites(archive, path, folder, scale, df, df_pak, df_flag, flag_img):
    data = {x:open(os.path.join(path, folder, x), "rb").read() for x in os.listdir(os.path.join(path, folder))}
    s = int(scale)

    # skip menu buttons (RoE)
    if folder.upper() in ["MMENUNG", "MMENULG", "MMENUHS", "MMENUCR", "MMENUQT", "GTSINGL", "GTMULTI", "GTCAMPN", "GTTUTOR", "GTBACK", "GTSINGL", "GTMULTI", "GTCAMPN", "GTTUTOR", "GTBACK"]:
        return
    
    # skip dialogbox - coloring not supported yet by vcmi
    if folder.upper() in ["DIALGBOX"]:
        return

    # skip water + rivers special handling - paletteAnimation - not supported yet by vcmi
    if folder.upper() in ["WATRTL", "LAVATL"] + ["CLRRVR", "MUDRVR", "LAVRVR"]:
        return

    # resize def
    max_size_x = df["full_width"].max() * s
    max_size_y = df["full_height"].max() * s
    for item in data.keys():
        name = os.path.splitext(item.replace(".shadow", ""))[0].upper()
        df_tmp = df[df["imagename"].str.upper() == name]
        df_pak_tmp = df_pak[(df_pak[2].str.upper() == name) & (df_pak[0].str.lower().str.contains("x" + scale))]
        if len(df_tmp) > 0:
            df_row = df_tmp.iloc[0]
            offset_sdhd_x = df_pak_tmp.iloc[0][4]
            offset_sdhd_y = df_pak_tmp.iloc[0][6]
            img = Image.open(io.BytesIO(data[item]))
            tmpimg = Image.new(img.mode, (max_size_x, max_size_y), (255, 255, 255, 0))
            tmpimg.paste(img, ((df_row["left_margin"] - offset_sdhd_x) * s, (df_row["top_margin"] - offset_sdhd_y) * s))
            img_byte_arr = io.BytesIO()
            tmpimg.save(img_byte_arr, format='PNG')
            data[item] = img_byte_arr.getvalue()
    
    # add flag overlay images
    for item in list(data.keys()):
        name = os.path.splitext(item)[0]
        df_flag_tmp = df_flag[df_flag[0].str.upper() == name.upper()]
        if len(df_flag_tmp) > 0:
            df_flag_tmp = df_flag_tmp.iloc[0]
            img = Image.open(io.BytesIO(data[item]))
            img = Image.new(img.mode, (img.width, img.height), (255, 255, 255, 0))
            for i in range(df_flag_tmp[1]):
                flag = flag_img[int(df_flag_tmp[4+i*3])][s]
                img.paste(flag, (int(df_flag_tmp[2+i*3])*s, int(df_flag_tmp[3+i*3])*s), flag)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                data[name + "-overlay.png"] = img_byte_arr.getvalue()

    # create outlines for creatures as overlay
    for item in list(data.keys()):
        name = os.path.splitext(item)[0]
        creature_images = [x.upper() for x in ["smbal", "smcart", "smcata", "smtent"] + ["CABEHE", "CADEVL", "CAELEM", "CALIZA", "CAMAGE", "cangel", "CAPEGS", "CBASIL", "CBDRGN", "CBDWAR", "cbehol", "Cbgog", "CBKNIG", "CBLORD", "CBTREE", "CBWLFR", "CCAVLR", "CCENTR", "CCERBU", "Ccgorg", "CCHAMP", "cchydr", "CCMCOR", "Ccrusd", "CcyclLor", "CCYCLR", "CDDRAG", "CDEVIL", "CDGOLE", "CDRFIR", "CDRFLY", "CDWARF", "CECENT", "CEELEM", "cefree", "cefres", "CELF", "Ceveye", "CFAMIL", "CFELEM", "CGARGO", "CGBASI", "CGDRAG", "CGENIE", "CGGOLE", "CGNOLL", "CGNOLM", "CGOBLI", "CGOG", "CGRELF", "CGREMA", "CGREMM", "CGRIFF", "CGTITA", "chalbd", "CHARPH", "CHARPY", "CHCBOW", "CHDRGN", "CHGOBL", "CHHOUN", "CHYDRA", "CIGOLE", "CIMP", "Citrog", "CLCBOW", "CLICH", "CLTITA", "CMAGE", "CMAGOG", "CMCORE", "Cmeduq", "Cmedus", "Cminok", "CMINOT", "Cmonkk", "CNAGA", "CNAGAG", "CNDRGN", "CNOSFE", "COGARG", "COGMAG", "COGRE", "COHDEM", "CORCCH", "CORC", "CPEGAS", "CPFIEN", "CPFOE", "CPKMAN", "CPLICH", "CPLIZA", "CRANGL", "CRDRGN", "Crgrif", "CROC", "CSGOLE", "CSKELE", "CSULTA", "Csword", "CTBIRD", "CTHDEM", "CTREE", "Ctrogl", "CUNICO", "CUWLFR", "CVAMP", "CWELEM", "CWIGHT", "CWRAIT", "CWSKEL", "CWUNIC", "CWYVER", "CWYVMN", "CYBEHE", "Czealt", "CZOMBI", "CZOMLO"]]
        if name.upper().startswith(tuple(creature_images)) and "shadow".upper() not in name.upper():
            img = Image.open(io.BytesIO(data[item]))
            img = get_stroke(img, 2 if s == 2 else 3)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            data[name + "-overlay.png"] = img_byte_arr.getvalue()

    # prison & elem conflux needs empty overlay
    if folder.upper() in ["AVXPRSN0", "AVGELEM0"]:
        for item in list(data.keys()):
            name = os.path.splitext(item)[0]
            img = Image.open(io.BytesIO(data[item]))
            img = Image.new(img.mode, (img.width, img.height), (255, 255, 255, 0))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            data[name + "-overlay.png"] = img_byte_arr.getvalue()

    for file, content in data.items():
        file = file.replace(".shadow", "-shadow")
        archive.writestr("sprites" + scale + "x/" + folder + "/" + file, content)
    archive.writestr("sprites" + scale + "x/" + folder + ".json", create_animation_config(folder, data.keys(), df))

def create_mod_config():
    conf = {
        "name": "Heroes III HD Edition",
        "description": "Extracted resources from the official Heroes of Might & Magic III - HD Edition to make them usable in VCMI.",
        "author": "Ubisoft",
        "contact": "vcmi.eu",
        "modType": "Graphical",
        "version": "1.0",
        
        "czech" : {
            "name": "Heroes III HD Edition",
            "description": "Extrahované zdroje z oficiální edice Heroes of Might & Magic III - HD Edition, které je možné použít ve VCMI."
        }
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)

def create_main_mod_config(scale):
    conf = {
        "author": "Ubisoft",
        "contact": "vcmi.eu",
        "description": "Resources (x" + scale + ")",
        "modType": "Graphical",
        "name": "HD (x" + scale + ")",
        "version": "1.0"
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)

def create_lang_mod_config(scale, language):
    languages = {
        "CH": "chinese",
        "CZ": "czech",
        "DE": "german",
        "EN": "english",
        "ES": "spanish",
        "FR": "french",
        "IT": "italian",
        "PL": "polish",
        "RU": "russian"
    }

    conf = {
        "author": "Ubisoft",
        "contact": "vcmi.eu",
        "description": "Translated resources (x" + scale + ")",
        "modType": "Translation",
        "name": "HD Localization (" + languages[language] + ") (x" + scale + ")",
        "version": "1.0",
        "language": languages[language]
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)

def create_animation_config(name, files, df):
    files = sorted(files)

    conf = {
        "basepath": name + "/",
        "images": [
            {
                "group": row["group"],
                "frame": row["frame"],
                "file": row["imagename"] + ".png"
            }
            for i, row in df.iterrows()
            if row["imagename"].upper() in [os.path.splitext(x)[0].upper() for x in files]
        ]
    }
    return json.dumps(conf, indent=4, ensure_ascii=False)
