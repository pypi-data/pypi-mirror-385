import inspect
import logging
import os
from copy import deepcopy
from datetime import datetime, timedelta

import numpy as np
from netCDF4 import Dataset

import rtctools.data.netcdf as netcdf

from ..test_case import TestCase
from .data_path import data_path

logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s", level=logging.DEBUG
)

export_path = os.path.join(data_path(), "timeseries_export.nc")

filepaths = {
    0: "timeseries_import_ensemblesize1_noRealization",
    1: "timeseries_import_ensemblesize1_withRealization",
    2: "timeseries_import_ensemble",
}

file_associations = {
    "test_inputfiles": list(range(3)),
    "test_read_times": list(range(3)),
    "test_get_ensemble_size": list(range(3)),
    "test_find_timeseries_variables": list(range(3)),
    "test_stations": list(range(3)),
    "test_read_timeseries_values": list(range(3)),
    "test_write_output_values": list(range(3)),
}

# aliases used to variable names in the netCDF-file
alias_dict = {
    # primary
    "time": "time",
    "station": "station_id",
    "ensemble": "realization",
    # other
    "latitude": "lat",
    "longtitude": "lon",
}


def get_input_dataset(key):
    filename = os.path.join(data_path(), filepaths[key])
    return Dataset(filename + ".nc")


def get_exported_dataset():
    return Dataset(export_path)


def key_to_file(filename):
    return list(filepaths.keys())[list(filepaths.values()).index(filename)]


def alias_of_variable(variable):
    if variable in alias_dict.keys():
        return alias_dict[variable]
    return variable


def variable_from_alias(alias):
    if alias in alias_dict.values():
        return list(alias_dict.keys())[list(alias_dict.values()).index(alias)]
    return alias


def create_expectation_list(files, expected_values):
    return {
        key_to_file(_file): _expected_value
        for (_file, _expected_value) in zip(files, expected_values)
    }


class TestInputDataset_requirements(TestCase):
    """
        Tests the files which are used for further testing for requirements
        concerning their use with FEWS. requirements include:

    - stations are identified by a variable 'station_id with required attribute
        'cf_role' with value 'timeseries_id'.
    - coordinate variable 'time' is of unlimited size, it has a required 'axis'
        attribute of 'T' and a required 'standard_name' attribute of 'time'
    - coordinate variable 'realization' is used to index ensemble members
    """

    def setUp(self):
        self._dimensions = {}
        self._variables = {}
        self._variable_associated_dimensions = {}
        self._variable_associated_attribute_requirements = {}

        # primary requirements
        self._dimensions[0] = ["time", "station", "realization"]
        self._variables[0] = ["time", "station", "ensemble"]
        self._variable_associated_dimensions[0] = {
            var: [pd] for (var, pd) in zip(self._variables[0], self._dimensions[0])
        }
        self._variable_associated_attribute_requirements[0] = dict(
            zip(
                self._variables[0],
                ({"axis": "T", "standard_name": "time"}, {"cf_role": "timeseries_id"}, None),
            )
        )

        # secondary requirements
        self._dimensions[1] = ["char_leng_id"]
        self._variables[1] = ["station"]
        self._variable_associated_dimensions[1] = {"station": ["char_leng_id"]}
        self._variable_associated_attribute_requirements[1] = None

    def tearDown(self):
        if os.path.exists(export_path):
            os.remove(export_path)

    def test_inputfiles(self):
        frame = inspect.currentframe()
        func_name = inspect.getframeinfo(frame).function
        for file_key in file_associations[func_name]:
            logging.debug("testing file '{}' in '{}'".format(filepaths[file_key], func_name))
            for requirement_level in self._dimensions.keys():
                self._subtest_inputfile(file_key, requirement_level)

    def _subtest_inputfile(self, file_key, rl):
        # test for basic requirements of input-files used in these tests
        self.dataset = get_input_dataset(file_key)
        self.ncdf_var = {}
        if self._variables[rl]:
            self.variable_found = dict.fromkeys(self._variables[rl], False)
            aliases_of_interest = tuple(map(alias_of_variable, self._variables[rl]))

        # search for variables of interest
        if self._variables[rl]:
            for _variable_name, _variable_data in self.dataset.variables.items():
                for _variable, _variable_alias in zip(self._variables[rl], aliases_of_interest):
                    if _variable_name == _variable_alias:
                        self.variable_found[_variable] = True
                        self.ncdf_var[_variable] = _variable_data

            # check for existence of variable of interest (ensemble is not required)
            for _variable, _variable_alias in zip(self._variables[rl], aliases_of_interest):
                if _variable != "ensemble":
                    self.assertTrue(
                        self.variable_found[_variable],
                        "Variable '{}' was not found by its alias '{}' in file '{}.nc' .".format(
                            _variable, _variable_alias, filepaths[file_key]
                        ),
                    )

                # check requirements of attributes for found variables
                if self._variable_associated_attribute_requirements[rl]:
                    if self._variable_associated_attribute_requirements[rl][_variable]:
                        for (
                            _attribute,
                            _attribute_requirement,
                        ) in self._variable_associated_attribute_requirements[rl][
                            _variable
                        ].items():
                            self.assertTrue(
                                _attribute in self.ncdf_var[_variable].ncattrs()
                                and getattr(self.ncdf_var[_variable], _attribute)
                                == _attribute_requirement,
                                "Variable '{}' with alias '{}' in '{}.nc' "
                                "is missing attribute '{}' with value '{}'.".format(
                                    _variable,
                                    _variable_alias,
                                    filepaths[file_key],
                                    _attribute,
                                    _attribute_requirement,
                                ),
                            )

                # check associated dimensions for found variables
                if self._variable_associated_dimensions[rl]:
                    if self._variable_associated_dimensions[rl][_variable]:
                        if self.variable_found[_variable]:
                            for _dimension in self._variable_associated_dimensions[rl][_variable]:
                                self.assertIn(
                                    _dimension,
                                    self.ncdf_var[_variable].dimensions,
                                    "Variable '{}' should be associated to "
                                    "dimension {} in '{}.nc'.".format(
                                        _variable_alias, _dimension, filepaths[file_key]
                                    ),
                                )


class TestImportDataset(TestCase):
    """
    Test reading of netCDF-files
    """

    def tearDown(self):
        if os.path.exists(export_path):
            os.remove(export_path)

    def test_get_ensemble_size(self):
        files = (
            "timeseries_import_ensemblesize1_noRealization",
            "timeseries_import_ensemblesize1_withRealization",
            "timeseries_import_ensemble",
        )
        expected_values = (1, 1, 3)
        self.expected_sizes = create_expectation_list(files, expected_values)

        frame = inspect.currentframe()
        func_name = inspect.getframeinfo(frame).function
        for file_key in file_associations[func_name]:
            logging.debug("testing file '{}' in '{}'".format(filepaths[file_key], func_name))
            self._subtest_get_ensemble_size(file_key)

    def test_read_times(self):
        files = (
            "timeseries_import_ensemblesize1_noRealization",
            "timeseries_import_ensemblesize1_withRealization",
            "timeseries_import_ensemble",
        )
        forecast_datetime = datetime(1970, 1, 1, 0, 0)
        expected_datetimes = [
            [forecast_datetime + timedelta(minutes=i) for i in range(25)],
        ] * 3
        self.expected_datetimes = create_expectation_list(files, expected_datetimes)

        frame = inspect.currentframe()
        func_name = inspect.getframeinfo(frame).function
        for file_key in file_associations[func_name]:
            logging.debug("testing file '{}' in '{}'".format(filepaths[file_key], func_name))
            self._subtest_read_times(file_key)

    def test_find_timeseries_variables(self):
        files = (
            "timeseries_import_ensemblesize1_noRealization",
            "timeseries_import_ensemblesize1_withRealization",
            "timeseries_import_ensemble",
        )
        expected_variables = [
            ["u", "x", "u_min", "u_max", "w", "constant_input"],
        ] * 3
        self.expected_variables = create_expectation_list(files, expected_variables)

        frame = inspect.currentframe()
        func_name = inspect.getframeinfo(frame).function
        for file_key in file_associations[func_name]:
            logging.debug("testing file '{}' in '{}'".format(filepaths[file_key], func_name))
            self._subtest_find_timeseries_variables(file_key)

    def test_stations(self):
        files = (
            "timeseries_import_ensemblesize1_noRealization",
            "timeseries_import_ensemblesize1_withRealization",
            "timeseries_import_ensemble",
        )
        expected_station_lengths = [2] * 3
        self.expected_station_lengths = create_expectation_list(files, expected_station_lengths)
        self.expected_location_id = {}
        self.expected_location_id[0] = create_expectation_list(files, ["loc_a"] * 3)
        self.expected_location_id[1] = create_expectation_list(files, ["loc_b"] * 3)
        self.expected_station_attributes_lengths = create_expectation_list(files, [2] * 3)
        self.expected_station_attributes = create_expectation_list(
            files,
            [
                ["lon", "lat"],
            ]
            * 3,
        )
        self.expected_lat_loc_a = create_expectation_list(files, [51.9856484] * 3)

        frame = inspect.currentframe()
        func_name = inspect.getframeinfo(frame).function
        for file_key in file_associations[func_name]:
            logging.debug("testing file '{}' in '{}'".format(filepaths[file_key], func_name))
            self._subtest_stations(file_key)

    def test_read_timeseries_values(self):
        files = (
            "timeseries_import_ensemblesize1_noRealization",
            "timeseries_import_ensemblesize1_withRealization",
            "timeseries_import_ensemble",
        )
        x_var_s = np.zeros((25, 2))
        x_var_e = np.zeros((25, 2, 3))
        self.expected_x_values = {}
        self.expected_x_values["loc_b"] = create_expectation_list(
            files,
            [
                deepcopy(x_var_s),
            ]
            * 2
            + [deepcopy(x_var_e)],
        )
        x_var_s[0, 0] = 1.02
        x_var_s[2, 0] = 0.03
        x_var_e[0, 0, 0] = 1.02
        x_var_e[2, 0, 0] = 0.03
        self.expected_x_values["loc_a"] = create_expectation_list(
            files,
            [
                deepcopy(x_var_s),
            ]
            * 2
            + [deepcopy(x_var_e)],
        )

        frame = inspect.currentframe()
        func_name = inspect.getframeinfo(frame).function
        for file_key in file_associations[func_name]:
            logging.debug("testing file '{}' in '{}'".format(filepaths[file_key], func_name))
            self._subtest_read_timeseries_values(file_key)

    # subtests # TestImportDataset #

    def _subtest_get_ensemble_size(self, file_key):
        self.dataset = netcdf.ImportDataset(data_path(), filepaths[file_key])
        self.assertEqual(self.dataset.ensemble_size, self.expected_sizes[file_key])

    def _subtest_read_times(self, file_key):
        self.dataset = netcdf.ImportDataset(data_path(), filepaths[file_key])
        datetimes = self.dataset.read_import_times()
        time_diffs = [
            (x - y).total_seconds() for (x, y) in zip(datetimes, self.expected_datetimes[file_key])
        ]
        # TODO: can this check be made precise?
        diff_tol = 10**-4
        for time_diff in time_diffs:
            self.assertAlmostEqual(time_diff, 0, diff_tol)

    def _subtest_find_timeseries_variables(self, file_key):
        self.dataset = netcdf.ImportDataset(data_path(), filepaths[file_key])
        variables = self.dataset.find_timeseries_variables()
        self.assertEqual(variables, self.expected_variables[file_key])

    def _subtest_stations(self, file_key):
        self.dataset = netcdf.ImportDataset(data_path(), filepaths[file_key])
        stations = self.dataset.read_station_data()

        ids = stations.station_ids
        self.assertEqual(len(ids), self.expected_station_lengths[file_key])
        for location in self.expected_location_id.values():
            self.assertIn(location[file_key], ids)

        for id in ids:
            read_attributes = stations.attributes[id].keys()
            self.assertEqual(
                len(read_attributes), self.expected_station_attributes_lengths[file_key]
            )
            for _attribute in self.expected_station_attributes[file_key]:
                self.assertIn(_attribute, read_attributes)

        self.assertEqual(stations.attributes["loc_a"]["lat"], self.expected_lat_loc_a[file_key])

    def _subtest_read_timeseries_values(self, file_key):
        self.dataset = netcdf.ImportDataset(data_path(), filepaths[file_key])
        stations = self.dataset.read_station_data()
        ensemble_size = self.dataset.ensemble_size

        for station_id in self.expected_x_values.keys():
            station_index = list(stations.station_ids).index(station_id)
            for ensemble_member in range(ensemble_size):
                values = self.dataset.read_timeseries_values(station_index, "x", ensemble_member)

                if ensemble_size == 1:
                    self.assertSequenceEqual(
                        self.expected_x_values[station_id][file_key][:, station_index].tolist(),
                        values.tolist(),
                    )
                else:
                    self.assertSequenceEqual(
                        self.expected_x_values[station_id][file_key][:, station_index][
                            :, ensemble_member
                        ].tolist(),
                        values.tolist(),
                    )


class TestExportDataset(TestCase):
    def tearDown(self):
        try:
            self.dataset.close()
        except Exception:
            pass
        if os.path.exists(export_path):
            os.remove(export_path)

    def check_attributes(self, _variable, _attributes, _attribute_values):
        for _attribute, _attribute_value in zip(_attributes, _attribute_values):
            self.assertIn(
                _attribute,
                self.dataset.variables[_variable].ncattrs(),
                "Variable '{}' is missing attribute '{}'.".format(_variable, _attribute),
            )
            self.assertEqual(
                getattr(self.dataset.variables[_variable], _attribute),
                _attribute_value,
                "Attribute '{}' of variable '{}' does not match its expected value.".format(
                    _attribute, _variable
                ),
            )

    def check_associated_dimensions(self, _variables, _expected_variable_associated_dimensions):
        for _variable, _expected_dimensions in zip(
            _variables, _expected_variable_associated_dimensions
        ):
            _variable_associated_dimensions = self.dataset.variables[_variable].dimensions
            self.assertEqual(
                set(_variable_associated_dimensions),
                set(_expected_dimensions),
                "The dimensions of variable '{}' are not as expected.".format(_variable),
            )

    def test_global_attributes(self):
        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.assertEqual(self.dataset._ExportDataset__dataset.title, "RTC-Tools Output Data")
        self.assertEqual(self.dataset._ExportDataset__dataset.institution, "Deltares")
        self.assertEqual(self.dataset._ExportDataset__dataset.source, "RTC-Tools")
        self.assertEqual(self.dataset._ExportDataset__dataset.Conventions, "CF-1.6")
        self.assertEqual(self.dataset._ExportDataset__dataset.featureType, "timeseries")
        self.assertIn(
            "history",
            self.dataset._ExportDataset__dataset.ncattrs(),
            "The dataset is missing global attribute 'history'.",
        )

    def test_write_times(self):
        times = np.array([-120, -300, -60, 300, 360])
        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.dataset.write_times(times, -180.0, datetime(2018, 12, 21, 17, 30))
        self.dataset.close()
        self.dataset = get_exported_dataset()

        self.assertIn("time", self.dataset.dimensions, "Dimension 'time' is missing.")
        self.assertEqual(self.dataset.dimensions["time"].name, "time")
        self.assertTrue(
            self.dataset.dimensions["time"].isunlimited(), "The time dimension should be unlimited"
        )
        self.assertEqual(self.dataset.variables["time"].size, len(times))

        self.assertIn("time", self.dataset.variables)
        time_variable = "time"
        time_attributes = ("standard_name", "units", "axis")
        time_attribute_values = ("time", "seconds since 2018-12-21 17:28:00", "T")
        self.check_attributes(time_variable, time_attributes, time_attribute_values)
        self.assertTrue(np.array_equal(self.dataset.variables["time"][:], times + 300))

    def test_write_station_data(self):
        # TODO: rewrite test to be independent of succes of reading a netcdf file.
        self.import_dataset = netcdf.ImportDataset(data_path(), "timeseries_import_ensemble")
        stations = self.import_dataset.read_station_data()

        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.dataset.write_station_data(stations, stations.station_ids)
        self.dataset.close()
        self.dataset = get_exported_dataset()

        for _dimension in ("station", "char_leng_id"):
            self.assertIn(
                _dimension,
                self.dataset.dimensions,
                "Dimension '{}' is missing, but should be available "
                "to be able to identify the stations.".format(_dimension),
            )
        self.assertEqual(self.dataset.dimensions["station"].name, "station")
        self.assertEqual(self.dataset.dimensions["station"].size, 2)
        self.assertEqual(self.dataset.dimensions["char_leng_id"].name, "char_leng_id")
        self.assertEqual(self.dataset.dimensions["char_leng_id"].size, 5)

        _variable = "station_id"
        _attributes = ("long_name", "cf_role")
        _attribute_values = ("station identification code", "timeseries_id")
        self.check_attributes(_variable, _attributes, _attribute_values)

        for _variable in ("station_id", "lat", "lon"):
            self.assertIn(
                _variable,
                self.dataset.variables,
                "Variable '{}' is missing, but should be available "
                "to be able to identify the stations.".format(_variable),
            )
        for _attribute in ("long_name", "cf_role"):
            self.assertIn(
                _attribute,
                self.dataset.variables["station_id"].ncattrs(),
                "Variable 'station id' is missing attribute '{}'.".format(_attribute),
            )

        _variable = "station_id"
        _attributes = ("long_name", "cf_role")
        _attribute_values = ("station identification code", "timeseries_id")
        self.check_attributes(_variable, _attributes, _attribute_values)

        _variable = "lat"
        _attributes = ("standard_name", "long_name", "units", "axis")
        _attribute_values_lat = ("latitude", "Station coordinates, latitude", "degrees_north", "Y")
        _attribute_values_lon = (
            "longtitude",
            "Station coordinates, longtitude",
            "degrees_east",
            "X",
        )
        self.check_attributes("lat", _attributes, _attribute_values_lat)
        self.check_attributes("lon", _attributes, _attribute_values_lon)

        name_loc1 = b""
        for char in self.dataset.variables["station_id"][0].data:
            name_loc1 += char
        self.assertTrue(name_loc1 == b"loc_a")
        self.assertTrue(self.dataset.variables["lon"][0].data == 4.3780269)
        self.assertTrue(self.dataset.variables["lat"][0].data == 51.9856484)

    def test_write_ensemble_data_without_ensemble(self):
        ensemble_size = 1
        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.dataset.write_ensemble_data(ensemble_size)
        self.dataset.close()
        self.dataset = get_exported_dataset()

        self.assertTrue("realization" not in self.dataset.dimensions)
        self.assertTrue("realization" not in self.dataset.variables)

    def test_write_ensemble_data_with_ensemble(self):
        ensemble_size = 3
        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.dataset.write_ensemble_data(ensemble_size)
        self.dataset.close()
        self.dataset = get_exported_dataset()

        self.assertIn("realization", self.dataset.dimensions)
        self.assertIn("realization", self.dataset.variables)
        self.assertEqual(self.dataset.variables["realization"].size, ensemble_size)

        _variable = "realization"
        _attributes = ("standard_name", "long_name", "units")
        _attribute_values = ("realization", "Index of an ensemble member within an ensemble", 1)
        self.check_attributes(_variable, _attributes, _attribute_values)

    def test_create_variables_without_ensemble(self):
        # TODO: rewrite test to be independent of succes of reading a netcdf file.

        unique_parameter_ids = ["u_min", "u_max", "x", "w", "constant_input", "u"]
        ensemble_size = 1
        initial_time = 0.0
        reference_datetime = datetime(1970, 1, 1, 0, 0)
        times = [x * 60 for x in range(25)]

        self.import_dataset = netcdf.ImportDataset(
            data_path(), "timeseries_import_ensemblesize1_noRealization"
        )
        stations = self.import_dataset.read_station_data()

        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.dataset.write_station_data(stations, stations.station_ids)
        self.dataset.write_ensemble_data(ensemble_size)
        self.dataset.write_times(times, initial_time, reference_datetime)
        self.dataset.create_variables(unique_parameter_ids, ensemble_size)
        self.dataset.close()
        self.dataset = get_exported_dataset()

        for _variable in unique_parameter_ids:
            self.assertIn(
                _variable, self.dataset.variables, "Variable {} is not created.".format(_variable)
            )
        self.check_associated_dimensions(
            unique_parameter_ids,
            [
                ["time", "station"],
            ]
            * 7,
        )

        # TODO: check fill_value

    def test_create_variables_with_ensemble(self):
        # TODO: rewrite test to be independent of succes of reading a netcdf file.

        unique_parameter_ids = [
            "u_min",
            "u_max",
            "x",
            "w",
            "constant_input",
            "constant_output",
            "u",
        ]
        ensemble_size = 3
        initial_time = 0.0
        reference_datetime = datetime(1970, 1, 1, 0, 0)
        times = [x * 60 for x in range(25)]

        self.import_dataset = netcdf.ImportDataset(
            data_path(), "timeseries_import_ensemblesize1_noRealization"
        )
        stations = self.import_dataset.read_station_data()

        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.dataset.write_station_data(stations, stations.station_ids)
        self.dataset.write_ensemble_data(ensemble_size)
        self.dataset.write_times(times, initial_time, reference_datetime)
        self.dataset.create_variables(unique_parameter_ids, ensemble_size)
        self.dataset.close()
        self.dataset = get_exported_dataset()

        for _variable in unique_parameter_ids:
            self.assertIn(
                _variable, self.dataset.variables, "Variable {} is not created.".format(_variable)
            )
        self.check_associated_dimensions(
            unique_parameter_ids,
            [
                ["time", "station", "realization"],
            ]
            * 7,
        )

        # TODO: check fill_value

    def test_write_output_values(self):
        files = (
            "timeseries_import_ensemblesize1_noRealization",
            "timeseries_import_ensemblesize1_withRealization",
            "timeseries_import_ensemble",
        )
        x_var_s = np.zeros((25, 2))
        x_var_e = np.zeros((25, 2, 3))
        self.expected_x_values = {}
        self.expected_x_values["loc_b"] = create_expectation_list(
            files,
            [
                deepcopy(x_var_s),
            ]
            * 2
            + [deepcopy(x_var_e)],
        )
        x_var_s[0, 0] = 1.02
        x_var_s[2, 0] = 0.03
        x_var_e[0, 0, 0] = 1.02
        x_var_e[2, 0, 0] = 0.03
        self.expected_x_values["loc_a"] = create_expectation_list(
            files,
            [
                deepcopy(x_var_s),
            ]
            * 2
            + [deepcopy(x_var_e)],
        )

        frame = inspect.currentframe()
        func_name = inspect.getframeinfo(frame).function
        for file_key in file_associations[func_name]:
            logging.debug("testing file '{}' in '{}'".format(filepaths[file_key], func_name))
            self._subtest_write_output_values(file_key)

    def _subtest_write_output_values(self, file_key):
        # TODO: rewrite test to be independent of succes of reading a netcdf file.

        unique_parameter_ids = ["u_min", "u_max", "x", "w", "constant_input", "u"]
        initial_time = 0.0
        reference_datetime = datetime(1970, 1, 1, 0, 0)
        times = [x * 60 for x in range(25)]

        self.import_dataset = netcdf.ImportDataset(data_path(), filepaths[file_key])
        stations = self.import_dataset.read_station_data()
        ensemble_size = self.import_dataset.ensemble_size

        variables = {}
        for station_id in stations.station_ids:
            variables[station_id] = {}
            for _variable in unique_parameter_ids:
                variables[station_id][_variable] = {}
                for ensemble_member in range(ensemble_size):
                    variables[station_id][_variable][ensemble_member] = (
                        self.import_dataset.read_timeseries_values(
                            list(stations.station_ids).index(station_id), _variable, ensemble_member
                        )
                    )

        self.dataset = netcdf.ExportDataset(data_path(), "timeseries_export")
        self.dataset.write_times(times, initial_time, reference_datetime)
        self.dataset.write_station_data(stations, stations.station_ids)
        self.dataset.write_ensemble_data(ensemble_size)

        self.dataset.create_variables(unique_parameter_ids, ensemble_size)

        for station_id in stations.station_ids:
            for _variable in unique_parameter_ids:
                for ensemble_member in range(ensemble_size):
                    self.dataset.write_output_values(
                        station_id,
                        _variable,
                        ensemble_member,
                        variables[station_id][_variable][ensemble_member],
                        ensemble_size,
                    )

        self.dataset.close()
        self.dataset = netcdf.ImportDataset(data_path(), "timeseries_export")
        stations = self.dataset.read_station_data()
        ensemble_size = self.import_dataset.ensemble_size

        for station_id in self.expected_x_values.keys():
            station_index = list(stations.station_ids).index(station_id)
            for ensemble_member in range(ensemble_size):
                values = self.dataset.read_timeseries_values(station_index, "x", ensemble_member)

                if ensemble_size == 1:
                    self.assertSequenceEqual(
                        self.expected_x_values[station_id][file_key][:, station_index].tolist(),
                        values.tolist(),
                    )
                else:
                    self.assertSequenceEqual(
                        self.expected_x_values[station_id][file_key][:, station_index][
                            :, ensemble_member
                        ].tolist(),
                        values.tolist(),
                    )
        self.dataset._ImportDataset__dataset.close()
