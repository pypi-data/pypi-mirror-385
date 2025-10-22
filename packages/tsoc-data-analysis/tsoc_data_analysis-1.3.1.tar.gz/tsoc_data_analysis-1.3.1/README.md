# TSOC Data Analysis

**Author:** Sustainable Power Systems Lab (SPSL), [https://sps-lab.org](https://sps-lab.org), contact: info@sps-lab.org

A comprehensive Python tool for analyzing TSOC power system operational data from Excel files. Provides a powerful command-line interface (CLI) and modular Python API for load analysis, generator categorization, wind power analysis, reactive power calculations, and representative operating point extraction.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-sphinx-blue.svg)](https://tsoc-data-analysis.sps-lab.org/)
[![PyPI](https://img.shields.io/pypi/v/tsoc-data-analysis.svg)](https://pypi.org/project/tsoc-data-analysis/)

## 📖 Full Documentation

**For complete installation instructions, detailed usage examples, configuration options, and troubleshooting, visit:**

**[https://tsoc-data-analysis.sps-lab.org/](https://tsoc-data-analysis.sps-lab.org/)**

## Quick Installation

```bash
pip install tsoc-data-analysis
```

## Quick Start

### Python API
```python
from tsoc_data_analysis import execute, extract_representative_ops

# Load and analyze data
success, df = execute(month='2024-01', data_dir='raw_data', output_dir='results')
if success:
    # Extract representative points
    rep_df, diagnostics = extract_representative_ops(
        df, max_power=450, MAPGL=200, output_dir='results'
    )
```

## Key Features

- **Month-based data filtering** for efficient processing
- **Load calculations** (Total Load, Net Load) with statistics
- **Wind power analysis** with generation profiles
- **Generator categorization** (Voltage Control vs PQ Control)
- **Reactive power analysis** with comprehensive calculations
- **Data validation** with advanced gap filling and anomaly detection
- **Representative operating points extraction** using K-means clustering
- **Comprehensive logging** and error handling

## Requirements

- Python 3.7+
- pandas>=1.3.0, numpy>=1.20.0, matplotlib>=3.3.0, seaborn>=0.11.0
- openpyxl>=3.0.0, scikit-learn>=1.0.0, scipy>=1.7.0
- psutil>=5.8.0, joblib>=1.1.0

## Documentation Sections

- **[Installation Guide](https://tsoc-data-analysis.sps-lab.org/installation.html)** - Detailed setup instructions
- **[User Guide](https://tsoc-data-analysis.sps-lab.org/user_guide.html)** - Getting started and basic workflow
- **[Configuration Guide](https://tsoc-data-analysis.sps-lab.org/configuration.html)** - Customizing system parameters
- **[Examples](https://tsoc-data-analysis.sps-lab.org/examples.html)** - Code examples and workflows
- **[Troubleshooting](https://tsoc-data-analysis.sps-lab.org/troubleshooting.html)** - Common issues and solutions

## Support

For detailed information, examples, and troubleshooting, please visit the [full documentation](https://tsoc-data-analysis.sps-lab.org/).

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
