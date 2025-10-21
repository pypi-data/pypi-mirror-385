import os
import ctypes

class DLL:

    def __init__(self, lib_path):
        """Loads a DLL or shared library and stores it."""
        try:
            self.lib = ctypes.CDLL(lib_path)
        except OSError as e:
            self.lib = None
            print(f"Error loading DLL: {e}")

    def get_function(self, func_name, arg_types=None, rest_type=None):
        """
        Retrieves a function from the loaded DLL and sets its argument and return types.
        Returns None if the library or function is not found.
        """
        if not self.lib:
            return None
        
        try:
            func = getattr(self.lib, func_name)
            if arg_types:
                func.argtypes = arg_types
            if rest_type:
                func.restype = rest_type
            return func
        except AttributeError:
            print(f"Function '{func_name}' not found in the DLL.")
            return None

    def load_library(self, lib_path):
        """
        Loads or reloads a DLL or shared library.
        """
        try:
            self.lib = ctypes.CDLL(lib_path)
            return True
        except OSError as e:
            print(f"Error loading DLL: {e}")
            self.lib = None
            return False