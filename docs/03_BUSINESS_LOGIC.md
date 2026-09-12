# Business Logic

## NBM Residuals
The Normal Behavior Model (NBM) predicts expected temperatures based on operational conditions (wind speed, power, RPM). The residual is the difference between predicted and actual temperature. High residuals indicate potential faults.

## Asset Health Index
Calculated iteratively based on moving averages of NBM residuals. An index from 0 to 100, where 100 is perfectly healthy.

## Financial Loss Estimator
Estimated financial impact of potential downtime or catastrophic failure based on current asset health, probability of failure, and emergency replacement costs vs preventive maintenance costs.

## Priority Score
Ranks assets for maintenance based on a combination of Health Index, Financial Loss Estimate, and production criticality.
