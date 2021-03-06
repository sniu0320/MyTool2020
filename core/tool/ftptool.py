# coding:utf8
from ftplib import FTP
import os
import sys
import logging
# from progressbar import ProgressBar

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

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    filename='ftp.log')

file_size = 0			# 文件总大小，计算进度时用
upload_size = 0			# 已上传的数据大小，计算进度时用
download_size = 0


def upload(f, remote_path, local_path):
    '''
    upload(ftp, "ftp_a.txt", "a.txt")   # 将当前目录下的a.txt文件上传到ftp服务器的tmp目录，命名为ftp_a.txt
    '''
    global file_size
    file_size = os.path.getsize(local_path)
    print("start upload {}({}):".format(local_path, file_size))

    fp = open(local_path, "rb")

    def upload_file_progress_bar(block):
        global upload_size
        upload_size = upload_size+len(block)
        transferred = upload_size
        toBeTransferred = file_size
        # suffix = ''
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

    buf_size = 8192
    f.storbinary("STOR {}".format(remote_path), fp, buf_size, callback=upload_file_progress_bar)
    fp.close()


def download(f, remote_path, local_path):
    '''
    download(ftp, "ftp_a.txt", "b.txt")  # 将ftp服务器tmp目录下的ftp_a.txt文件下载到当前目录，命名为b.txt
    '''
    global file_size
    file_size = f.size(remote_path)
    print("start download {}({}):".format(local_path, file_size))

    fp = open(local_path, "wb")

    def download_file_progress_bar(block):
        global download_size
        download_size = download_size+len(block)
        transferred = download_size
        toBeTransferred = file_size
        # suffix = ''
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

    buf_size = 8192
    f.retrbinary('RETR {}'.format(remote_path), fp.write, buf_size, callback=download_file_progress_bar)
    fp.close()

# def download(f, remote_path, local_path):
#     '''
#     download(ftp, "ftp_a.txt", "b.txt")  # 将ftp服务器tmp目录下的ftp_a.txt文件下载到当前目录，命名为b.txt
#     '''
#     fp = open(local_path, "wb")
#     buf_size = 8192

#     size = f.size(remote_path)
#     pbar = ProgressBar(widgets=widgets, maxval=size)
#     pbar.start()

#     def file_write(data):
#         fp.write(data)
#         global pbar
#         pbar += len(data)
#     f.retrbinary('RETR {}'.format(remote_path), file_write, buf_size)
#     fp.close()


def get_file_list_in_current_path(path=os.getcwd(), remove='.py'):
    '''获取当前目录下的文件'''
    file_list = []
    for f in os.listdir(path):
        if not f.endswith(remove):
            # f = os.path.join(path, f)
            if os.path.isfile(f):
                file_list.append(f)
    return file_list


def run(file_list, ip, username, password):
    try:
        ftp = FTP()
        ftp.connect(ip, 21)      # 第一个参数可以是ftp服务器的ip或者域名，第二个参数为ftp服务器的连接端口，默认为21
        ftp.login(username, password)     # 匿名登录直接使用ftp.login()
        for file in file_list:
            upload(ftp, file, file)
            info = "upload {} to {} successfully".format(file, ip)
            print(info)
            logging.debug(info)
    except Exception as e:
        print("ERROR: {}".format(e))
        logging.error(e)
    finally:
        print("远端目录下的文件:")
        for i in ftp.nlst('.'):
            print(i)
        ftp.quit()


if __name__ == "__main__":
    ftpT1 = '10.233.70.1'
    ftpT1_username = 'admin'
    ftpT1_password = 'Zte@888888'
    ftpT2 = '10.233.70.99'
    ftpT2_username = 'admin'
    ftpT2_password = 'Zte@888888'
    file_list = get_file_list_in_current_path()
    run(file_list, ftpT1, ftpT1_username, ftpT1_password)
    run(file_list, ftpT2, ftpT2_username, ftpT2_password)
