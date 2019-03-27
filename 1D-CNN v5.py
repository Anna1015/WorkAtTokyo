import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.utils.data as Data
from torch.autograd import Variable
import matplotlib.pyplot as plt
import numpy as np
import os
import torch.nn.functional as F
from prettytable import PrettyTable

# predefine some const
EPOCH = 2
BATCH_SIZE = 200
LEARNING_RATE = 0.001
train_npy_FILE = "D:/TestWithMFCC39/NN for 0Health-1Dementia/npy/totalNPY for train.npy"
testDIR = "D:/TestWithMFCC39/NN for 0Health-1Dementia/npy/npy for test"
modelDIR = "D:/TestWithMFCC39/NN for 0Health-1Dementia/npy"
modelFILE = "reload_model.pth"


#用于打印分割线
def print_line(char,string):
    print(char*33,string,char*32)


# define the neural network
class myCNN1D(nn.Module):

    def num_flat_features(self,x):
        size=x.size()[1:] # all dimensions except the batch dimension
        num_features=1
        for s in size:
            num_features*=s
        return num_features

    def __init__(self):
        super(myCNN1D, self).__init__()
        self.layer1_conv = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=2, kernel_size=5, stride=1, padding=0, dilation=1, groups=1,
                      bias=True),
            nn.ReLU(),
            # nn.MaxPool1d(2)
        )
        self.layer2_conv = nn.Sequential(
            nn.Conv1d(in_channels=2, out_channels=3, kernel_size=6, stride=1, padding=0, dilation=1, groups=1,
                      bias=True),
            nn.ReLU()
        )
        self.layer3_fc1 = nn.Linear(3*5*6, 100)
        self.layer4_output = nn.Linear(100, 1)

    def forward(self, x):
        out = self.layer1_conv(x)
        out = self.layer2_conv(out)
        out = out.view(-1, self.num_flat_features(out))
        out = self.layer3_fc1(out)
        out = self.layer4_output(out)
        return out




# build a CNN
myConv = myCNN1D()

# Define Loss and Optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(myConv.parameters(), lr=LEARNING_RATE)


# 制作训练集
trainDS = np.load(train_npy_FILE)
print("The shape of train dataset is {}".format(trainDS.shape))
x_train = trainDS[:,1:]
y_train = trainDS[:,0]

x_train = x_train[:,:,1:]
y_train = y_train[:,:,0]
y_train = torch.from_numpy(y_train).float()
x_train = torch.from_numpy(x_train).float()

trainDataSet = Data.TensorDataset(x_train, y_train)

trainLoader = Data.DataLoader(
    dataset=trainDataSet,  # torch TensorDataset format
    batch_size=BATCH_SIZE,  # mini batch size
    shuffle=True,  # 要不要打乱数据 (打乱比较好)
    num_workers=1,  # 多线程来读数据
)


# 制作测试集合
testFILES = os.listdir(testDIR)


testMatrix = np.zeros(shape=(1,1,40))
for f in testFILES:
    if f[0]=='.':
        continue
    tempFILE = testDIR + '/' + f
    tempMatrix = np.loadtxt(tempFILE)
    print("The shape of {0} is {1}".format(tempFILE, tempMatrix.shape))
    tempMatrix = tempMatrix[:,np.newaxis]
    testMatrix = np.vstack((testMatrix,tempMatrix))
print("The shape of testMatrix is {}".format(testMatrix.shape))

x_test = testMatrix[:,:,1:]
y_test = testMatrix[:,:,0]
y_test = torch.from_numpy(y_test).float()
x_test = torch.from_numpy(x_test).float()

testDataSet = Data.TensorDataset(x_test, y_test)

testLoader = Data.DataLoader(
    dataset=testDataSet,  # torch TensorDataset format
    batch_size=BATCH_SIZE,  # mini batch size
    shuffle=True,  # 要不要打乱数据 (打乱比较好)
    num_workers=1,  # 多线程来读数据
)




# Train the Model
print_line('*','Training Begin')
for epoch in range(EPOCH):
    for i, (x_train, y_train) in enumerate(trainLoader):
        x_train = Variable(x_train)
        y_train = Variable(y_train)

        # Forward + Backward + Optimize
        optimizer.zero_grad()
        outputs = myConv(x_train)

        # y_train = y_train.type(torch.LongTensor)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

    print('Epoch [{}/{}] Loss: {:.8f}'.format(epoch + 1, EPOCH, loss.data))

#开始打印表格
    title = ['Training Results '+str(epoch+1)]
    for i in range(5):
        title.append('Sample '+str(i+1))

    table = PrettyTable(title)
    nn_output_list = ["Neural Network output"]
    for idx,nn_output in enumerate(outputs):
        if(idx == 5):
            break
        nn_output_list.append(np.round(np.array(nn_output.data[0]),decimals=4))
    table.add_row(nn_output_list)

    label_list = ["True Answer"]
    for idx, label in enumerate(y_train):
        if(idx == 5):
            break
        label_list.append(np.array(label.data[0]))
    table.add_row(label_list)

    print(table)


torch.save(myConv, modelDIR+'/'+modelFILE)
reload_model = torch.load(modelDIR+'/'+modelFILE)


# Test the Model
print_line('*','Testing Begin')
correct = 0
total = 0
for x_test, y_test in testLoader:
    x_test = Variable(x_test)
    outputs = reload_model(x_test)
    outputs = outputs.data.squeeze()

    for (output, label) in zip(outputs, y_test):
        total += 1
        if (output - 0) ** 2 - (output - 1) ** 2 < 0:
            predicted = 0
        else:
            predicted = 1
        if (predicted - label)**2<0.00001:
            correct+=1

print('Test Accuracy of the model on the {} test samples: {}%.'.format(testDataSet.__len__(),(100 * correct / total)))

#开始打印表格
title = ['Test Results']
for i in range(5):
    title.append('Sample '+str(i+1))

table = PrettyTable(title)
nn_output_list = ["Neural Network output"]
for idx,nn_output in enumerate(outputs):
    if(idx == 5):
        break
    nn_output_list.append(np.round(np.array(nn_output.data),decimals=4))
table.add_row(nn_output_list)

label_list = ["True Answer"]
for idx, label in enumerate(y_test):
    if(idx == 5):
        break
    label_list.append(np.array(label.data[0]))
table.add_row(label_list)

print(table)





