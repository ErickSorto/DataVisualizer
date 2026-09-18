import unittest
import numpy as np
from core import data_processor as dp

class TestDataProcessor(unittest.TestCase):
    def test_base_26_converter(self):
        self.assertEqual(dp.base_26_converter('A'), 0)
        self.assertEqual(dp.base_26_converter('F'), 5)
        self.assertEqual(dp.base_26_converter('AB'), 27)
        self.assertEqual(dp.base_26_converter('AAZ'), 727)
        self.assertEqual(dp.base_26_converter('JKL'), 7057)

    def test_add_remove_filenames(self):
        processor = dp.DataProcessor()
        processor.add_filenames(['file1', 'file2', 'file3', 'file4'])
        self.assertEqual(processor.get_filenames(), (['file1', 'file2', 'file3', 'file4'],['file1', 'file2', 'file3', 'file4']))
        processor.remove_filenames(['file2'])
        self.assertEqual(processor.get_filenames(), (['file1', 'file3', 'file4'],['file1', 'file3', 'file4']))
        processor.deactivate_filenames(['file3'])
        self.assertEqual(processor.get_filenames(), (['file1', 'file3', 'file4'],['file1', 'file4']))
        processor.activate_filenames(['file3'])
        self.assertEqual(processor.get_filenames(), (['file1', 'file3', 'file4'],['file1', 'file3', 'file4']))
        processor.activate_filenames(['file2'])
        # should do nothing since it can't activate a file that isn't in known files
        self.assertEqual(processor.get_filenames(), (['file1', 'file3', 'file4'],['file1', 'file3', 'file4']))
        processor.remove_filenames(['file2'])
        self.assertEqual(processor.get_filenames(), (['file1', 'file3', 'file4'],['file1', 'file3', 'file4']))

    def test_load_file(self):
        processor = dp.DataProcessor()
        correct = np.array([[1,2,3],
                           [4,5,6],
                           [7,8,9]])
        np.testing.assert_array_equal(processor.load_file('tests/test_data/load_file_data_1.xlsx')[0], correct)
        np.testing.assert_array_equal(processor.load_file('tests/test_data/load_file_data_1.csv')[0], correct)

        correct = np.array([[1,np.nan,3],
                            [4,5,6],
                            [7,8,9]])
        np.testing.assert_array_equal(processor.load_file('tests/test_data/load_file_data_2.xlsx')[0], correct)
        np.testing.assert_array_equal(processor.load_file('tests/test_data/load_file_data_2.csv')[0], correct)

        correct = np.array([[[1,2],
                             [3,4]],
                             [[5,6],
                              [7,8]]])
        np.testing.assert_array_equal(processor.load_file('tests/test_data/load_file_data_3.xlsx'), correct)

    def test_get_column(self):
        processor = dp.DataProcessor()
        filepath = 'tests/test_data/get_column_data.xlsx'

        ans = processor.get_column(filepath, 0, 'index', True)
        np.testing.assert_array_equal(ans[0], [1,2,3])

        ans = processor.get_column(filepath, 0, 'index', False)
        np.testing.assert_array_equal(ans[0], [2,3])

        ans = processor.get_column(filepath, 1, 'index', True)
        np.testing.assert_array_equal(ans[0], ['this', 'is a', 'test'])

        ans = processor.get_column(filepath, 'this', 'label', True)
        np.testing.assert_array_equal(ans[0], ['is a', 'test'])

        ans = processor.get_column(filepath, 'label1', 'label', True)
        np.testing.assert_array_equal(ans[0], [1,2])

        ans = processor.get_column(filepath, 'label2', 'label', False)
        np.testing.assert_array_equal(ans[0], [3,4])

        #testing if it will ignore columns that don't exist
        ans = processor.get_column(filepath, 10, 'index', False)
        np.testing.assert_array_equal(ans,[[]])

        ans = processor.get_column(filepath, 'label3', 'label', False)
        np.testing.assert_array_equal(ans,[[]])

        #testing for multilple sheets
        filepath = 'tests/test_data/get_column_data_2.xlsx'
        ans = processor.get_column(filepath, 'label1', 'label', False)
        np.testing.assert_array_equal(ans, [[1,3],[5,7]])
        ans = processor.get_column(filepath, 'label2', 'label', False)
        np.testing.assert_array_equal(ans, [[2,4],[6,8]])

    def test_get_row(self):
        processor = dp.DataProcessor()
        filepath = 'tests/test_data/get_row_data.xlsx'

        ans = processor.get_row(filepath, 0, 'index', True)
        np.testing.assert_array_equal(ans[0], [1,2,3])

        ans = processor.get_row(filepath, 0, 'index', False)
        np.testing.assert_array_equal(ans[0], [2,3])

        ans = processor.get_row(filepath, 1, 'index', True)
        np.testing.assert_array_equal(ans[0], ['this', 'is a', 'test'])

        ans = processor.get_row(filepath, 'this', 'label', True)
        np.testing.assert_array_equal(ans[0], ['is a', 'test'])

        ans = processor.get_row(filepath, 'label1', 'label', True)
        np.testing.assert_array_equal(ans[0], [1,2])

        ans = processor.get_row(filepath, 'label2', 'label', False)
        np.testing.assert_array_equal(ans[0], [3,4])

        #testing if it will ignore columns that don't exist
        ans = processor.get_row(filepath, 10, 'index', False)
        np.testing.assert_array_equal(ans,[[]])

        ans = processor.get_row(filepath, 'label3', 'label', False)
        np.testing.assert_array_equal(ans,[[]])

        #testing for multiple sheets
        filepath = 'tests/test_data/get_row_data_2.xlsx'
        ans = processor.get_row(filepath, 'label1', 'label', False)
        np.testing.assert_array_equal(ans, [[1,3],[5,7]])
        ans = processor.get_row(filepath, 'label2', 'label', False)
        np.testing.assert_array_equal(ans, [[2,4],[6,8]])

    def test_search_column(self):
        processor = dp.DataProcessor()
        processor.add_filenames(['tests/test_data/search_column_data.xlsx'])

        ans = processor.search_column(['label1'], ['label'], [True])
        np.testing.assert_array_equal(ans, [[1,4]])

        ans = processor.search_column(['label1', 'B'], ['label', 'index'], [True, False])
        np.testing.assert_array_equal(ans, [[1,4],[2,5]])

        ans = processor.search_column(['label1', 'B', 'label3'], ['label', 'index', 'label'], [True, True, True])
        np.testing.assert_array_equal(ans, [[1,4],[2,5],[3,6]])

        #label 4 does not exist so it should get a list of empty columns and raise a NameError
        with self.assertRaises(NameError):
            processor.search_column(['label1', 'label4'], ['label', 'label'], [True, True])

        processor.add_filenames(['tests/test_data/search_column_data_2.xlsx'])

        ans = processor.search_column(['label1'], ['label'], [False])
        np.testing.assert_array_equal(ans, [[1,4,1,3,5,7]])

        ans = processor.search_column(['A'], ['index'], [False])
        np.testing.assert_array_equal(ans, [[1,4,1,3,5,7]])

        ans = processor.search_column(['label1', 'label2'], ['label', 'label'], [False, False])
        np.testing.assert_array_equal(ans, [[1,4,1,3,5,7],[2,5,2,4,6,8]])

        ans = processor.search_column(['label1', 'label2', 'label3'], ['label', 'label', 'label'], [False, False, False])
        np.testing.assert_array_equal(ans, [[1,4],[2,5],[3,6]])

    def test_search_row(self):
            processor = dp.DataProcessor()
            processor.add_filenames(['tests/test_data/search_row_data.xlsx'])
    
            ans = processor.search_row(['label1'], ['label'], [True])
            np.testing.assert_array_equal(ans, [[1,4]])
    
            ans = processor.search_row(['label1', 2], ['label', 'index'], [True, False])
            np.testing.assert_array_equal(ans, [[1,4],[2,5]])
    
            ans = processor.search_row(['label1', 2, 'label3'], ['label', 'index', 'label'], [True, True, True])
            np.testing.assert_array_equal(ans, [[1,4],[2,5],[3,6]])
    
            #label 4 does not exist so it should get a list of empty rows and throw a NameError
            with self.assertRaises(NameError):
                processor.search_row(['label1', 'label4'], ['label', 'label'], [True, True])
    
            processor.add_filenames(['tests/test_data/search_row_data_2.xlsx'])
    
            ans = processor.search_row(['label1'], ['label'], [False])
            np.testing.assert_array_equal(ans, [[1,4,1,3,5,7]])
    
            ans = processor.search_row([1], ['index'], [False])
            np.testing.assert_array_equal(ans, [[1,4,1,3,5,7]])
    
            ans = processor.search_row(['label1', 'label2'], ['label', 'label'], [False, False])
            np.testing.assert_array_equal(ans, [[1,4,1,3,5,7],[2,5,2,4,6,8]])
    
            ans = processor.search_row(['label1', 'label2', 'label3'], ['label', 'label', 'label'], [False, False, False])
            np.testing.assert_array_equal(ans, [[1,4],[2,5],[3,6]])


if __name__ == '__main__':
    unittest.main()

