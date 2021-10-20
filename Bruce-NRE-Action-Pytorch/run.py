
#系统相关
import argparse
import os

#框架相关
import torch
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn as nn

#自定义
from BruceNRE.config import config
from BruceNRE.utils import make_seed, load_pkl
from BruceNRE.process import process
from BruceNRE.dataset import CustomDataset, collate_fn
from BruceNRE import models
from BruceNRE.trainer import train, validate

__Models__ = {
    "BruceCNN":models.BruceCNN,
    "BruceBiLSTM":models.BruceBiLSTM,
    "BruceBiLSTMPro":models.BruceBiLSTMPro
}

parser = argparse.ArgumentParser(description='关系抽取')
parser.add_argument('--model_name', type=str, default='BruceBiLSTMPro', help='model name')
args = parser.parse_args()

if __name__ == "__main__":
    model_name = args.model_name if args.model_name else config.model_name#model_name:BruceCNN

# 初始化随机数设置
make_seed(config.seed)

# 计算设备设置
if config.use_gpu and torch.cuda.is_available():
    device = torch.device('cuda', config.gpu_id)
else:
    device = torch.device('cpu')
print(torch.cuda.is_available())

if not os.path.exists(config.out_path):#看有没有这几个文件
    process(config.data_path, config.out_path, file_type='csv')#开始预处理文件     data_path = 'data/origin' #原始数据 out_path = 'data/out' #数据处理的最终结果保存

vocab_path = os.path.join(config.out_path, 'vocab.pkl')#路径拼接
train_data_path = os.path.join(config.out_path, 'train.pkl')
test_data_path = os.path.join(config.out_path, 'test.pkl')

vocab = load_pkl(vocab_path, 'vocab')
vocab_size = len(vocab.word2idx)#6618个字

train_dataset = CustomDataset(train_data_path, 'train data')
test_dataset = CustomDataset(test_data_path, 'test data')

train_dataloader = DataLoader(#dataloader本质是一个可迭代对象，使用iter()访问，不能使用next()访问；
    dataset=train_dataset,
    batch_size=config.batch_size,
    shuffle=True,
    drop_last=True,
    collate_fn=collate_fn
)
test_dataloader = DataLoader(
    dataset=test_dataset,
    batch_size=config.batch_size,
    shuffle=True,
    drop_last=True,
    collate_fn=collate_fn
)

model = __Models__[model_name](vocab_size, config)#动态导入
model.to(device)

print(model)

optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer,'max', factor=config.decay_rate, patience=config.decay_patience)#该方法中提供了多种基于epoch训练次数进行学习率调整的方法;

#patience：几个epoch不变时，才改变学习速率，默认为10  factor：new_lr = lr * factor，默认0.1  以min为例，当优化的指标不在下降时，改变学习数率。

loss_fn = nn.CrossEntropyLoss()

best_macro_f1, best_macro_epoch = 0, 1
best_micro_f1, best_micro_epoch = 0, 1
best_macro_model, best_micro_model = '', ''
print("******************开始训练*********************")

for epoch in range(1, config.epoch + 1):
    train(epoch, device, train_dataloader, model, optimizer, loss_fn, config)
    macro_f1, micro_f1 = validate(test_dataloader, model, device, config)
    model_name = model.save(epoch=epoch)
    scheduler.step(macro_f1)

    if macro_f1 > best_macro_f1:
        best_macro_f1 = macro_f1
        best_macro_epoch = epoch
        best_macro_model = model_name
    if micro_f1 > best_micro_f1:
        best_micro_f1 = micro_f1
        best_micro_epoch = epoch
        best_micro_model = model_name

print("*****************模型训练完成*********************")
print(f'best macro f1:{best_micro_f1:.4f}', f'in epoch:{best_micro_epoch}, saved in:{best_micro_model}')
print(f'best micro f1:{best_micro_f1:.4f}', f'in epoch:{best_micro_epoch}, saved in:{best_micro_model}')
