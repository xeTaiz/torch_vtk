#%%
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
import time

from torchvtk.rendering.raycast import *
from torchvtk.utils.tf_utils    import apply_tf_torch, read_inviwo_tf
from torchvtk.datasets          import TorchDataset

# TODO: Add tests whether results with different dtypes (maybe devices) are similar.
# TODO: Also maybe save reference image to reproduce in tests
#%%
if __name__ == '__main__':
#%%
    dtype  = torch.float32
    device = torch.device('cpu')

    ds = TorchDataset.CQ500('/run/media/dome/Data/data/torchvtk')
    data = ds[42]
    print(data.keys())
    v = data['vol'][None].to(dtype)
    v = F.interpolate(v[None], size=(128,128,128), mode='trilinear').squeeze(0)

    tf     = read_inviwo_tf('data/boron.itf')
    # v = np.load('data/boron.npy')
    # v = torch.from_numpy(v.astype(np.float32))[None] / 2**16
    v = apply_tf_torch(v, tf)
    print(v.shape)
    # v = v[None,None].expand(1, 4, -1, -1, -1)
    rand_pos = get_random_pos(1, 100)
    rand_pos = torch.tensor([-8.36, 14.6, 14.6])[None]           # From inviwo comparison
    view_mat = get_view_mat(rand_pos)
    proj_mat = get_proj_mat(0.5236, 1.0, near=0.1, far=100)[None]   # Inviwo: fov 30deg
    tfm = torch.bmm(view_mat, proj_mat)
    # Debug
    ms = torch.tensor([[[0,0,0,1.0]]]) # origin
    vs = torch.bmm(ms, view_mat); print('Origin in View Space:', vs.squeeze())
    cs = torch.bmm(vs, proj_mat); print('Origin in Clip Space:', cs.squeeze())
    direct = torch.bmm(ms, tfm);  print('Direct transform:', direct)
    print('View Matrix:\n', view_mat)
    print('Proj Matrix:\n', proj_mat)
    # Render
    vr = VolumeRaycaster(ray_samples=256, density_factor=128, resolution=(240,240))
    v = v.to(dtype).to(device)
    t0 = time.time()
    im = vr.forward(v[None], tfm=None)
    im = im.squeeze().permute(1,2,0).cpu().numpy().astype(np.float32)
    print('Time elapsed:', time.time() - t0)
    plt.imshow(im)


# %%


# %%
