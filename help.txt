文件：
main.py	            主逻辑
setup.py	        安装程序打包部署 setuptools 百度就有教程
requirements.txt	插件及目录版本控制 pip freeze 直接打印应用的包
README.txt	        帮助文档

目录：
#log	            日志目录
#conf	            配置目录
#data               数据目录
#modules	        模块,class等
#output	            输出目录
#tests	            存放测试代码


安装第三方库：
pip install -r requirements.txt
备注：
自动生成requirements.txt
 pip install pipreqs
 pipreqs ./



1.模块名和包名采用小写字母并且以下划线分隔单词的形式；
如:regex_syntax,py_compile,_winreg
2.类名或异常名采用每个单词首字母大写的方式；
如：BaseServer,ForkingMixIn,KeyboardInterrupt
3.全局或者类常量，全部使用大写字母，并且以下划线分隔单词；
如：MAX_LOAD
4.其余变量命名包括方法名，函数名，普通变量名则是采用全部小写字母，并且以下划线分隔单词的形式命名。
如：my_thread
5.以上的内容如果是内部的，则使用下划线开头命名。
如：__init__,__new__

