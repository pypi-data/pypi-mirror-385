"""
Tests for the system_configuration module.

Author: Sustainable Power Systems Lab (SPSL)
Web: https://sps-lab.org
Contact: info@sps-lab.org
"""

import pytest
import numpy as np
from tsoc_data_analysis.system_configuration import (
    FILES,
    COLUMN_PREFIXES,
    DATA_VALIDATION,
    REPRESENTATIVE_OPS,
    clean_column_name,
    convert_numpy_types
)


class TestSystemConfiguration:
    """Test cases for system configuration module."""

    def test_files_structure(self):
        """Test that FILES dictionary has expected structure."""
        expected_keys = {
            'substation_mw', 'substation_mvar', 'wind_power',
            'shunt_elements', 'gen_voltage', 'gen_mvar'
        }
        assert set(FILES.keys()) == expected_keys
        assert all(isinstance(value, str) for value in FILES.values())
        assert all(value.endswith('.xlsx') for value in FILES.values())

    def test_column_prefixes_structure(self):
        """Test that COLUMN_PREFIXES dictionary has expected structure."""
        expected_keys = {
            'substation_mw', 'substation_mvar', 'wind_power',
            'shunt_elements', 'gen_voltage', 'gen_mvar'
        }
        assert set(COLUMN_PREFIXES.keys()) == expected_keys
        assert all(isinstance(value, str) for value in COLUMN_PREFIXES.values())

    def test_data_validation_structure(self):
        """Test that DATA_VALIDATION has expected structure."""
        assert 'type_checks' in DATA_VALIDATION
        assert 'limit_checks' in DATA_VALIDATION
        assert 'gap_filling' in DATA_VALIDATION

    def test_representative_ops_structure(self):
        """Test that REPRESENTATIVE_OPS has expected structure."""
        assert 'defaults' in REPRESENTATIVE_OPS
        assert 'quality_thresholds' in REPRESENTATIVE_OPS
        assert 'ranking_weights' in REPRESENTATIVE_OPS
        assert 'output_files' in REPRESENTATIVE_OPS

    def test_clean_column_name(self):
        """Test clean_column_name function."""
        # Test basic functionality
        result = clean_column_name('ss_mw_STATION1_132REACTOR_REACTIVE_POWER')
        assert result == 'ss_mw_STATION1'
        
        # Test with no suffix to remove
        result = clean_column_name('ss_mw_STATION1')
        assert result == 'ss_mw_STATION1'
        
        # Test with multiple suffixes
        result = clean_column_name('ss_mw_STATION1_132REACTOR_REACTIVE_POWER_EXTRA_SUFFIX')
        assert result == 'ss_mw_STATION1'

    def test_convert_numpy_types(self):
        """Test convert_numpy_types function."""
        # Test numpy integers
        data = {'int64': np.int64(42), 'int32': np.int32(24)}
        result = convert_numpy_types(data)
        assert result['int64'] == 42
        assert result['int32'] == 24
        assert isinstance(result['int64'], int)
        assert isinstance(result['int32'], int)
        
        # Test numpy floats
        data = {'float64': np.float64(3.14), 'float32': np.float32(2.71)}
        result = convert_numpy_types(data)
        assert result['float64'] == 3.14
        assert result['float32'] == 2.71
        assert isinstance(result['float64'], float)
        assert isinstance(result['float32'], float)
        
        # Test numpy arrays
        data = {'array': np.array([1, 2, 3])}
        result = convert_numpy_types(data)
        assert result['array'] == [1, 2, 3]
        assert isinstance(result['array'], list)
        
        # Test nested structures
        data = {
            'nested': {
                'int64': np.int64(42),
                'array': np.array([1, 2, 3])
            }
        }
        result = convert_numpy_types(data)
        assert result['nested']['int64'] == 42
        assert result['nested']['array'] == [1, 2, 3]
        
        # Test regular Python types (should remain unchanged)
        data = {'regular_int': 42, 'regular_float': 3.14, 'regular_list': [1, 2, 3]}
        result = convert_numpy_types(data)
        assert result == data


if __name__ == '__main__':
    pytest.main([__file__]) 