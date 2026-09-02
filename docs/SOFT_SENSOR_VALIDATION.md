# Soft-sensor validation

The productivity soft sensor is evaluated with leave-one-batch-out validation. Each fold
calibrates the PLS model on complete synthetic batches and evaluates it on a different batch
that was not used for preprocessing, component estimation, or fitting.

This separation is intentional. Randomly splitting time points from one bioprocess run can
place adjacent, autocorrelated observations in both calibration and test sets and produce an
optimistic estimate of generalization.

## Reported evidence

Each external-validation fold records:

- held-out and calibration batch identities;
- number of calibration and external observations;
- RMSE, MAE, bias, and R²;
- fraction of predictions inside the calibration applicability domain; and
- a SHA-256 fingerprint of the fitted preprocessing and PLS parameters.

The example writes a machine-readable JSON report:

```bash
python examples/validate_soft_sensor.py
```

## Applicability domain

The reference computes squared Mahalanobis distance in standardized predictor space and sets
an empirical upper limit from calibration data. A prediction outside this envelope is flagged;
it is not silently treated as equivalent to an interpolation.

The statistic is illustrative. A manufacturing implementation would pre-specify the domain,
justify its threshold using representative batches, evaluate robustness to raw-material and
scale effects, and define fallback behavior before use.

## Remaining limitations

The data are synthetic, batches share one generator, and hyperparameters are not selected in a
nested validation loop. The reported metrics therefore test implementation behavior and study
design, not manufacturing performance or suitability for real-time release.
