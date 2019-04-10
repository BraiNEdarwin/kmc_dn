import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from kmc_dopant_networks_utils import visualize_traffic

# Requires installation: sudo apt-get install ffmpeg

def getWriter(fps, title):
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title=title)
    writer = FFMpegWriter(fps=fps, metadata=metadata)
    return writer

def initScatterAnimation(kmc):
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(right=kmc.xdim)
    ax.set_ylim(top=kmc.ydim)
    acceptors, = ax.plot(kmc.xCoords[:kmc.N], kmc.yCoords[:kmc.N], 'o', color='black')
    history_acceptors, = ax.plot(kmc.xCoords[:kmc.N], kmc.yCoords[:kmc.N], 'o', color='black')
    donors, = ax.plot(kmc.xCoords[kmc.N:], kmc.yCoords[kmc.N:], 'o', color='red')
    history_donors, = ax.plot(kmc.xCoords[kmc.N:], kmc.yCoords[kmc.N:], 'o', color='red')

    text_element = ax.text(0.5, -0.1, "Error: , time: , strategy: ", horizontalalignment='center')

    return acceptors, donors, history_acceptors, history_donors, text_element, fig



def animateTransition(kmc, donors, acceptors, history_donors, history_acceptors, text_element, index, target_pos, writer, splits, refresh_history, alpha, text):
    acceptorDataX = [kmc.xCoords[j] for j in range(kmc.N)]
    acceptorDataY = [kmc.yCoords[j] for j in range(kmc.N)]
    donorDataX = [kmc.xCoords[j] for j in range(kmc.N, kmc.N+kmc.M)]
    donorDataY = [kmc.yCoords[j] for j in range(kmc.N, kmc.N+kmc.M)]

    text_element.set_text(text)

    for i in range(splits):
        if index < kmc.N:
            acceptorDataX[index] = (kmc.xCoords[index]*(splits-i)+target_pos[0]*i) / splits
            acceptorDataY[index] = (kmc.yCoords[index]*(splits-i)+target_pos[1]*i) / splits
        else:
            donorDataX[index-kmc.N] = (kmc.xCoords[index]*(splits-i)+target_pos[0]*i) / splits
            donorDataY[index-kmc.N] = (kmc.yCoords[index]*(splits-i)+target_pos[1]*i) / splits
        donors.set_data(donorDataX, donorDataY)
        acceptors.set_data(acceptorDataX, acceptorDataY)
        if refresh_history:
            history_acceptors.set_data(acceptorDataX, acceptorDataY)
            history_acceptors.set_alpha(0.5)
            history_donors.set_data(donorDataX, donorDataY)
            history_donors.set_alpha(0.5)
        else:
            history_acceptors.set_alpha(alpha)
            history_donors.set_alpha(alpha)
        writer.grab_frame()

def trafficAnimation(kmc, search_results, writer, file_name):
    fig = plt.figure()
    with writer.saving(fig, file_name, 100):
        for entry in search_results:
            kmc.electrodes = entry[0]
            kmc.current = entry[1]
            kmc.traffic = entry[2]
            plt.clf()
            visualize_traffic(kmc, figure=fig)
            writer.grab_frame()
