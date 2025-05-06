#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from uldaq import (get_daq_device_inventory, DaqDevice, ScanStatus, create_float_buffer, \
                   InterfaceType, AiInputMode, Range, ScanOption, AInScanFlag, \
    AOutScanFlag)
import numpy as np
from math import pi

class DAQ():
    INTERFACE_TYPE = InterfaceType.USB
    def __init__(self):
        self.daq_device = None
        self.ai_device = None
        self.ao_device = None
        self.ai_info = None
        self.ao_info = None
        self.status = ScanStatus.IDLE
        self.actual_in_rate = 0.0
        self.actual_out_rate = 0.0
        self.buffer_in = None
        self.buffer_out = None
        self.input_average = 0.0
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
        self.initDAQ()

    def initDAQ(self) -> None:
        # Get descriptors for all of the available DAQ devices.
        devices = get_daq_device_inventory(self.INTERFACE_TYPE)
        number_of_devices = len(devices)
        if number_of_devices == 0:
            raise RuntimeError('Error: No DAQ devices found')
        if number_of_devices > 1:
            raise RuntimeError('Error: More than one DAQ device found.')

        # Create the DAQ device from the descriptor
        self.daq_device = DaqDevice(devices[0])
        # Get the AiDevice and AoDevice objects and verify that it is valid.
        self.ai_device = self.daq_device.get_ai_device()
        self.ao_device = self.daq_device.get_ao_device()

        if self.ai_device is None:
            raise RuntimeError('Error: The DAQ device does not support analog '
                               'input')
        if self.ao_device is None:
            raise RuntimeError('Error: The DAQ device does not support analog '
                               'output')

        # Verify the specified device supports hardware pacing for analog input and output.
        self.ai_info = self.ai_device.get_info()
        self.ao_info = self.ao_device.get_info()

        if not self.ai_info.has_pacer():
            raise RuntimeError('\nError: The specified DAQ device does not '
                               'support hardware paced analog input')
        if not self.ao_info.has_pacer():
            raise RuntimeError('Error: The DAQ device does not support paced '
                               'analog output')

        # Establish a connection to the DAQ device.
        descriptor = self.daq_device.get_descriptor()
        print('\nConnecting to', descriptor.dev_string, '- please wait...')
        self.daq_device.connect(connection_code=0)
        # Verify the device is connected.
        if not self.daq_device.is_connected():
            raise RuntimeError('Error: The DAQ device is not connected')

    def start_input_thread(self) -> None:
        """
        Starts a thread that will handle the input data acquisition process.
        """
        channel = self.analog_input_map["channel"]
        input_mode = self.analog_input_map["mode"]
        voltage_range = self.analog_input_map["voltage_range"]
        samples_per_channel = self.analog_input_map["samples_per_channel"]
        rate = self.analog_input_map["sample_rate"]
        scan_options = self.analog_input_map["scan_operation"]
        flags = self.analog_input_map["scan_flag"]

        self.buffer_in = create_float_buffer(1,samples_per_channel)

        self.actual_in_rate = self.ai_device.a_in_scan(channel, channel, input_mode,
                            voltage_range, samples_per_channel,
                            rate, scan_options, flags, self.buffer_in)

    def start_output_thread(self, waveform: np.ndarray) -> None:
        """
        Starts a thread that will handle the output data generation process.
        """
        channel = self.analog_output_map["channel"]
        voltage_range = self.analog_output_map["voltage_range"]
        samples_per_channel = self.analog_output_map["samples_per_channel"]
        rate = self.analog_output_map["sample_rate"]
        scan_options = self.analog_output_map["scan_operation"]
        flags = self.analog_output_map["scan_flag"]

        # Create buffer correctly
        self.buffer_out = create_float_buffer(1, samples_per_channel)
        buffer_np = np.ctypeslib.as_array(self.buffer_out)
        # Copy waveform into buffer
        np.copyto(buffer_np, waveform.flatten())

        self.actual_out_rate = self.ao_device.a_out_scan(channel, channel,
                                           voltage_range, samples_per_channel,
                                           rate, scan_options,
                                           flags, self.buffer_out)

    def generate_waveform(self, waveform_type: str = "sine", amplitude: float = 1.0, offset: float = 0.0) -> np.ndarray:
        """
        Generate a waveform (sine, triangle) to output.
        """
        samples_per_channel = self.analog_output_map["samples_per_channel"]
        t = np.linspace(0, 2 * pi, samples_per_channel, endpoint=False)

        if waveform_type == "sine":
            return amplitude * np.sin(t) + offset
        elif waveform_type == "triangle":
            return amplitude * 2 * (t / pi - np.floor(t / pi + 0.5)) + offset
        else:
            raise ValueError("Unsupported waveform type")

    def calculate_input_average(self) -> float:
        """
        Calculate the average of the input data in buffer_in.
        """
        if self.buffer_in is not None:
            input_data = np.ctypeslib.as_array(self.buffer_in)
            self.input_average = np.mean(input_data)
        return self.input_average

    def print_input_data_and_average(self) -> None:
        """
        Print the data from the input buffer and the average of the input data.
        """
        if self.buffer_in is not None:
            # Convert buffer to numpy array
            input_data = np.ctypeslib.as_array(self.buffer_in)
            # Calculate average
            input_average = np.mean(input_data)
            print("Input Data:", input_data)
            print("Input Data Average:", input_average)

    def check_input_thread(self) -> bool:
        if self.ai_device.get_scan_status() == ScanStatus.RUNNING:
            return True
        return False

    def check_output_thread(self) -> bool:
        if self.ao_device.get_scan_status() == ScanStatus.RUNNING:
            return True
        return False

    def close_DAQ(self) -> None:
        """
        Closes the DAQ system. This method should ensure that all resources are 
        released and the system is properly shut down.
        """
        if self.daq_device:
            # Stop the scan.
            in_status = self.ai_device.get_scan_status()
            out_status = self.ao_device.get_scan_status()
            if ScanStatus.RUNNING == in_status:
                self.ai_device.scan_stop()
            if ScanStatus.RUNNING == out_status:
                self.ao_device.scan_stop()

            # Disconnect from the DAQ device.
            if self.daq_device.is_connected():
                self.daq_device.disconnect()
            # Release the DAQ device resource.
            self.daq_device.release()

    def __del__(self):
        self.close_DAQ()