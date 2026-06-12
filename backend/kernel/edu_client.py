import ctypes
import os

KERNEL_LIB_PATH = os.path.join(os.path.dirname(__file__), "build/libkernel.so")
kernel_lib = ctypes.CDLL(KERNEL_LIB_PATH)

# Define FFI arguments and return types
kernel_lib.extract_dense_chunks.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
kernel_lib.extract_dense_chunks.restype = ctypes.c_void_p  # Return as void pointer to prevent auto-conversion

kernel_lib.free_extracted_text.argtypes = [ctypes.c_void_p]
kernel_lib.free_extracted_text.restype = None

class NativeEduScanner:
    @staticmethod
    def extract_high_signal_text(raw_text: str, density_threshold: int = 2) -> str:
        """
        Passes a massive document to the C++ kernel. The kernel slices it, 
        drops the fluff, and returns only the highly technical paragraphs.
        """
        encoded_text = raw_text.encode('utf-8')
        length = len(encoded_text)
        
        # 1. Execute C++ Extraction
        ptr = kernel_lib.extract_dense_chunks(encoded_text, length, density_threshold)
        
        if not ptr:
            return "" # Kernel determined the text was mostly fluff/noise
            
        try:
            # 2. Cast the raw memory address to a Python C-String and decode it
            c_string = ctypes.cast(ptr, ctypes.c_char_p)
            condensed_text = c_string.value.decode('utf-8')
            return condensed_text
        finally:
            # 3. ABSOLUTE GUARANTEE: Free the C++ memory to prevent system OOM crashes
            kernel_lib.free_extracted_text(ptr)
