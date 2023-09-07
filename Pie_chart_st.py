from bokeh.plotting import figure
from bokeh.transform import cumsum
from utils import get_frequent, get_indices_from_df, color_palette
import pandas as pd
from math import pi
import numpy as np
from bokeh.models import LabelSet, ColumnDataSource, Legend, LegendItem, HoverTool



class PieChart_st():
    def __init__(self, plot_data):
        self.plot_data = plot_data
        self.df = pd.DataFrame(plot_data.source.data).copy()
        # For explainability
        self.dim_red = ["UMAP", 'tSNE', 'PCA', 'bh-SNE']
        self.saliency = ["saliency map", "activation map", "probability map"]

    def plot_settings(self, p):
        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None
        p.legend.label_text_font_size = '7pt'
        # p.legend.glyph_height=10
        p.legend.label_standoff=1
        p.legend.spacing=1

    
    def generate_plot(self, column_name):
        extra_title_string = ''
        p = figure(height=400, width=400, title=column_name + extra_title_string, x_range=(-1, 1), y_range=(-1, 1), sizing_mode="fixed")
        selected = self.df.copy()
        
        x_val = list(self.plot_data.get_column_from_name(self.df, column_name))
        x_val, y_val, _ = get_frequent(top=len(x_val), selected=selected, column_name=column_name, plot_data=self.plot_data) 
        if column_name == 'explainability':
            x_val, y_val = self.aggregatation('dim reduction', x_val.copy(), y_val.copy())


        if (len(x_val) == 0):               
            print('no data')
        else:
            top_number = 15

            if (len(x_val) > top_number):
                x_val_top = x_val[-(top_number-1):]
                y_val_top = y_val[-(top_number-1):]
                x_val_top.append('Others')
                y_val_top.append(np.sum(y_val[0:(len(y_val)-top_number+1)]))
                x_val = x_val_top
                y_val = y_val_top

            color_indices = pd.Series([False] * len(selected))
            for c in x_val:
                indices_temp = get_indices_from_df(column_name=column_name, selected=selected, category=c, brackets_list=self.plot_data.brackets_list)
                color_indices = indices_temp | color_indices
            selected = selected[color_indices]
                
            res = pd.DataFrame({'x': x_val, 'y': y_val})
            # res['angle'] = [x/sum(values)*2*pi for x in values]
            res['angle'] = res['y'] / res['y'].sum() * 2*pi
            res['percentage'] = res['y'] / res['y'].sum() * 100
            res['percentage'] = res['percentage'].apply(lambda x: str(round(x, 2)) + '%')
            res['color'] = tuple(reversed(color_palette('diverging', len(x_val))))
            res['end_angle'] = res['angle'].cumsum()

             
            res['label_angle'] = res['end_angle'] - res['angle'] / 2
            res['label_x_pos'] = 0.4 * np.cos(res['label_angle']) - 0.3
            res['label_y_pos'] = 0.5 * np.sin(res['label_angle'])

            new_x = []
            for x in res['x'].tolist():
                new_x.append(x[0:14]+'...' if len(x) > 15 else x)
            res['x'] = new_x

        r = p.wedge(x=-0.3, y=0, radius=0.6, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color='white', fill_color='color', legend_field='x', source=res)
        # r = p.wedge(x=0, y=0, radius=0.8, start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        # line_color='white', fill_color='color', source=res)
        self.plot_settings(p=p)
        # res["percentage"] = res["percentage"].str.pad(35, side = "left")
        # labels = LabelSet(x=-0.3, y=0.0, text='percentage', angle=cumsum('angle', include_zero=True), source=ColumnDataSource(data=res), text_font_size='11px', render_mode='canvas')
        labels = LabelSet(x='label_x_pos', y='label_y_pos', text='percentage', level='glyph', source=ColumnDataSource(data=res), text_font_size='9px')
        p.add_layout(labels)
        hover = HoverTool(tooltips="@x: @y, percentage: @percentage")
        p.add_tools(hover)

        # legend = Legend(items=[LegendItem(label=dict(field="x"), renderers=[r])], location=(0, 0), label_text_font_size = '9px', label_width=5)
        # p.add_layout(legend, 'left')
        

        return p

    def aggregatation(self, agg_str, x_val, y_val):
        if agg_str == 'dim reduction':
            agg_list = self.dim_red
        elif agg_str == 'saliency':
            agg_list = self.saliency
         
        x_val_new = [agg_str]
        y_val_new = [0]

        for i in range(len(x_val)):
            name = x_val[i]
            number = y_val[i]
            if name in agg_list:
                y_val_new[0] += number
            else:
                x_val_new.append(name)
                y_val_new.append(number)
        
        sorted_idx = np.argsort(y_val_new).tolist()
        x_val_new = [x_val_new[x] for x in sorted_idx]
        y_val_new = [y_val_new[y] for y in sorted_idx]
        
        # print(x_val_new)
        # print(y_val_new)  
        return x_val_new, y_val_new  