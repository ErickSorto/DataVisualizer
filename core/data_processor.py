import numpy as np
import pandas as pd
from pathlib import Path
import math
import matplotlib.pyplot as plt
import re

'''
Notes on how this whole thing works
    step 1: initialize a main object and add files.
    step 2: call the method coresponding to what output the user wants with all of their data
Notes on common method parameters
    id(s): label for a row/column or an excel format
    is_col: boolean value for whether data is coming from a column or row
    selection(s): denotes whether the corresponding id is a label or an excel format. Either 'label' or 'index'
    first_element(s): bool value for whether or not the first entry in a row/column should be included (ignored if selection is 'label')
    axis_scale,x_scale,y_scale: how the axes of the plot are scaled. Options are 'linear' (default), 'log', 'symlog' (log scale that allows 0, negative), 'logit' (google it)
'''

def base_26_converter(letters: str) -> str | int:
    '''
    Args:
        inputs: letters (dtype: string)
        outputs: index (dtype: string)
    Behavior:
        converts excel letter indexing into base 10
    Remark:
        output assumes zero indexing so output = input - 1
    '''
    map = {
        'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,'j':10,'k':11,'l':12,'m':13,
        'n':14,'o':15,'p':16,'q':17,'r':18,'s':19,'t':20,'u':21,'v':22,'w':23,'x':24,'y':25,'z':26
    }
    letters = [i for i in letters.lower()][::-1]
    index = 0
    for i in range(len(letters)):
        index += map[letters[i]] * (26 ** i)
    return index - 1

# for testing purposes. returns the names of all files in a folder
def get_all_filenames(path: str | Path) -> list[str]:
    path = Path(path)
    return [str(i) for i in path.iterdir()]

class DataProcessor():
    '''
    Data:
        filenames (dtype: set[str])
        active_filenames (dtype: set[str])
    '''
    def __init__(self):
        self.filenames : set[str] = set()
        self.active_filenames : set[str] = set()

    def add_filenames(self, filenames: list[str] | list[Path] |Path | str):
        '''
        Args:
            filenames
        Behavior:
            add filenames into self.filenames and self.active_filenames
        '''
        # convert to list (if needed):
        if isinstance(filenames, (str, Path)):
            filenames = [filenames]
            
        for i in filenames:
            self.filenames.add(i)
            self.active_filenames.add(i)

    def remove_filenames(self, filenames: list[str] | list[Path] | Path | str):
        '''
        Args:
            filenames
        Behavior:
            remove filenames in self.filenames and self.active_filenames
        '''
        # convert to list (if needed):
        if isinstance(filenames, (str, Path)):
            filenames = [filenames]

        for i in filenames:
            if i in self.filenames:
                self.filenames.remove(i)
            if i in self.active_filenames:
                self.active_filenames.remove(i)

    def activate_filenames(self, filenames: list[str] | list[Path] | Path | str):
        '''
        Args:
            filenames
        Behavior:
            move filenames in self.filenames to self.active_filenames
        '''
        # convert to list (if needed):
        if isinstance(filenames, (str, Path)):
            filenames = [filenames]

        for i in filenames:
            if i in self.filenames:
                self.active_filenames.add(i)

    def deactivate_filenames(self, filenames: list[str] | list[Path] | Path | str):
        '''
        Args:
            filenames
        Behavior:
            move filenames in self.active_filenames to self.filenames
        '''
        # convert to list (if needed):
        if isinstance(filenames, (str, Path)):
            filenames = [filenames]

        find = False
        for i in filenames:
            if i in self.active_filenames:
                self.active_filenames.remove(i)
                find = True
        if not find:
            raise FileNotFoundError()               

    def get_filenames(self):
        '''
        Behavior:
            returns sorted list of filenames stored in object
        '''
        return (sorted(list(self.filenames)), sorted(list(self.active_filenames)))

    def load_file(self, filename):
        '''
        Args:
            filename
        Behavior:
            reads in xlsx and csv files and returns a 2 dimensional numpy array
        '''

        if filename.endswith(('xlsx', 'xls', 'xlsm', 'xlsb', 'odf', 'ods', 'odt')):
            sheets = list(pd.read_excel(filename, header=None, sheet_name=None).values()) #file no longer exists (FileNotFoundError) or is open elsewhere (PermissionError)
            for i in range(len(sheets)):
                sheets[i] = sheets[i].to_numpy()
            return sheets
        elif '.csv' in filename:
            return [pd.read_csv(filename, header=None).to_numpy()] #same issue

    def get_column(self, filename, column_id, selection='label', include_first_element=True):
        '''
        Args:
            filename: the file you want to analyse
            column_id: an integer/string indicates which column you want
            selection: either 'label' or 'index'
            include_first_element: a bool value indicates whether to choose the first element
        Return:
            list/np.array
        Behavior:
            Given the argments, function will return you a list/numpy array (of your desired column)
        '''
        sheets = self.load_file(filename)
        columns = []
        if selection == 'label':
            for contents in sheets:
                found = False
                for i in range(len(contents[0])):
                    if contents[0][i] == column_id:
                        columns.append(contents[1:,i])
                        found = True
                if not found:
                    columns.append([])
        
        elif selection == 'index':
            for contents in sheets:
                if column_id >= len(contents[0]):
                    columns.append([])
                else:
                    column = contents[:,column_id]
                    if type(column[0]) != type(column[1]) or not include_first_element:
                        column = column[1:]
                    columns.append(column)
        return columns

    def get_row(self, filename, row_id, selection='label', include_first_element=True):
        '''
        Args:
            filename: the file you want to analyse
            row_id: an integer/string indicates which row you want
            selection: either 'label' or 'index'
            include_first_element: a bool value indicates whether to choose the first element
        Return:
            list/np.array
        Behavior:
            Given the argments, function will return you a list/numpy array (of your desired row)
        '''
        sheets = self.load_file(filename)
        rows = []
        if selection == 'label':
            for contents in sheets:
                found = False
                for i in range(len(contents)):
                    if contents[i][0] == row_id:
                        rows.append(contents[i][1:])
                        found = True
                if not found:
                    rows.append([])
        
        elif selection == 'index':
            for contents in sheets:
                if row_id >= len(contents):
                    rows.append([])
                else:
                    row = contents[row_id]
                    if type(row[0]) != type(row[1]) or not include_first_element:
                        row = row[1:]
                    rows.append(row)

        return rows

    # be careful here: this is only allowed after python 3.8
    def search_column(self, column_ids : list[str], selections: list[str], first_elements : list[bool]):
        '''
        Args:
            column_ids: a list of strings indicate which column you want
            selections: a list of selections indicate you want 'index' or 'label'
            first_elements: a list of bool value indicate whether you want to include first elements
        Return:
            list/np.array
        Behavior:
            given above argments, return a list/np.array that collects such columns across all .csv files (or excel) 
        '''
        num_columns = len(column_ids)
        # fix bug (2026/09/17):
        # create a deep copy of column_ids:
        column_ids_copy = column_ids.copy()
        for i in range(num_columns):
            if selections[i] == 'index':
                column_ids_copy[i] = base_26_converter(column_ids[i])

        aggregate_columns = [np.array([]) for _ in range(num_columns)]
        for filename in sorted(list(self.active_filenames)):
            columns = []
            for i in range(num_columns):
                columns.append(self.get_column(filename, column_ids_copy[i], selections[i], first_elements[i]))

            fail = [False for _ in range(len(columns[0]))]
            for i in range(num_columns - 1):
                for j in range(len(columns[i])):
                    if len(columns[i][j]) != len(columns[i+1][j]):
                        fail[j] = True
            for j in range(len(columns[0])):
                if not fail[j]:
                    for i in range(num_columns):
                        aggregate_columns[i] = np.concatenate((aggregate_columns[i], columns[i][j]))
        print(len(aggregate_columns[0]))
        if len(aggregate_columns[0]) == 0:
            raise NameError('no data found')
        return aggregate_columns

    def search_row(self, row_ids : list[str], selections: list[str], first_elements : list[bool]):
        '''
        Args:
            row_ids: a list of strings indicate which row you want
            selections: a list of selections indicate you want 'index' or 'label'
            first_elements: a list of bool value indicate whether you want to include first elements
        Return:
            list/np.array
        Behavior:
            given above argments, return a list/np.array that collects such rows across all .csv files (or excel) 
        '''
        num_rows = len(row_ids)

        # fix bug (2026/09/17):
        # create a deepcopy of column_ids:
        row_ids_copy = row_ids.copy()
        for i in range(num_rows):
            if selections[i] == 'index':
                row_ids_copy[i] = int(row_ids[i]) - 1

        aggregate_rows = [np.array([]) for _ in range(num_rows)]
        for filename in sorted(list(self.active_filenames)):
            rows = []
            for i in range(num_rows):
                rows.append(self.get_row(filename, row_ids_copy[i], selections[i], first_elements[i]))

            fail = [False for _ in range(len(rows[0]))]
            for i in range(num_rows - 1):
                for j in range(len(rows[i])):
                    if len(rows[i][j]) != len(rows[i+1][j]):
                        fail[j] = True
            for j in range(len(rows[0])):
                if not fail[j]:
                    for i in range(num_rows):
                        aggregate_rows[i] = np.concatenate((aggregate_rows[i], rows[i][j]))

        if len(aggregate_rows[0]) == 0:
            raise NameError('no data found')
        return aggregate_rows

    def statistics(self, id : str, is_col : bool, selection='label', first_element=False):
        '''
        Args:
            id: a string indicate which row/column you want to choose
            is_col: a bool value indicates whether you want to choose a column
            selection: either 'label' or 'index'
            first_element: a bool value indicates whether to choose the first element
        Return:
            statistics of that row/column
            format: (mean, median, sd)
        '''
        if is_col:
            data = self.search_column([id], [selection], [first_element])[0]
        else:
            data = self.search_row([id], [selection], [first_element])[0]

        data = data[~pd.isna(data.astype(float))]

        mean = 0
        for i in data:
            mean +=i
        mean /= len(data) #no data will cause ZeroDivisionError

        if len(data) % 2 == 0:
            median = (data[int(len(data) / 2)] + data[int((len(data)) - 1)])
        else:
            median = data[int(len(data) / 2)]

        standard_dev = 0
        for i in data:
            standard_dev += (i - mean) ** 2
        standard_dev /= len(data)
        standard_dev = math.sqrt(standard_dev)

        return (mean, median, standard_dev)

    def box_plot(self, ids: list[str], is_col : bool, selections : list[str], first_elements : list[bool], 
                title=None, label=None, axis_scale = 'linear'):
        '''
        Behavior:
            plot a box
        '''

        plt.close()

        if is_col:
            data = self.search_column(ids, selections, first_elements)
        else:
            data = self.search_row(ids, selections, first_elements)

        plt.boxplot(data, tick_labels=ids)

        if title != None:
            plt.title(title)
        if label != None:
            plt.ylabel(label)

        plt.yscale(axis_scale)

        plt.show()

    def histogram(self, ids : list[str], is_col : bool, selections: list[str], first_elements : list[bool],
                title=None, x_label=None, y_label=None , x_scale='linear', y_scale='linear', bins=10):
        '''
        Behavior:
            plot a histogram
        '''
        # fix bug (2026/09/17): AttributeError: 'DataProcessor' object has no attribute 'column_search'
        # print(f'inside processor.histogram, before search_column: {ids}, and the type of ids[0] is: {type(ids[0])}')
        
        plt.close()
        
        if is_col:
            data = self.search_column(ids, selections, first_elements)
        else:
            data = self.search_row(ids, selections, first_elements)

        # fix bug (2026/09/17): TypeError: 'value' must be an instance of str or bytes, not a int
        # Explanation: inside function: search_column and search_row, you use:
        # column_ids[i] = base_26_converter(column_ids[i])
        # row_ids[i] = int(row_ids[i]) - 1
        # Because in python, list are passed in a mutable way (aka. pass by reference in C++)
        # so, change in search_column and search_row would affect here!

        # fix bug (2026/09/17): TypeError: '<=' not supported between instances of 'int' and 'str'
        # Explanation: data has different type (mix string and int)
        # be careful when you choose your data
        # print(f'before plt.hist(): {ids} and dtype of ids[0]: {type(ids[0])}')
        plt.hist(data, bins=bins, rwidth=0.9, label=ids)

        if title != None:
            plt.title(title)
        if x_label != None:
            plt.xlabel(x_label)
        if y_label != None:
            plt.ylabel(y_label)

        plt.xscale(x_scale)
        plt.yscale(y_scale)
        plt.legend()

        plt.show()
        
    def pie_chart(self, id: str, is_col: bool, selection='label', first_element=True, title=None):
        '''
        Behavior: 
            plot a chart
        '''

        plt.close()

        if is_col:
            data = self.search_column([id], [selection], [first_element])[0]
        else:
            data = self.search_row([id], [selection], [first_element])[0]

        frequencies = {}
        for i in data:
            if i in frequencies.keys():
                frequencies[i] += 1
            else:
                frequencies[i] = 1

        plt.pie(frequencies.values(), labels=frequencies.keys())

        if title:
            plt.title(title)

        plt.show()

    def line_plot(self, ids : list[str], is_col : bool, selections : list[str], first_elements : list[bool],
                title='None', x_label=None, y_label=None, x_scale='linear', y_scale='linear'):
        '''
        Behavior:
            plot a line
        Note: 
            first element of arrays is the x axis and all subsequent entries will be separate plots along the y axis
        '''
        plt.close()

        if is_col:
            data = self.search_column(ids, selections, first_elements)
        else:
            data = self.search_row(ids, selections, first_elements)

        sorted = np.argsort(data[0])
        for i in range(len(data)):
            data[i] = data[i][sorted]

        for i in range(1, len(data)):
            plt.plot(data[0], data[i], label=ids[i])

        if title != None:
            plt.title(title)
        if x_label != None:
            plt.xlabel(x_label)
        if y_label != None:
            plt.ylabel(y_label)

        plt.xscale(x_scale)
        plt.yscale(y_scale)

        plt.legend()

        plt.show()

    def scatter_plot(self, ids : list[str], is_col : bool, selections : list[str], first_elements : list[str],
                     title=None, x_label=None, y_label=None, x_scale='linear', y_scale='linear'):
        '''
        Behavior:
            plot a scatter (x verses y)
        Note: 
            first entry will be used as x and second entry in arrays will be used as y
        '''

        plt.close()

        if is_col:
            data = self.search_column(ids, selections, first_elements)
        else:
            data = self.search_row(ids, selections, first_elements)

        plt.scatter(data[0], data[1])

        if title != None:
            plt.title(title)
        if x_label != None:
            plt.xlabel(x_label)
        if y_label != None:
            plt.ylabel(y_label)

        plt.xscale(x_scale)
        plt.yscale(y_scale)

        plt.show()

if __name__ == '__main__':
    main = DataProcessor()
    main.add_filenames('./test_data/student_performance.xlsx')
    print(main.statistics('label', True, 'label', False))
    