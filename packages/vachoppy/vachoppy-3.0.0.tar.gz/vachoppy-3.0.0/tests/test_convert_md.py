import os
import json
import h5py
import pytest
import numpy as np
from pathlib import Path
from numpy.testing import assert_allclose
from vachoppy.core import parse_md

@pytest.fixture
def converted_files(tmp_path):
    """
    Fixture to run parse_md and return paths for answer and generated files.
    Generated files are created in a temporary directory.
    """
    current_dir = Path(__file__).parent
    outcar = current_dir / 'test_data' / '1.convert' / '1.vasp' / 'OUTCAR'
    traj_O_answer = current_dir / 'test_data' / '1.convert' / '1.vasp' / 'TRAJ_O.h5'
    traj_Ti_answer = current_dir / 'test_data' / '1.convert' / '1.vasp' / 'TRAJ_Ti.h5'

    if not outcar.is_file():
        pytest.fail(f"Test input file not found: {outcar}")
        
    try:
        original_cwd = Path.cwd()
        os.chdir(tmp_path)
        parse_md(str(outcar), format=None, temperature=2100.0, dt=2.0, label='TEST', verbose=False)
        os.chdir(original_cwd)
    except Exception as e:
        os.chdir(original_cwd)
        pytest.fail(f"Failed to run parse_md(): {e}")

    traj_O_test = tmp_path / 'TRAJ_O_TEST.h5'
    traj_Ti_test = tmp_path / 'TRAJ_Ti_TEST.h5'

    if not traj_O_test.is_file():
        pytest.fail(f"Test output file not found: {traj_O_test}")
    if not traj_Ti_test.is_file():
        pytest.fail(f"Test output file not found: {traj_Ti_test}")

    return {
        "O": {"answer": traj_O_answer, "test": traj_O_test},
        "Ti": {"answer": traj_Ti_answer, "test": traj_Ti_test}
    }


@pytest.mark.parametrize("element", ["O", "Ti"])
def test_convert_metadata(converted_files, element):
    """Tests if the metadata in the generated file matches the answer file."""
    paths = converted_files[element]

    with h5py.File(paths["answer"], 'r') as f_answer, \
         h5py.File(paths["test"], 'r') as f_test:

        expected_metadata = json.loads(f_answer.attrs['metadata'])
        actual_metadata = json.loads(f_test.attrs['metadata'])

        expected_counts = expected_metadata.pop('atom_counts')
        actual_counts = actual_metadata.pop('atom_counts')
        
        assert actual_counts == expected_counts
        assert actual_metadata == pytest.approx(expected_metadata)


@pytest.mark.parametrize("element", ["O", "Ti"])
def test_convert_positions(converted_files, element):
    """Tests if the 'positions' dataset in the generated file matches the answer."""
    paths = converted_files[element]

    with h5py.File(paths["answer"], 'r') as f_answer, \
         h5py.File(paths["test"], 'r') as f_test:

        expected_positions = f_answer['positions'][:]
        actual_positions = f_test['positions'][:]
        assert_allclose(actual_positions, expected_positions)


@pytest.mark.parametrize("element", ["O", "Ti"])
def test_convert_forces(converted_files, element):
    """Tests if the 'forces' dataset in the generated file matches the answer."""
    paths = converted_files[element]

    with h5py.File(paths["answer"], 'r') as f_answer, \
         h5py.File(paths["test"], 'r') as f_test:

        expected_forces = f_answer['forces'][:]
        actual_forces = f_test['forces'][:]
        assert_allclose(actual_forces, expected_forces)
     