# coding:utf8
from ftplib import FTP
import os
import sys

'''
FTP对象常用方法:
ftp.cwd(path)   # 设置FTP当前操作的路径，同linux中的cd
ftp.dir()   # 显示目录下所有信息
ftp.nlst()  # 获取目录下的文件，显示的是文件名列表
ftp.mkd(directory)  # 新建远程目录
ftp.rmd(directory)  # 删除远程目录
ftp.rename(old, new)    # 将远程文件old重命名为new
ftp.delete(file_name) # 删除远程文件
ftp.storbinary(cmd, fp, bufsize)    # 上传文件，cmd是一个存储命令，可以为"STOR filename.txt"， fp为类文件对象（有read方法），bufsize设置缓冲大小
ftp.retrbinary(cmd, callback, bufsize)  # 下载文件，cmd是一个获取命令，可以为"RETR filename.txt"， callback是一个回调函数，用于读取获取到的数据块
'''


def upload(f, remote_path, local_path):
    fp = open(local_path, "rb")
    buf_size = 1024
    f.storbinary("STOR {}".format(remote_path), fp, buf_size)
    fp.close()


def download(f, remote_path, local_path):
    fp = open(local_path, "wb")
    buf_size = 1024
    f.retrbinary('RETR {}'.format(remote_path), fp.write, buf_size)
    fp.close()


def progress_bar(transferred, toBeTransferred, suffix=''):
    bar_len = 30
    filled_len = int(round(bar_len * transferred/float(toBeTransferred)))
    percents = round(100.0 * transferred/float(toBeTransferred), 1)
    bar = '#' * filled_len + '-' * (bar_len - filled_len)
    if transferred == toBeTransferred:
        sys.stdout.write('  %s%s |%s| %s bytes\r' % (percents, '%', bar, toBeTransferred))
        print("\r")
    else:
        sys.stdout.write('  %s%s |%s| %s bytes\r' % (percents, '%', bar, transferred))
    sys.stdout.flush()


def get_file_list_in_current_path(path=os.getcwd(), remove='.p'):
    '''获取当前目录下的文件'''
    # print(">>>Get all files in current path(remove {}):".format(remove))
    file_list = []
    for f in os.listdir(path):
        if not f.endswith(remove):
            # f = os.path.join(path, f)
            if os.path.isfile(f):
                file_list.append(f)
    return file_list


if __name__ == "__main__":
    ftpT1 = '10.233.70.1'
    ftpT1_username = 'ss'
    ftpT1_password = 'ss'
    ftpT2 = '10.233.70.99'
    ftpT2_username = 'ss'
    ftpT2_password = 'ss'

    file_list = get_file_list_in_current_path()
    try:
        ftp = FTP()
        ftp.connect(ftpT1, 21)      # 第一个参数可以是ftp服务器的ip或者域名，第二个参数为ftp服务器的连接端口，默认为21
        ftp.login(ftpT1_username, ftpT1_username)     # 匿名登录直接使用ftp.login()
        # ftp.cwd("tmp")                # 切换到tmp目录
        for file in file_list:
            upload(ftp, file, file)
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        ftp.quit()

    try:
        ftp = FTP()
        ftp.connect(ftpT2, 21)      # 第一个参数可以是ftp服务器的ip或者域名，第二个参数为ftp服务器的连接端口，默认为21
        ftp.login(ftpT2_username, ftpT2_username)     # 匿名登录直接使用ftp.login()
        # ftp.cwd("tmp")                # 切换到tmp目录
        for file in file_list:
            upload(ftp, file, file)
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        ftp.quit()


    # upload(ftp, "ftp_a.txt", "a.txt")   # 将当前目录下的a.txt文件上传到ftp服务器的tmp目录，命名为ftp_a.txt
    # download(ftp, "ftp_a.txt", "b.txt")  # 将ftp服务器tmp目录下的ftp_a.txt文件下载到当前目录，命名为b.txt
    # ftp.quit()