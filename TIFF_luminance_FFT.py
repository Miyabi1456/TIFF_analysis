# -*- cording: utf-8 -*-
import tifffile
import numpy as np
import glob
import os, tkinter, tkinter.filedialog, tkinter.messagebox
from itertools import chain
import csv
import matplotlib.pyplot as plt
import re
import pandas as pd

def directory_select():
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("All files","*"),("TIFF","tif")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo("TIFF luminance FFT","対象の画像を選択してください")
    input_dir = os.path.dirname(tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir))

    tkinter.messagebox.showinfo('TIFF luminance FFT','保存ディレクトリを選択してください')
    output_dir = tkinter.filedialog.askdirectory(initialdir = iDir)

    if not input_dir:#input_dirがnoneのときTrue
        print("ファイルが選択されませんでした")
        input()
        exit()

    return input_dir, output_dir

def read_tiff_path(input_dir):
    ext_list = ["tif"]#読み込む対象の拡張子.TIFFのみとする
    img_path_list = list(chain.from_iterable([glob.glob(os.path.join(input_dir, "*." + ext)) for ext in ext_list]))
    img_name_list = [os.path.basename(n) for n in img_path_list ]
    print("画像の枚数:" + str(len(img_name_list)))

    temp_list = [(re.search("[0-9]+", x).group(), x) for x in img_name_list] #文字列の中で数字部分を抜き出す
    temp_list.sort(key=lambda x:int(x[0])) #[数字,"文字列"]タプルの数字部分を使ってソート
    img_name_list = [x[1] for x in temp_list] #数字でソートされたタプルから文字列だけを取り出してリスト化
    img_path_list = [os.path.join(input_dir,img_name) for img_name in img_name_list]

    return img_path_list

def get_one_pixel_list(img_path_list, x_pixel, y_pixel):
    """
    連番画像から特定のピクセルの輝度を抜き出す.
    """
    pixel_list = np.array([])
    for img_path in img_path_list:
        pixel_list = np.append(pixel_list, tifffile.imread(img_path)[y_pixel,x_pixel]) #画像の配列(高さ,横,色)

    return pixel_list

def luminance_fft(pixel_list, N, fs):
    hammingWindow = np.hamming(N)    # ハミング窓(よく使われるらしい)
    #hanningWindow = np.hanning(N)    # ハニング窓
    #blackmanWindow = np.blackman(N)  # ブラックマン窓
    #bartlettWindow = np.bartlett(N)  # バートレット窓

    x = pixel_list / np.amax(pixel_list) * 2.0 - 1.0 #最大値で正規化
    windowedData = hammingWindow * x #窓関数の適用

    windowedDFT = np.fft.fft(windowedData)
    windowedAmp = [np.sqrt(c.real**2 + c.imag**2) for c in windowedDFT]

    freqlist = np.fft.fftfreq(N, d = 1.0/fs) #周波数軸の値を計算

    return windowedData, windowedAmp, freqlist

def main():
    input_dir, output_dir = directory_select()
    img_path_list = read_tiff_path(input_dir)

    print("パラメーターの設定:")
    N = len(img_path_list)#サンプル点数.画像の枚数に相当
    print("サンプル点数:" + str(N))
    #print("画像のbit深度[bit]=",end="")
    #bit=int(input())
    print("フレームレート[fps]=", end="")
    fs = float(input()) #サンプリング周波数[Hz]
    #tw = N/fs #時間窓長さ[s]
    start = 0 #何枚目からFFTを始めるか.普通は0
    print("参照点のピクセル座標(画像の左上が(0,0)であることに注意):")
    print("x=", end="")
    x_pixel = int(input())
    print("y=", end="")
    y_pixel = int(input())#参照点の座標.調べたい座標はあらかじめ別のソフトで調べておく

    pixel_list = get_one_pixel_list(img_path_list, x_pixel, y_pixel)
    
    windowedData, fft_amp, freqlist = luminance_fft(pixel_list, N ,fs)

    #CSVに出力
    fft_df = pd.DataFrame({"freq[Hz]" : freqlist, "amp" : fft_amp}, columns = ("freq[Hz]", "amp"))
    orig_df = pd.DataFrame({"time[s]" : np.arange(start,N/fs,1.0/fs), "amp" : windowedData}, columns = ("time[s]", "amp"))

    fft_df.to_csv(os.path.join(output_dir, "fft.csv"), index = False)
    orig_df.to_csv(os.path.join(output_dir, "wave.csv"), index  =False)
    

    plt.subplot(1,2,1)  # 2行1列のグラフの1番目の位置にプロット
    plt.plot(range(start, start+N), windowedData)
    plt.axis([start, start+N, -1.0, 1.0])
    plt.xlabel("time [sample]")
    plt.ylabel("amplitude")

    plt.subplot(1,2,2)
    plt.plot(freqlist, fft_amp, marker='o', linestyle='-')
    plt.axis([0, fs/2, 0, max(fft_amp)*1.1])
    plt.xlabel("frequency [Hz]")
    plt.ylabel("amplitude spectrum")

    plt.show()


if __name__ == "__main__":
    main()
