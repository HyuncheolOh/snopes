import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

class BoxPlot:
    '''
    def __init__(self, data):
        self.data = data
        plt.boxplot(data, showfliers=False)
    '''
    def __init__(self, subplot_num):
        self.fig_num = 1
        self.fig = plt.figure(figsize=(20,20))
        self.subplot_x = subplot_num
        self.subplot_y = subplot_num

    def set_data(self, data, label):
        self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        self.ax.boxplot(data, showfliers = False)
        self.fig_num += 1

    def set_data_with_position(self, data, lebel, grid):
        self.ax = self.fig.add_subplot(grid)
        self.ax.boxplot(data, showfliers = True)

    def set_title(self, title):
        self.ax.title.set_text(title)

    def set_xticks(self, x_ticks):
        plt.xticks(np.arange(len(x_ticks)), x_ticks) 

    def set_label(self, x, y):
        self.x_label = x
        self.y_label = y

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def save_image(self, path):
        plt.savefig(path, bbox_inches='tight')

