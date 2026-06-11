import ctypes
import os
from typing import List

# Load the compiled shared object (.so) kernel library
KERNEL_LIB_PATH = os.path.join(os.path.dirname(__file__), "build/libkernel.so")
kernel_lib = ctypes.CDLL(KERNEL_LIB_PATH)

# Define the exact C++ function signature for the Python interpreter
# float compute_rolling_z_score(const float* prices, size_t length);
kernel_lib.compute_rolling_z_score.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t]
kernel_lib.compute_rolling_z_score.restype = ctypes.c_float

class NativeQuantEngine:
    @staticmethod
    def calculate_z_score(prices: List[float]) -> float:
        """
        Bypasses Python math to evaluate standard deviation via AVX-512 C++ intrinsics.
        """
        length = len(prices)
        if length == 0:
            return 0.0
            
        # Create a contiguous C-compatible float array in memory
        c_float_array = (ctypes.c_float * length)(*prices)
        
        # Execute the hardware-accelerated math
        return kernel_lib.compute_rolling_z_score(c_float_array, length)
