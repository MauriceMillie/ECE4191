%% ECE4191 Module 3 - Experiment 3 Node 646 MPC-CIL plots
% Generates the two useful Node 646 plots for the Experiment 3 assessment:
%
%   1) Node 646-B battery command vs simulated time
%      Positive = discharge, negative = charge
%
%   2) Predicted vs measured Node 646 battery SoC
%
% It also calculates:
%   - mean absolute SoC error (MAE)
%   - SoC RMSE
%   - maximum absolute SoC error
%   - final SoC error
%
% Expected controller log:
%   mpc_cil_node646_schedule_20260911_173110.csv
%
% Output:
%   Experiment3_Assessment_Output_Final
%
% The CSV contains 192 half-hour steps = 4 simulated days.

clear;
clc;
close all;

%% ========================================================================
% SETTINGS
% ========================================================================

INPUT_FILE = "mpc_cil_node646_schedule_20260911_173110.csv";
OUTPUT_FOLDER = "Experiment3_Assessment_Output_Final";

SIM_HOURS_PER_STEP = 0.5;
N_EXPECTED_STEPS = 192;

SAVE_PNG = true;
SAVE_FIG = true;

%% ========================================================================
% LOCATE FILE
% ========================================================================

scriptPath = mfilename("fullpath");

if strlength(scriptPath) == 0
    dataDir = pwd;
else
    dataDir = fileparts(scriptPath);
end

inputPath = fullfile(dataDir, INPUT_FILE);
outputDir = fullfile(dataDir, OUTPUT_FOLDER);

assert(isfile(inputPath), ...
    "Could not find the E3 MPC-CIL log:\n%s", inputPath);

if ~isfolder(outputDir)
    mkdir(outputDir);
end

fprintf("============================================================\n");
fprintf(" ECE4191 EXPERIMENT 3 - NODE 646 MPC-CIL ANALYSIS\n");
fprintf("============================================================\n");
fprintf("Input : %s\n", inputPath);
fprintf("Output: %s\n\n", outputDir);

%% ========================================================================
% LOAD DATA
% ========================================================================

T = readtable(inputPath, ...
    "VariableNamingRule", "preserve", ...
    "TextType", "string");

requiredColumns = [
    "step"
    "battery_646_kw"
    "battery_action"
    "soc_predicted_pct"
    "soc_measured_pct"
];

missingColumns = requiredColumns( ...
    ~ismember(requiredColumns, string(T.Properties.VariableNames)));

assert(isempty(missingColumns), ...
    "Input CSV is missing required column(s): %s", ...
    strjoin(missingColumns, ", "));

if height(T) ~= N_EXPECTED_STEPS
    warning( ...
        "Expected %d rows for 4 days, but found %d.", ...
        N_EXPECTED_STEPS, height(T));
end

step = double(T.("step"));
simHour = step .* SIM_HOURS_PER_STEP;

batteryKW = double(T.("battery_646_kw"));
batteryAction = string(T.("battery_action"));

socPredicted = double(T.("soc_predicted_pct"));
socMeasured = double(T.("soc_measured_pct"));

%% ========================================================================
% SANITY CHECKS
% ========================================================================

assert(all(isfinite(batteryKW)), ...
    "battery_646_kw contains non-finite values.");

assert(all(isfinite(socPredicted)), ...
    "soc_predicted_pct contains non-finite values.");

assert(all(isfinite(socMeasured)), ...
    "soc_measured_pct contains non-finite values.");

% Verify the text action agrees with the sign of the battery command.
expectedAction = strings(height(T),1);

expectedAction(batteryKW > 0.5) = "Discharge";
expectedAction(batteryKW < -0.5) = "Charge";
expectedAction(abs(batteryKW) <= 0.5) = "Idle";

actionMismatch = ~strcmpi(expectedAction, batteryAction);

if any(actionMismatch)
    warning( ...
        "%d battery_action entries do not match battery_646_kw sign.", ...
        sum(actionMismatch));
end

%% ========================================================================
% SOC ERROR METRICS
% ========================================================================

socError = socMeasured - socPredicted;

socMAE = mean(abs(socError), "omitnan");
socRMSE = sqrt(mean(socError.^2, "omitnan"));
socMaxAbs = max(abs(socError));
socFinalError = socError(end);

[~, maxErrorIdx] = max(abs(socError));
maxErrorHour = simHour(maxErrorIdx);

fprintf("Node 646-B battery command range:\n");
fprintf("  Minimum: %.3f kW\n", min(batteryKW));
fprintf("  Maximum: %.3f kW\n\n", max(batteryKW));

fprintf("Node 646 SoC tracking:\n");
fprintf("  MAE                 : %.3f percentage points\n", socMAE);
fprintf("  RMSE                : %.3f percentage points\n", socRMSE);
fprintf("  Maximum absolute err: %.3f percentage points at %.2f h\n", ...
    socMaxAbs, maxErrorHour);
fprintf("  Final error         : %.3f percentage points\n\n", socFinalError);

%% ========================================================================
% FIGURE 1 - NODE 646-B BATTERY COMMAND
% ========================================================================

fig1 = figure( ...
    "Name", "Experiment 3 - Node 646-B battery command", ...
    "Color", "w", ...
    "Position", [100 100 1250 650]);

plot(simHour, batteryKW, ...
    "LineWidth", 1.5, ...
    "DisplayName", "Node 646-B battery command");

hold on;

yline(0, "-", ...
    "0 kW", ...
    "HandleVisibility", "off");

addDaySeparators(gca, 4);

hold off;
grid on;
box on;

xlabel("Simulated time (hours)");
ylabel("Battery power command (kW)");
title("Experiment 3 (MPC-CIL): Node 646-B Battery Command");
subtitle("Positive = discharge; negative = charge");

xlim([0 96]);

legend("Location", "best");

saveAssessmentFigure( ...
    fig1, outputDir, ...
    "05A_Exp3_Node646_Battery_Command", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 2 - PREDICTED VS MEASURED NODE 646 SOC
% ========================================================================

fig2 = figure( ...
    "Name", "Experiment 3 - Node 646 SoC comparison", ...
    "Color", "w", ...
    "Position", [120 120 1250 650]);

plot(simHour, socPredicted, ...
    "--", ...
    "LineWidth", 1.4, ...
    "DisplayName", "MPC predicted SoC");

hold on;

plot(simHour, socMeasured, ...
    "LineWidth", 1.7, ...
    "DisplayName", "Measured Typhoon SoC");

yline(0, ":", "HandleVisibility", "off");
yline(100, ":", "HandleVisibility", "off");

addDaySeparators(gca, 4);

hold off;
grid on;
box on;

xlabel("Simulated time (hours)");
ylabel("Battery State of Charge (%)");
title("Experiment 3 (MPC-CIL): Node 646 Predicted vs Measured SoC");

subtitle(sprintf( ...
    "MAE = %.2f pp | RMSE = %.2f pp | Max |error| = %.2f pp", ...
    socMAE, socRMSE, socMaxAbs));

xlim([0 96]);
ylim([-2 102]);

legend("Location", "best");

saveAssessmentFigure( ...
    fig2, outputDir, ...
    "05B_Exp3_Node646_Predicted_vs_Measured_SoC", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% OPTIONAL FIGURE 3 - SOC ERROR
% ========================================================================

fig3 = figure( ...
    "Name", "Experiment 3 - Node 646 SoC error", ...
    "Color", "w", ...
    "Position", [140 140 1250 620]);

plot(simHour, socError, ...
    "LineWidth", 1.4);

hold on;

yline(0, "-", ...
    "0 pp", ...
    "HandleVisibility", "off");

addDaySeparators(gca, 4);

hold off;
grid on;
box on;

xlabel("Simulated time (hours)");
ylabel("Measured - predicted SoC (percentage points)");
title("Experiment 3 (MPC-CIL): Node 646 SoC Tracking Error");

subtitle(sprintf( ...
    "MAE = %.2f pp | RMSE = %.2f pp | Max |error| = %.2f pp", ...
    socMAE, socRMSE, socMaxAbs));

xlim([0 96]);

saveAssessmentFigure( ...
    fig3, outputDir, ...
    "05C_Exp3_Node646_SoC_Error", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% EXPORT SUPPORT TABLES
% ========================================================================

plotData = table( ...
    step, ...
    simHour, ...
    batteryKW, ...
    batteryAction, ...
    socPredicted, ...
    socMeasured, ...
    socError, ...
    'VariableNames', { ...
    'Step', ...
    'SimHour', ...
    'Battery646_kW', ...
    'BatteryAction', ...
    'SoC_Predicted_pct', ...
    'SoC_Measured_pct', ...
    'SoC_Error_pctPoint'});

writetable(plotData, ...
    fullfile(outputDir, ...
    "Experiment3_Node646_ControllerPlotData.csv"));

summaryTable = table( ...
    min(batteryKW), ...
    max(batteryKW), ...
    socMAE, ...
    socRMSE, ...
    socMaxAbs, ...
    maxErrorHour, ...
    socFinalError, ...
    'VariableNames', { ...
    'MinBatteryCommand_kW', ...
    'MaxBatteryCommand_kW', ...
    'SoC_MAE_pctPoint', ...
    'SoC_RMSE_pctPoint', ...
    'SoC_MaxAbsError_pctPoint', ...
    'SoC_MaxErrorSimHour', ...
    'SoC_FinalError_pctPoint'});

writetable(summaryTable, ...
    fullfile(outputDir, ...
    "Experiment3_Node646_ControllerSummary.csv"));

%% ========================================================================
% SIMPLE ORAL-ASSESSMENT SUMMARY
% ========================================================================

fprintf("============================================================\n");
fprintf(" E3 NODE 646 ORAL-ASSESSMENT SUMMARY\n");
fprintf("============================================================\n");

fprintf("Q1 - Battery behaviour:\n");
fprintf("  Node 646-B command ranges from %.2f kW (charging)\n", ...
    min(batteryKW));
fprintf("  to %.2f kW (discharging).\n", max(batteryKW));
fprintf("  Positive command = discharge; negative command = charge.\n\n");

fprintf("Q2 - SoC model error:\n");
fprintf("  Mean absolute SoC error = %.3f percentage points.\n", socMAE);
fprintf("  SoC RMSE                = %.3f percentage points.\n", socRMSE);
fprintf("  Maximum absolute error  = %.3f percentage points.\n", socMaxAbs);
fprintf("  Final SoC error         = %.3f percentage points.\n\n", socFinalError);

fprintf("Generated plots:\n");
fprintf("  05A_Exp3_Node646_Battery_Command.png\n");
fprintf("  05B_Exp3_Node646_Predicted_vs_Measured_SoC.png\n");
fprintf("  05C_Exp3_Node646_SoC_Error.png\n");
fprintf("\nOutput folder:\n  %s\n", outputDir);
fprintf("============================================================\n");

%% ========================================================================
% LOCAL FUNCTIONS
% ========================================================================

function addDaySeparators(ax, nDays)

    for d = 1:(nDays - 1)

        xline(ax, 24*d, ":", ...
            "HandleVisibility", "off");
    end
end


function saveAssessmentFigure( ...
    fig, outputDir, baseName, savePng, saveFig)

    if savePng

        exportgraphics( ...
            fig, ...
            fullfile(outputDir, baseName + ".png"), ...
            "Resolution", 300);
    end

    if saveFig

        savefig( ...
            fig, ...
            fullfile(outputDir, baseName + ".fig"));
    end
end
