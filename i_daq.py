#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    i_daq.py
    This module defines the IDAQ interface for a Data Acquisition (DAQ) system.
    It provides an abstract base class that outlines the methods and attributes
    required for configuring and operating a DAQ system.
"""
from abc import ABC, abstractmethod
from ctypes import Array
from uldaq import InterfaceType, AiInputMode, Range, ScanOption, AInScanFlag, \
    AOutScanFlag, create_float_buffer

class IDAQ(ABC):
    """
    Abstract class that defines the interface for a Data Acquisition (DAQ) system.

    Attributes:
        analog_input_map (dict): default configuration for analog input channels.
        analog_output_map (dict): default configuration for analog output channels.
        DAQ_initialised (bool): flag indicating whether the DAQ system has been initialized.
        DAQ_running (bool): flag indicating whether the DAQ system is currently running.
    """

    INTERFACE_TYPE = InterfaceType.USB

    def __init__(self):
        self.analog_input_map = {
            "mode": AiInputMode.SINGLE_ENDED,
            "channel": 1,
            "voltage_range": Range.BIP10VOLTS,
            "sample_rate": 1000.0,
            "samples_per_channel": 10000,
            "scan_operation": ScanOption.CONTINUOUS,
            "scan_flag": AInScanFlag.DEFAULT,
        }

        self.analog_output_map = {
            "channel": 1,
            "voltage_range": Range.BIP10VOLTS,
            "sample_rate": 1000.0,
            "samples_per_channel": 10000,
            "scan_operation": ScanOption.CONTINUOUS,
            "scan_flag": AOutScanFlag.DEFAULT,
        }

    @abstractmethod
    def initDAQ(self) -> None:
        """
        Initializes the DAQ system. This method should set up the hardware and 
        prepare it for operation.
        """

    @abstractmethod
    def start_input_thread(self) -> None:
        """
        Starts a thread that will handle the input data acquisition process.

        Args:
            in_buffer (Array): A ctypes array buffer that will store the input data.
        """

    @abstractmethod
    def start_output_thread(self) -> None:
        """
        Starts a thread that will handle the output data generation process.

        Args:
            out_buffer (Array): A ctypes array buffer that will be used for output data.
        """

    @abstractmethod
    def check_input_thread(self) -> bool:
        """
        """

    @abstractmethod
    def check_output_thread(self) -> bool:
        """
        """

    @abstractmethod
    def close_DAQ(self) -> None:
        """
        Closes the DAQ system. This method should ensure that all resources are 
        released and the system is properly shut down.
        """
