**NOTE: FOR MORE STATS, USE LATEST MODEL EVALUATION FILE!!**



Fetching and formatting data arrays...



Validation experiments on ordinary weeks (training data only)...



&#x20; \[ordinary] 09 Jan 2012 - 15 Jan 2012   (days > 38C held out: 0, left in training: 2)

&#x20;   baseline (5 features)                WAPE  10.6% | MAE 0.034 | R2  0.599 | peak bias -0.009 kW

&#x20;   + temp history                       WAPE   8.3% | MAE 0.026 | R2  0.764 | peak bias -0.004 kW

&#x20;   + min temp                           WAPE   6.3% | MAE 0.020 | R2  0.863 | peak bias -0.013 kW

&#x20;   + holiday flag                       WAPE   7.9% | MAE 0.025 | R2  0.791 | peak bias -0.011 kW

&#x20;   + previous-day load                  WAPE   7.3% | MAE 0.023 | R2  0.820 | peak bias -0.008 kW

&#x20;   all (10 features)                    WAPE   6.2% | MAE 0.020 | R2  0.861 | peak bias +0.003 kW

&#x20;   all minus previous-day load          WAPE   6.1% | MAE 0.019 | R2  0.877 | peak bias -0.006 kW

&#x20;   all + hot-day weights                WAPE   6.1% | MAE 0.019 | R2  0.857 | peak bias -0.011 kW

&#x20;   all minus lag + hot-day weights      WAPE   5.8% | MAE 0.018 | R2  0.882 | peak bias -0.008 kW

&#x20;   all + boosting                       WAPE   6.5% | MAE 0.020 | R2  0.841 | peak bias +0.003 kW

&#x20;   all minus lag + boosting             WAPE   6.3% | MAE 0.020 | R2  0.863 | peak bias +0.000 kW

&#x20;   all minus lag + boosting + weights   WAPE   6.6% | MAE 0.021 | R2  0.850 | peak bias +0.004 kW



&#x20; \[ordinary] 06 Feb 2012 - 12 Feb 2012   (days > 38C held out: 0, left in training: 2)

&#x20;   baseline (5 features)                WAPE   6.3% | MAE 0.020 | R2  0.867 | peak bias -0.039 kW

&#x20;   + temp history                       WAPE   5.9% | MAE 0.019 | R2  0.884 | peak bias -0.036 kW

&#x20;   + min temp                           WAPE   6.2% | MAE 0.020 | R2  0.867 | peak bias -0.040 kW

&#x20;   + holiday flag                       WAPE   6.3% | MAE 0.020 | R2  0.867 | peak bias -0.039 kW

&#x20;   + previous-day load                  WAPE   5.0% | MAE 0.016 | R2  0.916 | peak bias -0.027 kW

&#x20;   all (10 features)                    WAPE   4.9% | MAE 0.016 | R2  0.921 | peak bias -0.025 kW

&#x20;   all minus previous-day load          WAPE   5.7% | MAE 0.018 | R2  0.894 | peak bias -0.031 kW

&#x20;   all + hot-day weights                WAPE   5.0% | MAE 0.016 | R2  0.918 | peak bias -0.024 kW

&#x20;   all minus lag + hot-day weights      WAPE   5.8% | MAE 0.019 | R2  0.892 | peak bias -0.031 kW

&#x20;   all + boosting                       WAPE   4.9% | MAE 0.016 | R2  0.918 | peak bias -0.025 kW

&#x20;   all minus lag + boosting             WAPE   5.3% | MAE 0.017 | R2  0.901 | peak bias -0.033 kW

&#x20;   all minus lag + boosting + weights   WAPE   5.4% | MAE 0.018 | R2  0.900 | peak bias -0.032 kW



&#x20; Average WAPE over the ordinary windows (lower is better):

&#x20;   all (10 features)                      5.5%

&#x20;   all + hot-day weights                  5.6%

&#x20;   all + boosting                         5.7%

&#x20;   all minus lag + hot-day weights        5.8%

&#x20;   all minus lag + boosting               5.8%

&#x20;   all minus previous-day load            5.9%

&#x20;   all minus lag + boosting + weights     6.0%

&#x20;   + previous-day load                    6.1%

&#x20;   + min temp                             6.3%

&#x20;   + holiday flag                         7.1%

&#x20;   + temp history                         7.1%

&#x20;   baseline (5 features)                  8.5%



Validation experiments on HOT windows (training data only)...



&#x20; \[hot] 28 Nov 2012 - 04 Dec 2012   (days > 38C held out: 1, left in training: 1)

&#x20;   baseline (5 features)                WAPE   9.1% | MAE 0.033 | R2  0.861 | peak bias -0.078 kW

&#x20;   + temp history                       WAPE   8.8% | MAE 0.032 | R2  0.894 | peak bias -0.018 kW

&#x20;   + min temp                           WAPE   8.4% | MAE 0.031 | R2  0.884 | peak bias -0.055 kW

&#x20;   + holiday flag                       WAPE   9.2% | MAE 0.034 | R2  0.853 | peak bias -0.082 kW

&#x20;   + previous-day load                  WAPE  11.1% | MAE 0.041 | R2  0.737 | peak bias -0.064 kW

&#x20;   all (10 features)                    WAPE  11.3% | MAE 0.042 | R2  0.702 | peak bias -0.075 kW

&#x20;   all minus previous-day load          WAPE   7.7% | MAE 0.028 | R2  0.908 | peak bias -0.008 kW

&#x20;   all + hot-day weights                WAPE   9.0% | MAE 0.033 | R2  0.860 | peak bias -0.001 kW

&#x20;   all minus lag + hot-day weights      WAPE   8.4% | MAE 0.031 | R2  0.887 | peak bias -0.050 kW

&#x20;   all + boosting                       WAPE  10.3% | MAE 0.038 | R2  0.768 | peak bias -0.058 kW

&#x20;   all minus lag + boosting             WAPE   7.1% | MAE 0.026 | R2  0.914 | peak bias -0.043 kW

&#x20;   all minus lag + boosting + weights   WAPE   9.5% | MAE 0.035 | R2  0.844 | peak bias +0.041 kW



&#x20; \[hot] 16 Jan 2013 - 22 Jan 2013   (days > 38C held out: 1, left in training: 1)

&#x20;   baseline (5 features)                WAPE  17.2% | MAE 0.065 | R2  0.598 | peak bias -0.239 kW

&#x20;   + temp history                       WAPE  14.8% | MAE 0.056 | R2  0.634 | peak bias -0.248 kW

&#x20;   + min temp                           WAPE  14.0% | MAE 0.053 | R2  0.670 | peak bias -0.245 kW

&#x20;   + holiday flag                       WAPE  17.4% | MAE 0.066 | R2  0.597 | peak bias -0.240 kW

&#x20;   + previous-day load                  WAPE  13.8% | MAE 0.053 | R2  0.662 | peak bias -0.240 kW

&#x20;   all (10 features)                    WAPE  15.0% | MAE 0.057 | R2  0.595 | peak bias -0.262 kW

&#x20;   all minus previous-day load          WAPE  13.4% | MAE 0.051 | R2  0.658 | peak bias -0.255 kW

&#x20;   all + hot-day weights                WAPE  14.0% | MAE 0.053 | R2  0.637 | peak bias -0.259 kW

&#x20;   all minus lag + hot-day weights      WAPE  12.3% | MAE 0.047 | R2  0.709 | peak bias -0.237 kW

&#x20;   all + boosting                       WAPE  12.8% | MAE 0.049 | R2  0.716 | peak bias -0.232 kW

&#x20;   all minus lag + boosting             WAPE  13.2% | MAE 0.050 | R2  0.693 | peak bias -0.240 kW

&#x20;   all minus lag + boosting + weights   WAPE  13.3% | MAE 0.051 | R2  0.695 | peak bias -0.232 kW



&#x20; Average WAPE over the hot windows (lower is better):

&#x20;   all minus lag + boosting              10.1%

&#x20;   all minus lag + hot-day weights       10.4%

&#x20;   all minus previous-day load           10.6%

&#x20;   + min temp                            11.2%

&#x20;   all minus lag + boosting + weights    11.4%

&#x20;   all + hot-day weights                 11.5%

&#x20;   all + boosting                        11.6%

&#x20;   + temp history                        11.8%

&#x20;   + previous-day load                   12.5%

&#x20;   all (10 features)                     13.1%

&#x20;   baseline (5 features)                 13.1%

&#x20;   + holiday flag                        13.3%



Pick the recipe that does well on BOTH groups, then set the switches in CHANGE 12 below.



Final load model: hgb | 8 features | hot-day weighting: False | Drop holiday dates: True | Drop load lag: True | Drop 3d mean: False | Drop prev day max temp: False

Training Random Forest Regressors (using all CPU cores)...

&#x20; Load Model training completed successfully.

&#x20; PV Model training completed successfully.

Executing forecasts across the evaluation timeline...

Freezing models and writing compressed .pkl binaries...



=================== FINAL EVALUATION RESULTS ===================

Target Holdout Week: Jan 7 - Jan 13, 2013

Aggregate Pool Scaling Factor: 1 houses



\[LOAD MODEL] MAE: 0.07 kW | R2 Score: 0.665

\[PV MODEL]   MAE: 0.02 kW | R2 Score: 0.928

=================================================================





\--- LOAD: detailed metrics ---

&#x20; Whole week        : MAE 0.072 kW | RMSE 0.124 | WAPE 17.1% | MAPE(actual>0.01) 13.1% | R2 0.665

&#x20; Excluding Tue 08 Jan: MAE 0.054 kW | RMSE 0.088 | WAPE 14.1% | MAPE(actual>0.01) 11.6% | R2 0.593

&#x20; Per day:

&#x20;   Mon 07 Jan: MAE 0.020 kW | WAPE 5.7% | MAPE 6.1%

&#x20;   Tue 08 Jan: MAE 0.182 kW | WAPE 27.3% | MAPE 22.1%

&#x20;   Wed 09 Jan: MAE 0.061 kW | WAPE 16.4% | MAPE 13.8%

&#x20;   Thu 10 Jan: MAE 0.018 kW | WAPE 6.1% | MAPE 6.0%

&#x20;   Fri 11 Jan: MAE 0.081 kW | WAPE 18.3% | MAPE 14.8%

&#x20;   Sat 12 Jan: MAE 0.124 kW | WAPE 25.5% | MAPE 23.6%

&#x20;   Sun 13 Jan: MAE 0.018 kW | WAPE 5.3% | MAPE 5.5%



\--- PV: detailed metrics ---

&#x20; Whole week        : MAE 0.023 kW | RMSE 0.048 | WAPE 17.4% | MAPE(actual>0.05) 20.0% | R2 0.928

&#x20; Per day:

&#x20;   Mon 07 Jan: MAE 0.012 kW | WAPE 6.8% | MAPE 7.8%

&#x20;   Tue 08 Jan: MAE 0.016 kW | WAPE 9.2% | MAPE 11.3%

&#x20;   Wed 09 Jan: MAE 0.055 kW | WAPE 42.0% | MAPE 37.3%

&#x20;   Thu 10 Jan: MAE 0.012 kW | WAPE 15.0% | MAPE 16.0%

&#x20;   Fri 11 Jan: MAE 0.010 kW | WAPE 5.3% | MAPE 5.3%

&#x20;   Sat 12 Jan: MAE 0.039 kW | WAPE 35.7% | MAPE 41.8%

&#x20;   Sun 13 Jan: MAE 0.019 kW | WAPE 26.7% | MAPE 21.8%

Exporting baseline forecasts to CSV archive...

&#x20; Saved successfully as './Code\_and\_Data/average\_household\_forecasts\_v3.csv'.

Plotting predicted vs actual (load and PV)...

&#x20; Rendering plot windows, close them to end code execution :)



