import sqlite3
import pathlib
import warnings
import numpy as np
import pandas as pd
import datetime as dt
try:
    from pyrsktools import RSK
except ModuleNotFoundError:
    warnings.warn("Missing pyRSKtools library. .rsk files can not be imported.")
from .AbstractReader import AbstractReader


class RBRXR420(AbstractReader):

    def read(self, file_path: str) -> "pd.DataFrame":
        """

        Parameters
        ----------
        file_path

        Returns
        -------

        """
        file_extention = pathlib.Path(file_path).suffix.lower()
        if file_extention in [".dat", ".hex"]:
            with open(file_path, "r") as f:
                first_50 = [next(f) for i in range(50)]
                for line_num in range(len(first_50)):
                    if first_50[line_num].lower().startswith("logger start:"):
                        header_length = line_num + 1
                        break

            with open(file_path, "r") as f:
                header_lines = [next(f) for i in range(header_length)]
                self._parse_meta(header_lines)

                data_lines = f.readlines()
                if file_extention == ".dat":
                    line_num = 0
                    for line_num in range(len(data_lines)):
                        if data_lines[line_num] != "\n":
                            split_line = data_lines[line_num].split()
                        else:
                            split_line = ["no data"]
                        if split_line[0].lower() == "temp":
                            break
                    if line_num == len(data_lines) - 1:
                        raise RuntimeError("No column names found")
                    data_lines = data_lines[line_num:]
                    first_line = data_lines[0].split()
                    second_line = data_lines[1].split()

                    if len(first_line) == len(second_line):
                        self._read_standard_dat_format(data_lines[1:], False)
                    elif len(first_line) + 2 == len(second_line):
                        try:
                            is_datetime = bool(dt.datetime.strptime(" ".join(second_line[:2]), "%Y/%m/%d %H:%M:%S"))
                        except ValueError:
                            is_datetime = False
                        if is_datetime:
                            self._read_standard_dat_format(data_lines[1:], True)
                        else:
                            raise RuntimeError("Error, expected date time with format %Y/%m/%d %H:%M:%S at start of"
                                               "row.")
                    else:
                        raise RuntimeError("Error: Number of column names and number of columns do not match any"
                                           "expected pattern.")

                else:
                    self._read_standard_hex_format(data_lines)
        elif file_extention == ".xls":
            self._read_standard_xls_format(file_path)
        elif file_extention == ".xlsx":
            self._read_standard_xlsx_format(file_path)
        elif file_extention == ".rsk":
            self._read_standard_rsk_format(file_path)
        else:
            raise IOError("Unrecognised file. File is not a .dat, .hex, .xls, .xlsx, or .rsk.")
        return self.DATA

    def _parse_meta(self, header_lines: list):
        self.META["logger model"] = header_lines[0].split()[1]
        self.META["logger SN"] = header_lines[0].split()[3]
        sample_interval = dt.datetime.strptime(header_lines[5].split()[-1], "%H:%M:%S")
        self.META["download date"] = dt.datetime.strptime(header_lines[1][14:31], "%y/%m/%d %H:%M:%S")
        self.META["sample interval"] = dt.timedelta(hours=sample_interval.hour, minutes=sample_interval.minute,
                                                    seconds=sample_interval.second)
        self.META["logging start"] = dt.datetime.strptime(" ".join(header_lines[3].split()[-2:]),
                                                          "%y/%m/%d %H:%M:%S")
        line_7_info = header_lines[6].split(",")
        self.META["num channels"] = int(line_7_info[0].split()[-1])
        self.META["num samples"] = int(line_7_info[1].split()[-1])
        formatting = header_lines[7].split("%")[1]
        if formatting.endswith("\n"):
            self.META["precision"] = int(formatting[-3])
        else:
            self.META["precision"] = int(formatting[-2])

        self.META["calibration parameters"] = {}
        calibration_start_line = 8
        for i in range(self.META["num channels"]):
            self.META["calibration parameters"][f"channel {i + 1}"] = {}
            for j in range(4):
                line_num = calibration_start_line + 4 * i + j
                if header_lines[line_num].lower().startswith("calibration"):
                    self.META["calibration parameters"][f"channel {i + 1}"][chr(ord("a") + j)]\
                        = float(header_lines[line_num].split()[-1])
                else:
                    self.META["calibration parameters"][f"channel {i + 1}"][chr(ord("a") + j)] \
                        = float(header_lines[line_num].split()[0])

        self.META['raw'] = "".join(header_lines)
        return

    def _read_standard_dat_format(self, raw_data: list, time_stamps: bool = False):
        """

        Parameters
        ----------
        raw_data
        line_numbers

        Returns
        -------

        """
        self.DATA = pd.DataFrame(columns=[f"channel {i + 1}" for i in range(self.META["num channels"])])
        line_num = 0
        for line in raw_data:
            line_data = line.split()
            if time_stamps:
                self.DATA.loc[dt.datetime.strptime(" ".join(line_data[:2]), "%Y/%m/%d %H:%M:%S")] = line_data[2:]
            else:
                self.DATA.loc[self.META["logging start"] + self.META["sample interval"] * line_num] = line_data
            line_num += 1
        for col in self.DATA:
            self.DATA[col] = pd.to_numeric(self.DATA[col], errors='coerce')
        self.DATA.reset_index(inplace=True)
        self.DATA.rename(columns={"index": "TIME"}, inplace=True)
        return

    def _read_standard_hex_format(self, raw_data: list):
        """

        Parameters
        ----------
        raw_data

        Returns
        -------

        """
        for line_num in range(len(raw_data)):
            if raw_data[line_num].lower().startswith("number of bytes of data"):
                hex_header_length = line_num + 2
                break
            elif raw_data[line_num].lower().startswith("number of bytes in header"):
                header_bytes = int(raw_data[line_num].split()[-1])
        num_hex_header_values = int(header_bytes / 3)
        hex_vals = []
        raw_data = raw_data[hex_header_length:]
        for line_num in range(len(raw_data)):
            line = raw_data[line_num]
            line_hex_vals = [line[i: i + 6] for i in range(0, len(line), 6)][:-1]
            for hex_val in line_hex_vals:
                hex_vals.append(hex_val)
        hex_vals = hex_vals[num_hex_header_values:]

        self.DATA = pd.DataFrame(columns=[f"channel {i + 1}" for i in range(self.META["num channels"])])
        line_num = 0
        hex_num = 0
        for line in range(self.META["num samples"]):
            line_time = self.META["logging start"] + self.META["sample interval"] * line_num
            time_hex_vals = hex_vals[hex_num: hex_num + 8]
            line_vals = [int(h, 16) / int("FFFFFF", 16) for h in time_hex_vals]
            line_temps = []
            for channel in range(len(line_vals)):
                val = line_vals[channel]
                if val not in [0, 1]:
                    a = self.META["calibration parameters"][f"channel {channel + 1}"]["a"]
                    b = self.META["calibration parameters"][f"channel {channel + 1}"]["b"]
                    c = self.META["calibration parameters"][f"channel {channel + 1}"]["c"]
                    d = self.META["calibration parameters"][f"channel {channel + 1}"]["d"]
                    x = np.log((1 / val) - 1)
                    temp = 1 / (a + b * x + c * x**2 + d * x**3) - 273.15
                    line_temps.append(round(temp, self.META["precision"]))
                else:
                    line_temps.append(np.nan)
            self.DATA.loc[line_time] = line_temps
            line_num += 1
            hex_num += 8
        for col in self.DATA:
            self.DATA[col] = pd.to_numeric(self.DATA[col], errors='coerce')
        self.DATA.reset_index(inplace=True)
        self.DATA.rename(columns={"index": "TIME"}, inplace=True)
        return

    def _read_standard_xls_format(self, file_path: str):
        xls = pd.ExcelFile(file_path)
        sheet = xls.sheet_names[0]
        xls.close()
        raw_data = pd.read_excel(file_path, sheet, header=None)
        raw_meta = raw_data.iloc[:5].copy()
        if raw_meta.iloc[0, 0] != "RBR data file":
            raise IOError("Not a valid .xls file")
        meta = {}
        for i, r in raw_meta.iterrows():
            for j in range(0, len(r) - 1, 2):
                if not pd.isna(raw_meta.iloc[i, j]):
                    meta[raw_meta.iloc[i, j]] = raw_meta.iloc[i, j + 1]
        self.META["logger model"] = meta["Model:"]
        self.META["logger SN"] = meta["Serial Number:"]
        self.META["sample interval"] = dt.timedelta(seconds=int(meta["Logging sampling period (s):"]))
        self.META["logging start"] = dt.datetime.strptime(meta["Logging start time:"], "%Y/%m/%d")

        column_names = {}
        for col in raw_data:
            if col == 0:
                col_name = "TIME"
            else:
                col_name = f"channel {col}"
            column_names[col] = col_name
        self.DATA = raw_data.iloc[6:].copy()
        self.DATA.reset_index(drop=True, inplace=True)
        self.DATA.rename(columns=column_names, inplace=True)
        for col in self.DATA:
            if col == "TIME":
                self.DATA["TIME"] = pd.to_datetime(self.DATA["TIME"], format="%d/%m/%Y %H:%M:%S.%f")
            else:
                self.DATA[col] = pd.to_numeric(self.DATA[col], errors='coerce')
        return

    def _read_standard_xlsx_format(self, file_path: str):
        meta_table = {"Instrument": pd.read_excel(file_path, sheet_name="Metadata", header=9, nrows=1),
                      "Schedule": pd.read_excel(file_path, sheet_name="Metadata", header=24, nrows=1),
                      "Sampling": pd.read_excel(file_path, sheet_name="Metadata", header=28, nrows=1)}
        self.META["logger model"] = meta_table["Instrument"]["Model"].loc[0]
        self.META["logger SN"] = meta_table["Instrument"]["Serial"].loc[0]
        self.META["sample interval"] = dt.timedelta(seconds=int(meta_table["Sampling"]["Period"].loc[0]))
        self.META["logging start"] = meta_table["Schedule"]["Start time"].loc[0]

        self.DATA = pd.read_excel(file_path, sheet_name="Data", header=1)

        column_names = {}
        for col in self.DATA:
            if col == "Time":
                col_name = "TIME"
            elif col == "Temperature":
                col_name = "channel 1"
            else:
                col_name = f"channel {int(col.split('.')[-1]) + 1}"
            column_names[col] = col_name
        self.DATA.rename(columns=column_names, inplace=True)

        for col in self.DATA:
            if col == "TIME":
                self.DATA["TIME"] = pd.to_datetime(self.DATA["TIME"], format="%Y-%m-%d %H:%M:%S.%f")
            else:
                self.DATA[col] = pd.to_numeric(self.DATA[col], errors='coerce')
        return

    def _read_standard_rsk_format(self, file_path: str):
        raw_meta = {}
        try:
            with RSK(file_path) as rsk:
                rsk.open()
                rsk.readdata()
                rsk_data = rsk.data
                raw_meta["calibration"] = rsk.calibrations
                raw_meta["instrument"] = rsk.instrument
                raw_meta["schedule"] = rsk.scheduleInfo
                raw_meta["parameter key"] = rsk.parameterKeys
                raw_meta["epoch"] = rsk.epoch
        except NameError:
            raise ModuleNotFoundError("You must install pyRSKtools")
        except sqlite3.OperationalError:
            raise RuntimeError("An error occurred when opening the .rsk file. Try opening the .rsk file in the ruskin\n"
                               " software then rerunning the code.")
        self.DATA = pd.DataFrame(rsk_data)

        self.META["logger model"] = raw_meta["instrument"].model
        self.META["logger SN"] = raw_meta["instrument"].serialID
        self.META["sample interval"] = dt.timedelta(seconds=raw_meta["schedule"].samplingPeriod/1000)
        self.META["logging start"] = raw_meta["epoch"].startTime
        self.META["utc offset"] = [int(float(element.value) * 3600) for element in raw_meta["parameter key"]
                                   if element.key == "OFFSET_FROM_UTC"][0]
        self.META["calibration parameters"] = {}
        for cal in raw_meta["calibration"]:
            self.META["calibration parameters"][f"channel {cal.channelOrder}"] = {}
            self.META["calibration parameters"][f"channel {cal.channelOrder}"]["a"] = cal.c[0]
            self.META["calibration parameters"][f"channel {cal.channelOrder}"]["b"] = cal.c[1]
            self.META["calibration parameters"][f"channel {cal.channelOrder}"]["c"] = cal.c[2]
            self.META["calibration parameters"][f"channel {cal.channelOrder}"]["d"] = cal.c[3]

        column_names = {}
        for col in self.DATA:
            if col == "timestamp":
                col_name = "TIME"
            elif col == "temperature":
                col_name = "channel 1"
            else:
                col_name = f"channel {int(col[-1]) + 1}"
            column_names[col] = col_name
        self.DATA.rename(columns=column_names, inplace=True)
        return
