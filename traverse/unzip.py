# -*- coding=utf8 -*-
import os

File_list = []


# 获取文件夹下的文件名
def listdir(path, list_name):
    for file in os.listdir(path):
        if file[-4:] == ".zip":  # 字符串切片
            list_name.append(file)
    return list_name


def main():
    source_dir = "F:\\github_file\\"
    listdir(source_dir, File_list)

    # 创建压缩包文件存储路径及文件名
    unzip_dir = source_dir+"unzip\\"
    # window RAR解压缩命令
    for file in File_list:
        # 必须使用这种格式,使用+进行字符连接时，因为语言中转义字符的存在会出现路径识别时的错误。
        rar_command = '"D:\Program Files\WinRAR\WinRAR.exe" x %s * %s\\'%(source_dir+file, unzip_dir+file[:-4])
        os.system(rar_command)


main()
