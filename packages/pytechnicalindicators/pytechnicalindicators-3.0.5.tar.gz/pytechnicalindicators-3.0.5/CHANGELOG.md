# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.5] - 2025-10-19

### Changed
- Updated rust_ti dependency from 2.1.5 to 2.2.0

### Added
- Added support for new probability distribution deviation models from rust_ti 2.2.0:
	- `LogStandardDeviation` - Log-scale standard deviation for analyzing log-returns
	- `LaplaceStdEquivalent` - Laplace (double exponential) distribution scaled to standard deviation
	- `CauchyIQRScale` - Cauchy distribution scaled by interquartile range for extreme outliers
- Added string aliases for new deviation models: `"log"`, `"logstd"`, `"laplace"`, `"cauchy"`
- Enhanced `PyDeviationModel::from_string()` to support the new deviation models

### Fixed
- Updated test expectations for median and mode absolute deviation calculations due to improved algorithms in rust_ti 2.2.0

---

## [3.0.4] - 2025-10-08

### Changed
- Updated rust_ti dependency from 2.1.4 to 2.1.5
	- Updated `break_down_trends` function to use new `TrendBreakConfig` struct from rust_ti 2.1.5
	- Updated parameter names in `break_down_trends`

---

## [3.0.3] - 2025-08-13

### Added
- Updated README.md to add links to How-Tos, a summary of benchmarks, and a badge linking to Read the Docs.

---

## [3.0.2] - 2025-08-07

### Changed
- Minor document updates
- Updated RustTI version to include volatilty system fix

### Added
- Better badges to README

---

## [3.0.1] - 2025-08-04

### Changed
- Updated the package version number...

---

## [3.0.0] - 2025-08-04

### Added
- Added bindings using PyO3 and Maturin

### Changed
- Major changes to all functions, they are now bindings for the same functions in RustTI

### Removed
- Pure python functionality

---

Older releases aren't tracked in this file but some information can be found [here](https://github.com/chironmind/PyTechnicalIndicators/releases)

