import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import MinMaxScaler
from torch.utils import data


class DataLoader():
    """A class for loading and transforming data for the LSTM model"""

    def __init__(self, path, split, cols, label_col, MinMax, start_from=None):
        filename = path
        dataframe = pd.read_csv(filename)

        if start_from is not None:
            dataframe.Date = pd.to_datetime(dataframe.Date)
            start = pd.to_datetime(start_from)
            dataframe = dataframe.loc[dataframe.Date > start]

        i_split = int(len(dataframe) * split)
        dataframe = dataframe.get(cols)
        self.data_train = dataframe.values[:i_split]
        self.data_test = dataframe.values[i_split:]
        self.len_train = len(self.data_train)
        self.len_test = len(self.data_test)
        self.label_col_indx = (dataframe.columns.get_loc(label_col))  # Get index of label column
        if MinMax:
            self.scaler = MinMaxScaler()
            self.data_train = self.scaler.fit_transform(self.data_train)
            self.data_test = self.scaler.transform(self.data_test)

        self.w_normalisation_p0_train = []
        self.w_normalisation_p0_test = []
        self.seq_len = None


    def get_train_data(self, seq_len,normalise):
        '''
        Seq_len: total length, ie. the last gets to be the label
        '''
        self.seq_len = seq_len
        seq_len += 1
        data_x = []
        data_y = []
        for i in range(self.len_train - seq_len):
            x, y,  first_row= self._next_window(i, seq_len, 'train', normalise)
            self.w_normalisation_p0_train.append(first_row)
            data_x.append(x)
            data_y.append(y)
        return np.array(data_x), np.array(data_y)

    def get_test_data(self, seq_len, normalise):
        '''
        Seq_len: total length, ie. the last gets to be the label
        '''
        seq_len += 1
        data_x = []
        data_y = []
        for i in range(self.len_test - seq_len):
            x, y,  first_row= self._next_window(i, seq_len, 'test', normalise)
            self.w_normalisation_p0_test.append(first_row)
            data_x.append(x)
            data_y.append(y)
        return np.array(data_x), np.array(data_y)

    def _next_window(self, i, seq_len, split, normalise):
        """Generates the next data window from the given index location i"""
        ''
        if split == 'train':
            window = self.data_train[i:i + seq_len]
            first_row = window[0, :]
            window = self.normalise_windows(window, single_window=True)[0] if normalise else window
            x = window[:-1]
            y = window[-1, [self.label_col_indx]]

        if split == 'test':
            window = self.data_test[i:i + seq_len]
            first_row = window[0, :]
            window = self.normalise_windows(window, single_window=True)[0] if normalise else window
            x = window[:-1]
            y = window[-1, [self.label_col_indx]]

        return x, y, first_row

    def normalise_windows(self, window_data, single_window=False):
        '''Normalise window with a base value of zero'''
        normalised_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            normalised_window = []
            for col_i in range(window.shape[1]):
                normalised_col = [((float(p) / float(window[0, col_i])) - 1) for p in window[:, col_i]]
                normalised_window.append(normalised_col)
            normalised_window = np.array(
                normalised_window).T  # reshape and transpose array back into original multidimensional format
            normalised_data.append(normalised_window)
        return np.array(normalised_data)




class Dataset(data.Dataset):
    'Characterizes a dataset for PyTorch'

    def __init__(self, dataset):
        'Initialization'
        self.data, self.labels = dataset

    def __len__(self):
        'Denotes the total number of samples'
        return self.data.shape[0]

    def __getitem__(self, index):
        'Generates one sample of data'
        # Select sample
        dt = torch.from_numpy(self.data).type(torch.Tensor)
        x = dt[index]
        y = self.labels[index]
        return x, y


def denormalise(mode,p_0, n_i, scaler):
    assert(mode in ['MinMax', "window"])
    if mode == "window":
        return p_0 * (n_i + 1)
    if mode == 'MinMax':
        return scaler.inverse_transform(np.array([n_i, 1]).reshape(1, 2))[0:0]


