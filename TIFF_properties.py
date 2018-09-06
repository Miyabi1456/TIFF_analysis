# -*- cording: utf-8 -*-
import tifffile
import numpy as np
import glob
import os, tkinter, tkinter.filedialog, tkinter.messagebox
from itertools import chain
from matplotlib import pyplot as plt

def directory_select():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("All files","*"),("TIFF","tif")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo("TIFF properties","対象の画像を選択してください")
    img_dir = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)

    if not img_dir:
        print("ファイルが選択されませんでした")
        input()
        exit()

    return img_dir

def main():
    img_dir = directory_select()
    img = tifffile.imread(img_dir)

    print(img.shape)

    print("平均")
    print(np.mean(img))

    print("最大値")
    print(np.max(img))

    print("最小値")
    print(np.min(img))

    print("標準偏差")
    print(np.std(img))

    bit = 2**8-1
    hist, bins = np.histogram(img.flatten(),bit,[0,bit])

    cdf = hist.cumsum()
    cdf_normalized = cdf * hist.max()/ cdf.max()

    plt.plot(cdf_normalized, color = 'b')
    plt.hist(img.flatten(),bit,[0,bit], color = 'r')
    plt.xlim([0,bit])
    plt.legend(('cdf','histogram'), loc = 'upper left')
    plt.show()

if __name__ == "__main__":
    main()
