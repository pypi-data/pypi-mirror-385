# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-21

### Added

#### Core Features
- **Excel Parsing**: Convert Excel files to JSON with complete formatting information
  - Support for .xlsx and .xls formats
  - Extract cell values, formulas, and formatting
  - Preserve merged cells, row heights, and column widths
  - Font, fill, border, and alignment information extraction

- **Excel Generation**: Create formatted Excel files from JSON data
  - Generate Excel files from Pydantic models
  - Apply cell formatting (fonts, colors, borders, alignment)
  - Support for merged cells and dimension adjustments
  - Formula preservation and calculation

- **Advanced Formatting**: Modify cell styles and layout
  - Modify cell formats (fonts, fills, borders, alignment)
  - Merge and unmerge cell ranges
  - Adjust row heights and column widths
  - Batch formatting operations

- **Formula Support**: Execute and calculate 20+ common Excel formulas
  - Mathematical functions: SUM, AVERAGE, MAX, MIN, COUNT, ROUND
  - Logical functions: IF, AND, OR, NOT
  - Text functions: CONCATENATE, LEN, LEFT, RIGHT, MID
  - Formula dependency analysis and circular reference detection
  - Batch formula recalculation

- **Multi-Sheet Operations**: Manage multiple worksheets
  - Create, delete, rename, copy, and move sheets
  - Merge multiple Excel files into a single workbook
  - Flexible duplicate handling strategies (rename, skip, overwrite)
  - Format preservation during merge operations

- **Supabase Integration**: Direct read/write operations with Supabase Storage
  - Upload Excel files to Supabase Storage
  - Download files from Supabase Storage
  - List and manage files in buckets
  - Automatic file validation and error handling

#### Performance Optimizations
- **Caching Mechanism**: LRU cache with TTL support
  - Parse cache (50 entries, 1-hour TTL)
  - Format cache (200 entries, 30-minute TTL)
  - Thread-safe implementation
  - Cache statistics and management

- **Concurrent Processing**: Multi-threaded operations
  - Thread pool management with context managers
  - Concurrent file processing with order preservation
  - Progress tracking and error handling
  - Configurable worker count

- **Stream Processing**: Memory-efficient large file handling
  - Read-only and write-only modes for openpyxl
  - Chunk-based processing
  - Memory monitoring and optimization
  - Handles files >10MB efficiently

#### Error Handling and Monitoring
- **Comprehensive Error System**: 20+ custom exception classes
  - Error code system (E001-E599)
  - Detailed error context and stack traces
  - Multiple recovery strategies (retry, fallback, ignore, propagate)
  - Automatic retry with exponential backoff

- **Advanced Logging**: Multi-level logging system
  - Main log, error log, audit log, performance log
  - Structured logging (JSON Lines format)
  - Error tracking and statistics
  - Log rotation and management

- **Performance Monitoring**: Real-time metrics collection
  - Response time tracking (P50, P95, P99 percentiles)
  - Error rate monitoring with time windows
  - Resource usage monitoring (CPU, memory, disk)
  - Prometheus-compatible metrics export

#### Documentation
- **Comprehensive API Documentation**: Detailed API reference
  - 12 MCP tools with examples
  - Input/output schemas
  - Error handling guidelines
  - Best practices

- **Architecture Documentation**: System design and patterns
  - Component architecture
  - Data flow diagrams
  - Design patterns used
  - Performance considerations

- **Development Guide**: Setup and contribution guidelines
  - Development environment setup
  - Code quality standards
  - Testing guidelines
  - Contribution workflow

- **Examples**: Practical usage examples
  - Basic operations
  - Advanced scenarios
  - Integration examples
  - Troubleshooting guide

### MCP Tools (12 Total)

1. **parse_excel_to_json**: Parse Excel files to JSON format
2. **create_excel_from_json**: Generate Excel files from JSON data
3. **modify_cell_format**: Edit cell formatting (fonts, colors, borders)
4. **merge_cells**: Merge cell ranges
5. **unmerge_cells**: Unmerge cell ranges
6. **set_row_heights**: Adjust row heights
7. **set_column_widths**: Adjust column widths
8. **manage_storage**: Upload/download files to/from Supabase
9. **set_formula**: Set Excel formulas in cells
10. **recalculate_formulas**: Recalculate all formulas in a workbook
11. **manage_sheets**: Create, delete, rename, copy, move sheets
12. **merge_excel_files**: Merge multiple Excel files

### Technical Highlights

- **Type Safety**: Full type annotations with mypy validation
- **Code Quality**: Black formatting, Ruff linting, 100% compliance
- **Test Coverage**: 300+ test cases, 85-100% coverage across modules
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Zero Dependencies**: No Microsoft Office or WPS required
- **Production Ready**: Comprehensive error handling and monitoring

### Performance Benchmarks

- Single file (1MB) parsing: 0.598s (target: <2s) - **3.3x faster**
- Batch (20 files) parsing: 0.192s (target: <10s) - **52x faster**
- Generate 1000 rows: 0.026s (target: <3s) - **115x faster**
- Merge 10 files: 0.117s (target: <8s) - **68x faster**
- Stream processing (5000 rows): 0.04MB memory increase (target: <500MB) - **12500x better**

### Dependencies

#### Core Dependencies
- openpyxl >= 3.1.0
- supabase >= 2.0.0
- mcp >= 1.0.0
- python-dotenv >= 1.0.0
- formulas >= 1.2.0
- pydantic >= 2.0.0
- psutil >= 5.9.0

#### Development Dependencies
- pytest >= 8.0.0
- pytest-asyncio >= 0.23.0
- pytest-cov >= 4.1.0
- pytest-mock >= 3.12.0
- black >= 24.0.0
- ruff >= 0.3.0
- mypy >= 1.8.0
- pip-audit >= 2.6.0
- types-openpyxl
- types-psutil

### Security

- **Input Validation**: All user inputs validated
- **Path Traversal Protection**: File path sanitization
- **DoS Prevention**: File size limits and timeout mechanisms
- **Secure Credentials**: Environment variable management
- **No Known Vulnerabilities**: All dependencies scanned and verified

### Breaking Changes

None (initial release)

### Deprecated

None (initial release)

### Removed

None (initial release)

### Fixed

None (initial release)

### Known Issues

None

## [Unreleased]

### Planned Features

- Async/await support for I/O operations
- Redis caching backend option
- GraphQL API support
- Advanced chart generation
- Data validation rules
- Conditional formatting
- Pivot table support

---

## Release Notes

### v1.0.0 - Initial Release

This is the first stable release of Excel MCP Server with Supabase Storage. The project has undergone 12 development stages with comprehensive testing and documentation.

**Highlights**:
- 12 MCP tools for comprehensive Excel operations
- Performance optimizations (caching, concurrency, streaming)
- Production-grade error handling and monitoring
- Extensive documentation and examples
- 85-100% test coverage
- Zero security vulnerabilities

**Installation**:
```bash
# Via uvx (recommended)
uvx mcp-excel-supabase

# Via pip
pip install mcp-excel-supabase

# From GitHub
uvx --from git+https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage mcp-excel-supabase
```

**Quick Start**:
See [README.md](README.md) and [docs/uvx-installation.md](docs/uvx-installation.md) for detailed installation and usage instructions.

**Support**:
- GitHub Issues: https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/issues
- Documentation: https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/blob/main/docs/README.md

---

[1.0.0]: https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/releases/tag/v1.0.0
[Unreleased]: https://github.com/1126misakp/Excel-MCP-Server-with-Supabase-Storage/compare/v1.0.0...HEAD

