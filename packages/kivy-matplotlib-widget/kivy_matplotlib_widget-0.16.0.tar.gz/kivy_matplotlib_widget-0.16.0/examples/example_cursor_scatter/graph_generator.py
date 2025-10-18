import matplotlib as mpl
import matplotlib.pyplot as plt
from kivy.metrics import dp

#optimized draw on Agg backend
mpl.rcParams['path.simplify'] = True
mpl.rcParams['path.simplify_threshold'] = 1.0
mpl.rcParams['agg.path.chunksize'] = 1000

#define some matplotlib figure parameters
mpl.rcParams['font.family'] = 'Verdana'
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.linewidth'] = 1.0

font_size_axis_title=dp(13)
font_size_axis_tick=dp(12)        

class GraphGenerator(object):
    """class that generate Matplotlib graph."""

    def __init__(self):
        """Create empty structure plot. 
        
        """       
        super().__init__()

        self.fig, self.ax1 = plt.subplots(1, 1)

        # self.line1, = self.ax1.plot([0,1,2,3,4], [1,2,8,9,4],label='line1')
        # self.line2, = self.ax1.plot([2,8,10,15], [15,0,2,4],label='line2')
        
        
        self.ptid = ['1','2','3','4','5','6','7','8','9','10']
        self.x = [2,4,5,7,6,8,9,11,12,12]
        self.y = [1,2,3,4,5,6,7,8,9,10]

        self.scatter1 = self.ax1.scatter(self.x, self.y, s=30, color='magenta', alpha=0.7, marker='x', picker=3)
        for i, ptlbl in enumerate(self.ptid):
            self.ax1.annotate(ptlbl, (self.x[i], self.y[i]),xytext=(5,0),textcoords='offset points',size=8,color='darkslategrey')        
        
        self.fig.subplots_adjust(left=0.13,top=0.96,right=0.93,bottom=0.2)
    
        self.ax1.set_xlabel("axis_x",fontsize=font_size_axis_title)
        self.ax1.set_ylabel("axis_y",fontsize=font_size_axis_title)
                