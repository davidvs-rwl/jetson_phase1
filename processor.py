#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import butter, filtfilt

class DataProcessor:
    def preprocess(self, data, functions=[]):
        """
        Perform preprocessing on the input data.
        Args:
            data: The raw input data to preprocess.
        Returns:
            Preprocessed data.
        """
        for func in functions:
            data = func(data)
        return data

    def postprocess(self, data, functions=[]):
        """
        Perform postprocessing on the processed data.
        Args:
            data: The processed data to postprocess.
        Returns:
            Postprocessed data.
        """
        for func in functions:
            data = func(data)
        return data

    def process(self, data, functions=[]):
        """
        Perform the main processing on the data.
        Args:
            data: The input data to process.
        Returns:
            Fully processed data.
        """
        for func in functions:
            data = func(data)
        return data

    def butter_lowpass(self, cutoff, fs, order=5):
        """
        Creates a low-pass Butterworth filter.
        cutoff: The cutoff frequency of the low-pass filter.
        fs: The sampling frequency of the signal.
        order: The order of the filter (default is 5).
        """
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_highpass(self, cutoff, fs, order=5):
        """
        Creates a high-pass Butterworth filter.
        cutoff: The cutoff frequency of the high-pass filter.
        fs: The sampling frequency of the signal.
        order: The order of the filter (default is 5).
        """
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        """
        Creates a bandpass Butterworth filter.
        lowcut: The low cutoff frequency of the bandpass filter.
        highcut: The high cutoff frequency of the bandpass filter.
        fs: The sampling frequency of the signal.
        order: The order of the filter (default is 5).
        """
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band', analog=False)
        return b, a

    def apply_filter(self, b, a, buffer_in):
        """
        Applies the filter to the input buffer using filtfilt (zero-phase filtering).
        b, a: The filter coefficients.
        buffer_in: The input data buffer to be filtered.
        """
        return filtfilt(b, a, buffer_in)

    def lowpass_filter(self, cutoff, buffer_in, fs, order=5):
        """
        Applies a low-pass filter to the input buffer.
        cutoff: The cutoff frequency of the low-pass filter.
        buffer_in: The input data buffer to be filtered.
        fs: The sampling frequency of the signal.
        order: The order of the filter (default is 5).
        """
        b, a = self.butter_lowpass(cutoff, fs, order)
        return self.apply_filter(b, a, buffer_in)

    def highpass_filter(self, cutoff, buffer_in, fs, order=5):
        """
        Applies a high-pass filter to the input buffer.
        cutoff: The cutoff frequency of the high-pass filter.
        buffer_in: The input data buffer to be filtered.
        fs: The sampling frequency of the signal.
        order: The order of the filter (default is 5).
        """
        b, a = self.butter_highpass(cutoff, fs, order)
        return self.apply_filter(b, a, buffer_in)

    def bandpass_filter(self, lowcut, highcut, buffer_in, fs, order=5):
        """
        Applies a bandpass filter to the input buffer.
        lowcut: The low cutoff frequency of the bandpass filter.
        highcut: The high cutoff frequency of the bandpass filter.
        buffer_in: The input data buffer to be filtered.
        fs: The sampling frequency of the signal.
        order: The order of the filter (default is 5).
        """
        b, a = self.butter_bandpass(lowcut, highcut, fs, order)
        return self.apply_filter(b, a, buffer_in)
    


