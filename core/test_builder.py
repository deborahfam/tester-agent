"""
test_builder.py
~~~~~~~~~~~~~~~~

Builds pytest-compatible test files from a list of generated test cases.
Provides functions to create a single ``test_<slug>.py`` file associated with
a specific solution, as well as to package multiple solutions and their tests
in a ZIP ready for distribution.

Test generation is done so that each test case appears as an entry in a
``@pytest.mark.parametrize``.  It is assumed that the solution implements a
function called ``solve`` and that test cases provide a serializable
representation of the arguments and expected value.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List


def build_pytest_file(test_cases: List[Dict], module_name: str, output_path: str, func_name: str = "solve") -> None:
    """Generates a pytest test file from a list of cases.

    :param test_cases: List of dictionaries with keys ``input`` and ``expected``.
    :param module_name: Name of the module containing the function to test (without
      extension).  For example, ``solution_1``.
    :param output_path: Path of the test file to create.
    :param func_name: Name of the function to invoke in the module.
    """
    # Prepare the list of tuples (input, expected) for pytest
    param_lines = []
    for case in test_cases:
        input_data = case.get("input")
        expected = case.get("expected")
        param_lines.append((input_data, expected))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("import pytest\n")
        f.write(f"from {module_name} import {func_name}\n\n")
        f.write("TEST_CASES = ")
        json_str = json.dumps(param_lines, indent=2)
        f.write(json_str)
        f.write("\n\n")
        f.write("@pytest.mark.parametrize(\"inp, expected\", TEST_CASES)\n")
        f.write(f"def test_{func_name}(inp, expected):\n")
        f.write("    if isinstance(inp, list):\n")
        f.write("        result = {func_name}(*inp)\n".format(func_name=func_name))
        f.write("    elif inp is None:\n")
        f.write("        result = {func_name}()\n".format(func_name=func_name))
        f.write("    else:\n")
        f.write("        result = {func_name}(inp)\n".format(func_name=func_name))
        f.write("    assert result == expected\n")


def create_test_suite_for_solutions(test_cases: List[Dict], solution_files: Iterable[str], output_dir: str, func_name: str = "solve") -> List[str]:
    """Creates test files for each provided solution file.

    :param test_cases: List of test cases.
    :param solution_files: Iterable with paths to .py solution files.
    :param output_dir: Directory where test files will be saved.
    :param func_name: Name of the function to test.
    :return: List of paths to the generated test files.
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    test_paths = []
    for sol_path in solution_files:
        sol_name = Path(sol_path).stem
        test_filename = f"test_{sol_name}.py"
        test_path = output_dir_path / test_filename
        build_pytest_file(test_cases, sol_name, str(test_path), func_name=func_name)
        test_paths.append(str(test_path))
    return test_paths