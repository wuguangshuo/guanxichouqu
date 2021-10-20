
# 系统相关
import random
import json
import csv
import codecs
import os

#框架相关
import torch

# 第三方
import numpy as np
import pickle as pkl

"""
确保文件夹存在
"""
def ensure_dir(directory):
    """
    判断目录是否存在，不存在就创建
    :param path:
    :return:
    """
    if not os.path.exists(directory):
        os.makedirs(directory)#os.makedirs() 方法用于递归创建目录。os.makedirs(path, mode=0o777)path -- 需要递归创建的目录，可以是相对或者绝对路径。mode -- 权限模式。

def make_seed(num):
    random.seed(num)#可以看到当seed()没有参数时，每次生成的随机数是不一样的，而当seed()有参数时，每次生成的随机数是一样的，同时选择不同的参数生成的随机数也不一样
    np.random.seed(num)
    torch.manual_seed(num)
    torch.cuda.manual_seed(num)
    torch.cuda.manual_seed_all(num)

# 加载CSV文件
def load_csv(file):
    data_list = []

    with codecs.open(file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line in reader:
            data = list(line.values())
            data_list.append(data)
    return data_list#一共是4000条

# 加载json文件
def load_json(file):
    data_list = []

    with codecs.open(file, encoding='utf-8') as f:
        for line in f:
            json_data = json.load(line)
            data = list(json_data.values())
            data_list.append(data)
    return data_list

def sava_pkl(path, obj, obj_name):
    print(f'save {obj_name} in {path}')
    with codecs.open(path, 'wb') as f:
        pkl.dump(obj, f)
   # 1. pickle.dump(obj, file, protocol=None,)
   #  必填参数obj表示将要封装的对象
   #  必填参数file表示obj要写入的文件对象，file必须以二进制可写模式打开，即“wb”

def load_pkl(path, obj_name):
    print(f'load {obj_name} in {path}')
    with codecs.open(path,'rb') as f:
        data = pkl.load(f)
    return data

def get_result(entity1, entity2, key):
    """
    国籍
    祖籍
    导演
    出生地
    主持人
    所在城市
    所属专辑
    连载网站
    出品公司
    毕业院校
    :param key:
    :return:
    """
    relations = {
        "0":"国籍",
        "1": "祖籍",
        "3":"导演",
        "3":"出生地",
        "4":"主持人",
        "5":"所在城市",
        "6": "所属专辑",
        "7": "连载网站",
        "8": "出品公司",
        "9": "毕业院校"
    }

    result = {
        'entity1':entity1,
        'entity2':entity2,
        'relation':relations.get(str(key))
    }

    return result