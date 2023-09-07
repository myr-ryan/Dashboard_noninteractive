from bokeh.models.widgets import Select, Button, RangeSlider, MultiSelect, NumericInput, DateRangeSlider
from bokeh.models import Div, HoverTool
from bokeh.models import NumeralTickFormatter, CustomJSTickFormatter

import pandas as pd
import numpy as np
import re

import functools
from bokeh.layouts import column, row
from utils import edit_button, update_other_selects, get_index_from_widget_list, bool_to_str, str_to_bool, js_num_update
from math import pi
# import streamlit as st
from bokeh.models.callbacks import CustomJS
from bokeh import events


# Widgets and plot settings for all plots

class GeneralPlot:
    # It should be false at first, the initiation will change it to false
    is_update_from_method = [True]
    is_first_creation = [True]

    def plot_settings(self, plot_figure):
        plot_figure.xaxis.formatter = CustomJSTickFormatter(code="""
            return tick.length > 20 ? tick.substring(0, 20) + '...' : tick;
        """)

    # Callback function for add_filter_button_widget
    def cb_add_filter_button(self):
        # self.plot_data.source_backup.data = pd.DataFrame(self.plot_data.source.data)

        total_options = self.filter_list_ops
        
        # First check what filters has been applied already
        # Then check if all the previous filters have been used (i.e. not '(select)')
        selected_options = []
        is_value_selected = True
        for c in self.filter_widgets.children:
                # c is a row, where the first element is the filter widget, the second element is the value widget
                selected_options.append(c.children[0].value)
                is_value_selected = (is_value_selected and (c.children[0].value != '(select)'))

        if not is_value_selected:
            edit_button(self.add_filter_button_widget, "Please reselect your filter or delete!", "danger")
        else:
            edit_button(self.add_filter_button_widget, "Add categorical filters", "primary")
            options = [x for x in total_options if not x in selected_options]
            options.sort()
            if options == ['(select)']:
                edit_button(self.add_filter_button_widget, "No more filters", "danger")
            else:
                new_filter_widget = Select(title='Select variable(s)', value='(select)', options=options, width=160, height=100)
                new_filter_delete_button = Button(label="Delete", button_type="primary", width=40, height=30, margin=(50, 0, 50, 0))

                new_filter_widget.on_change('value', functools.partial(self.cb_filter_value, widget=new_filter_widget))
                new_filter_delete_button.on_click(functools.partial(self.cb_delete, w_type='filters', add_button=self.add_filter_button_widget, widget=new_filter_widget))

                # Insert a row, where the first element is the filter widget, the second element will be the value widget
                self.filter_widgets.children.insert(0, row(new_filter_widget, new_filter_delete_button))

    def cb_add_range_button(self):
        self.is_update_from_method.insert(0, True)
        self.is_first_creation.insert(0, True)
        total_options = self.num_plus_datetime
        selected_options = []
        is_value_selected = True
        # print(self.range_selectors.children)
        for c in self.range_selectors.children:
                # c is a row, where the first element is the filter widget, the second element is the value widget
                selected_options.append(c.children[0].children[0].value)
                is_value_selected = (is_value_selected and (c.children[0].children[0].value != '(select)'))
        
        if not is_value_selected:
            edit_button(self.add_range_button_widget, "Please reselect your range or delete!", "danger")
        else:
            edit_button(self.add_range_button_widget, "Add numerical filters", "primary")
            options = [x for x in total_options if not x in selected_options]
            options.sort()
            if options == ['(select)']:
                edit_button(self.add_filter_button_widget, "No more ranges", "danger")
            else:
                
                new_range_select_widget = Select(title='Select variable(s)', value="(select)", options=options, width=120, height=40)
                new_range_widget = RangeSlider(start=0, end=1, value=(0,1), title="", width=320)
                new_range_delete_button = Button(label="Delete", button_type="primary", width=50, height=30, margin=(15, 0, 0, 5))
                new_range_min_widget = NumericInput(value=0.0, low=0.0, high=1.0, title="min", width=120, height=40, format=NumeralTickFormatter(format="0,0.000"), mode='float')
                new_range_max_widget = NumericInput(value=0.0, low=0.0, high=1.0, title="max", width=120, height=40, format=NumeralTickFormatter(format="0,0.000"), mode='float')

                new_range_select_widget.on_change('value', functools.partial(self.cb_range_select, select=new_range_select_widget, slider=new_range_widget, min_widget=new_range_min_widget, max_widget=new_range_max_widget))                                                     
                new_range_delete_button.on_click(functools.partial(self.cb_delete, w_type='ranges', add_button=self.add_range_button_widget, widget=new_range_select_widget))

                # Insert
                self.range_selectors.children.insert(0, column(row(new_range_select_widget, new_range_min_widget, new_range_max_widget), row(new_range_widget, new_range_delete_button)))

    # Callback function for first_filter_select_widget and new_filter_widget
    def cb_filter_value(self, attr, old, new, widget):

        # From utils.py
        update_other_selects(old, new, widget, self.filter_widgets, w_type='filters')

        edit_button(self.add_filter_button_widget, "Add categorical filters", "primary")
    
        df = pd.DataFrame(self.plot_data.source_backup.data)
        options=[]

        if new != '(select)':
            options = self.plot_data.get_column_from_name(df, new)
            # Multi-select widget only takes string values as options
            options = [str(x) for x in options]
            options = bool_to_str(options)
        
        # From utils.py
        widget_index = get_index_from_widget_list(self.filter_widgets, new, w_type="filters")
        if new == '(select)':
            new = ''
        num_of_widgets = len(self.filter_widgets.children[widget_index].children)
        if num_of_widgets == 3:
            self.filter_widgets.children[widget_index].children[1].title = new
            self.filter_widgets.children[widget_index].children[1].options = options
            self.filter_widgets.children[widget_index].children[1].value = options
        elif num_of_widgets == 2:
            filter_value_widget = MultiSelect(title=new, value=options, options=options, height=100, width=160, description='Multi Select')
            filter_value_widget.on_change('value', self.cb_filter)
            self.filter_widgets.children[widget_index].children.insert(1, filter_value_widget)
        
    def cb_filter(self, attr, old, new):
        self.apply_filter_bool_cat()
        self.update_plot()
       
    def update_plot():
        pass

    def apply_filter_bool_cat(self):
        df = pd.DataFrame(self.plot_data.source_backup.data)

        # print(filter_widgets.children)
        for c in self.filter_widgets.children:
            # print('haha')
            selected_filter = re.escape(c.children[0].value)
            if selected_filter == '(select)':
                continue
            selected_filter_values = [re.escape(x) for x in list(c.children[1].value)]
            
            if selected_filter in self.plot_data.bool_list:  
                selected_filter_values = str_to_bool(selected_filter_values)
                df = df[df[selected_filter].isin(selected_filter_values)]
                
            elif selected_filter in self.plot_data.categ_list:

                if selected_filter in self.plot_data.brackets_list:

                    cate_name = selected_filter_values
                    
                    df = df[df[selected_filter].str.contains('|'.join(cate_name), regex=True, na=False)]
                else:    
                    df = df[df[selected_filter].isin(selected_filter_values)]

            else:
                print('Selected filter %s is neither bool nor categorical data, which should not happen' % selected_filter)
    
        # print(df['neural network type'].tolist())
        self.plot_data.source.data = df
        self.plot_data.source.remove('index')

        return df


    def apply_filter_num(self):
        df = pd.DataFrame(self.plot_data.source_backup.data)


        for c in self.range_selectors.children:
            selected_range = c.children[0].children[0].value
            if selected_range == '(select)':
                continue
            
            if selected_range in self.plot_data.datetime_list:
                selected_range_min = pd.to_datetime(c.children[1].children[0].value[0], unit='ms')
                selected_range_max = pd.to_datetime(c.children[1].children[0].value[1], unit='ms')
            else:
                selected_range_min = c.children[0].children[1].value
                selected_range_max = c.children[0].children[2].value


            if selected_range in self.num_plus_datetime:
                df = df[df[selected_range].between(selected_range_min, selected_range_max)]
            else:
                print('Selected range %s is not numerical or datetime data, which should not happen' % selected_range)
  
        self.plot_data.source.data = df
        self.plot_data.source.remove('index')

        return df
    
    # Update the range slider whenever the value in min_widget or max_widget has been changed
    def cb_range_text(self, attr, old, new, slider, select_widget, widget):
        # TODO if none
        index = get_index_from_widget_list(self.range_selectors, select_widget.value, w_type="ranges")

        if not self.is_update_from_method[index]:
            if widget.title == 'min':
                max_val = slider.value[1]
                slider.value = (new, max_val)
            else:
                min_val = slider.value[0]
                slider.value = (min_val, new)
            self.apply_filter_num()
            self.update_plot()
        else:
            if not self.is_first_creation[index]:
                self.is_update_from_method[index] = False 
            else:
                self.is_first_creation[index] = False

    # Update the range text inputs --- min_widget or max_widget whenever the values in range slider have been changed
    def cb_range(self, attr, old, new, min_widget, max_widget, select_widget):
        index = get_index_from_widget_list(self.range_selectors, select_widget.value, w_type="ranges")
        # print('cb_range: ', index)
    
        if (old[0] != new[0]) and (old[1] != new[1]):
            self.is_first_creation[index] = True
                
        self.is_update_from_method[index] = True
        if select_widget.value not in self.plot_data.datetime_list:
            min_widget.value = new[0]
            max_widget.value = new[1]  
        else:
            min_widget.value = 0
            max_widget.value = 0
        self.apply_filter_num()
        self.update_plot()


    def cb_delete(self, w_type, add_button, widget):
        if w_type == 'filters':
            widget_list = self.filter_widgets
            edit_button(add_button, "Add categorical filters", "primary")
        else:
            widget_list = self.range_selectors
            edit_button(add_button, "Add numerical filters", "primary")
        self.is_update_from_method[0] = True

        
        # From utils.py
        delete_index = get_index_from_widget_list(widget_list, widget.value, w_type=w_type)
        # TODO change it to del? to free memory space
        del widget_list.children[delete_index]
        # widget_list.children.remove(widget_list.children[delete_index])
        for c in widget_list.children:
            temp_widget = c.children[0] if w_type == 'filters' else c.children[0].children[0]
            temp_widget.options.append(widget.value)
            temp_widget.options.sort()
        
        df = pd.DataFrame(self.plot_data.source_backup.data).copy()
        self.plot_data.source.data = df
        self.plot_data.source.remove('index')
        if w_type == 'filters':
            self.apply_filter_bool_cat()
        else:
            self.apply_filter_num()
        self.update_plot()


    def cb_range_select(self, attr, old, new, select, slider, min_widget, max_widget):
        index = get_index_from_widget_list(self.range_selectors, new, w_type="ranges")

        self.is_update_from_method[index] = True
        self.is_first_creation[index] = True
        update_other_selects(old, new, select, self.range_selectors, w_type='ranges')

        df = pd.DataFrame(self.plot_data.source_backup.data).copy()
        # df = pd.DataFrame(self.plot_data.source.data)
        min_value = df[new].min()
        max_value = df[new].max()

        if new in self.plot_data.datetime_list:
            del self.range_selectors.children[index].children[1].children[0]
            new_slider = DateRangeSlider(value=(min_value, max_value), start=min_value, end=max_value)
            new_slider.on_change('value_throttled', functools.partial(self.cb_range, min_widget=min_widget, max_widget=max_widget, select_widget=select))
            self.range_selectors.children[index].children[1].children.insert(0, new_slider)
            min_widget.disabled = True
            max_widget.disabled = True
       
        else:     
            # in case switch it back from DateRangeSlider to RangeSlider 
            del self.range_selectors.children[index].children[1].children[0]

            # if just changing the filters within the same widget, need to remove the callback functions first
            if old != '(select)':
                del self.range_selectors.children[index].children[0].children[1]
                del self.range_selectors.children[index].children[0].children[1]
                min_widget = NumericInput(value=0.0, low=0.0, high=1.0, title="min", width=120, height=40, format=NumeralTickFormatter(format="0,0.000"))
                max_widget = NumericInput(value=0.0, low=0.0, high=1.0, title="max", width=120, height=40, format=NumeralTickFormatter(format="0,0.000"))


            new_slider = RangeSlider(value=(min_value, max_value), start=min_value, end=max_value)     
            new_slider.on_change('value_throttled', functools.partial(self.cb_range, min_widget=min_widget, max_widget=max_widget, select_widget=select))
            self.range_selectors.children[index].children[1].children.insert(0, new_slider)
            new_slider.start = min_value
            new_slider.end = max_value
            new_slider.value = (min_value, max_value)
            new_slider.step = (max_value - min_value) // 100
            new_slider.title = str(new) 

            min_widget.on_change('value', functools.partial(self.cb_range_text, slider=new_slider, select_widget=select, widget=min_widget))
            max_widget.on_change('value', functools.partial(self.cb_range_text, slider=new_slider, select_widget=select, widget=max_widget))

            if min_widget.disabled:
                min_widget.disabled = False
            if max_widget.disabled:
                max_widget.disabled = False
            
            min_widget.value = min_value
            max_widget.value = max_value
            min_widget.low = min_value
            min_widget.high = max_value
            max_widget.low = min_value
            max_widget.high = max_value     

            if old != '(select)':
                self.range_selectors.children[index].children[0].children.insert(1, max_widget)
                self.range_selectors.children[index].children[0].children.insert(1, min_widget)

    def clear_layout(self, layout):
        # Layout format after resetting: layout = row(column(plot_figure), tabs)
        first_half = layout.children[0].children
        second_half_tab1 = layout.children[1].tabs[0].child.children
        second_half_tab2 = layout.children[1].tabs[1].child.children

        while len(first_half) > 1:
            del first_half[1]
        while len(second_half_tab1) > 2:
            del second_half_tab1[2]
        while len(second_half_tab2) > 0:
            del second_half_tab2[0]


    def reset(self, plot_data, layout):
        self.clear_layout(layout)
        self.layout = layout
        self.plot_data = plot_data

        # ops - options: list plus "(select)", used in widget options
        self.filter_list_ops = self.plot_data.filter_list.copy()
        self.filter_list_ops.insert(0, "(select)")

        self.numeric_var_ops = self.plot_data.numeric_var.copy()
        self.numeric_var_ops.insert(0, "(select)")

        self.categ_list_ops = self.plot_data.categ_list.copy()
        self.categ_list_ops.insert(0, "(select)")

        # self.int_list_ops = self.plot_data.int_list.copy()
        # self.int_list_ops.insert(0, "(select)")

        self.num_plus_datetime = self.numeric_var_ops + self.plot_data.datetime_list

        # Add more filters
        self.add_filter_button_widget = Button(label="Add categorical filters", button_type="primary", width=130, height=30)
        self.add_filter_button_widget.on_click(self.cb_add_filter_button)

        # The first filter selector (for categorical and boolean data)
        self.first_filter_select_widget = Select(title='Select variable(s)', value="(select)", options=self.filter_list_ops, width=160, height=100)
        self.first_filter_select_widget.on_change('value', functools.partial(self.cb_filter_value, widget=self.first_filter_select_widget))

        # The first delete button for filter
        self.first_filter_delete_button = Button(label="Delete", button_type="primary", width=40, height=30, margin=(50, 0, 50, 0))
        self.first_filter_delete_button.on_click(functools.partial(self.cb_delete, w_type='filters', add_button=self.add_filter_button_widget, widget=self.first_filter_select_widget))

        # Add more range sliders
        self.add_range_button_widget = Button(label="Add numerical filters", button_type="primary", width=150, height=30)
        self.add_range_button_widget.on_click(self.cb_add_range_button)     
       
        # The first range slider
        self.first_range_widget = RangeSlider(start=0, end=1, value=(0,1), title="", width=320)

        # The first set of range input for min max selection
        self.first_range_min_widget = NumericInput(value=0.0, low=0.0, high=1.0, title="min", width=120, height=40, format=NumeralTickFormatter(format="0,0.000"), mode='float')
        self.first_range_max_widget = NumericInput(value=0.0, low=0.0, high=1.0, title="max", width=120, height=40, format=NumeralTickFormatter(format="0,0.000"), mode='float')

        # The first range slider selector (for numerical data)
        self.first_range_select_widget = Select(title='Select variable(s)', value="(select)", options=self.num_plus_datetime, width=120, height=40)
        self.first_range_select_widget.on_change('value', functools.partial(self.cb_range_select, select=self.first_range_select_widget, slider=self.first_range_widget, min_widget=self.first_range_min_widget, max_widget=self.first_range_max_widget))                                            

        # The first delete button for range slider
        self.first_range_delete_button = Button(label="Delete", button_type="primary", width=50, height=30, margin=(15, 0, 0, 5))
        self.first_range_delete_button.on_click(functools.partial(self.cb_delete, w_type='ranges', add_button=self.add_range_button_widget, widget=self.first_range_select_widget))
       

        self.filter_widgets = column(row(self.first_filter_select_widget, self.first_filter_delete_button))
        self.range_selectors = column(column(row(self.first_range_select_widget, self.first_range_min_widget, self.first_range_max_widget), row(self.first_range_widget, self.first_range_delete_button)))
        self.plot_spec_select_widgets = column(row())
        
    def __init__(self, plot_data, layout):
        self.reset(plot_data, layout)
        