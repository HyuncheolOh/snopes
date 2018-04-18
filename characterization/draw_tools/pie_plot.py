import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

class PiePlot:

    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.colors = []
        for name, hex_value in matplotlib.colors.cnames.iteritems():
            self.colors.append(hex_value)

    def set_data(self, data, labels):
        pie = self.ax.pie(data, colors = self.colors, autopct='%1.1f%%', startangle=0)
        plt.legend(pie[0], labels, loc='center right', bbox_to_anchor=(1,0.5), bbox_transform=plt.gcf().transFigure, fontsize=6)
        plt.subplots_adjust(left=0.0, right=0.7)

    def save_image(self, path):
        plt.savefig(path)


