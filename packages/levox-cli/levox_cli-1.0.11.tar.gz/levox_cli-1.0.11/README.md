# Levox - Enterprise-Grade Compliance Auditor & PII Detection CLI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Levox is an enterprise-grade compliance auditor that provides real-time GDPR/CCPA violation alerts for engineers and executive-ready compliance dashboards for auditors, positioning your organization as audit-grade with industry-leading compliance practices.

## 🚀 Features

### Core Detection Pipeline
- **7-Stage Detection Pipeline**: Regex → AST Analysis → Context Analysis → Dataflow → CFG Analysis → ML Filtering → GDPR Compliance
- **Multi-Language Support**: Python, JavaScript, and extensible parser architecture
- **Performance Optimized**: <10s incremental scans, <30s full repository scans
- **Low False Positives**: Target <10% false positive rate
- **Memory Efficient**: Memory-mapped file operations for large codebases

### Enterprise Compliance Features
- **Real-Time Compliance Alerts**: Immediate GDPR/CCPA violation detection with specific article references
- **Multi-Framework Support**: Unified GDPR + CCPA compliance analysis
- **Executive Dashboards**: Professional compliance dashboards for audits and executive reporting
- **Compliance Scoring**: Industry-grade scoring algorithm (0-100 scale) with A+ to F grading
- **Industry Benchmarking**: Compare compliance scores against SaaS, FinTech, HealthTech, E-commerce peers
- **Cross-Framework Mapping**: Intelligent mapping between GDPR and CCPA violations
- **Cryptographic Audit Logs**: Tamper-proof audit trails with SHA-256 hash chains
- **Real-Time Monitoring**: Continuous compliance assessment and automated alerting

### Enterprise Licensing
- **Starter**: Basic PII detection with compliance awareness
- **Pro**: GDPR compliance alerts, scoring, and executive dashboards
- **Business**: GDPR + CCPA support, multi-framework analysis, industry benchmarking
- **Enterprise**: Full compliance suite, API access, cryptographic audit logs, real-time monitoring

## 🏗️ Architecture

```
levox/
├── levox/
│   ├── cli.py                 # Main CLI entry point
│   ├── core/
│   │   ├── engine.py          # Detection engine orchestrator
│   │   ├── config.py          # Configuration management
│   │   └── exceptions.py      # Custom exceptions
│   ├── detection/
│   │   ├── regex_engine.py    # Stage 1: Optimized regex detection
│   │   ├── ast_analyzer.py    # Stage 2: AST-based context analysis
│   │   ├── context_analyzer.py # Stage 3: Semantic context analysis
│   │   ├── dataflow.py        # Stage 4: Taint/dataflow analysis
│   │   ├── cfg_analyzer.py    # Stage 5: Control Flow Graph analysis
│   │   └── ml_filter.py       # Stage 6: ML-based false positive reduction
│   ├── compliance/           # Enterprise Compliance Suite
│   │   ├── compliance_alerter.py # Real-time compliance alerts
│   │   ├── gdpr_analyzer.py  # GDPR compliance analysis
│   │   ├── ccpa_analyzer.py  # CCPA compliance analysis
│   │   ├── framework_engine.py # Multi-framework orchestrator
│   │   ├── framework_mapper.py # Cross-framework mapping
│   │   ├── compliance_scoring.py # Compliance scoring engine
│   │   ├── compliance_dashboard.py # Executive dashboards
│   │   ├── audit_logger.py   # Cryptographic audit logging
│   │   └── models.py         # Compliance data models
│   ├── parsers/
│   │   ├── base.py           # Base parser interface
│   │   ├── python_parser.py  # Python AST parser
│   │   ├── javascript_parser.py # JS parser
│   │   └── multi_lang.py     # Multi-language coordinator
│   ├── utils/
│   │   ├── file_handler.py   # Memory-mapped file operations
│   │   ├── validators.py     # Luhn, format validators
│   │   └── performance.py    # Performance monitoring
│   └── models/
│       ├── detection_result.py # Result data models
│       └── confidence.py       # Confidence scoring
```

## 📦 Installation

### From Source

```bash
git clone https://github.com/levox/levox.git
cd levox
pip install -e .
```

### From PyPI

```bash
pip install levox-cli
```

### From PyPI (Development Version)

```bash
pip install --upgrade levox-cli
```

## 🚀 Quick Start

### Basic Usage

```bash
# Scan current directory
levox scan

# Scan specific directory
levox scan /path/to/codebase

# Scan with CFG analysis (Premium+)
levox scan --cfg

# Generate detailed report
levox scan --output report.json --format json

# Configure detection rules
levox configure --rules custom-rules.yaml
```

### Compliance Commands (Pro+)

```bash
# Full compliance audit with real-time alerts
levox compliance audit /path/to/codebase

# Quick compliance score check
levox compliance score /path/to/codebase

# Generate executive dashboard
levox compliance dashboard --company my-company

# View compliance trends over time
levox compliance trends --company my-company --days 90

# Compare against industry benchmarks
levox compliance benchmark --industry saas

# Export compliance reports
levox compliance export --format pdf --output compliance-report.pdf
```

### Advanced Compliance Scanning

```bash
# Enable compliance mode with real-time alerts
levox scan --compliance-mode --alert-threshold high

# Multi-framework compliance (Business+)
levox scan --compliance-frameworks gdpr,ccpa --executive-summary

# Compliance-focused scanning with specific frameworks
levox scan --compliance-frameworks gdpr --compliance-mode --alert-threshold critical
```

### Advanced CFG Analysis

```bash
# Enable deep scanning with CFG analysis
levox scan --cfg --cfg-confidence 0.7

# Alternative flag name
levox scan --deep-scan

# Full enterprise scan with all stages
levox scan --license-tier enterprise --cfg --format json
```

### CLI Commands

#### Core Commands
- `levox scan` - Scan codebase for PII/GDPR violations
- `levox configure` - Configure detection rules and settings
- `levox status` - Show system status and capabilities
- `levox company` - Company profile management for compliance tracking
- `levox evidence` - Generate audit-ready evidence packages

#### Compliance Commands (Pro+)
- `levox compliance audit` - Full compliance audit with real-time alerts
- `levox compliance score` - Quick compliance score check
- `levox compliance dashboard` - Generate executive dashboard
- `levox compliance trends` - View compliance trends over time
- `levox compliance benchmark` - Compare against industry benchmarks
- `levox compliance export` - Export compliance reports in various formats

#### Compliance Features by Tier

**Starter Tier:**
- Basic PII detection with regex patterns
- Compliance awareness and guidance
- JSON reports only

**Pro Tier:**
- GDPR compliance alerts with real-time notifications
- Compliance scoring and grading (A+ to F)
- Executive dashboards for audit preparation
- HTML, PDF, SARIF report formats

**Business Tier:**
- GDPR + CCPA dual compliance support
- Multi-framework analysis and cross-framework mapping
- Industry benchmarking against peers
- Compliance trends and analytics

**Enterprise Tier:**
- Full compliance suite with API access
- Cryptographic audit logs with SHA-256 hash chains
- Real-time compliance monitoring
- Advanced compliance analytics and automation

## ⚙️ Configuration

### Detection Pipeline Stages

**STAGE 1: Regex Detection (Basic)**
- Fast pattern matching for basic PII patterns
- Optimized regex engine with minimal false positives

**STAGE 2: AST Analysis (Premium+)**
- Abstract syntax tree parsing for code structure
- Multi-language support with Tree-sitter

**STAGE 3: Context Analysis (Premium+)**
- Semantic analysis of variable/function names
- Context-aware false positive reduction

**STAGE 4: Dataflow Analysis (Enterprise)**
- Tracks data movement through code
- Taint analysis for sensitive data flows

**STAGE 5: CFG Analysis (Premium+)**
- Control Flow Graph analysis for complex PII flows
- Detects conditional exposure, loop accumulation, transformation chains

**STAGE 6: ML Filtering (Enterprise)**
- Machine learning false positive reduction
- Confidence scoring and validation

**STAGE 7: GDPR Compliance (Pro+)**
- Real-time GDPR violation alerts with article references
- Compliance scoring and grading system
- Executive dashboards for audit preparation
- Multi-framework support (GDPR + CCPA in Business+)
- Cross-framework violation mapping
- Industry benchmarking and trend analysis

### License Tiers

- **Starter**: Basic PII detection, compliance awareness, JSON reports
- **Pro**: GDPR compliance alerts, scoring, executive dashboards, HTML/PDF reports
- **Business**: GDPR + CCPA support, multi-framework analysis, industry benchmarking
- **Enterprise**: Full compliance suite, API access, cryptographic audit logs, real-time monitoring

### Detection Rules

Create custom detection rules in `configs/rules.yaml`:

```yaml
patterns:
  credit_card:
    regex: '\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    confidence: 0.8
    risk_level: high
    
  email:
    regex: '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    confidence: 0.9
    risk_level: medium
```

## 🔍 Detection Pipeline

### Level 1: Regex Engine
- High-performance pattern matching
- Optimized for common PII formats
- Fast initial screening

### Level 2: AST Analysis
- Context-aware detection
- Variable name analysis
- Comment and string extraction

### Level 3: Dataflow Analysis
- Taint tracking
- Variable propagation
- Cross-function analysis

### Level 4: ML Filtering
- False positive reduction
- Context classification
- Confidence scoring

## 📊 Performance

- **Incremental Scans**: <10 seconds for modified files
- **Full Repository**: <30 seconds for 10,000 files
- **Memory Usage**: <500MB for large codebases
- **False Positive Rate**: Target <10%

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=levox

# Run specific test suite
pytest tests/test_detection/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.levox.ai](https://docs.levox.ai)
- **Issues**: [GitHub Issues](https://github.com/levox/levox/issues)
- **Discussions**: [GitHub Discussions](https://github.com/levox/levox/discussions)

## 🏆 Enterprise Support

For enterprise customers, we offer:
- Custom detection rules
- API integration
- Dedicated support
- Training and consulting

Contact us at enterprise@levox.ai for more information.
