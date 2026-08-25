# Bioprocess PAT / QbD Integration

A non-proprietary Python reference for integrating process analytical technology (PAT) data into a Quality-by-Design (QbD) bioprocess framework.

The repository uses a synthetic fed-batch process to connect process knowledge, multivariate PAT measurements, soft sensors, process-state monitoring, and control-strategy logic in one traceable computational system.

## Scope

- QbD knowledge model linking critical process parameters (CPPs), critical quality attributes (CQAs), and process risks
- synthetic upstream PAT/process time series
- signal validation and normalization
- PCA multivariate monitoring
- Hotelling T² and squared prediction error (SPE/Q)
- PLS soft sensing for a synthetic productivity endpoint
- illustrative design-space checks
- combined process-state assessment
- advisory control-strategy events
- requirement/risk/control/verification traceability
- tests and CI

## Architecture

```text
QbD process knowledge
        |
        v
   CPP / CQA map
        |
        v
PAT + historian signals
        |
        v
validation -> normalization
        |
        +--------------------+
        |                    |
        v                    v
 PCA / T² / SPE          PLS soft sensor
        |                    |
        +---------+----------+
                  |
                  v
           process assessment
                  |
                  v
      control-strategy advisory
                  |
                  v
          traceable evidence
```

## Synthetic signal set

Temperature, pH, dissolved oxygen, agitation, gas flow, feed rate, biomass/capacitance proxy, glucose, lactate, and three Raman-like latent features.

These are illustrative engineering signals, not a production recipe.

## QbD integration

The repository treats PAT as part of the process-control strategy rather than as a stand-alone sensor layer. It makes explicit the chain:

**CQA risk → CPP/process variable → PAT measurement → model/statistic → decision criterion → control response → verification evidence**

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
pytest -q
python examples/run_reference.py
```

## Limitations

This is a synthetic engineering reference, not a validated manufacturing system, process recipe, GMP control strategy, real-time release testing system, or regulatory submission. Thresholds and model parameters are illustrative only.

No confidential employer information, proprietary process conditions, BioMIR algorithms, or production records are included.

## Author

Yonathan Emmanuel

## License

MIT.
