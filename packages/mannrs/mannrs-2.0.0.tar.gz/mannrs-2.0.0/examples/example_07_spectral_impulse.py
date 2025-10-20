from mannrs import Stencil
import matplotlib.pyplot as plt
import numpy as np
vmax = 20
print("generating stencil...")
stencil = Stencil(
    L=5.0,
    gamma=3.2,
    Lx=200,
    Ly=200,
    Lz=200,
    Nx=128,
    Ny=128,
    Nz=128,
    parallel=True,
    sinc_thres=12,
    aperiodic_x=False,
    aperiodic_y=False,
    aperiodic_z=False,
)

kx, ky, kz, impu, impv, impw, impuw = stencil.stencil.spectral_impulses()

X, Y = np.meshgrid(kx, ky)
Z = impu[:, :, 0].real
colors = np.empty(Z.shape, dtype=str)
colors=impu[:, :, 0].imag
print(impu[:, :, 0].shape)
# i = len(kz)//2

ax = plt.figure().add_subplot(projection='3d')
surf = ax.plot_surface(X, Y, Z, linewidth=0)
# axes[0].imshow(impu[:, :, 0].real, vmax=vmax)
# axes[1].imshow(impv[:, :, 0].real, vmax=vmax)
# axes[2].imshow(impw[:, :, 0].real, vmax=vmax)
# axes[3].imshow(impuw[:, :, 0].real)

plt.show()