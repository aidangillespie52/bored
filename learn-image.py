import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import torch.optim as optim
from PIL import Image
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
img_size = 128

print("Using:", device)


fig, axes = plt.subplots(1, 2, figsize=(12, 4))
ims = []
for ax in axes:
    im = ax.imshow([[0]], cmap="plasma")
    ims.append(im)
    plt.colorbar(im, ax=ax)

plt.ion()


def plot_imgs(flat_imgs, titles=None):
    for i, flat_img in enumerate(flat_imgs):
        plot_img_arr = flat_img.detach().cpu().numpy()
        plot_img_arr = (plot_img_arr * 255).astype(np.uint8)
        plot_img_mat = plot_img_arr.reshape(img_size, img_size)

        ims[i].set_data(plot_img_mat)
        ims[i].set_clim(vmin=plot_img_mat.min(), vmax=plot_img_mat.max())

        if titles is not None:
            axes[i].set_title(titles[i])

    fig.canvas.draw()
    plt.pause(0.001)

img_path = "cat.jpg"
epochs = 1000

img = Image.open(img_path).convert("L") # grayscale
img = img.resize((img_size, img_size), Image.LANCZOS)
resized = img.resize((img_size, img_size))
img_arr = np.array(img)
img_norm = img_arr / 255.0
img_tensor = torch.tensor(img_norm, dtype=torch.float32).to(device)

class FNN(nn.Module):
    def __init__(self):
        super().__init__()
        
        # 512 x 512 gray scale images flattened
        self.inp = nn.Linear(img_size*img_size, 256)
        self.l1 = nn.Linear(256, 512)
        self.out = nn.Linear(512, img_size*img_size)
        
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = x.reshape(-1)
        x = self.relu(self.inp(x))
        x = self.relu(self.l1(x))
        x = self.out(x)
        x = x.reshape(img_size,img_size)
        
        return x

class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        
        # 512 x 512 gray scale images flattened
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1)   # 16 * img_size/2 * img_size/2
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1)  # 32 * img_size/4 * img_size/4
        
        last_size = 32 * img_size/4 * img_size/4
        self.out = nn.Linear(int(last_size), img_size*img_size)
        
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = x.unsqueeze(dim=0)
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = x.reshape(-1)
        x = self.out(x)
        x = x.reshape(img_size,img_size)
        
        return x

cnn_model = CNN().to(device)
cnn_optimizer = optim.Adam(cnn_model.parameters(), lr=1e-3)

fnn_model = FNN().to(device)
fnn_optimizer = optim.Adam(fnn_model.parameters(), lr=1e-3)

mse_loss = nn.MSELoss()

for epoch in tqdm(range(epochs)):
    # fnn
    fnn_model.train()
    fnn_optimizer.zero_grad()
    
    fnn_out = fnn_model(img_tensor)
    loss = mse_loss(fnn_out, img_tensor)
    
    loss.backward()
    fnn_optimizer.step()
    
    # cnn
    cnn_model.train()
    cnn_optimizer.zero_grad()
    
    cnn_out = cnn_model(img_tensor)
    loss = mse_loss(cnn_out, img_tensor)
    
    loss.backward()
    cnn_optimizer.step()
    
    plot_imgs([fnn_out, cnn_out], titles=["FNN", "CNN"])