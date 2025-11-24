from dearpygui.core import *
from dearpygui.simple import *
from numpy.__config__ import show
from utils.callback import on_close_callback
import numpy as np
import os
import io

def file_picker(sender, data):
    try:
        open_file_dialog(callback=apply_selected_file, extensions=".*,.txt")
    except Exception as e:
        log_error(f"open_file_dialog failed: {e}")

def apply_selected_file(sender, data):
    try:
        print(data)
        if not data or len(data) < 2:
            log_debug("File dialog canceled or returned empty data")
            return
        directory = data[0]
        file = data[1]
        if not directory or not file:
            log_debug("File dialog returned invalid directory or file")
            return
        file_path = os.path.join(directory, file)
        set_value("directory", directory)
        set_value("file", file)
        set_value("file_path", file_path)
        try:
            # Try robust decoding in case default locale (gbk) fails
            # We read as bytes then decode with fallbacks and pass a StringIO to genfromtxt
            with open(file_path, 'rb') as f:
                raw = f.read()
            last_err = None
            for enc in ("utf-8", "utf-8-sig", "gbk", "cp1252"):
                try:
                    text = raw.decode(enc)
                    break
                except Exception as e:
                    last_err = e
                    text = None
            if text is None:
                raise last_err or UnicodeDecodeError("unknown", b"", 0, 1, "decode failed")
            custom_data = np.genfromtxt(io.StringIO(text), delimiter="\t", skip_header=3)
        except Exception as e:
            log_error(f"Failed to read file '{file_path}': {e}")
            show_logger()
            return
        if custom_data is None or np.size(custom_data) == 0:
            log_error(f"No data parsed from file '{file_path}'")
            show_logger()
            return

        add_data("custom_data", custom_data)

        select_data_window()
    except Exception as e:
        log_error(f"apply_selected_file crashed: {e}")
        show_logger()

def select_data_window():
    try:
        data = get_data("custom_data")
        column_num = np.size(data, 1)
        add_data("column_num", column_num)
        with window('Choose X Y', height=220, on_close = on_close_callback):
            with child('X Column', width=80,height=160):
                for i in range(column_num):
                    add_selectable(f"xc{i}", callback=update_select)
            add_same_line()
            with child('Y Column', width=80,height=160):
                for i in range(column_num):
                    add_selectable(f"yc{i}")
            add_button("OK", callback=OK_callback)
    except Exception as e:
        log_error(f"select_data_window failed: {e}")
        show_logger()

def update_select(sender, data):
    try:
        my_var = get_value(sender)
        if my_var == True:
            for j in range(get_data("column_num")):
                if f"xc{j}" != sender:
                    set_value(f"xc{j}", False)
    except Exception as e:
        log_error(f"update_select failed: {e}")

def OK_callback(sender, data):
    try:
        x_col = 0
        y_col = []
        for j in range(get_data("column_num")):
            if get_value(f"xc{j}") == True:
                x_col = j
            if get_value(f'yc{j}') == True:
                y_col.append(j)
        add_data("x_col", x_col)
        add_data("y_col", y_col)
        delete_item('Choose X Y')
        delete_item('file picker')
    except Exception as e:
        log_error(f"OK_callback failed: {e}")

def print_data(sender, data):
    try:
        log_debug(get_data("custom_data"))
    except Exception as e:
        log_error(f"print_data failed: {e}")