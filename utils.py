from bokeh.palettes import brewer, d3, inferno, viridis, cividis
import numpy as np
import pandas as pd
     
# Translation between boolean '0' / '1' and 'False' / 'True' 
def bool_to_str(value_list):
    if len(value_list) == 2:
        for x in value_list:
            if (x == '0') or (x == '0.0') or (x == '1') or (x == '1.0'):
                return ['True', 'False']

    return value_list

# Translation between boolean '0' / '1' and 'False' / 'True' 
def str_to_bool(value_list):
    res = []
    for x in value_list:
        if (x == 'False'):
            res.append(False)
        elif (x == 'True'):
            res.append(True)

    return res if res != [] else value_list

def update_other_selects(old, new, select_widget, widget_list, w_type):
    # If the filter is selected from scretch, remove the '(select)' option
    if old == '(select)':
        select_widget.options.remove('(select)')
    # If the selected filter changed, need to update other filter's options as well      
    for c in widget_list.children:
        temp_widget = c.children[0] if w_type == 'filters' else c.children[0].children[0]
        if temp_widget != select_widget:
            temp_widget.options.remove(new)
            if old != '(select)':
                temp_widget.options.append(old)
            temp_widget.options.sort()
    
def js_num_update(general_plot):
    general_plot.apply_filter_num()
    general_plot.update_plot()




def get_index_from_widget_list(widget_list, widget_value, w_type):
        index = -1
        for i in range(len(widget_list.children)):
            temp_w_value = widget_list.children[i].children[0].value if w_type == 'filters' else widget_list.children[i].children[0].children[0].value
            if temp_w_value == widget_value:
                return i
        print('Failed to find in the widget list')
        return index

def edit_button(button, label, type):
    button.label = label
    button.button_type = type

# palette HEX from https://colorbrewer2.org/#type=diverging&scheme=BrBG&n=3
def color_diverging(num):
    palette = {
        1: ('#2b8cbe'),
        2: ('#ece7f2', '#2b8cbe'),
        3: ('#ef8a62','#f7f7f7','#67a9cf'),
        4: ('#ca0020','#f4a582','#92c5de','#0571b0'),
        5: ('#ca0020','#f4a582','#f7f7f7','#92c5de','#0571b0'),
        6: ('#b2182b','#ef8a62','#fddbc7','#d1e5f0','#67a9cf','#2166ac'),
        7: ('#b2182b','#ef8a62','#fddbc7','#f7f7f7','#d1e5f0','#67a9cf','#2166ac'),
        8: ('#b2182b','#d6604d','#f4a582','#fddbc7','#d1e5f0','#92c5de','#4393c3','#2166ac'),
        9: ('#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac'),
        10: ('#67001f','#b2182b','#d6604d','#f4a582','#fddbc7','#d1e5f0','#92c5de','#4393c3','#2166ac','#053061'),
        11: ('#67001f','#b2182b','#d6604d','#f4a582','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac','#053061')
    }
    
    if (num < 1) or (num > 11):
        return ()    
    else:
        return palette[num]

# palette HEX from https://colorbrewer2.org/#type=sequential&scheme=BuGn&n=3
def color_sequential(num):
    palette = {
        1: ('#2b8cbe'),
        2: ('#ece7f2', '#2b8cbe'),
        3: ('#ece7f2','#a6bddb','#2b8cbe'),
        4: ('#f1eef6','#bdc9e1','#74a9cf','#0570b0'),
        5: ('#f1eef6','#bdc9e1','#74a9cf','#2b8cbe','#045a8d'),
        6: ('#f1eef6','#d0d1e6','#a6bddb','#74a9cf','#2b8cbe','#045a8d'),
        7: ('#f1eef6','#d0d1e6','#a6bddb','#74a9cf','#3690c0','#0570b0','#034e7b'),
        8: ('#fff7fb','#ece7f2','#d0d1e6','#a6bddb','#74a9cf','#3690c0','#0570b0','#034e7b'), 
        9: ('#fff7fb','#ece7f2','#d0d1e6','#a6bddb','#74a9cf','#3690c0','#0570b0','#045a8d','#023858')
    }

    if (num < 1) or (num > 9):
        return ()
    else:
        return palette[num]

# palette HEX from https://colorbrewer2.org/#type=qualitative&scheme=Accent&n=3
def color_qualitative(num):
    palette = {
        1: ('#1f78b4'),
        2: ('#a6cee3','#1f78b4'),
        3: ('#a6cee3','#1f78b4','#b2df8a'),
        4: ('#a6cee3','#1f78b4','#b2df8a','#33a02c'),
        5: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99'),
        6: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c'),
        7: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f'),
        8: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00'),
        9: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6'),
        10: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a'),
        11: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99'),
        12: ('#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928')
    }
    
    if (num < 1) or (num > 12):
        return ()
    else:
        return palette[num]
    

def color_palette(nature, num):
    if num < 0:
        return None
    elif num == 1:
        return ['#2b8cbe']
    elif num == 2:
        return ['#ece7f2', '#2b8cbe']
    else:
        if nature == "sequential":
            return inferno(num)
            # return cividis(num)
            # return viridis(num)
            # nature_to_schemes = {
            # # 'sequential': 'PuBu',
            # # 'sequential': 'RdBu',
            # 'sequential': 'Iridescent',
            # 'diverging': 'RdYlBu',
            # 'qualitative': 'Paired'
            # }
            # return brewer[nature_to_schemes[nature]][num]
        # return TolRainbow[num]      
        else:
            return d3['Category20'][num]
        # # brewer only works for num between 3 and 9
        # # # All palettes
        # # nature_to_schemes = {
        # #     'sequential': ['BuGn', 'BuPu', 'GnBu', 'OrRd', 'PuBu', 'PuBuGn', 'Blues', 'Greens', 'Greys', 
        # #                    'PuRd', 'RdPu', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'Oranges', 'Purples', 'Reds'],
        # #     'diverging': ['BrBG', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral'],
        # #     'qualitative': ['Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2', 'Set1', 'Set2', 'Set3']       
        # # }
        # nature_to_schemes = {
        #     'sequential': 'PuBu',
        #     'diverging': 'RdYlBu',
        #     'qualitative': 'Paired'
        # }

        # # # # Palettes used in https://www.shapography.com/
        # # schemes = ['Purple', 'BuGn', 'Blues', 'YlOrRd', 'RdPu', 'PuRd', 'Greys', 'Greens', 'GnBu', 'Reds', 'YlOrBr']
        
        
        # # for i in nature_to_schemes[nature]:
        # #     print(brewer[i][5])

        # return brewer[nature_to_schemes[nature]][num]



def get_frequent(top, selected, column_name, plot_data, include_others=False, sort=True):
            # Extract x axis from the multi-select widget
            x_val = plot_data.get_column_from_name(selected, column_name)

            # Next count the frequency for each x axis value
            # brackets_list could contain multiple values, so need to deal with it separately
            if column_name in plot_data.brackets_list:
                y_val = []
                deleted = []
                for x in x_val:
                    counter = 0
                    for l in plot_data.get_column_from_name(selected, column_name, resolve_bracket=False, unique=False):
                        # Adding '\'' + .. + '\'' is to prevent scenarios like DenseNet will also be detected in DenseNet121        
                        if '\'' + x + '\'' in str(l):           
                            counter += 1
                    if counter == 0:
                        deleted.append(x)

                    else:
                        y_val.append(counter)
                
                x_val = [x for x in x_val if x not in deleted]
                    
            else:
                y_val = []
                deleted = []
                for x in x_val:
                    counter = plot_data.get_column_from_name(selected, column_name, resolve_bracket=False, unique=False).count(x)
                    if int(counter) == 0:
                        deleted.append(x)
                    else:
                        y_val.append(counter)
                
                x_val = [x for x in x_val if x not in deleted]

            title_string = ''
            if len(x_val) > top:
                # print('true')
                top_idx = np.argsort(y_val)[-top:].tolist()
                others_y = np.sum([y_val[y] for y in range(len(y_val)) if y not in top_idx])
                x_val = [x_val[x] for x in top_idx]
                y_val = [y_val[y] for y in top_idx]
                title_string += '(top' + str(top) + ')'
                if include_others:
                    x_val.append('others')    
                    y_val.append(others_y)
                    # sort_idx = np.argsort(y_val).tolist()
                    # x_val = [x_val[x] for x in sort_idx]
                    # y_val = [y_val[y] for y in sort_idx]
            else:
                if sort:
                    # print('sorted')
                    sorted_idx = np.argsort(y_val).tolist()
                    x_val = [x_val[x] for x in sorted_idx]
                    y_val = [y_val[y] for y in sorted_idx]

            return x_val, y_val, title_string


def get_indices_from_df(column_name, selected, category, brackets_list):
     
    if column_name in brackets_list:
        contained_string = '\'' + category + '\''
        indices = selected[column_name].str.contains(contained_string, na=False, case=True, regex=False)
    else:
        contained_string = category
        indices = selected[column_name].str.fullmatch(contained_string, na=False)
    
    return indices

def apply_cat_filters(selected_filter_values, plot_data, column_name):
    df = pd.DataFrame(plot_data.source_backup.data)

    if column_name in plot_data.brackets_list:
        cate_name = selected_filter_values
        df = df[df[column_name].str.contains('|'.join(cate_name), regex=True, na=True)]
    else:    
        df = df[df[column_name].isin(selected_filter_values)]
    
    plot_data.source.data = df
    plot_data.source.remove('index')

    return plot_data



def get_location(plot_data, column_name):
    location_file = pd.read_csv("datasheet/countries.csv")
    df = pd.DataFrame(plot_data.source.data).copy()
    # countries = plot_data.get_column_from_name(df, column_name)
    
    countries, y_val, title_string = get_frequent(top=56, selected=df, column_name=column_name, plot_data=plot_data, include_others=False, sort=False)
    # y_val = [str(y) for y in y_val]
    radius = [(y - min(y_val)) / (max(y_val) - min(y_val)) * 10 for y in y_val]
    radius = [r + 3.0 for r in radius]
    longitudes = []
    latitudes = []
    for c in countries:
        longitudes.append(float(location_file[location_file['country'] == c]['longitude']))
        latitudes.append(float(location_file[location_file['country'] == c]['latitude']))
    # print(location_file[location_file['country'] in countries]['longitude'])


    res = {"country": countries, "count": y_val, "radius": radius, "longitude": longitudes, "latitude": latitudes}
    return pd.DataFrame(res)


# if __name__ == "__main__":
#     color_palette('qualitative')