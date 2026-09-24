%% ECE4191 Module 3 - Experiment 2 (MPC)
% EXACT-DATA / HEADER-SAFE ASSESSMENT PLOTTING SCRIPT
%
% Built for the Experiment 2 files:
%
%   measured_rmsVoltages1.csv
%   measured_rmsVoltages2.csv
%   measured_rmsVoltages3.csv
%   measuredPower1.csv
%   measuredPower2.csv
%   mpc_feeder_schedule_20260911_171853.csv
%   node632_probe1.csv
%   Node634_rmsVoltages.csv
%
% NOTE: The file names intentionally DO NOT contain "(1)".
%
% This script produces the five required Experiment 2 plots:
%   1. Measured feeder active power at Node 632
%   2. Measured active power at all time-varying node-phases
%   3. Node 634 RMS voltages A/B/C with +/-5% limits
%   4. RMS voltages at all other monitored nodes with +/-5% limits
%   5. Measured Node 646 battery SoC
%
% It also calculates the data needed for ALL Experiment 2 oral questions:
%   Q1-Q3   Voltage violations, timing, worst case
%   Q4-Q6   Reverse active-power flow, timing, largest reverse flow
%   Q7-Q9   Feeder peak time, magnitude, measurement method
%   Q10     Node contributions to feeder peak
%   Q11     Peak-load voltage behaviour; optional automatic QP comparison
%   Q12     QP-vs-MPC voltage comparison if Experiment 1 output is present
%
% Experiment 2 runs for four simulated days:
%       192 half-hour steps
%       2 real seconds per half-hour step
%       384 real seconds total
%
% IMPORTANT:
% If Signal Analyzer started before the Raspberry Pi playback, change
% PLAYBACK_START_REAL_S below. The default assumes both started together.
%
% For Q1, Q10 and Q11 the assessment also asks for comparison with Module 1.
% Module 1 data was not supplied with this Experiment 2 dataset, so this
% script calculates all Experiment 2 quantities and clearly flags the
% remaining Module 1 comparison requirement.
%
% If the folder:
%       Experiment1_Assessment_Output_Final
% exists beside this script, Q11/Q12 automatically compare QP and MPC.

clear;
clc;
close all;

%% ========================================================================
% USER SETTINGS
% ========================================================================

PLAYBACK_START_REAL_S = 0.0;

REAL_SECONDS_PER_STEP = 2.0;
SIM_HOURS_PER_STEP = 0.5;

N_PLAYBACK_STEPS = 192;
PLAYBACK_DURATION_REAL_S = N_PLAYBACK_STEPS * REAL_SECONDS_PER_STEP;
PLAYBACK_END_REAL_S = PLAYBACK_START_REAL_S + PLAYBACK_DURATION_REAL_S;

% Assessment voltage limits.
NOMINAL_634_V = 277.0;
NOMINAL_OTHER_V = 2401.0;

LOWER_634_V = 0.95 * NOMINAL_634_V;       % 263.15 V
UPPER_634_V = 1.05 * NOMINAL_634_V;       % 290.85 V

LOWER_OTHER_V = 0.95 * NOMINAL_OTHER_V;   % 2280.95 V
UPPER_OTHER_V = 1.05 * NOMINAL_OTHER_V;   % 2521.05 V

SAVE_PNG = true;
SAVE_FIG = true;

OUTPUT_FOLDER = "Experiment2_Assessment_Output_Final";

% Optional Experiment 1 output for Q11/Q12.
EXP1_OUTPUT_FOLDER = "Experiment1_Assessment_Output_Final";

FONT_SIZE = 10;
LINE_WIDTH = 1.25;
LIMIT_LINE_WIDTH = 1.15;

%% ========================================================================
% INPUT FILES - NO "(1)" IN FILE NAMES
% ========================================================================

SCHEDULE_FILE = "mpc_feeder_schedule_20260911_171853.csv";

POWER_FILE_1 = "measuredPower1.csv";
POWER_FILE_2 = "measuredPower2.csv";

FEEDER_POWER_FILE = "node632_probe1.csv";

NODE634_VOLTAGE_FILE = "Node634_rmsVoltages.csv";

RMS_VOLTAGE_FILE_1 = "measured_rmsVoltages1.csv";
RMS_VOLTAGE_FILE_2 = "measured_rmsVoltages2.csv";
RMS_VOLTAGE_FILE_3 = "measured_rmsVoltages3.csv";

%% ========================================================================
% DATA DIRECTORY / OUTPUT DIRECTORY
% ========================================================================

scriptPath = mfilename("fullpath");

if strlength(scriptPath) == 0
    dataDir = pwd;
else
    dataDir = fileparts(scriptPath);
end

outputDir = fullfile(dataDir, OUTPUT_FOLDER);

if ~isfolder(outputDir)
    mkdir(outputDir);
end

schedulePath = fullfile(dataDir, SCHEDULE_FILE);
powerPath1 = fullfile(dataDir, POWER_FILE_1);
powerPath2 = fullfile(dataDir, POWER_FILE_2);
feederPath = fullfile(dataDir, FEEDER_POWER_FILE);
node634VoltagePath = fullfile(dataDir, NODE634_VOLTAGE_FILE);
voltagePath1 = fullfile(dataDir, RMS_VOLTAGE_FILE_1);
voltagePath2 = fullfile(dataDir, RMS_VOLTAGE_FILE_2);
voltagePath3 = fullfile(dataDir, RMS_VOLTAGE_FILE_3);

requiredFiles = [
    string(schedulePath)
    string(powerPath1)
    string(powerPath2)
    string(feederPath)
    string(node634VoltagePath)
    string(voltagePath1)
    string(voltagePath2)
    string(voltagePath3)
];

for k = 1:numel(requiredFiles)
    assert(isfile(requiredFiles(k)), ...
        "Required file not found:\n%s", requiredFiles(k));
end

fprintf("============================================================\n");
fprintf(" ECE4191 MODULE 3 - EXPERIMENT 2 (MPC)\n");
fprintf(" EXACT-DATA / HEADER-SAFE ASSESSMENT ANALYSIS - FPRINTF FIXED\n");
fprintf("============================================================\n");
fprintf("Playback window : %.2f to %.2f real seconds\n", ...
    PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
fprintf("Simulated period: 0 to %.1f hours (4 days)\n", ...
    N_PLAYBACK_STEPS * SIM_HOURS_PER_STEP);
fprintf("Output folder   : %s\n\n", outputDir);

%% ========================================================================
% LOAD MPC SCHEDULE
% ========================================================================

S = readtable(schedulePath, ...
    "VariableNamingRule", "preserve");

requiredScheduleColumns = [
    "step"
    "day"
    "k"
    "p_load_fc_kw"
    "p_pv_fc_kw"
    "p_load_total_actual_kw"
    "p_pv_total_actual_kw"
    "baseline_grid_kw"
    "battery_agg_kw"
    "battery_action"
    "grid_kw"
    "grid_forecast_kw"
    "soc_predicted_pct"
    "soc_measured_646_pct"
    "mpc_status"
];

assert(all(ismember(requiredScheduleColumns, ...
    string(S.Properties.VariableNames))), ...
    "The MPC schedule CSV is missing one or more expected columns.");

assert(height(S) >= N_PLAYBACK_STEPS, ...
    "Expected at least %d MPC schedule rows; found %d.", ...
    N_PLAYBACK_STEPS, height(S));

S = S(1:N_PLAYBACK_STEPS, :);

% Schedule values are interval-ending quantities.
scheduleSimHour = double(S.("step")) * SIM_HOURS_PER_STEP;

fprintf("MPC schedule rows: %d\n", height(S));
fprintf("Measured Node 646 SoC range: %.2f%% to %.2f%%\n\n", ...
    min(double(S.("soc_measured_646_pct"))), ...
    max(double(S.("soc_measured_646_pct"))));

%% ========================================================================
% LOAD ACTIVE-POWER DATA
% ========================================================================

P1 = readTyphoonCsv(powerPath1);
P2 = readTyphoonCsv(powerPath2);
PF = readTyphoonCsv(feederPath);

P1 = cropRealTime(P1, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
P2 = cropRealTime(P2, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
PF = cropRealTime(PF, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);

% HEADER-SAFE MAPPING
% -------------------
% Long Typhoon Signal Analyzer headers can be truncated or modified by
% MATLAB. The uploaded Experiment 2 files have the following verified
% column order, so numeric column positions are used instead.
%
% measuredPower1.csv
%   1 Time
%   2 611-C
%   3 634-A
%   4 634-B
%   5 634-C
%   6 645-B
%   7 646-B
%   8 652-A
%   9 692-C
%
% measuredPower2.csv
%   1 Time
%   2 671-A
%   3 675-B
%   4 671-B
%   5 671-C
%   6 675-A
%   7 675-C

powerMap = {
    "N611_C", 1, 2;
    "N634_A", 1, 3;
    "N634_B", 1, 4;
    "N634_C", 1, 5;
    "N645_B", 1, 6;
    "N646_B", 1, 7;
    "N652_A", 1, 8;
    "N692_C", 1, 9;
    "N671_A", 2, 2;
    "N675_B", 2, 3;
    "N671_B", 2, 4;
    "N671_C", 2, 5;
    "N675_A", 2, 6;
    "N675_C", 2, 7
};

powerSeries = struct();

for k = 1:size(powerMap,1)

    field = string(powerMap{k,1});
    sourceNumber = powerMap{k,2};
    columnIndex = powerMap{k,3};

    if sourceNumber == 1
        T = P1;
    else
        T = P2;
    end

    assert(width(T) >= columnIndex, ...
        "Power CSV %d has only %d columns; expected column %d for %s.", ...
        sourceNumber, width(T), columnIndex, field);

    powerSeries.(char(field)).realTime = double(T.("Time"));
    powerSeries.(char(field)).simHour = realToSimHour( ...
        double(T.("Time")), PLAYBACK_START_REAL_S, ...
        REAL_SECONDS_PER_STEP, SIM_HOURS_PER_STEP);

    % Typhoon P_measured values are in watts.
    powerSeries.(char(field)).kW = double(T{:,columnIndex}) / 1000.0;

    % Diagnostics only.
    powerSeries.(char(field)).sourceColumn = ...
        string(T.Properties.VariableNames{columnIndex});
end

powerFields = string(fieldnames(powerSeries));

% Feeder-head power.
assert(ismember("Node 632.Probe1", ...
    string(PF.Properties.VariableNames)), ...
    "Node 632.Probe1 was not found in node632_probe1.csv.");

feederRealTime = double(PF.("Time"));
feederSimHour = realToSimHour( ...
    feederRealTime, PLAYBACK_START_REAL_S, ...
    REAL_SECONDS_PER_STEP, SIM_HOURS_PER_STEP);

feederKW = double(PF.("Node 632.Probe1")) / 1000.0;

%% ========================================================================
% LOAD RMS-VOLTAGE DATA
% ========================================================================

V634 = readTyphoonCsv(node634VoltagePath);
V1 = readTyphoonCsv(voltagePath1);
V2 = readTyphoonCsv(voltagePath2);
V3 = readTyphoonCsv(voltagePath3);

V634 = cropRealTime(V634, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
V1 = cropRealTime(V1, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
V2 = cropRealTime(V2, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
V3 = cropRealTime(V3, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);

voltageTables = {V634, V1, V2, V3};
voltageSeries = struct();

for t = 1:numel(voltageTables)

    T = voltageTables{t};
    names = string(T.Properties.VariableNames);

    for k = 1:numel(names)

        name = names(k);

        % Ignore exported bounds; calculate exact assessment bounds ourselves.
        if name == "Time" || ...
                contains(lower(name), "upperbound") || ...
                contains(lower(name), "lowerbound")
            continue;
        end

        token = regexp(char(name), ...
            '^Node\s+(\d+)\.V([123])_rms$', ...
            'tokens', 'once');

        if isempty(token)
            continue;
        end

        node = string(token{1});
        phaseIndex = str2double(token{2});
        phaseChars = 'ABC';
        phase = string(phaseChars(phaseIndex));

        field = "N" + node + "_" + phase;

        if isfield(voltageSeries, char(field))
            continue;
        end

        voltageSeries.(char(field)).node = node;
        voltageSeries.(char(field)).phase = phase;
        voltageSeries.(char(field)).realTime = double(T.("Time"));
        voltageSeries.(char(field)).simHour = realToSimHour( ...
            double(T.("Time")), PLAYBACK_START_REAL_S, ...
            REAL_SECONDS_PER_STEP, SIM_HOURS_PER_STEP);

        voltageSeries.(char(field)).V = double(T.(char(name)));
        voltageSeries.(char(field)).sourceColumn = name;

        if node == "634"
            voltageSeries.(char(field)).nominalV = NOMINAL_634_V;
            voltageSeries.(char(field)).lowerV = LOWER_634_V;
            voltageSeries.(char(field)).upperV = UPPER_634_V;
        else
            voltageSeries.(char(field)).nominalV = NOMINAL_OTHER_V;
            voltageSeries.(char(field)).lowerV = LOWER_OTHER_V;
            voltageSeries.(char(field)).upperV = UPPER_OTHER_V;
        end
    end
end

voltageFields = string(fieldnames(voltageSeries));

fprintf("Loaded %d active-power channels.\n", numel(powerFields));
fprintf("Loaded %d RMS-voltage channels.\n\n", numel(voltageFields));

%% ========================================================================
% REQUIRED FIGURE 1 - NODE 632 FEEDER ACTIVE POWER
% ========================================================================

[peakFeederKW, peakIdx] = max(feederKW);
[minFeederKW, minIdx] = min(feederKW);

peakFeederRealTime = feederRealTime(peakIdx);
peakFeederHour = feederSimHour(peakIdx);
minFeederHour = feederSimHour(minIdx);

fig1 = figure( ...
    "Name", "Experiment 2 - Node 632 feeder active power", ...
    "Color", "w", ...
    "Position", [80 80 1250 650]);

plot(feederSimHour, feederKW, ...
    "LineWidth", 1.6, ...
    "DisplayName", "Measured Node 632 feeder power");

hold on;

yline(0, "-", ...
    "0 kW", ...
    "HandleVisibility", "off");

plot(peakFeederHour, peakFeederKW, "o", ...
    "MarkerSize", 8, ...
    "LineWidth", 1.4, ...
    "DisplayName", sprintf("Peak %.1f kW", peakFeederKW));

plot(minFeederHour, minFeederKW, "s", ...
    "MarkerSize", 8, ...
    "LineWidth", 1.4, ...
    "DisplayName", sprintf("Minimum %.1f kW", minFeederKW));

addDaySeparators(gca, 4);

hold off;
grid on;
box on;

xlabel("Simulated time (hours)");
ylabel("Measured feeder active power (kW)");
title("Experiment 2 (MPC): Measured Feeder Active Power at Node 632");
subtitle(sprintf("Peak %.1f kW | Minimum %.1f kW", ...
    peakFeederKW, minFeederKW));

xlim([0 96]);
legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig1, outputDir, ...
    "01_Exp2_Node632_Feeder_Active_Power", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 2 - ALL TIME-VARYING NODE-PHASE ACTIVE POWERS
% ========================================================================

fig2 = figure( ...
    "Name", "Experiment 2 - node-phase active powers", ...
    "Color", "w", ...
    "Position", [20 20 1700 950]);

tl2 = tiledlayout(4,4, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl2, ...
    "Experiment 2 (MPC): Measured Active Power at Time-Varying Node-Phases", ...
    "FontWeight", "bold");

for k = 1:numel(powerFields)

    field = powerFields(k);
    s = powerSeries.(char(field));

    nexttile;

    plot(s.simHour, s.kW, ...
        "LineWidth", LINE_WIDTH);

    hold on;
    yline(0, "-", "HandleVisibility", "off");
    addDaySeparators(gca, 4);
    hold off;

    grid on;
    box on;

    title(powerFieldLabel(field));
    ylabel("kW");
    xlim([0 96]);

    set(gca, "FontSize", 8);
end

xlabel(tl2, "Simulated time (hours)");

saveAssessmentFigure(fig2, outputDir, ...
    "02_Exp2_All_TimeVarying_NodePhase_Active_Powers", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 3 - NODE 634 RMS VOLTAGES
% ========================================================================

node634Fields = voltageFields(startsWith(voltageFields, "N634_"));

assert(numel(node634Fields) == 3, ...
    "Expected three Node 634 voltage phases; found %d.", ...
    numel(node634Fields));

fig3 = figure( ...
    "Name", "Experiment 2 - Node 634 RMS voltage", ...
    "Color", "w", ...
    "Position", [90 90 1250 650]);

hold on;

for k = 1:numel(node634Fields)

    f = node634Fields(k);
    s = voltageSeries.(char(f));

    plot(s.simHour, s.V, ...
        "LineWidth", 1.4, ...
        "DisplayName", "Phase " + s.phase);
end

yline(LOWER_634_V, "--", ...
    sprintf("-5%% limit = %.2f V", LOWER_634_V), ...
    "LineWidth", LIMIT_LINE_WIDTH, ...
    "HandleVisibility", "off");

yline(UPPER_634_V, "--", ...
    sprintf("+5%% limit = %.2f V", UPPER_634_V), ...
    "LineWidth", LIMIT_LINE_WIDTH, ...
    "HandleVisibility", "off");

addDaySeparators(gca, 4);

hold off;
grid on;
box on;

xlabel("Simulated time (hours)");
ylabel("RMS line-to-ground voltage (V)");
title("Experiment 2 (MPC): Node 634 RMS Voltages");
subtitle("Nominal = 277 V; permitted range = 263.15-290.85 V");

xlim([0 96]);
legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig3, outputDir, ...
    "03_Exp2_Node634_RMS_Voltages", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 4 - ALL OTHER MONITORED RMS VOLTAGES
% ========================================================================

otherFields = voltageFields(~startsWith(voltageFields, "N634_"));

otherNodes = strings(0);

for k = 1:numel(otherFields)
    s = voltageSeries.(char(otherFields(k)));
    otherNodes(end+1) = s.node; %#ok<SAGROW>
end

otherNodes = unique(otherNodes, "stable");

fig4 = figure( ...
    "Name", "Experiment 2 - all other monitored RMS voltages", ...
    "Color", "w", ...
    "Position", [10 10 1750 1000]);

nCols = 4;
nRows = ceil(numel(otherNodes) / nCols);

tl4 = tiledlayout(nRows, nCols, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl4, ...
    "Experiment 2 (MPC): RMS Voltages at All Other Monitored Feeder Nodes", ...
    "FontWeight", "bold");

for n = 1:numel(otherNodes)

    node = otherNodes(n);

    nexttile;
    hold on;

    fieldsThisNode = strings(0);

    for k = 1:numel(otherFields)

        f = otherFields(k);
        s = voltageSeries.(char(f));

        if s.node == node
            fieldsThisNode(end+1) = f; %#ok<SAGROW>
        end
    end

    for k = 1:numel(fieldsThisNode)

        f = fieldsThisNode(k);
        s = voltageSeries.(char(f));

        plot(s.simHour, s.V, ...
            "LineWidth", 1.0, ...
            "DisplayName", "Phase " + s.phase);
    end

    yline(LOWER_OTHER_V, "--", ...
        "LineWidth", 0.9, ...
        "HandleVisibility", "off");

    yline(UPPER_OTHER_V, "--", ...
        "LineWidth", 0.9, ...
        "HandleVisibility", "off");

    addDaySeparators(gca, 4);

    hold off;
    grid on;
    box on;

    title("Node " + node);
    ylabel("V");
    xlim([0 96]);

    legend("Location", "best", "FontSize", 7);
    set(gca, "FontSize", 8);
end

xlabel(tl4, "Simulated time (hours)");

saveAssessmentFigure(fig4, outputDir, ...
    "04_Exp2_All_Other_Monitored_RMS_Voltages", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 5 - NODE 646 MEASURED BATTERY SOC
% ========================================================================

socMeasured = double(S.("soc_measured_646_pct"));
socPredicted = double(S.("soc_predicted_pct"));

fig5 = figure( ...
    "Name", "Experiment 2 - Node 646 battery SoC", ...
    "Color", "w", ...
    "Position", [100 100 1250 650]);

plot(scheduleSimHour, socMeasured, ...
    "LineWidth", 1.7, ...
    "DisplayName", "Measured Node 646 SoC");

hold on;

plot(scheduleSimHour, socPredicted, "--", ...
    "LineWidth", 1.2, ...
    "DisplayName", "MPC predicted SoC");

yline(0, ":", "HandleVisibility", "off");
yline(100, ":", "HandleVisibility", "off");

addDaySeparators(gca, 4);

hold off;
grid on;
box on;

xlabel("Simulated time (hours)");
ylabel("Battery State of Charge (%)");
title("Experiment 2 (MPC): Node 646 Battery State of Charge");

xlim([0 96]);
ylim([-2 102]);

legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig5, outputDir, ...
    "05_Exp2_Node646_Measured_SoC", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% Q1-Q3 - VOLTAGE VIOLATIONS
% ========================================================================

voltageStats = table();
voltageIntervals = table();

for k = 1:numel(voltageFields)

    f = voltageFields(k);
    s = voltageSeries.(char(f));

    v = s.V;

    under = v < s.lowerV;
    over = v > s.upperV;
    violation = under | over;

    [minV, iMin] = min(v);
    [maxV, iMax] = max(v);

    minPU = minV / s.nominalV;
    maxPU = maxV / s.nominalV;

    underMagnitude = max(0, s.lowerV - minV);
    overMagnitude = max(0, maxV - s.upperV);

    if underMagnitude >= overMagnitude && underMagnitude > 0

        worstType = "UNDER";
        worstVoltage = minV;
        worstHour = s.simHour(iMin);
        worstLimit = s.lowerV;
        worstMagnitude = underMagnitude;

    elseif overMagnitude > 0

        worstType = "OVER";
        worstVoltage = maxV;
        worstHour = s.simHour(iMax);
        worstLimit = s.upperV;
        worstMagnitude = overMagnitude;

    else

        worstType = "NONE";
        worstVoltage = NaN;
        worstHour = NaN;
        worstLimit = NaN;
        worstMagnitude = 0;
    end

    newRow = table( ...
        s.node, ...
        s.phase, ...
        s.nominalV, ...
        minV, ...
        minPU, ...
        maxV, ...
        maxPU, ...
        any(under), ...
        any(over), ...
        worstType, ...
        worstVoltage, ...
        worstHour, ...
        string(formatSimHour(worstHour)), ...
        worstLimit, ...
        worstMagnitude, ...
        'VariableNames', { ...
        'Node','Phase','Nominal_V', ...
        'Min_V','Min_pu','Max_V','Max_pu', ...
        'UnderVoltage','OverVoltage', ...
        'WorstType','WorstVoltage_V','WorstSimHour','WorstWhen', ...
        'RelevantLimit_V','ViolationMagnitude_V'});

    voltageStats = [voltageStats; newRow]; %#ok<AGROW>

    intervals = logicalIntervals(violation);

    for q = 1:height(intervals)

        iStart = intervals.StartIndex(q);
        iEnd = intervals.EndIndex(q);

        type = "MIXED";

        if all(under(iStart:iEnd))
            type = "UNDER";
        elseif all(over(iStart:iEnd))
            type = "OVER";
        end

        startHour = s.simHour(iStart);
        endHour = s.simHour(iEnd);

        intervalRow = table( ...
            s.node, ...
            s.phase, ...
            type, ...
            startHour, ...
            endHour, ...
            string(formatSimHour(startHour)), ...
            string(formatSimHour(endHour)), ...
            'VariableNames', { ...
            'Node','Phase','Type', ...
            'StartSimHour','EndSimHour','StartWhen','EndWhen'});

        voltageIntervals = [voltageIntervals; intervalRow]; %#ok<AGROW>
    end
end

violatingStats = voltageStats( ...
    voltageStats.UnderVoltage | voltageStats.OverVoltage, :);

writetable(voltageStats, ...
    fullfile(outputDir, "Experiment2_AllVoltageStatistics.csv"));

writetable(violatingStats, ...
    fullfile(outputDir, "Experiment2_VoltageViolations.csv"));

if ~isempty(voltageIntervals)
    writetable(voltageIntervals, ...
        fullfile(outputDir, "Experiment2_VoltageViolationIntervals.csv"));
end

%% ========================================================================
% Q4-Q6 - REVERSE ACTIVE POWER FLOW
% ========================================================================

powerStats = table();
reverseIntervals = table();

for k = 1:numel(powerFields)

    field = powerFields(k);
    s = powerSeries.(char(field));

    parts = split(field, "_");
    node = erase(parts(1), "N");
    phase = parts(2);

    reverse = s.kW < 0;

    [minimumKW, iMinimum] = min(s.kW);
    [maximumKW, ~] = max(s.kW);

    if any(reverse)
        largestReverseHour = s.simHour(iMinimum);
        largestReverseWhen = string(formatSimHour(largestReverseHour));
    else
        largestReverseHour = NaN;
        largestReverseWhen = "N/A";
    end

    newRow = table( ...
        node, ...
        phase, ...
        any(reverse), ...
        minimumKW, ...
        maximumKW, ...
        largestReverseHour, ...
        largestReverseWhen, ...
        'VariableNames', { ...
        'Node','Phase','ReverseFlow', ...
        'MinimumPower_kW','MaximumPower_kW', ...
        'WorstReverseSimHour','WorstReverseWhen'});

    powerStats = [powerStats; newRow]; %#ok<AGROW>

    intervals = logicalIntervals(reverse);

    for q = 1:height(intervals)

        iStart = intervals.StartIndex(q);
        iEnd = intervals.EndIndex(q);

        startHour = s.simHour(iStart);
        endHour = s.simHour(iEnd);

        intervalRow = table( ...
            node, ...
            phase, ...
            startHour, ...
            endHour, ...
            string(formatSimHour(startHour)), ...
            string(formatSimHour(endHour)), ...
            'VariableNames', { ...
            'Node','Phase', ...
            'StartSimHour','EndSimHour','StartWhen','EndWhen'});

        reverseIntervals = [reverseIntervals; intervalRow]; %#ok<AGROW>
    end
end

reverseStats = powerStats(powerStats.ReverseFlow, :);

writetable(powerStats, ...
    fullfile(outputDir, "Experiment2_AllActivePowerStatistics.csv"));

writetable(reverseStats, ...
    fullfile(outputDir, "Experiment2_ReversePowerFlow.csv"));

if ~isempty(reverseIntervals)
    writetable(reverseIntervals, ...
        fullfile(outputDir, "Experiment2_ReversePowerFlowIntervals.csv"));
end

%% ========================================================================
% EXTRA FIGURE 6 - WORST MINIMUM VOLTAGE BY NODE-PHASE
% ========================================================================

[sortedMinPU, orderVoltage] = sort(voltageStats.Min_pu, "ascend");

voltageLabels = ...
    "N" + voltageStats.Node + "-" + voltageStats.Phase;

voltageLabels = voltageLabels(orderVoltage);

fig6 = figure( ...
    "Name", "Experiment 2 - minimum voltage summary", ...
    "Color", "w", ...
    "Position", [120 80 1250 800]);

barh(categorical(voltageLabels, voltageLabels), sortedMinPU);

hold on;

xline(0.95, "--", ...
    "0.95 pu lower limit", ...
    "LineWidth", 1.25);

xline(1.05, "--", ...
    "1.05 pu upper limit", ...
    "LineWidth", 1.25);

hold off;
grid on;
box on;

xlabel("Minimum measured RMS voltage (pu)");
ylabel("Node-phase");
title("Experiment 2 (MPC): Worst Minimum Voltage by Node-Phase");

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig6, outputDir, ...
    "06_Exp2_Worst_Minimum_Voltage_Summary", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% EXTRA FIGURE 7 - REVERSE ACTIVE POWER SUMMARY
% ========================================================================

[sortedMinimumPower, orderPower] = sort( ...
    powerStats.MinimumPower_kW, "ascend");

powerLabels = ...
    "N" + powerStats.Node + "-" + powerStats.Phase;

powerLabels = powerLabels(orderPower);

fig7 = figure( ...
    "Name", "Experiment 2 - reverse power summary", ...
    "Color", "w", ...
    "Position", [130 80 1250 750]);

barh(categorical(powerLabels, powerLabels), sortedMinimumPower);

hold on;
xline(0, "-", "0 kW");
hold off;

grid on;
box on;

xlabel("Minimum measured active power (kW)");
ylabel("Node-phase");
title("Experiment 2 (MPC): Largest Reverse Active Power by Node-Phase");
subtitle("Negative values indicate reverse active power flow");

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig7, outputDir, ...
    "07_Exp2_Reverse_Power_Flow_Summary", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% Q7-Q10 - FEEDER PEAK AND NODE CONTRIBUTIONS
% ========================================================================

contributionRows = table();

for k = 1:numel(powerFields)

    field = powerFields(k);
    s = powerSeries.(char(field));

    powerAtPeak = interp1( ...
        s.realTime, ...
        s.kW, ...
        peakFeederRealTime, ...
        "linear", ...
        "extrap");

    parts = split(field, "_");
    node = erase(parts(1), "N");
    phase = parts(2);

    newRow = table( ...
        node, ...
        phase, ...
        powerAtPeak, ...
        'VariableNames', { ...
        'Node','Phase','PowerAtFeederPeak_kW'});

    contributionRows = [contributionRows; newRow]; %#ok<AGROW>
end

nodes = unique(contributionRows.Node, "stable");
nodeTotals = zeros(numel(nodes),1);

for n = 1:numel(nodes)

    nodeTotals(n) = sum( ...
        contributionRows.PowerAtFeederPeak_kW( ...
        contributionRows.Node == nodes(n)), ...
        "omitnan");
end

[nodeTotalsSorted, orderNode] = sort(nodeTotals, "descend");
nodesSorted = nodes(orderNode);

peakContributionTable = table( ...
    nodesSorted, ...
    nodeTotalsSorted, ...
    100 * nodeTotalsSorted / peakFeederKW, ...
    'VariableNames', { ...
    'Node','MeasuredContribution_kW','ShareOfFeederPeak_pct'});

writetable(peakContributionTable, ...
    fullfile(outputDir, ...
    "Experiment2_PeakLoad_NodeContributions.csv"));

%% ========================================================================
% EXTRA FIGURE 8 - NODE CONTRIBUTIONS AT FEEDER PEAK
% ========================================================================

fig8 = figure( ...
    "Name", "Experiment 2 - node contributions at peak", ...
    "Color", "w", ...
    "Position", [140 100 1150 650]);

bar(categorical( ...
    "Node " + nodesSorted, ...
    "Node " + nodesSorted), ...
    nodeTotalsSorted);

grid on;
box on;

xlabel("Node");
ylabel("Measured active-power contribution (kW)");
title("Experiment 2 (MPC): Node Contributions at Measured Feeder Peak");
subtitle(sprintf("Node 632 feeder peak = %.1f kW at %s", ...
    peakFeederKW, formatSimHour(peakFeederHour)));

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig8, outputDir, ...
    "08_Exp2_Node_Contributions_At_Feeder_Peak", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% Q11 - VOLTAGES DURING THE MPC PEAK-LOAD PERIOD
% ========================================================================

peakVoltageRows = table();

for k = 1:numel(voltageFields)

    f = voltageFields(k);
    s = voltageSeries.(char(f));

    voltageAtPeak = interp1( ...
        s.realTime, ...
        s.V, ...
        peakFeederRealTime, ...
        "linear", ...
        "extrap");

    puAtPeak = voltageAtPeak / s.nominalV;

    status = "within";

    if puAtPeak < 0.95
        status = "UNDER";
    elseif puAtPeak > 1.05
        status = "OVER";
    end

    newRow = table( ...
        s.node, ...
        s.phase, ...
        voltageAtPeak, ...
        puAtPeak, ...
        status, ...
        'VariableNames', { ...
        'Node','Phase','VoltageAtPeak_V','VoltageAtPeak_pu','Status'});

    peakVoltageRows = [peakVoltageRows; newRow]; %#ok<AGROW>
end

writetable(peakVoltageRows, ...
    fullfile(outputDir, ...
    "Experiment2_Voltages_At_Feeder_Peak.csv"));

[sortedPeakPU, orderPeak] = sort( ...
    peakVoltageRows.VoltageAtPeak_pu, "ascend");

peakLabels = ...
    "N" + peakVoltageRows.Node + "-" + peakVoltageRows.Phase;

peakLabels = peakLabels(orderPeak);

fig9 = figure( ...
    "Name", "Experiment 2 - voltage profile at peak", ...
    "Color", "w", ...
    "Position", [150 80 1250 800]);

barh(categorical(peakLabels, peakLabels), sortedPeakPU);

hold on;

xline(0.95, "--", ...
    "0.95 pu lower limit", ...
    "LineWidth", 1.2);

xline(1.05, "--", ...
    "1.05 pu upper limit", ...
    "LineWidth", 1.2);

hold off;
grid on;
box on;

xlabel("RMS voltage at feeder peak (pu)");
ylabel("Node-phase");
title("Experiment 2 (MPC): Feeder Voltage Profile at Peak Net Load");
subtitle(sprintf("Peak %.1f kW at %s", ...
    peakFeederKW, formatSimHour(peakFeederHour)));

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig9, outputDir, ...
    "09_Exp2_Voltage_Profile_At_Feeder_Peak", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% NODE 632 REVERSE-FLOW DIAGNOSTIC
% ========================================================================

feederReverse = feederKW < 0;
feederReverseIntervals = logicalIntervals(feederReverse);

if ~isempty(feederReverseIntervals)

    feederReverseOutput = table();

    for q = 1:height(feederReverseIntervals)

        iStart = feederReverseIntervals.StartIndex(q);
        iEnd = feederReverseIntervals.EndIndex(q);

        startHour = feederSimHour(iStart);
        endHour = feederSimHour(iEnd);

        intervalRow = table( ...
            startHour, ...
            endHour, ...
            string(formatSimHour(startHour)), ...
            string(formatSimHour(endHour)), ...
            'VariableNames', { ...
            'StartSimHour','EndSimHour','StartWhen','EndWhen'});

        feederReverseOutput = ...
            [feederReverseOutput; intervalRow]; %#ok<AGROW>
    end

    writetable(feederReverseOutput, ...
        fullfile(outputDir, ...
        "Experiment2_Node632_ReverseFlowIntervals.csv"));
end

%% ========================================================================
% NODE 646 DATA FOR REQUIRED CROSS-EXPERIMENT COMPARISON
% ========================================================================

% Node 646 is Phase B. Write a compact E2 comparison series which can later
% be overlaid with Module 1, E1 and E3.

p646 = powerSeries.N646_B;

v646Field = "N646_B";

if isfield(voltageSeries, char(v646Field))

    v646 = voltageSeries.(char(v646Field));

    commonHour = p646.simHour;

    v646Interp = interp1( ...
        v646.simHour, ...
        v646.V, ...
        commonHour, ...
        "linear", ...
        "extrap");

    node646Comparison = table( ...
        commonHour, ...
        p646.kW, ...
        v646Interp, ...
        'VariableNames', { ...
        'SimHour','Node646B_ActivePower_kW','Node646B_RMSVoltage_V'});

    writetable(node646Comparison, ...
        fullfile(outputDir, ...
        "Experiment2_Node646B_ComparisonSeries.csv"));
end

%% ========================================================================
% Q11/Q12 - OPTIONAL AUTOMATIC QP VS MPC COMPARISON
% ========================================================================

exp1Dir = fullfile(dataDir, EXP1_OUTPUT_FOLDER);

exp1VoltageStatsFile = fullfile( ...
    exp1Dir, "Experiment1_AllVoltageStatistics.csv");

exp1PeakVoltageFile = fullfile( ...
    exp1Dir, "Experiment1_Voltages_At_Feeder_Peak.csv");

qpComparisonAvailable = ...
    isfile(exp1VoltageStatsFile) && isfile(exp1PeakVoltageFile);

if qpComparisonAvailable

    E1Stats = readtable(exp1VoltageStatsFile, ...
        "VariableNamingRule", "preserve");

    E1Peak = readtable(exp1PeakVoltageFile, ...
        "VariableNamingRule", "preserve");

    qpWorstMinPU = min(double(E1Stats.("Min_pu")));
    mpcWorstMinPU = min(voltageStats.Min_pu);

    qpViolatingPhases = sum( ...
        double(E1Stats.("Min_pu")) < 0.95 | ...
        double(E1Stats.("Max_pu")) > 1.05);

    mpcViolatingPhases = height(violatingStats);

    qpLowestPeakPU = min(double(E1Peak.("VoltageAtPeak_pu")));
    mpcLowestPeakPU = min(peakVoltageRows.VoltageAtPeak_pu);

    qpMpcSummary = table( ...
        ["QP"; "MPC"], ...
        [qpWorstMinPU; mpcWorstMinPU], ...
        [qpViolatingPhases; mpcViolatingPhases], ...
        [qpLowestPeakPU; mpcLowestPeakPU], ...
        'VariableNames', { ...
        'Controller','WorstMinimumVoltage_pu', ...
        'ViolatingNodePhases','LowestVoltageAtOwnPeak_pu'});

    writetable(qpMpcSummary, ...
        fullfile(outputDir, ...
        "Experiment2_QP_vs_MPC_VoltageSummary.csv"));

    fig10 = figure( ...
        "Name", "QP vs MPC voltage comparison", ...
        "Color", "w", ...
        "Position", [170 100 950 620]);

    bar(categorical(["QP","MPC"]), ...
        [qpWorstMinPU, mpcWorstMinPU]);

    hold on;
    yline(0.95, "--", "0.95 pu lower limit");
    hold off;

    grid on;
    box on;

    ylabel("Worst minimum monitored voltage (pu)");
    title("Experiment 1 QP vs Experiment 2 MPC: Worst Minimum Voltage");

    saveAssessmentFigure(fig10, outputDir, ...
        "10_QP_vs_MPC_Worst_Minimum_Voltage", ...
        SAVE_PNG, SAVE_FIG);

    % Common node-phase comparison at each experiment's own feeder peak.
    e1Labels = "N" + string(E1Peak.("Node")) + "-" + string(E1Peak.("Phase"));
    e2Labels = "N" + peakVoltageRows.Node + "-" + peakVoltageRows.Phase;

    commonLabels = intersect(e1Labels, e2Labels, "stable");

    if ~isempty(commonLabels)

        qpPeakValues = NaN(numel(commonLabels),1);
        mpcPeakValues = NaN(numel(commonLabels),1);

        for c = 1:numel(commonLabels)

            i1 = find(e1Labels == commonLabels(c), 1);
            i2 = find(e2Labels == commonLabels(c), 1);

            qpPeakValues(c) = double(E1Peak.("VoltageAtPeak_pu")(i1));
            mpcPeakValues(c) = peakVoltageRows.VoltageAtPeak_pu(i2);
        end

        peakComparisonTable = table( ...
            commonLabels, qpPeakValues, mpcPeakValues, ...
            mpcPeakValues - qpPeakValues, ...
            'VariableNames', { ...
            'NodePhase','QP_PeakVoltage_pu','MPC_PeakVoltage_pu', ...
            'MPC_minus_QP_pu'});

        writetable(peakComparisonTable, ...
            fullfile(outputDir, ...
            "Experiment2_QP_vs_MPC_PeakVoltageComparison.csv"));
    end

else

    fprintf("\nQP comparison files not found in:\n  %s\n", exp1Dir);
    fprintf('%s\n', [ ...
        'Q11/Q12 MPC results will still be calculated, but the automatic ' ...
        'QP-vs-MPC comparison requires the Experiment 1 output folder.']);
end

%% ========================================================================
% COMMAND-WINDOW ANSWERS FOR THE EXPERIMENT 2 ASSESSMENT
% ========================================================================

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 2 ASSESSMENT SUMMARY\n");
fprintf("============================================================\n");

% Q1-Q3
fprintf("\nQ1 - Nodes violating voltage limits after MPC:\n");

if isempty(violatingStats)

    fprintf("  None.\n");

else

    violatingNodes = unique(violatingStats.Node, "stable");
    fprintf('  %s\n', char(strjoin("Node " + violatingNodes, ", ")));

    fprintf("\nQ2/Q3 - Worst violation by affected node-phase:\n");

    for r = 1:height(violatingStats)

        fprintf('  Node %s Phase %s: %s, worst %.2f V (%.4f pu) at %s; %.2f V beyond limit.\n', ...
            char(violatingStats.Node(r)), ...
            char(violatingStats.Phase(r)), ...
            char(violatingStats.WorstType(r)), ...
            violatingStats.WorstVoltage_V(r), ...
            violatingStats.WorstVoltage_V(r) / ...
                violatingStats.Nominal_V(r), ...
            char(violatingStats.WorstWhen(r)), ...
            violatingStats.ViolationMagnitude_V(r));
    end
end

fprintf('  Module 1 comparison for Q1 requires the Module 1 no-control data.\n');

% Q4-Q6
fprintf("\nQ4 - Nodes exhibiting reverse active power flow after MPC:\n");

if isempty(reverseStats)

    fprintf("  None.\n");

else

    reverseNodes = unique(reverseStats.Node, "stable");
    fprintf('  %s\n', char(strjoin("Node " + reverseNodes, ", ")));

    fprintf("\nQ5/Q6 - Largest reverse flow by affected node-phase:\n");

    for r = 1:height(reverseStats)

        fprintf('  Node %s Phase %s: %.2f kW at %s.\n', ...
            char(reverseStats.Node(r)), ...
            char(reverseStats.Phase(r)), ...
            reverseStats.MinimumPower_kW(r), ...
            char(reverseStats.WorstReverseWhen(r)));
    end
end

% Q7-Q9
fprintf("\nQ7 - Highest total feeder net load occurs at:\n");
fprintf('  %s\n', char(formatSimHour(peakFeederHour)));

fprintf("\nQ8 - Peak feeder net load after MPC:\n");
fprintf("  %.3f kW (%.3f MW)\n", ...
    peakFeederKW, peakFeederKW / 1000);

fprintf("\nQ9 - Measurement method:\n");
fprintf('%s\n', [ ...
    '  The feeder-head active power is measured directly at Node 632 ' ...
    'using Node 632.Probe1. The peak feeder net load is the maximum ' ...
    'measured Node 632.Probe1 value during the four-day MPC run.']);

% Q10
fprintf("\nQ10 - Node contributions at measured feeder peak:\n");
disp(peakContributionTable);
fprintf('  Module 1 comparison for Q10 requires the Module 1 no-control data.\n');

% Q11
[lowestPeakPU, lowestPeakIdx] = min( ...
    peakVoltageRows.VoltageAtPeak_pu);

fprintf("\nQ11 - Peak-load influence on feeder voltages:\n");
fprintf('  MPC feeder peak occurs at %s.\n', ...
    char(formatSimHour(peakFeederHour)));

fprintf("  Lowest monitored voltage at that instant:\n");
fprintf("  Node %s Phase %s = %.2f V = %.4f pu.\n", ...
    peakVoltageRows.Node(lowestPeakIdx), ...
    peakVoltageRows.Phase(lowestPeakIdx), ...
    peakVoltageRows.VoltageAtPeak_V(lowestPeakIdx), ...
    lowestPeakPU);

fprintf("  Node-phases below 0.95 pu at MPC peak: %d\n", ...
    sum(peakVoltageRows.VoltageAtPeak_pu < 0.95));

if qpComparisonAvailable

    fprintf("  QP lowest voltage at its feeder peak : %.4f pu\n", ...
        qpLowestPeakPU);

    fprintf("  MPC lowest voltage at its feeder peak: %.4f pu\n", ...
        mpcLowestPeakPU);
else
    fprintf("  QP peak-period comparison unavailable until E1 output is present.\n");
end

fprintf("  Module 1 portion of Q11 still requires Module 1 data.\n");

% Q12
fprintf("\nQ12 - QP versus MPC voltage comparison:\n");

if qpComparisonAvailable

    fprintf("  QP worst minimum voltage  : %.4f pu\n", qpWorstMinPU);
    fprintf("  MPC worst minimum voltage : %.4f pu\n", mpcWorstMinPU);
    fprintf("  QP violating node-phases  : %d\n", qpViolatingPhases);
    fprintf("  MPC violating node-phases : %d\n", mpcViolatingPhases);

    if mpcWorstMinPU > qpWorstMinPU

        fprintf('%s\n', [ ...
            '  Based on worst minimum voltage, MPC produced the higher ' ...
            'minimum measured feeder voltage in these runs.']);

    elseif mpcWorstMinPU < qpWorstMinPU

        fprintf('%s\n', [ ...
            '  Based on worst minimum voltage, QP produced the higher ' ...
            'minimum measured feeder voltage in these runs.']);

    else

        fprintf("  QP and MPC have the same worst minimum voltage.\n");
    end

    fprintf('%s\n', [ ...
        '  Use the violation count and peak-period voltage results above ' ...
        'as additional evidence when explaining Q12 orally.']);
else
    fprintf('%s\n', [ ...
        '  Place Experiment1_Assessment_Output_Final beside this script ' ...
        'and rerun to generate the automatic QP-vs-MPC comparison.']);
end

% Additional useful diagnostics.
fprintf("\nAdditional Experiment 2 diagnostics:\n");

fprintf("  Minimum Node 632 feeder power : %.3f kW at %s\n", ...
    minFeederKW, formatSimHour(minFeederHour));

fprintf("  Node 632 samples below 0 kW  : %d of %d\n", ...
    sum(feederReverse), numel(feederReverse));

fprintf("  Measured Node 646 SoC range  : %.2f%% to %.2f%%\n", ...
    min(socMeasured), max(socMeasured));

[lowestPU, lowestIdx] = min(voltageStats.Min_pu);

fprintf("  Lowest measured feeder voltage: Node %s Phase %s = %.4f pu\n", ...
    voltageStats.Node(lowestIdx), ...
    voltageStats.Phase(lowestIdx), ...
    lowestPU);

fprintf("\nFigures and CSV summaries saved to:\n  %s\n", outputDir);
fprintf("============================================================\n");

%% ========================================================================
% LOCAL FUNCTIONS
% ========================================================================

function T = readTyphoonCsv(path)

    T = readtable(path, ...
        "VariableNamingRule", "preserve");

    assert(ismember("Time", string(T.Properties.VariableNames)), ...
        "File does not contain a Time column:\n%s", path);
end


function T = cropRealTime(T, startS, endS)

    mask = ...
        double(T.("Time")) >= startS & ...
        double(T.("Time")) <= endS;

    T = T(mask,:);

    assert(~isempty(T), ...
        "No samples remain after cropping to %.2f-%.2f s.", ...
        startS, endS);
end


function simHour = realToSimHour( ...
    realTime, startRealS, realSecondsPerStep, simHoursPerStep)

    simHour = ...
        (realTime - startRealS) .* ...
        (simHoursPerStep / realSecondsPerStep);
end


function label = powerFieldLabel(field)

    parts = split(string(field), "_");

    label = ...
        "Node " + ...
        erase(parts(1), "N") + ...
        " Phase " + ...
        parts(2);
end


function intervals = logicalIntervals(mask)

    mask = logical(mask(:));

    edges = diff([false; mask; false]);

    starts = find(edges == 1);
    ends = find(edges == -1) - 1;

    intervals = table( ...
        starts, ...
        ends, ...
        'VariableNames', {'StartIndex','EndIndex'});
end


function text = formatSimHour(simHour)

    if isnan(simHour)

        text = "N/A";
        return;
    end

    % 0-24 h = Day 1, 24-48 h = Day 2, etc.
    day = floor(simHour / 24) + 1;

    hourWithinDay = simHour - (day - 1) * 24;

    % Keep day 4 endpoint at Day 4 24:00 instead of Day 5 00:00.
    if day > 4
        day = 4;
        hourWithinDay = 24;
    end

    hoursWhole = floor(hourWithinDay);
    minutesWhole = round((hourWithinDay - hoursWhole) * 60);

    if minutesWhole == 60
        hoursWhole = hoursWhole + 1;
        minutesWhole = 0;
    end

    text = sprintf("Day %d %02d:%02d", ...
        day, hoursWhole, minutesWhole);
end


function addDaySeparators(ax, nDays)

    for d = 1:(nDays - 1)

        xline(ax, 24*d, ":", ...
            "HandleVisibility", "off");
    end
end


function saveAssessmentFigure( ...
    fig, outputDir, baseName, savePng, saveFig)

    if savePng

        exportgraphics(fig, ...
            fullfile(outputDir, baseName + ".png"), ...
            "Resolution", 300);
    end

    if saveFig

        savefig(fig, ...
            fullfile(outputDir, baseName + ".fig"));
    end
end
