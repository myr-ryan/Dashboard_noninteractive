from bokeh.plotting import figure
from bokeh.models import LabelSet, ColumnDataSource
from bokeh.models import HoverTool
from datetime import datetime
import math

import pandas as pd
from utils import get_frequent



class BarChart_st():
    def __init__(self, plot_data):
        self.plot_data = plot_data
        self.df = pd.DataFrame(plot_data.source.data).copy()
    
    def plot_settings(self, p, x_label, y_label):
        p.xaxis.axis_label = x_label
        p.yaxis.axis_label = y_label

    
    def generate_plot(self, column_name):

        # x_val = self.plot_data.get_column_from_name(self.df, column_name)
        
        selected = self.df.copy()

        x_val, y_val, title_string = get_frequent(top=26, selected=selected, column_name=column_name, plot_data=self.plot_data, include_others=False, sort=False)
        x_val = [str(x.year) for x in x_val]
        res = {'x': x_val, 'y': y_val}
        p = figure(x_range=x_val, height=400, width=700, title='Publication year', tooltips=None)
        hover = HoverTool(tooltips=[("Number", "@{y}")])
        p.add_tools(hover)
        p.vbar(x='x', top='y', width=0.5, source=pd.DataFrame(res))
        labels = LabelSet(x='x', y='y', text='y', x_offset=5, y_offset=5, source=ColumnDataSource(data=res), text_align='right', text_font_size='11px')
        p.add_layout(labels)
        self.plot_settings(p=p, x_label='Year', y_label='No. of studies')
        


        return p

    