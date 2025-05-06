#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import numpy as np
import time
from mcc_daq import DAQ, create_float_buffer

def main():
    try:
        daq = None
        # Create DAQ object
        daq = DAQ()

        # Generate triangle waveform
        output_wave = daq.generate_waveform(waveform_type="triangle", amplitude=1.0, offset=0.0)
        
        # Start output thread (send the waveform to the DAQ device)
        daq.start_output_thread(output_wave)

        # Start input thread (start acquiring input)
        daq.start_input_thread()

        # Check if the threads are running
        while True:
            if daq.check_output_thread() and daq.check_input_thread():
                print("Both input and output threads are running.")
                daq.print_input_data_and_average()
            else:            
                # Sleep for a while before checking again
                time.sleep(1)

    except RuntimeError as e:
        print(f"Runtime error: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the DAQ device when done or if an error occurs
        try:
            if daq is not None:
                daq.close_DAQ()
            pass
        except Exception as e:
            print(f"Error while closing DAQ: {e}")
        print("DAQ connection closed.")

if __name__ == "__main__":
    main()
