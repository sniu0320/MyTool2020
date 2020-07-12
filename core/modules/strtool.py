# -*- coding: UTF-8 -*-

class strTool(object):
    '''
    字符串工具包
    '''
    def __init__(self):
        pass

    @staticmethod  
    # 静态方法，名义上归类管理，实际上访问不了类或实例的属性，可以直接调用 strTool.test(str)
    # @classmethod #类方法，只能访问类属性，不能访问实例属性
    # @property #属性方法，把一个方法办成一个静态属性,隐藏实现细节。set时需要 @test.setter
    # 属性方法可以在DUT类时使用
    def test(str):
        '''
        测试方法
        '''
        print("test is ok{}".format(str))
