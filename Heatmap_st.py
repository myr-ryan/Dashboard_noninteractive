from bokeh.plotting import figure
from bokeh.transform import linear_cmap
from bokeh.models import BasicTicker, PrintfTickFormatter, ColorBar, FixedTicker, HoverTool
from bokeh.palettes import d3
import pandas as pd
import numpy as np
from math import pi
from utils import get_frequent, get_indices_from_df, color_palette



class Heatmap_st():
    def __init__(self, plot_data):
        self.plot_data = plot_data
        self.df = pd.DataFrame(plot_data.source.data).copy()
        self.dict = {'performance_mean': 'avg',
                     'performance_accuracy': 'acc',
                     'performance_F1': 'F1',
                     'performance_sensitivity (recall)': 'rec',
                    #  'performance_NPV': 'NPV',
                     'performance_specificity': 'spec',
                     'performance_precision (PPV)': 'pre',
                     'performance_auc': 'auc'}

    def plot_settings(self, p):
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.xaxis.major_label_orientation = pi / 4
        # p.xaxis.major_label_standoff = 10  # To prevent labels from overlapping
        # p.yaxis.major_label_orientation = pi / 3
        # p.legend.label_text_font_size = '8pt'
        # p.legend.glyph_height=10
        # p.legend.label_height=10
    

    def generate_plot(self, column_name, exclude_seg=False, exclude_prefix=False):
        selected = self.df.copy()
        if exclude_seg:
            selected = selected[selected['ml_task_description'].isin(['bi_cla', 'mul_cla', 'weakly_sup', 'unsupervised'])]

        all_plotable = [x for x in self.plot_data.numeric_var if 'performance' in x and (x != 'performance_NPV')]
        y_label = [self.dict[x] for x in all_plotable]

        if column_name in ['DataSize_all', 'DataSize_training', 'DataSize_testing', 'DataSize_validation']:
            selected = selected[selected['image_type'].isin(['WSIs'])]
            melted_df, x_label = self.deal_with_datasize(column_name, selected, all_plotable)
        else:
            # 2023.09.05: 88 neural network types
            x_val, fre_y, title_string = get_frequent(top=20, selected=selected, column_name=column_name, plot_data=self.plot_data, include_others=False)
            if column_name == 'neural_network_type':
                # 2023.09.05: delete 
                del x_val[1]
                del fre_y[1]
            # print(fre_y)
            # if exclude_prefix:
            #     x_val = [s.split('_')[1:][0] for s in x_val]
            if exclude_prefix:
                x_label = [str(x_val[i].split('_')[1:][0]) + ' (' + str(fre_y[i]) + ')' for i in range(len(x_val))]
            else:
                x_label = [str(x_val[i]) + ' (' + str(fre_y[i]) + ')' for i in range(len(x_val))]

            df_stack = pd.DataFrame([])
            for cat in x_val: 
                indices = get_indices_from_df(column_name, selected, cat, self.plot_data.brackets_list)
                stacked_per_task = selected[all_plotable][indices]
                stacked_per_task = stacked_per_task.reset_index()
                stacked_per_task = stacked_per_task.drop(['index'], axis=1)
                df_stack = pd.concat([df_stack, stacked_per_task.median(axis=0, skipna=True)], axis=1)
            
            df_stack = df_stack.fillna(0)
            df_stack.columns = x_label

            # df_stack = df_stack.transpose()
            # if (df_stack.max(axis=0) - df_stack.min(axis=0)).any() != 0:
            #     df_stack = (df_stack - df_stack.min(axis=0)) / (df_stack.max(axis=0) - df_stack.min(axis=0))
            # else:
            #     # TODO test this
            #     df_stack = df_stack / df_stack.min(axis=0)
            # df_stack = df_stack.transpose()

            melted_df = df_stack.reset_index().melt(id_vars='index')
            melted_df.columns = ['All_numerical', column_name, 'nums']

            melted_df["All_numerical"] = melted_df["All_numerical"].astype("str")
            melted_df["All_numerical"] = [self.dict[x] for x in melted_df["All_numerical"]]
            melted_df[column_name] = melted_df[column_name].astype("str")
            # print(melted_df[melted_df['neural_network_type']=='ShuffleNet'])

        p = figure(height=400, width=400, title=column_name, x_range=x_label, y_range=y_label, x_axis_location='above', sizing_mode="fixed")
        y_range = all_plotable
        y_range = [str(x) for x in y_range]    
        self.plot_settings(p)
        ticks = np.linspace(0.5, 1.0, 11, dtype=np.float32)
        color_ticks = FixedTicker(ticks=ticks)
        # colors = tuple(reversed(color_palette("sequential", 30)))
        colors = color_palette("sequential", 30)
        p.rect(x=column_name, y="All_numerical", width=1, height=1, source=melted_df, fill_color=linear_cmap('nums', colors, low=0.5, high=1.0), line_color=None) 
        hover = HoverTool(tooltips="median: @nums")
        p.add_tools(hover)
        p.add_layout(ColorBar(color_mapper=linear_cmap('nums', colors, low=0.5, high=1.0)['transform'], width=8, location=(0,0), ticker=color_ticks), 'right')

        return p

    def deal_with_datasize(self, column_name, selected, all_plotable):
        length_x = 11

        splits = np.linspace(0.0, 1.0, length_x)
        # print(splits)
        quantiles = selected[column_name].quantile(q=splits)
        selected['interval'] = pd.cut(selected[column_name], bins=quantiles, labels=False, include_lowest=True)
        # print(selected.groupby('interval')[all_plotable].median)
        median_by_interval = selected.groupby('interval')[all_plotable].median()
        median_by_interval = median_by_interval.reset_index().drop(columns=['interval'])
        # print(median_by_interval)
        melted_df = median_by_interval.reset_index().melt(id_vars='index')
        # print(melted_df)
    
        quantile_counts = selected['interval'].value_counts().sort_index()
        # print(quantile_counts)

        x_val = []
        quantile_list = quantiles.tolist()
        for i in range(len(quantile_list) - 1):
            x_val.append(str(round(quantile_list[i])) + '-' + str(round(quantile_list[i+1])) + ' slides (' + str(quantile_counts.tolist()[i]) + ')')    
        x_label = x_val
        replace_list = np.linspace(0, length_x-2, length_x-1)
        # print(replace_list)
        melted_df['index'] = melted_df['index'].replace(replace_list, x_val)
        melted_df['variable'] = melted_df['variable'].replace(self.dict)
        melted_df = melted_df.rename(columns={'index': column_name, 'value': 'nums', 'variable': 'All_numerical'})
        # print(melted_df)

        return melted_df, x_label

