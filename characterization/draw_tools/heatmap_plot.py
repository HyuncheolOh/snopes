import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

class HeatmapPlot:

    def __init__(self):
        self.fig_num = 1
        plt.figure(figsize=(20,20))

    def set_data(self, data):
#        self.ax = sns.heatmap(data, cmap="YlGnBu")
        self.ax = sns.heatmap(data)

    def save_image(self, path):
        plt.savefig(path)

