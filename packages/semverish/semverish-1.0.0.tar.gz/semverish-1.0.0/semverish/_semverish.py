import os
from cffi import FFI
import json

ffi = FFI()

ffi.cdef("""
char* NaturalSortedVersions(char* versions, _Bool descending);
char* AnalyzeConstrains(char* language, char* constraints, char* versions);
void FreeCString(char* str);
""", override=True)  # allows reloads without error


lib_path = os.path.join(os.path.dirname(__file__), "libpyversions.so")
C = ffi.dlopen(lib_path)

def natural_sorted_versions(versions: list, descending: bool = False) -> list[str]:
    versions_json = json.dumps(versions).encode("utf-8")
    c_data = ffi.new("char[]", versions_json)

    res = C.NaturalSortedVersions(c_data, descending)
    py_res_str = ffi.string(res).decode()

    C.FreeCString(res)

    # If Go returned an error string, you can optionally raise an exception
    if py_res_str.startswith("ERROR:"):
        raise RuntimeError(py_res_str)

    return json.loads(py_res_str)

def analyze_constraints(language: str, constraints: str, versions: list[str]) -> list[str]:
    # Convert Python list to JSON string
    versions_json = json.dumps(versions).encode("utf-8")

    # Convert Python strings to C strings
    c_language = ffi.new("char[]", language.encode("utf-8"))
    c_constraints = ffi.new("char[]", constraints.encode("utf-8"))
    c_versions = ffi.new("char[]", versions_json)

    # Call the C function
    res = C.AnalyzeConstrains(c_language, c_constraints, c_versions)
#     res = C.AnalyzeConstrains(
#          ffi.cast("char*", c_language),
#          ffi.cast("char*", c_constraints),
#          ffi.cast("char*", c_versions),
#      )

    # Convert returned C string to Python string
    py_res_str = ffi.string(res).decode("utf-8")

    # Free C string memory
    C.FreeCString(res)

    # If Go returned an error string, you can optionally raise an exception
    if py_res_str.startswith("ERROR:"):
        raise RuntimeError(py_res_str)

    # Decode JSON string into Python list
    return json.loads(py_res_str)

