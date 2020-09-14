# -*- coding: UTF-8 -*-

import sys
import os
import ftplib

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


class FtpTools(object):
    """
    ftp client
    """
    def __init__(self, ftpserver, user='test',  passwd='test', remotedir=None):
        self.ftpserver = ftpserver
        self.user = user
        self.passwd = passwd
        self.remotedir = remotedir
        self.connection = self.connectFtp()
        self.localdir = self.getlocaldir()  # 没用
        self.fcount = self.dcount = 0

    def connectFtp(self):
        connection = ftplib.FTP(self.ftpserver)
        connection.login(self.user, self.passwd)
        if self.remotedir is not None:
            connection.cwd(self.remotedir)
        self.connection = connection

    def getlocaldir(self):
        return '.'

    def cleanLocals(self):
        """
        try to delete all local files first to remove garbage
        """
        if self.cleanall:
            for localname in os.listdir(self.localdir):    # local dirlisting
                try:                                       # local file delete
                    print('deleting local', localname)
                    os.remove(os.path.join(self.localdir, localname))
                except:
                    print('cannot delete local', localname)

    def downloadOne(self, remotename, localpath, buf_size=81920):
        """
        download one file by FTP in text or binary mode
        local name need not be same as remote name
        """
        print("----------downloadOne----------")
        print("localpath:", localpath)
        print("remotename:", remotename)
        print("----------downloadOne----------")
        self.filesize = self.connection.size(remotename)
        self.downloadsize = 0

        def download_file_progress_bar(block):
            self.downloadsize = self.downloadsize+len(block)
            transferred = self.downloadsize
            toBeTransferred = self.filesize
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

        fp = open(localpath, "wb")
        print("start download {}({}):".format(localpath, self.filesize))
        self.connection.retrbinary('RETR {}'.format(remotename), fp.write, buf_size, callback=download_file_progress_bar)
        fp.close()

    def uploadOne(self, localname, localpath, remotename=None, buf_size=81920):
        """
        upload one file by FTP in text or binary mode
        remote name need not be same as local name
        """
        print("----------uploadOne----------")
        print("localname:", localname)
        print("localpath:", localpath)
        print("remotename:", remotename)
        print("----------uploadOne----------")
        if remotename is None:
            remotename = localname
        self.filesize = os.path.getsize(localpath)
        self.uploadsize = 0
        try:
            suffix = localpath.split('.')[-1]
            oldfile = localpath.replace(suffix, '_old'+suffix)
            self.connection.delete(oldfile)
            self.connection.remotename(localpath, oldfile)
        except:
            pass

        def upload_file_progress_bar(block):
            self.uploadsize = self.uploadsize+len(block)
            transferred = self.uploadsize
            toBeTransferred = self.filesize
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

        fp = open(localpath, "rb")
        print("start upload {}({}):".format(localpath, self.filesize))
        self.connection.storbinary("STOR {}".format(remotename), fp, buf_size, callback=upload_file_progress_bar)
        fp.close()

    def uploadDir(self, localdir='.'):
        """
        for each directory in an entire tree
        upload simple files, recur into subdirectories
        """
        localfiles = os.listdir(localdir)
        print("----------uploadDir----------")
        for localname in localfiles:
            print("localname:", localname)
        print("----------uploadDir----------")
        for localname in localfiles:
            localpath = os.path.join(localdir, localname)
            print('uploading', localpath, 'to', localname)
            if not os.path.isdir(localpath):
                self.uploadOne(localname, localpath, localname)
                self.fcount += 1
            else:
                try:
                    self.connection.mkd(localname)
                    print('{} directory created'.format(localname))
                except:
                    print('{} directory not created'.format(localname))
                self.connection.cwd(localname)            # change remote dir
                self.uploadDir(localpath)                  # upload local subdir
                self.connection.cwd('..')                  # change back up
                self.dcount += 1
                print('{} directory exited'.format(localname))

    def downloadDir(self):
        """
        download all files from remote site/dir per config
        ftp nlst() gives files list, dir() gives full details
        """
        remotefiles = self.connection.nlst()         # nlst is remote listing
        print("----------downloadDir----------")
        for remotename in remotefiles:
            print("remotename:", remotename)
        print("----------downloadDir----------")
        for remotename in remotefiles:
            if remotename in ('.', '..'):
                continue
            localpath = os.path.join(self.localdir, remotename)
            print('downloading', remotename, 'to', localpath, 'as', end=' ')
            self.downloadOne(remotename, localpath)
        print('Done:', len(remotefiles), 'files downloaded.')

    def close(self):
        self.connection.quit()


if __name__ == '__main__':
    ftp2 = FtpTools('10.233.70.99', 'admin', 'Zte@888888', 'T2_Version')
    ftp2.uploadDir('test')
    ftp2.close()
