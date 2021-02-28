import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data
import torch.nn.functional as F
import torchvision
from torchvision import transforms
import time
from PIL import Image, ImageFile
import torchvision.models as models
import os

def readVariable(key, defaultValue):
    value = os.getenv(key, 'null')
    print('read env key: {0}, value:{1}'.format( key, value))
    if value == 'null' :
        return defaultValue
    return value

# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# all changable variables in docker:
modelHub = readVariable("MODEL_HUB", "pytorch/vision")
modelName = readVariable("MODEL_NAME", "resnet50")
train_data_path = readVariable("TRAIN_SET", "./train/")
val_data_path = readVariable("VAL_SET", "./val/")
test_data_path = readVariable("TEST_SET","./test/")
batch_size=int(readVariable("BATCH_SIZE","64"))
trace_name=readVariable("TRACE_FOLDER","/tmp/") + modelName + time.strftime("%Y%m%d%H%M%S", time.localtime()) + ".json" 
epochs = int(readVariable("EPOCHS", "1"))
loss_rate = float(readVariable("LOSS_RATE", "0.001"))

simplenet = torch.hub.load(modelHub, modelName)
ImageFile.LOAD_TRUNCATED_IMAGES=True

def check_image(path):
    try:
        im = Image.open(path)
        return True
    except:
        return False

img_transforms = transforms.Compose([
    transforms.Resize((64,64)),    
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225] )
    ])


train_data = torchvision.datasets.ImageFolder(root=train_data_path,transform=img_transforms, is_valid_file=check_image)
val_data = torchvision.datasets.ImageFolder(root=val_data_path,transform=img_transforms, is_valid_file=check_image)
test_data = torchvision.datasets.ImageFolder(root=test_data_path,transform=img_transforms, is_valid_file=check_image)

train_data_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size)
val_data_loader  = torch.utils.data.DataLoader(val_data, batch_size=batch_size) 
test_data_loader  = torch.utils.data.DataLoader(test_data, batch_size=batch_size)

optimizer = optim.Adam(simplenet.parameters(), lr=loss_rate)

if torch.cuda.is_available():
    print("cuda")
    device = torch.device("cuda") 
else:
    print("cpu")
    device = torch.device("cpu")
simplenet.to(device)

def train(model, optimizer, loss_fn, train_loader, val_loader, epochs=1, device="cpu"):
    for epoch in range(epochs):
        training_loss = 0.0
        valid_loss = 0.0
        with torch.autograd.profiler.profile(use_cuda=False) as prof:
            model.train()
            for batch in train_loader:
                optimizer.zero_grad()
                inputs, targets = batch
                inputs = inputs.to(device)
                targets = targets.to(device)
                output = model(inputs)
                loss = loss_fn(output, targets)
                loss.backward()
                optimizer.step()
                training_loss += loss.data.item() * inputs.size(0)
        # print(prof)
        prof.export_chrome_trace(trace_name)
        print("Exported trace")
        training_loss /= len(train_loader.dataset)
        model.eval()

        num_correct = 0 
        num_examples = 0
        for batch in val_loader:
            inputs, targets = batch
            inputs = inputs.to(device)
            output = model(inputs)
            targets = targets.to(device)
            loss = loss_fn(output,targets) 
            valid_loss += loss.data.item() * inputs.size(0)
            correct = torch.eq(torch.max(F.softmax(output, dim=1), dim=1)[1], targets)
            num_correct += torch.sum(correct).item()
            num_examples += correct.shape[0]
        valid_loss /= len(val_loader.dataset)

        print('Epoch: {}, Training Loss: {:.2f}, Validation Loss: {:.2f}, accuracy = {:.2f}'.format(epoch, training_loss,
        valid_loss, num_correct / num_examples))

train(simplenet, optimizer,torch.nn.CrossEntropyLoss(), train_data_loader,val_data_loader, epochs=epochs, device=device)

# labels = ['cat','fish']

# img = Image.open("./val/fish/100_1422.JPG") 
# img = img_transforms(img).to(device)


# prediction = F.softmax(simplenet(img), dim=1)
# prediction = prediction.argmax()
# print(labels[prediction])

# torch.save(simplenet, "/tmp/simplenet") 
# simplenet = torch.load("/tmp/simplenet")

# torch.save(simplenet.state_dict(), "/tmp/simplenet")    
# simplenet = SimpleNet()
# simplenet_state_dict = torch.load("/tmp/simplenet")
# simplenet.load_state_dict(simplenet_state_dict)