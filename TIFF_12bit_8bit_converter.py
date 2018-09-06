# -*- cording: utf-8 -*-
import tifffile
import cv2
import numpy as np
import glob
import os, tkinter, tkinter.filedialog, tkinter.messagebox
from itertools import chain


def directory_select():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("All files","*"),("TIFF","tif")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo("TIFF8bit変換","対象の画像を選択してください")
    input_dir = os.path.dirname(tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir))

    if not input_dir:
        print("ファイルが選択されませんでした")
        input()
        exit()

    return input_dir

def convert12bit(img_path):
    img = tifffile.imread(img_path) #12bitを対象
    img_name = os.path.basename(img_path)
    img_dir = os.path.dirname(img_path)
    img_8bit = img / 16.0
    img_8bit = img_8bit.astype(np.uint8) #型変換
    img_name_8bit = img_name.replace(".tif","_8bit.tif")
    tifffile.imsave(os.path.join(img_dir,img_name_8bit), img_8bit)


def main():
    input_dir = directory_select()

    ext_list = ["tif"]
    img_path_list = list(chain.from_iterable([glob.glob(os.path.join(input_dir, "*." + ext)) for ext in ext_list]))

    for img_path in img_path_list:
        convert12bit(img_path)

if __name__ == "__main__":
    main()
