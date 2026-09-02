# Bioprocess PAT / QbD Integration

A non-proprietary Python reference for integrating process analytical technology (PAT) data
into a Quality-by-Design (QbD) bioprocess framework.

The repository uses synthetic fed-batch runs to connect process knowledge, multivariate PAT
measurements, soft sensors, process-state monitoring, and control-strategy logic in one
traceable computational system.

## Scope

- QbD knowledge model linking critical process parameters (CPPs), critical quality attributes
  (CQAs), and process risks
- synthetic upstream PAT and process time series
- PCA monitoring with Hotelling T² and squared prediction error (SPE/Q)
- PLS soft sensing for a synthetic productivity endpoint
- leave-one-batch-out external validation to avoid within-run leakage
- calibration applicability-domain screening and deterministic model fingerprints
- illustrative design-space checks and advisory process-state assessment
- requirement, risk, control, and verification traceability
- lint and branch-coverage quality gates across Python 3.10–3.12

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
        |             batch-wise validation
        |             applicability domain
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

Temperature, pH, dissolved oxygen, agitation, gas flow, feed rate, biomass/capacitance proxy,
glucose, lactate, and three Raman-like latent features.

These are illustrative engineering signals, not a production recipe.

## QbD integration

The repository treats PAT as part of the process-control strategy rather than a stand-alone
sensor layer. It makes the following chain explicit:

**CQA risk → CPP/process variable → PAT measurement → model/statistic → decision criterion →
control response → verification evidence**

## Soft-sensor validation

The validation example holds out entire synthetic batches. This is more defensible for a
longitudinal bioprocess than a random row split, which can leak autocorrelated observations
from one run into both calibration and test data.

```bash
python examples/validate_soft_sensor.py
```

The generated JSON report contains fold-level RMSE, MAE, bias, R², applicability-domain
coverage, batch identities, and fitted-model fingerprints. See
[`docs/SOFT_SENSOR_VALIDATION.md`](docs/SOFT_SENSOR_VALIDATION.md) for design choices and
limitations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
ruff check src tests examples
pytest --cov=bioprocess_pat --cov-report=term-missing
python examples/run_reference.py
python examples/validate_soft_sensor.py
```

## Limitations

This is a synthetic engineering reference, not a validated manufacturing system, process
recipe, GMP control strategy, real-time release testing system, or regulatory submission.
Thresholds and model parameters are illustrative only. The synthetic batches share one data
generator and do not establish performance under real raw-material, scale, site, instrument,
or process variation.

No confidential employer information, proprietary process conditions, BioMIR algorithms, or
production records are included.

## Author

Yonathan Emmanuel

## License

MIT.
