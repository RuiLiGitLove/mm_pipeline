import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from extraction import extract_distribution, kolmogrov_smirnov_test
from rmatching import convolved_circle_px
from scipy.interpolate import splrep, splev
from tifffile import imread
import os
import matplotlib.animation as animation

directory = "Data"
distributions = []
for f in os.listdir(directory):
    if f[-4:] != ".tif":
        continue
    im=imread(directory+'/'+f)
    try:
        dist = extract_distribution(im)
        if len(dist) == 26:
            distributions.append(dist)
    except:
        pass

h_dist = []
for dist in distributions:
    spl = splrep(range(len(dist)), dist)
    xorg = np.linspace(0, len(dist), 100)
    yorg = splev(xorg, spl)
    h = xorg[np.argmax(yorg)]
    h_dist.append(h)

r_test = np.arange(4.4, 6.6, 0.1)
sigmas = np.arange(2, 5, 0.1)
test_results = np.zeros((len(sigmas), len(distributions), len(r_test)))

for z, sig in enumerate(sigmas):
    for i, r in enumerate(r_test):
        for j, dist in enumerate(distributions):
            bins, model = convolved_circle_px(r, h_dist[j], sig, 26)
            test = kolmogrov_smirnov_test(dist, model)
            test_results[z, j, i] = test

min_val = np.amin(np.amin(test_results, axis=2), axis=0)
for i in range(len(sigmas)):
    test_results[i, :, :] = test_results[i, np.argsort(min_val), :]
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_zlim(0, 0.2)

def animate(i):
    ax.clear()
    ax.set_zlim(0, 0.2)
    plt.title("sigma = {}".format(sigmas[i]))
    X = r_test
    Y = range(len(distributions))
    X, Y = np.meshgrid(X, Y)
    Z = test_results[i, :, :]

    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

#    for i, results in enumerate(test_results[i]):
#        ax.plot(r_test, results, zs=i, zdir='y')


    # Add a color bar which maps values to colors.
#    fig.colorbar(surf, shrink=0.5, aspect=5)
Writer = animation.writers['ffmpeg']
writer = Writer(fps=20, metadata=dict(artist='Me'), bitrate=1800)
ani = animation.FuncAnimation(fig, animate, frames = 30, interval= 1000, repeat=True)
ani.save('test_mesh.mp4', writer=writer)