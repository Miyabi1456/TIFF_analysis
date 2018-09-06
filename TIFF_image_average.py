#!/usr/bin/env python
# -*- cording: utf-8 -*-
'''
使い方:
    起動したら平均化したい画像の中からどれか一枚を選択してください.
    平均化画像は選択したディレクトリ下の新たなディレクトリ内に保存されます.
    オプションとしてヒストグラム伸長があります.使用時はhistgram_extension変数にTrueを代入してください.
'''
import tifffile
import numpy as np
import glob
import os, tkinter, tkinter.filedialog, tkinter.messagebox
#import csv

#########################オプション########################################################################
histogram_extension = True #ヒストグラム伸長(拡張)を行う場合Trueにする.
##########################################################################################################

def directory_select():

    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("All files","*"),("TIFF","tif")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo("TIFF画像平均化","対象の画像を選択してください")
    input_dir = os.path.dirname(tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir))

    if not input_dir:#input_dirがnoneのときTrue
        print("ファイルが選択されませんでした")
        input()
        exit()

    return input_dir

def read_image_paths(input_dir):

    #画像ファイルへのパスをリスト形式でimg_pathに代入
    #読み込む対象の拡張子.TIFFのみとする
    img_path = glob.glob(os.path.join(input_dir, "*.tif"))
    print("画像の枚数:"+str(len(img_path)))

    return img_path

def images_average(img_path):

    img_array = tifffile.imread(img_path[0]) #画素数の違う画像の平均を取ろうとしないで
    shape = np.shape(img_array) #配列サイズの確認
    x_axis = shape[0] #横方向の画素数
    y_axis = shape[1] #縦方向の画素数

    for i in range(1,len(img_path)):
        img_array=np.append(img_array,tifffile.imread(img_path[i])) #1次元配列.img_arrayに読み込んだ画像を追加する
        bar = "#" * int(50*i/len(img_path)) + " " * int((50*(1-i/len(img_path))))
        print("\r[{0}]{1}/{2} 読み込み中".format(bar,i+1,len(img_path)),end="")
    print("\n",end="")

    img_array = np.reshape(img_array, (len(img_path), x_axis,y_axis)) #(枚数,横,縦)の3次元配列
    print("画像読み込み完了")

    print("平均計算中")
    average_img = np.average(img_array, axis=0) #x,y平面上の同じ座標の画素同士の平均を取る(次元方向の平均)

    if histogram_extension == True:
        max_luminance = np.max(average_img) #最大輝度
        min_luminance = np.min(average_img) #最小輝度

        normalization_img = (average_img - min_luminance)/(max_luminance - min_luminance) #0-1に正規化

        average_img_12bit = normalization_img * (2**12 - 1) #12bitTIFF
        average_img_12bit = average_img_12bit.astype(np.uint16) #小数切り捨て

        average_img_8bit = normalization_img * (2**8 - 1) #8bitTIFF
        average_img_8bit = average_img_8bit.astype(np.uint8) #小数切り捨て
    else:
        average_img_12bit = average_img.astype(np.uint16)
        average_img_8bit = average_img/16.0 #4bit分で除算
        average_img_8bit = average_img_8bit.astype(np.uint8)

    print("平均計算完了")

    return average_img_12bit,average_img_8bit

def post_process(input_dir,average_img_12bit,average_img_8bit):

    input_folder_name = input_dir.split("/")[-1]
    output_dir = os.path.join(input_dir,input_folder_name+"_average")

    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass


    if histogram_extension == True:
        filename_12bit = input_folder_name + "_average_HisExt_12bit.tif"
        filename_8bit = input_folder_name + "_average_HisExt_8bit.tif"
    else:
        filename_12bit = input_folder_name + "_average_12bit.tif"
        filename_8bit = input_folder_name + "_average_8bit.tif"

    tifffile.imsave(os.path.join(output_dir,filename_12bit),average_img_12bit)
    tifffile.imsave(os.path.join(output_dir,filename_8bit),average_img_8bit)

    '''
    with open("平均輝度.csv", "w") as f:
        writer = csv.writer(f, lineterminator="\n") # 改行コード（\n）を指定しておく
        writer.writerows(average_img) # 2次元配列
    '''

def main():
    
    print("ヒストグラム伸長オプション="+str(histogram_extension))
    input_dir = directory_select()
    img_path = read_image_paths(input_dir)
    average_img_12bit,average_img_8bit = images_average(img_path)
    post_process(input_dir,average_img_12bit,average_img_8bit)

if __name__ == "__main__":
    main()