from __future__ import annotations
import os, sys
import glob
import codecs
import json
import numpy as np
from PIL import Image
import psutil
import time
import gzip
import logging
import calendar
from pathlib import Path
from shutil import copyfileobj
from distutils.spawn import find_executable
import threading
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
try:
    from PATHS import CHIMERA, OCHIMERA
except ImportError:
    CHIMERA = OCHIMERA = None


def change_filename(input_filename, output_filename):
    try:
        os.rename(input_filename, output_filename)
        print(f"File name changed from '{input_filename}' to '{output_filename}'")
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
    except FileExistsError:
        print(f"Error: File '{output_filename}' already exists.")

def create_directory(dir):
    """
    Create a directory if it doesn't exist and return the dir otherwise None

    :return: str or None
    """

    try:
        os.makedirs(dir, exist_ok=True)

        return dir
    except Exception as e:
        print(f'Create folder error: {e}')

        return None


def create_symbolic_link(file_path, link_name):
    """
    Create symbolic link to a file

    :return: str or None
    """

    file_dir = os.path.dirname(file_path)
    link_path = os.path.join(file_dir, link_name)

    if os.path.isfile(link_path):
        print(f"Symbolic link '{link_name}' already exists")
        return link_path
    else:
        try:
            os.symlink(file_path, link_path)
            print(f"Symbolic link '{link_name}' created successfully")
            return link_path
        except Exception as e:
            print(f"Error creating symbolic link: {e}")

            return None


def interpolated_intercept(x, y1, y2):
    """

        Find the intercept of two curves, given by the same x data

    """

    def intercept(point1, point2, point3, point4):
        """

            Find the intersection between two lines
            the first line is defined by the line between point1 and point2
            the second line is defined by the line between point3 and point4
            each point is an (x,y) tuple.

            So, for example, you can find the intersection between
            intercept((0,0), (1,1), (0,1), (1,0)) = (0.5, 0.5)

            :return: Intercept, in (x,y) format

        """

        def line(p1, p2):
            A = (p1[1] - p2[1])
            B = (p2[0] - p1[0])
            C = (p1[0] * p2[1] - p2[0] * p1[1])

            return A, B, -C

        def intersection(L1, L2):
            D = L1[0] * L2[1] - L1[1] * L2[0]
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]

            x = Dx / D
            y = Dy / D

            return x, y

        L1 = line([point1[0], point1[1]], [point2[0], point2[1]])
        L2 = line([point3[0], point3[1]], [point4[0], point4[1]])

        R = intersection(L1, L2)

        return R

    if not isinstance(x, np.ndarray):
        x = np.asarray(x)
    if not isinstance(y1, np.ndarray):
        y1 = np.asarray(y1)
    if not isinstance(y2, np.ndarray):
        y2 = np.asarray(y2)
    idx = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)
    # Remove the first point usually (0, 1) to avoid all curves starting from (0, 1) which pick as one intersection
    if idx.size != 0:
        if idx[0][0] == 0:
            idx = np.delete(idx, 0, 0)
        xc, yc = intercept((x[idx], y1[idx]), ((x[idx + 1], y1[idx + 1])), ((x[idx], y2[idx])),
                           ((x[idx + 1], y2[idx + 1])))
        return xc, yc
    else:
        nullarr = np.empty(shape=(0, 0))
        return nullarr, nullarr


def interpolated_intercepts_general(x, y1, y2):
    """Find the intercepts of two curves, given by the same x data"""

    def intercept(point1, point2, point3, point4):
        """Find the intersection between two lines.

        The first line is defined by the line between point1 and point2.
        The second line is defined by the line between point3 and point4.
        Each point is an (x, y) tuple.

        Returns: the intercept, in (x, y) format.
        """

        def line(p1, p2):
            A = (p1[1] - p2[1])
            B = (p2[0] - p1[0])
            C = (p1[0] * p2[1] - p2[0] * p1[1])
            return A, B, -C

        def intersection(L1, L2):
            D = L1[0] * L2[1] - L1[1] * L2[0]
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]
            x = Dx / D
            y = Dy / D
            return x, y

        L1 = line([point1[0], point1[1]], [point2[0], point2[1]])
        L2 = line([point3[0], point3[1]], [point4[0], point4[1]])

        return intersection(L1, L2)

    idxs = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)


    xcs = []
    ycs = []

    for idx in idxs:
        xc, yc = intercept((x[idx], y1[idx]), (x[idx + 1], y1[idx + 1]), (x[idx], y2[idx]), (x[idx + 1], y2[idx + 1]))

        txc = xc[0].tolist()
        tyc = yc[0].tolist()

        xcs.append(txc)
        ycs.append(tyc)

    return xcs, ycs

def remove_duplicate_intersections(xs, ys):
    """
        Given two lists of xs and ys pair them and remove the duplicates pairs
        return unique pairs
        :param xs: list of x values
        :param ys: list of y values
    """

    rxs = [round(val, 5) for val in xs]
    rys = [round(val, 5) for val in ys]
    # round xs and ys to 4-5 decimal potins and then do the following
    pairs = list(zip(rxs, rys))
    unique_pairs = set(pairs)
    unique_pairs_list = sorted(list(unique_pairs), key=lambda x: x[0])

    return unique_pairs_list


def out_json(data_dict, out_file_path):
    """
    Given the data_dict and out_file_path, write the data to a json file
    """

    try:
        with codecs.open(out_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(data_dict, outfile)
        print("Data successfully written to", out_file_path)
    except Exception as e:
        print("Error:", e)


def first_non_zero_index(number_str):
    """
    Find the index of the first non-zero digit in a string representation of a number.
    """

    for i, digit in enumerate(number_str):
        if digit != '0':
            return i
    return -1


def keep_three_significant_digits(number, significant_digits=3):
    """
    Keep three significant digits without using scientific notation.
    """

    number_float = float(number)

    # Check if the number is an integer
    if number_float.is_integer():
        return int(number_float)  # Return the integer part as a string

    if number_float > 1:
        return round(number_float, significant_digits)
    else:
        # Convert the float to a string with the desired precision
        number_str = '{:.10f}'.format(number_float).rstrip('0')  # Avoid trailing zeros

        # Split the number into integer and fractional parts
        integer_part, decimal_part = number_str.split('.')
        non_zero_index = first_non_zero_index(decimal_part)
        if non_zero_index == -1:
            return round(number_float, significant_digits)
        else:
            final_decimal_part = decimal_part[:non_zero_index + significant_digits]
            final = f'{integer_part}.{final_decimal_part}'

            # Return the number with the desired number of significant digits
            return float(final)

def floattohex(numlist, above_one=False):
    """
        Produce hex color between red and green.

        :param numlist: A list of RGB values.
        :param above_one: Boolean True when values are greater than 1 otherwise False.
        :return: A list of hex values.
    """
    numlist = [-1 if i < 0 else i for i in numlist]
    if above_one:
        rgbs = [[int(num * 13), 0, int(num * 255)] if num >= 0 else [255, 0, 255] for num in numlist]
    else:
        rgbs = [[122, int(num * 255), int(num * 255)] if num >= 0 else [255, 0, 255] for num in numlist]
    resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]

    return resultlist


def float_to_hex(value, platelet=None):
    """
        Convert float to hex color if platelet is give using the platelet

    :param value: float between 0 and 1
    :param platelet: list of tuple with rgb values or default as None use rainbow

    """
    if not platelet:
        # default as rainbow
        colors = [
            # rainbow
            # (128, 0, 128),  # Violet
            # (75, 0, 130),  # Indigo
            # (0, 0, 255),  # Blue
            # (0, 128, 128),  # Blue-Green
            # (0, 255, 0),  # Green
            # (128, 255, 0),   # Yellow-Green
            # (255, 255, 0),  # Yellow
            # (255, 165, 0),  # Orange
            # (255, 69, 0),   # Orange-Red
            # (255, 0, 0)  # Red

            # bwr
            (0, 0, 255),  # Blue
            (255, 255, 255),  # White
            (255, 0, 0)  # Red
        ]
    else:
        colors = platelet

    index = int(value * (len(colors) - 1))
    if index >= len(colors) - 1:
        index = len(colors) - 2
    start_color = colors[index]
    end_color = colors[index + 1]
    fraction = (value - index / (len(colors) - 1)) * (len(colors) - 1)
    interpolated_color = [
        int(start + fraction * (end - start)) for start, end in zip(start_color, end_color)
    ]
    hex_color_code = '#{:02x}{:02x}{:02x}'.format(*interpolated_color)

    return hex_color_code


def check_same_keys(dict1, dict2):
    """
        check if two dictionaries have the same keys at all levels
    dict1: A dictionary
    dict2: A dictionary
    return True if all keys are same, else False
    """

    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return False

    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    if keys1 != keys2:
        return False

    for key in keys1:
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            if not check_same_keys(dict1[key], dict2[key]):
                return False
        else:
            if not isinstance(dict1[key], dict) and not isinstance(dict2[key], dict):
                continue
            else:
                return False

    return True


def scale_values(values, a, b):
    """
    scales values between a and b
    :param values: list of values
    :param a: value of lower bound
    :param b: value of upper bound
    """
    min_val = min(values)
    max_val = max(values)

    # Scale each value to the specified range [a, b]
    # scaled_values = [((val - min_val) / (max_val - min_val)) * (b - a) + a for val in values]
    scaled_values = [scale_value(val, min_val, max_val, a, b) for val in values]

    return scaled_values

def scale_value(value, a, b, c, d):
    # Scale value from range (a, b) to range (c, d)
    scaled_value = (value - a) * (d - c) / (b - a) + c
    return scaled_value

def inverse_scale_value(scaled_value, a, b, c, d):
    # Scale value from range (c, d) to range (a, b)
    inverse_scaled_value = (scaled_value - c) * (b - a) / (d - c) + a
    return inverse_scaled_value


def scale_image(image, scale):
    """
    """
    npimg = Image.open(image)
    im = npimg.resize(scale)
    image_name = os.path.basename(image)
    image_parts = image_name.split('_')
    first_part = '_'.join(image_parts[:-1])
    out_image_name = f'{first_part}_scaled_{image_parts[-1]}'
    dir_name = os.path.dirname(image)
    scaled_image = f'{dir_name}/{out_image_name}'
    im.save(scaled_image)

    return out_image_name


def pad_array(input_array, output_shape, pad_value=0):
    """
        Pad the input array to the specified output shape with the given pad value.

    :param input_array: the input array to be padded
    :param output_shape: the desired shape of the output array
    :param pad_value: the value used for padding
    """
    input_shape = input_array.shape
    pad_width = [(max(d_out - d_in, 0), max(d_in - d_out, 0)) for d_in, d_out in zip(input_shape, output_shape)]
    padded_array = np.pad(input_array, pad_width, mode='constant', constant_values=pad_value)

    return padded_array


# def profile_peak_memory(switch=False):
#     """
#     Custom decorator to report peak memory usage using memory_profiler.
#     The profiling is enabled or disabled based on the `switch` argument.
#     """
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             # Not using profiling
#             if not switch:
#                 return func(*args, **kwargs)
#
#             # If profiling is enabled
#             profiler = LineProfiler()
#             profiler.add_function(func)
#             profiler.enable_by_count()
#             try:
#                 result = func(*args, **kwargs)
#             finally:
#                 profiler.disable_by_count()
#
#             peak_memory = 0.0
#             for key, lines in profiler.code_map.items():
#                 for line_stat in lines:
#                     if line_stat[1]:
#                         current_mem = line_stat[1][1]
#                         if current_mem > peak_memory:
#                             peak_memory = current_mem
#             print(f"PEAK MEMORY for {func.__name__}: {peak_memory:.2f} MB")
#             return result
#
#         return wrapper
#     return decorator

def _rss_mib(include_children: bool) -> float:
    """Return RSS in MiB for current process (optionally incl. children)."""
    proc = psutil.Process(os.getpid())
    rss = proc.memory_info().rss
    if include_children:
        for child in proc.children(recursive=True):
            try:
                rss += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return rss / (1024 ** 2)


def profile_peak_memory(
    enabled: bool = True,
    interval: float = 0.05,           # seconds between samples
    include_children: bool = True,
    verbose: bool = True,
):
    """
    Decorator that measures absolute peak RSS and peak delta (above baseline)
    while the wrapped function runs. Sampling uses a background thread (no
    multiprocessing), so it works without `if __name__ == "__main__":`.

    Per-call override: pass `_memprof=True/False` to toggle profiling.
    After a profiled call, stats live on `wrapped.last_mem_stats`.

    Stats schema:
      {
        "peak_abs_mib": float,
        "peak_delta_mib": float,
        "baseline_mib": float,
        "trace_mib": List[float],
        "samples": int,
        "interval_sec": float,
        "include_children": bool,
      }
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_override = kwargs.pop("_memprof", None)
            do_profile = enabled if local_override is None else bool(local_override)

            # reset stats each call
            wrapper.last_mem_stats = None  # type: ignore[attr-defined]

            if not do_profile:
                return func(*args, **kwargs)

            # Baseline before the function starts
            baseline = _rss_mib(include_children)

            # Start sampler thread
            samples: List[float] = []
            stop_event = threading.Event()
            lock = threading.Lock()

            def sampler():
                # First sample immediately to catch early growth
                with lock:
                    samples.append(_rss_mib(include_children))
                while not stop_event.is_set():
                    time.sleep(interval)
                    with lock:
                        samples.append(_rss_mib(include_children))

            t = threading.Thread(target=sampler, daemon=True)
            t.start()

            try:
                result = func(*args, **kwargs)
            finally:
                stop_event.set()
                t.join(timeout=max(1.0, 3 * interval))  # finish cleanly

            with lock:
                trace = samples[:]  # copy

            if not trace:
                # Fallback: if the function returned before first tick
                trace = [baseline, _rss_mib(include_children)]

            peak_abs = max(trace)
            peak_delta = max(0.0, peak_abs - baseline)

            stats: Dict[str, Any] = {
                "peak_abs_mib": float(peak_abs),
                "peak_delta_mib": float(peak_delta),
                "baseline_mib": float(baseline),
                "trace_mib": trace,
                "samples": len(trace),
                "interval_sec": float(interval),
                "include_children": bool(include_children),
            }
            wrapper.last_mem_stats = stats  # type: ignore[attr-defined]

            if verbose:
                print(
                    f"[Memory] {func.__name__}: "
                    f"abs={stats['peak_abs_mib']:.2f} MiB, "
                    f"delta={stats['peak_delta_mib']:.2f} MiB "
                    f"(baseline={stats['baseline_mib']:.2f} MiB, "
                    f"samples={stats['samples']}, interval={interval:.3f}s, "
                    f"children={include_children})"
                )
            return result

        wrapper.last_mem_stats: Optional[Dict[str, Any]] = None  # type: ignore[attr-defined]
        return wrapper
    return decorator


def execution_time(label):
    """
    Decorator to print the execution time of a function with a custom label.

    :param label: The label to use in the print statement (e.g., "Inclusion").
    :return: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f'{label.capitalize()} time: {end - start:.4f} seconds')
            print('------------------------------------')
            return result
        return wrapper
    return decorator

def chimerax_envcheck():
    """
        Check the running environment for surface view.
        :return: ChimeraX binary path
    """
    def check_display():
        display = os.getenv('DISPLAY')
        if display is None:
            print('You may be running this program on a headless machine. '
                  'Please make sure either headless VTK or headless ChimeraX are properly installed accordingly.')

    def get_chimeraapp():
        if CHIMERA is not None:
            print(f'ChimeraX: {CHIMERA}')
            return CHIMERA
        else:
            chimera_path = find_executable('ChimeraX')
            assert chimera_path is not None, 'ChimeraX executable is not there.'
            print(f'ChimeraX: {chimera_path}')
            return chimera_path

    check_display()

    try:
        chimeraapp = get_chimeraapp()
    except AssertionError as e:
        sys.stderr.write(f'{e}\n')
        chimeraapp = False

    return chimeraapp


    # Q-score related started from here
def chimera_envcheck():
    """
        Check where is Chimera (not ChimeraX)
    :return: the path of old Chimera or None without Chimera
    """

    ochimeraapp = None
    try:
        if OCHIMERA is not None:
            ochimeraapp = OCHIMERA
            print('Chimera: {}'.format(ochimeraapp))
        else:
            assert find_executable('chimera') is not None
            ochimeraapp = find_executable('chimera')
            print('Chimera: {}'.format(ochimeraapp))

    except AssertionError:
        sys.stderr.write('ChimeraX executable is not there.\n')

    return ochimeraapp


def find_rawmap_file(directory):
    """
    Find the file name that ends with '_rawmap.map' in the given directory.

    :param directory: The directory to search in.
    :return: The file name if found, otherwise None.
    """
    search_pattern = os.path.join(directory, '*_rawmap.map')
    rawmap_files = glob.glob(search_pattern)

    if rawmap_files:
        return os.path.basename(rawmap_files[0])
    else:
        return None

def calculate_rawmap_contour_level(map_data, contour_level, rawmap_data):
    """
    Calculate a corresponding contour level for raw map based on the given contour level.

    :param map_data: Numpy array representing the map data.
    :param contour_level: Float representing the contour level.
    :param rawmap_data: Numpy array representing the raw map data.
    :return: A float representing the calculated contour level.
    """
    numvox = len(map_data[map_data >= contour_level])
    rawdata = rawmap_data.flatten()
    flatraw = sorted(rawdata)[::-1]
    rawcl = flatraw[numvox]
    return rawcl

def gzipfile(gzipped_file, update=False):
    """
    Uncompress a .gz file if the uncompressed version does not exist or needs updating.

    :param gzipped_file: Path to the .gz file.
    :param update: Boolean indicating whether to force updating the uncompressed file.
    """
    gzipped_file = Path(gzipped_file)
    uncompressed_file = gzipped_file.with_suffix('')  # Remove the .gz suffix

    if not uncompressed_file.exists() or update:
        try:
            with gzip.open(gzipped_file, 'rb') as f_in, open(uncompressed_file, 'wb') as f_out:
                copyfileobj(f_in, f_out)
            logging.info(f'File {uncompressed_file} has been successfully uncompressed.')
        except Exception as e:
            logging.error(f'Failed to uncompress {gzipped_file}: {e}')
    else:
        logging.info(f'File {uncompressed_file} already exists. No need to uncompress.')

def format_version_date(version_str):
    year = version_str[:4]
    month_num = int(version_str[4:6])
    month_name = calendar.month_name[month_num]
    if len(version_str) >= 8:
        day = int(version_str[6:8])
        # Add ordinal suffix to the day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{month_name} {day}{suffix} {year}"
    else:
        return f"{month_name} {year}"
