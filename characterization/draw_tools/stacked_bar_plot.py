import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

class StackBarPlot:

    def __init__(self, x_index, y_values, subplot_num = 111):
        self.fig_num = 1
        self.bar_width = 1 
        self.colors = plt.get_cmap('gist_rainbow') 
        self.colors = []
        self.subplot_num = subplot_num
        self.fig = plt.figure(figsize=(30,10))

        for name, hex_value in matplotlib.colors.cnames.iteritems():
            self.colors.append(hex_value)

        if subplot_num == 111:
            self.ax = self.fig.add_subplot(111)

            for i in range(len(y_values)):
                self.draw_bar(i, x_index, y_values[i], self.get_bottom(i, y_values))

    def get_bottom(self, index, data):
        if index == 0:
            return None
        else :
            bottom = np.zeros(len(data[0]))
            for i in range(index):
                bottom += np.array(data[i])
            return bottom

    def draw_bar(self, index, x_ticks, data, bottom):
        if index != 0:
            bar = self.ax.bar(x_ticks, data, color=self.colors[index], bottom=bottom, edgecolor='white', width=self.bar_width, align = 'center')
        else :
            bar = self.ax.bar(x_ticks, data, color=self.colors[index], edgecolor='white', width=self.bar_width, align = 'center')

    def set_data(self, x_index, y_values, title):
        self.ax = self.fig.add_subplot(self.subplot_num, self.subplot_num, self.fig_num)
        self.ax.title.set_text(title)
        for i in range(len(y_values)):
            self.draw_bar(i, x_index, y_values[i], self.get_bottom(i, y_values))
        self.fig_num += 1


    def set_legends(self, legends, title=""):
        plt.legend(legends, loc=2, title=title)
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

#        plt.legend(legends, loc='center left', title=title, fontsize=10)
        plt.legend(legends, loc='center left', title=title, fontsize=10, bbox_to_anchor=(1, 0.5))

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def set_xticks(self, x_ticks, rotation='horizontal'):
        plt.xticks(np.arange(len(x_ticks)), x_ticks, rotation=rotation)

    def set_width(self, width):
        self.ax.plot(width = width)


    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')

