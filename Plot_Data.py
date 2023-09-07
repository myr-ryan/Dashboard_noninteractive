from bokeh.models import ColumnDataSource
import numpy as np
import pandas as pd
from collections import Counter
import re


class Plot_Data:

    datetime_keywords = ['date', 'year', 'month']

    def __init__(self, data):
        self.source = ColumnDataSource(data=data)
        self.source_backup = ColumnDataSource(data=data)
        # Class variables
        self.column_names = []
        self.filter_list = []
        self.numeric_var = []
        self.bool_list = []
        self.categ_list = []
        self.brackets_list = []
        self.datetime_list = []
        self.string_list = []
        self.subspec_list = []

    
    def is_equal_two_list(self, list1, list2):

        if len(list1) == len(list2):
            is_same = all([x == y for x, y in zip(list1, list2)])
        else:
            is_same = False
        return is_same

    def get_column_from_name(self, df, column_name, resolve_bracket=True, unique=True, regex=False):

        column_data_no_nan = [x for x in df[column_name].tolist() if ((str(x) != 'nan') and (str(x) != '<NA>') and (str(x) != 'NaT'))]
        if unique:
            column_data_no_nan = np.unique(column_data_no_nan).tolist()
        
        if (resolve_bracket) and (column_name in self.brackets_list):

            for i in range(len(column_data_no_nan)):
                column_data_no_nan[i] = column_data_no_nan[i].replace('[', '')
                column_data_no_nan[i] = column_data_no_nan[i].replace(']', '')
                column_data_no_nan[i] = column_data_no_nan[i].replace('\'', '')
                column_data_no_nan[i] = column_data_no_nan[i].split(', ')

            if regex:
                res = np.unique([re.escape(x) for sublist in column_data_no_nan for x in sublist])
            else:
                res = np.unique([x for sublist in column_data_no_nan for x in sublist])

            return res.tolist()
        else:
            return [re.escape(x) for x in column_data_no_nan] if regex else column_data_no_nan

    def convert_with_warning(self, df, column_name, type):
        try: 
            if (type == 'Int64') or (type == 'Float64') or (type == bool):
                df[column_name] = df[column_name].fillna(0)
                df = df.astype({column_name: type})
            elif type == 'datetime64[ns]':
                if len(str(df.loc[0, column_name])) == 4:
                    df[column_name] = pd.to_datetime(df[column_name], format='%Y')
                else:
                    df[column_name] = pd.to_datetime(df[column_name])
            else:
                df = df.astype({column_name: type})
                
            return df
        except:
            print('Data type conversion failed for column ', column_name)

    def is_category(self, column_data_no_nan, c):  
        unique = np.unique(column_data_no_nan)
        # print(len(column_data_no_nan)/3.0)
        # print(len(unique))
        if len(unique) > 0:
            if (str(column_data_no_nan[0]).startswith('[')) and (str(column_data_no_nan[0]).endswith(']')):
                self.categ_list.append(c)
                self.brackets_list.append(c)
                return True
            elif (len(unique) != 1) and (len(unique) < (len(column_data_no_nan) / 3.0)):
                self.categ_list.append(c)
                return True
    
        return False

    def is_bool(self, column_data_no_nan, c):
        unique = np.unique(column_data_no_nan)
        if (len(unique) != 1) and (len(unique) != 2):
            return False
        elif self.is_equal_two_list(unique, [0., 1.]) or self.is_equal_two_list(unique, [0, 1]):
            self.bool_list.append(c)
            return True
        elif self.is_equal_two_list(unique, [1., 0.]) or self.is_equal_two_list(unique, [1, 0]):
            self.bool_list.append(c)
            return True
        elif (unique == [0]) or (unique == [0.0]):
            self.bool_list.append(c)
            return True
        elif (unique == [1]) or (unique == [1.0]):
            return True
        
        return False

    def type_conversion(self, df):

        for c in df.columns:  
                # print(df[c].dtype)
                if any(d in c.lower() for d in self.datetime_keywords):
                    self.datetime_list.append(c)
                    df = self.convert_with_warning(df, c, 'datetime64[ns]')
                elif df[c].dtype == 'string':
                    column_data_no_nan = [x for x in df[c].tolist() if ((str(x) != 'nan') and (str(x) != '<NA>'))]
                    if self.is_category(column_data_no_nan, c):
                        df = self.convert_with_warning(df, c, 'category')
                    else:
                        self.string_list.append(c)
                elif (df[c].dtype == 'Float64') or (df[c].dtype == 'Int64'):
                    column_data_no_nan = [x for x in df[c].tolist() if ((str(x) != 'nan') and (str(x) != '<NA>'))]   
                    if self.is_bool(column_data_no_nan, c):
                        df = self.convert_with_warning(df, c, bool)
                    elif self.is_category(column_data_no_nan, c):
                        df = self.convert_with_warning(df, c, 'category')
                    else:
                        self.numeric_var.append(c)
                else:
                    self.string_list.append(c)
                    df = self.convert_with_warning(df, c, 'string')

        return df



    def bol_to_cat(self, df, new_column_name, columns):

        cols_to_cat = df.loc[:, columns]
        df.drop(columns, axis=1, inplace=True)

        # Make them bracket like categorical data
        cols_to_cat = cols_to_cat.where(cols_to_cat != 1, cols_to_cat.columns.to_series(), axis=1)
        cols_to_cat.replace(0, np.nan, inplace=True)
        cols_to_cat.replace(False, np.nan, inplace=True)
        
        
        cols_to_cat[new_column_name] = cols_to_cat.values.tolist()
        cols_to_cat[new_column_name] = cols_to_cat[new_column_name].apply(lambda x: [i for i in x if (str(i) != "nan")])
        cols_to_cat[new_column_name] = cols_to_cat[new_column_name].apply(lambda x: [''.join(i) for i in x])
        cols_to_cat[new_column_name] = [str(x) if x != [] else np.nan for x in cols_to_cat[new_column_name]]

        df[new_column_name] = cols_to_cat[new_column_name].copy()
        df = self.convert_with_warning(df, new_column_name, 'category')
        # df[new_column_name].fillna(np.nan, inplace=True)
        
        return df


    def detect_cat_from_bool(self, df):
        columns = self.bool_list
        columns = [item.split('_') for item in columns]
        columns = [item for sublist in columns for item in sublist]
        element_count = Counter(columns)
        possible_cate_list = np.unique([element for element in columns if element_count[element] >= 5])
        for p in possible_cate_list:
            list_conv = [i for i in self.bool_list if ((i.startswith(p)) or (i.endswith(p)))]
            self.bool_list = [item for item in self.bool_list if item not in list_conv]
            self.categ_list.append(p)
            self.brackets_list.append(p)
            df = self.bol_to_cat(df, p, list_conv)

        return df



    def preprocessing(self, df):

        df = df.convert_dtypes() 
        # df = df.replace(pd.NA, np.nan)
        # df = df.applymap(lambda x: x if x is not pd.NA else np.nan)
        # df.fillna(np.nan, inplace=True)
        # df = df.replace({pd.NA: np.nan})

        df = self.type_conversion(df)   
        df = self.detect_cat_from_bool(df)


        self.column_names = df.columns.tolist()

        self.filter_list = self.categ_list + self.bool_list

        self.subspec_list = self.get_column_from_name(df, 'subspec')



        # Bokeh takes index in dataframe as a seperate column, which will cause issue afterwards
        # print(df.iloc[-1, 0])
        # print(df.iloc[-1, -1])
        # print(df)
        self.source.data = df
        self.source.remove('index')
        self.source_backup.data = df
        self.source_backup.remove('index')

        return df



    def debug_printing(self):

        print('Column names are: ', self.column_names)
        print('Filter list (categorical + boolean): ', self.filter_list)
        print('Bool list: ', self.bool_list)
        print('Numerical list: ', self.numeric_var)
        print('Datetime list: ', self.datetime_list)
        print('Bracket list: ', self.brackets_list)
        print('Category list: ', self.categ_list)

