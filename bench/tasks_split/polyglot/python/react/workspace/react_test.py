# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/react/canonical-data.json
# File last updated on 2023-07-19

from functools import partial
import unittest

from react import (
    InputCell,
    ComputeCell,
)


class ReactTest(unittest.TestCase):
    def test_input_cells_have_a_value(self):
        input = InputCell(10)
        self.assertEqual(input.value, 10)


    def test_compute_cells_calculate_initial_value(self):
        input = InputCell(1)
        output = ComputeCell(
            [
                input,
            ],
            lambda inputs: inputs[0] + 1,
        )
        self.assertEqual(output.value, 2)


    def test_compute_cells_update_value_when_dependencies_are_changed(self):
        input = InputCell(1)
        output = ComputeCell(
            [
                input,
            ],
            lambda inputs: inputs[0] + 1,
        )
        input.value = 3
        self.assertEqual(output.value, 4)


    def test_compute_cells_fire_callbacks(self):
        input = InputCell(1)
        output = ComputeCell(
            [
                input,
            ],
            lambda inputs: inputs[0] + 1,
        )
        cb1_observer = []
        callback1 = self.callback_factory(cb1_observer)
        output.add_callback(callback1)
        input.value = 3
        self.assertEqual(cb1_observer[-1], 4)


    def test_callbacks_do_not_report_already_reported_values(self):
        input = InputCell(1)
        output = ComputeCell(
            [
                input,
            ],
            lambda inputs: inputs[0] + 1,
        )
        cb1_observer = []
        callback1 = self.callback_factory(cb1_observer)
        output.add_callback(callback1)
        input.value = 2
        self.assertEqual(cb1_observer[-1], 3)
        input.value = 3
        self.assertEqual(cb1_observer[-1], 4)


    def test_callbacks_can_be_added_and_removed(self):
        input = InputCell(11)
        output = ComputeCell(
            [
                input,
            ],
            lambda inputs: inputs[0] + 1,
        )
        cb1_observer = []
        cb2_observer = []
        cb3_observer = []
        callback1 = self.callback_factory(cb1_observer)
        callback2 = self.callback_factory(cb2_observer)
        callback3 = self.callback_factory(cb3_observer)
        output.add_callback(callback1)
        output.add_callback(callback2)
        input.value = 31
        self.assertEqual(cb1_observer[-1], 32)
        self.assertEqual(cb2_observer[-1], 32)
        output.remove_callback(callback1)
        output.add_callback(callback3)
        input.value = 41
        self.assertEqual(len(cb1_observer), 1)
        self.assertEqual(cb2_observer[-1], 42)
        self.assertEqual(cb3_observer[-1], 42)


    def test_callbacks_should_only_be_called_once_even_if_multiple_dependencies_change(
        self,
    ):
        input = InputCell(1)
        plus_one = ComputeCell(
            [
                input,
            ],
            lambda inputs: inputs[0] + 1,
        )
        minus_one1 = ComputeCell(
            [
                input,
            ],
            lambda inputs: inputs[0] - 1,
        )
        minus_one2 = ComputeCell(
            [
                minus_one1,
            ],
            lambda inputs: inputs[0] - 1,
        )
        output = ComputeCell(
            [
                plus_one,
                minus_one2,
            ],
            lambda inputs: inputs[0] * inputs[1],
        )
        cb1_observer = []
        callback1 = self.callback_factory(cb1_observer)
        output.add_callback(callback1)
        input.value = 4
        self.assertEqual(cb1_observer[-1], 10)


    # Utility functions.
    def callback_factory(self, observer):
        def callback(observer, value):
            observer.append(value)

        return partial(callback, observer)
