# LINE⁴ | Global Risk Radar

live app: https://line4.vercel.app/

**AI Safety Intelligence System** — Real-time monitoring of catastrophic AI risk assessments from Anthropic, OpenAI, and DeepMind.

## Overview

LINE⁴ (Line Four) aggregates official safety evaluations across three frameworks to provide transparent, real-time visibility into AI safety assessments across major labs. The dashboard tracks risks across four critical dimensions: CBRN proliferation, cyber offense capabilities, autonomous replication, and deceptive alignment.

**Data Source:** Real assessments extracted from official lab System Cards
- Anthropic: Responsible Scaling Policy (RSP) with Automation Safety Levels (ASL)
- OpenAI: Preparedness Framework with severity assessments
- DeepMind: Frontier Safety Framework with Critical Capability Levels (CCL)

## Current Features

### Dashboard Capabilities
- **Risk Tracking**: 200+ deduplicated AI safety assessments across 3 labs
- **Multi-Framework Display**: Distinct visualization for each safety framework
- **Interactive Visualizations**: Trend analysis, risk distributions, correlation matrices
- **Pagination**: 15-item table views with Prev/Next navigation
- **Real-time Data**: Syncs with latest consolidated datasets
- **Professional UI**: Enterprise-grade beige/paper aesthetic, zero emojis

### Data Quality
- **Deduplication System**: Unique key enforcement (Lab|Model|Framework|Risk_Category)
- **Validation Pipeline**: Required field checks before inclusion
- **Framework Consistency**: Each lab uses distinct framework—no mixing
- **Version Control**: All data from verified, official sources

### Risk Categories Monitored
1. **CBRN Proliferation**: Biological, chemical capability risks
2. **Cyber Offense**: Code generation, exploit capabilities
3. **Autonomous Replication**: Self-replication, resource acquisition risks
4. **Deceptive Alignment**: Sandbagging, hidden goal pursuit risks

## Current Limitations

### Data Scope
- **Static Snapshots**: Dashboard reflects data state at deployment; no real-time lab integration
- **Limited Model Coverage**: ~30 unique models tracked (not all released models)
- **Framework Constraints**: Each lab publishes different evaluation frequencies—asynchronous updates
- **Evaluation Gaps**: Some risk categories evaluated inconsistently across labs

### Technical Constraints
- **No Live API Connections**: Cannot dynamically fetch latest system cards
- **Manual Data Updates**: Requires developer intervention to incorporate new lab publications
- **Single Environment**: No staging/production separation
- **Limited Historical Tracking**: Baseline data from ~Feb 2025 forward only

### UI/UX Limitations

- **Pagination Only**: No full-text search, filtering by date or model
- **No Export Functionality**: Cannot download reports or CSV extracts
- **Single Dashboard View**: No customizable dashboards per user role
- **No Alerting System**: Cannot set thresholds to trigger notifications

### Operational Constraints

- **No Scheduled Refreshes**: Watcher script disabled in production
- **No Multi-user Accounts**: Public read-only access only
- **No Audit Logging**: Cannot track who viewed/accessed data or when
- **No Rate Limiting**: No protections against abuse or excessive queries

## Future Directions

### Phase 1: Enhanced Data Integration (Q2-Q3 2026)

- **Automated Data Fetching**: Implement scheduled PDF extraction from lab system cards
- **Real-time RSS Feeds**: Subscribe to lab announcements for new model releases
- **Versioned History**: Track score changes over time with delta indicators
- **Snapshot Comparison**: "Before/After" analysis when labs update assessments

## Project Structure

```
line4-risk-radar/
├── app.py                      # Main dashboard (single-file architecture)
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata
├── README.md                  # This file
├── .env                       # Environment variables (local only)
├── .gitignore                 # Git ignore rules
├── .streamlit/
│   └── config.toml            # Streamlit configuration (production theme)
├── data/
│   └── live_risk_data.json    # Live update cache
├── consolidated_risk_data.json # Anthropic + DeepMind assessments
├── safety-data.json           # OpenAI evaluations
└── anthropic_model_data.json  # Fallback Anthropic data
```

## Data Sources

**Official Safety Documents:**
- [Anthropic System Cards](https://www.anthropic.com/system-cards)
- [OpenAI Safety Hub](https://openai.com/safety/evaluations-hub/)
- [DeepMind Model Cards](https://deepmind.google/models/model-cards/)

**Frameworks:**
- Anthropic: RSP v1.3 (Jan 2025)
- OpenAI: Preparedness Framework v2 (Nov 2025)
- DeepMind: Frontier Safety Framework v3 (Sept 2025)

## Contributing

Data contributions welcome:
1. Verify source from official lab publication
2. Extract risk scores following framework guidelines
3. Submit PR with updated JSON files
4. Include citation and publication date

## Limitations & Disclaimers

- **Research Use Only**: Not an official safety audit tool
- **No Real-time Guarantees**: Data reflects lab publications, not continuous monitoring
- **Framework Differences**: Scores not directly comparable across labs (different methodologies)
- **Limited Scope**: Focuses on published evaluations; does not include internal lab assessments
- **No Endorsement**: Dashboard presents data; does not validate lab claims.

## Technical Stack

- **Frontend**: Streamlit 1.28+
- **Data**: Pandas, JSON
- **Visualization**: Plotly interactive charts
- **Deployment**: Streamlit Community Cloud
- **Language**: Python 3.10+

## License

MIT License - See LICENSE file for details

**Last Updated**: February 1, 2026 | **Version**: 2.0.0
