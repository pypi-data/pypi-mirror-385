# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-17

### Added
- Initial release of pandas_ti
- Automatic OHLCV column detection and mapping
- DataFrame accessor system with `.ti` namespace
- Built-in help system with `df.ti.help()`
- Volatility indicators:
  - `TR()` - True Range
  - `ATR(length)` - Average True Range
  - `RTR()` - Relative True Range
  - `ARTR(length)` - Average Relative True Range
  - `SRTR(N, expand, n, method, L, full)` - Standardized Relative True Range with HAC/Newey-West adjustment
- Extensible architecture with `@indicator` decorator
- Support for Python 3.9+
- Comprehensive documentation and examples
- MIT License

### Features
- Zero-configuration column mapping
- Works with any DataFrame structure
- Custom column mapping support
- Self-documenting indicators
- Statistical volatility analysis with z-scores and percentiles
- HAC/Newey-West variance estimation for time series
- Full Windows compatibility

[0.1.0]: https://github.com/JavierCalzadaEspuny/pandas_ti/releases/tag/v0.1.0
