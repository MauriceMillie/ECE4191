%% ECE4191 Module 3 - Experiment 3 (MPC-CIL)
% REQUIRED PLOTS + E3 ASSESSMENT SUPPORT
%
% Expected input file names (no "(1)" or "(2)" suffixes):
%
%   measured_rmsVoltages1.csv
%   measured_rmsVoltages2.csv
%   measured_rmsVoltages3.csv
%   measuredPower1.csv
%   measuredPower2.csv
%   node632_probe1.csv
%   Node634_rmsVoltages.csv
%
% For the REQUIRED Node 646 measured SoC plot, provide the actual E3
% MPC-CIL controller log as:
%
%   experiment3_mpc_cil_schedule.csv
%
% The E3 controller log must contain a measured Node 646 SoC column.
%
% This script generates:
%   1) Node 632 measured feeder active power
%   2) Active power at all monitored time-varying node-phases
%   3) Node 634 RMS voltages A/B/C with +/-5% limits
%   4) RMS voltages at all other monitored feeder nodes with +/-5% limits
%   5) Measured Node 646 battery SoC (when the correct E3 log is supplied)
%
% It also generates:
%   - voltage statistics / violation tables
%   - Node 646 Phase B comparison series for later E1/E2/E3 overlay
%   - optional Experiment 2 vs Experiment 3 voltage comparison when
%     Experiment2_Assessment_Output_Final is available
%
% IMPORTANT:
% Experiment 3 is the MPC-CIL case where ONLY the battery at Node 646-B
% should be operational. The Node 646 battery power limit is 510 kW.
% This script therefore checks the controller log where possible and warns
% if it appears to be a feeder-wide Experiment 2 schedule instead.
%
% Timing:
%   2 real seconds = 30 simulated minutes
%   192 half-hour steps = 4 simulated days = 384 real seconds
%
% If Signal Analyzer started before the controller playback, adjust:
%       PLAYBACK_START_REAL_S

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

% Voltage limits required by the assessment.
NOMINAL_634_V = 277.0;
NOMINAL_OTHER_V = 2401.0;

LOWER_634_V = 0.95 * NOMINAL_634_V;       % 263.15 V
UPPER_634_V = 1.05 * NOMINAL_634_V;       % 290.85 V

LOWER_OTHER_V = 0.95 * NOMINAL_OTHER_V;   % 2280.95 V
UPPER_OTHER_V = 1.05 * NOMINAL_OTHER_V;   % 2521.05 V

% E3 Node 646 battery design limit.
NODE646_BATTERY_LIMIT_KW = 510.0;

SAVE_PNG = true;
SAVE_FIG = true;

OUTPUT_FOLDER = "Experiment3_Assessment_Output_Final";
EXP2_OUTPUT_FOLDER = "Experiment2_Assessment_Output_Final";

FONT_SIZE = 10;
LINE_WIDTH = 1.25;
LIMIT_LINE_WIDTH = 1.15;

% If true, a suspicious/full-feeder schedule will NOT be used for the
% required E3 SoC plot.
STRICT_E3_SOC_VALIDATION = true;

%% ========================================================================
% INPUT FILES - NO SUFFIXES SUCH AS "(1)" OR "(2)"
% ========================================================================

POWER_FILE_1 = "measuredPower1.csv";
POWER_FILE_2 = "measuredPower2.csv";

FEEDER_POWER_FILE = "node632_probe1.csv";

NODE634_VOLTAGE_FILE = "Node634_rmsVoltages.csv";

RMS_VOLTAGE_FILE_1 = "measured_rmsVoltages1.csv";
RMS_VOLTAGE_FILE_2 = "measured_rmsVoltages2.csv";
RMS_VOLTAGE_FILE_3 = "measured_rmsVoltages3.csv";

% Rename your ACTUAL Experiment 3 MPC-CIL controller log to this.
E3_SCHEDULE_FILE = "experiment3_mpc_cil_schedule.csv";

%% ========================================================================
% DATA / OUTPUT FOLDERS
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

powerPath1 = fullfile(dataDir, POWER_FILE_1);
powerPath2 = fullfile(dataDir, POWER_FILE_2);
feederPath = fullfile(dataDir, FEEDER_POWER_FILE);
node634VoltagePath = fullfile(dataDir, NODE634_VOLTAGE_FILE);
voltagePath1 = fullfile(dataDir, RMS_VOLTAGE_FILE_1);
voltagePath2 = fullfile(dataDir, RMS_VOLTAGE_FILE_2);
voltagePath3 = fullfile(dataDir, RMS_VOLTAGE_FILE_3);
schedulePath = fullfile(dataDir, E3_SCHEDULE_FILE);

requiredMeasurementFiles = [
    string(powerPath1)
    string(powerPath2)
    string(feederPath)
    string(node634VoltagePath)
    string(voltagePath1)
    string(voltagePath2)
    string(voltagePath3)
];

for k = 1:numel(requiredMeasurementFiles)

    assert(isfile(requiredMeasurementFiles(k)), ...
        "Required E3 measurement file not found:\n%s", ...
        requiredMeasurementFiles(k));
end

fprintf("============================================================\n");
fprintf(" ECE4191 MODULE 3 - EXPERIMENT 3 (MPC-CIL)\n");
fprintf(" REQUIRED PLOTS / HEADER-SAFE ANALYSIS\n");
fprintf("============================================================\n");
fprintf("Playback window : %.2f to %.2f real seconds\n", ...
    PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
fprintf("Simulated period: 0 to 96 hours (4 days)\n");
fprintf("Output folder   : %s\n\n", outputDir);

%% ========================================================================
% LOAD ACTIVE-POWER DATA
% ========================================================================

P1 = readTyphoonCsv(powerPath1);
P2 = readTyphoonCsv(powerPath2);
PF = readTyphoonCsv(feederPath);

P1 = cropRealTime(P1, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
P2 = cropRealTime(P2, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
PF = cropRealTime(PF, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);

% HEADER-SAFE COLUMN MAPPING
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
%
% Numeric positions are intentionally used because long Typhoon headers can
% be truncated/modified by MATLAB.

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
        double(T.("Time")), ...
        PLAYBACK_START_REAL_S, ...
        REAL_SECONDS_PER_STEP, ...
        SIM_HOURS_PER_STEP);

    % Typhoon measured active-power signals are in watts.
    powerSeries.(char(field)).kW = ...
        double(T{:,columnIndex}) / 1000.0;
end

powerFields = string(fieldnames(powerSeries));

% Node 632 feeder-head power.
assert(ismember("Node 632.Probe1", ...
    string(PF.Properties.VariableNames)), ...
    "Node 632.Probe1 was not found in node632_probe1.csv.");

feederRealTime = double(PF.("Time"));

feederSimHour = realToSimHour( ...
    feederRealTime, ...
    PLAYBACK_START_REAL_S, ...
    REAL_SECONDS_PER_STEP, ...
    SIM_HOURS_PER_STEP);

feederKW = double(PF.("Node 632.Probe1")) / 1000.0;

%% ========================================================================
% LOAD RMS VOLTAGE DATA
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
            double(T.("Time")), ...
            PLAYBACK_START_REAL_S, ...
            REAL_SECONDS_PER_STEP, ...
            SIM_HOURS_PER_STEP);

        voltageSeries.(char(field)).V = double(T.(char(name)));

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

fprintf("Loaded %d active-power node-phase channels.\n", ...
    numel(powerFields));

fprintf("Loaded %d RMS-voltage node-phase channels.\n\n", ...
    numel(voltageFields));

%% ========================================================================
% REQUIRED FIGURE 1 - NODE 632 FEEDER ACTIVE POWER
% ========================================================================

[peakFeederKW, peakIdx] = max(feederKW);
[minFeederKW, minIdx] = min(feederKW);

peakFeederHour = feederSimHour(peakIdx);
minFeederHour = feederSimHour(minIdx);

fig1 = figure( ...
    "Name", "Experiment 3 - Node 632 feeder active power", ...
    "Color", "w", ...
    "Position", [80 80 1250 650]);

plot(feederSimHour, feederKW, ...
    "LineWidth", 1.6, ...
    "DisplayName", "Measured Node 632 feeder power");

hold on;

yline(0, "-", "0 kW", "HandleVisibility", "off");

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

title("Experiment 3 (MPC-CIL): Measured Feeder Active Power at Node 632");

subtitle(sprintf("Peak %.1f kW | Minimum %.1f kW", ...
    peakFeederKW, minFeederKW));

xlim([0 96]);
legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig1, outputDir, ...
    "01_Exp3_Node632_Feeder_Active_Power", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 2 - ALL TIME-VARYING NODE-PHASE ACTIVE POWERS
% ========================================================================

fig2 = figure( ...
    "Name", "Experiment 3 - node-phase active powers", ...
    "Color", "w", ...
    "Position", [20 20 1700 950]);

tl2 = tiledlayout(4,4, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl2, ...
    "Experiment 3 (MPC-CIL): Measured Active Power at Time-Varying Node-Phases", ...
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
    "02_Exp3_All_TimeVarying_NodePhase_Active_Powers", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 3 - NODE 634 RMS VOLTAGES
% ========================================================================

node634Fields = voltageFields(startsWith(voltageFields, "N634_"));

assert(numel(node634Fields) == 3, ...
    "Expected three Node 634 voltage phases; found %d.", ...
    numel(node634Fields));

fig3 = figure( ...
    "Name", "Experiment 3 - Node 634 RMS voltage", ...
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

title("Experiment 3 (MPC-CIL): Node 634 RMS Voltages");
subtitle("Nominal = 277 V; permitted range = 263.15-290.85 V");

xlim([0 96]);
legend("Location", "best");

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig3, outputDir, ...
    "03_Exp3_Node634_RMS_Voltages", ...
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
    "Name", "Experiment 3 - all other monitored RMS voltages", ...
    "Color", "w", ...
    "Position", [10 10 1750 1000]);

nCols = 4;
nRows = ceil(numel(otherNodes) / nCols);

tl4 = tiledlayout(nRows, nCols, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl4, ...
    "Experiment 3 (MPC-CIL): RMS Voltages at All Other Monitored Feeder Nodes", ...
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
    "04_Exp3_All_Other_Monitored_RMS_Voltages", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 5 - MEASURED NODE 646 SOC
% ========================================================================

socPlotCreated = false;
scheduleValidForE3 = false;

if isfile(schedulePath)

    S = readtable(schedulePath, ...
        "VariableNamingRule", "preserve");

    names = string(S.Properties.VariableNames);

    % Find measured SoC column.
    socCandidates = [
        "soc_measured_646_pct"
        "soc646_measured_pct"
        "measured_soc_646_pct"
        "soc_measured_pct"
    ];

    socColumn = "";

    for c = 1:numel(socCandidates)

        if ismember(socCandidates(c), names)
            socColumn = socCandidates(c);
            break;
        end
    end

    % Validate whether this looks like a Node646-only E3 controller log.
    scheduleValidForE3 = true;

    if ismember("battery_agg_kw", names)

        maxCommand = max(abs(double(S.("battery_agg_kw"))));

        if maxCommand > NODE646_BATTERY_LIMIT_KW + 1

            scheduleValidForE3 = false;

            fprintf("\nWARNING: E3 schedule validation failed.\n");
            fprintf("  Maximum battery_agg_kw = %.2f kW.\n", maxCommand);
            fprintf("  Node 646 E3 battery limit = %.2f kW.\n", ...
                NODE646_BATTERY_LIMIT_KW);
            fprintf("  This log appears to be a feeder-wide Experiment 2 schedule.\n");
        end
    end

    if strlength(socColumn) == 0

        scheduleValidForE3 = false;

        fprintf("\nWARNING: E3 schedule has no recognised measured SoC column.\n");
    end

    if scheduleValidForE3 || ~STRICT_E3_SOC_VALIDATION

        if height(S) >= N_PLAYBACK_STEPS
            S = S(1:N_PLAYBACK_STEPS,:);
        end

        if ismember("step", names)

            socHour = double(S.("step")) .* SIM_HOURS_PER_STEP;

        else

            socHour = (1:height(S))' .* SIM_HOURS_PER_STEP;
        end

        socMeasured = double(S.(char(socColumn)));

        fig5 = figure( ...
            "Name", "Experiment 3 - Node 646 measured SoC", ...
            "Color", "w", ...
            "Position", [100 100 1250 650]);

        plot(socHour, socMeasured, ...
            "LineWidth", 1.7, ...
            "DisplayName", "Measured Node 646 SoC");

        hold on;

        % Plot controller-predicted SoC too if present.
        if ismember("soc_predicted_pct", names)

            socPredicted = double(S.("soc_predicted_pct"));

            plot(socHour, socPredicted, "--", ...
                "LineWidth", 1.2, ...
                "DisplayName", "Controller predicted SoC");
        end

        yline(0, ":", "HandleVisibility", "off");
        yline(100, ":", "HandleVisibility", "off");

        addDaySeparators(gca, 4);

        hold off;
        grid on;
        box on;

        xlabel("Simulated time (hours)");
        ylabel("Battery State of Charge (%)");

        title("Experiment 3 (MPC-CIL): Node 646 Measured Battery SoC");

        xlim([0 96]);
        ylim([-2 102]);

        legend("Location", "best");
        set(gca, "FontSize", FONT_SIZE);

        saveAssessmentFigure(fig5, outputDir, ...
            "05_Exp3_Node646_Measured_SoC", ...
            SAVE_PNG, SAVE_FIG);

        socPlotCreated = true;

        % SoC error support for oral question 2.
        if ismember("soc_predicted_pct", names)

            socPredicted = double(S.("soc_predicted_pct"));
            socError = socMeasured - socPredicted;

            socErrorTable = table( ...
                socHour, socMeasured, socPredicted, socError, ...
                'VariableNames', { ...
                'SimHour','MeasuredSoC_pct','PredictedSoC_pct','Error_pctPoint'});

            writetable(socErrorTable, ...
                fullfile(outputDir, ...
                "Experiment3_Node646_SoC_Error.csv"));

            fig6 = figure( ...
                "Name", "Experiment 3 - Node 646 SoC error", ...
                "Color", "w", ...
                "Position", [110 110 1250 620]);

            plot(socHour, socError, ...
                "LineWidth", 1.4);

            hold on;
            yline(0, "-", "HandleVisibility", "off");
            addDaySeparators(gca, 4);
            hold off;

            grid on;
            box on;

            xlabel("Simulated time (hours)");
            ylabel("Measured - predicted SoC (percentage points)");

            title("Experiment 3 (MPC-CIL): Node 646 SoC Tracking Error");

            xlim([0 96]);

            saveAssessmentFigure(fig6, outputDir, ...
                "06_Exp3_Node646_SoC_Error", ...
                SAVE_PNG, SAVE_FIG);
        end
    end

else

    fprintf("\nWARNING: Correct E3 controller log not found:\n");
    fprintf("  %s\n", schedulePath);
end

if ~socPlotCreated

    fprintf("\nREQUIRED PLOT 5 WAS NOT CREATED.\n");
    fprintf("Provide the actual Experiment 3 MPC-CIL controller log as:\n");
    fprintf("  experiment3_mpc_cil_schedule.csv\n");
    fprintf("The other four required E3 plots are still generated normally.\n");
end

%% ========================================================================
% VOLTAGE STATISTICS - SUPPORTS E3 ORAL QUESTIONS 3 AND 4
% ========================================================================

voltageStats = table();

for k = 1:numel(voltageFields)

    f = voltageFields(k);
    s = voltageSeries.(char(f));

    v = s.V;

    [minV, iMin] = min(v);
    [maxV, iMax] = max(v);

    minPU = minV / s.nominalV;
    maxPU = maxV / s.nominalV;

    under = minV < s.lowerV;
    over = maxV > s.upperV;

    newRow = table( ...
        s.node, ...
        s.phase, ...
        s.nominalV, ...
        minV, ...
        minPU, ...
        s.simHour(iMin), ...
        maxV, ...
        maxPU, ...
        s.simHour(iMax), ...
        under, ...
        over, ...
        'VariableNames', { ...
        'Node','Phase','Nominal_V', ...
        'Min_V','Min_pu','MinSimHour', ...
        'Max_V','Max_pu','MaxSimHour', ...
        'UnderVoltage','OverVoltage'});

    voltageStats = [voltageStats; newRow]; %#ok<AGROW>
end

writetable(voltageStats, ...
    fullfile(outputDir, ...
    "Experiment3_AllVoltageStatistics.csv"));

violatingStats = voltageStats( ...
    voltageStats.UnderVoltage | voltageStats.OverVoltage, :);

writetable(violatingStats, ...
    fullfile(outputDir, ...
    "Experiment3_VoltageViolations.csv"));

%% ========================================================================
% EXTRA VOLTAGE SUMMARY FIGURE
% ========================================================================

[sortedMinPU, orderVoltage] = sort( ...
    voltageStats.Min_pu, "ascend");

voltageLabels = ...
    "N" + voltageStats.Node + "-" + voltageStats.Phase;

voltageLabels = voltageLabels(orderVoltage);

figV = figure( ...
    "Name", "Experiment 3 - minimum voltage summary", ...
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

title("Experiment 3 (MPC-CIL): Worst Minimum Voltage by Node-Phase");

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(figV, outputDir, ...
    "07_Exp3_Worst_Minimum_Voltage_Summary", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% NODE 646-B SERIES FOR REQUIRED CROSS-EXPERIMENT COMPARISON
% ========================================================================

if isfield(powerSeries, "N646_B") && ...
        isfield(voltageSeries, "N646_B")

    p646 = powerSeries.N646_B;
    v646 = voltageSeries.N646_B;

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
        'SimHour', ...
        'Node646B_ActivePower_kW', ...
        'Node646B_RMSVoltage_V'});

    writetable(node646Comparison, ...
        fullfile(outputDir, ...
        "Experiment3_Node646B_ComparisonSeries.csv"));
end

%% ========================================================================
% OPTIONAL E2 VS E3 VOLTAGE COMPARISON - ORAL QUESTION 4
% ========================================================================

exp2Dir = fullfile(dataDir, EXP2_OUTPUT_FOLDER);

exp2VoltageStatsFile = fullfile( ...
    exp2Dir, "Experiment2_AllVoltageStatistics.csv");

if isfile(exp2VoltageStatsFile)

    E2 = readtable(exp2VoltageStatsFile, ...
        "VariableNamingRule", "preserve");

    e2Labels = "N" + string(E2.("Node")) + "-" + string(E2.("Phase"));
    e3Labels = "N" + voltageStats.Node + "-" + voltageStats.Phase;

    commonLabels = intersect(e2Labels, e3Labels, "stable");

    e2MinPU = NaN(numel(commonLabels),1);
    e3MinPU = NaN(numel(commonLabels),1);

    for c = 1:numel(commonLabels)

        i2 = find(e2Labels == commonLabels(c), 1);
        i3 = find(e3Labels == commonLabels(c), 1);

        e2MinPU(c) = double(E2.("Min_pu")(i2));
        e3MinPU(c) = voltageStats.Min_pu(i3);
    end

    E2E3 = table( ...
        commonLabels, ...
        e2MinPU, ...
        e3MinPU, ...
        e3MinPU - e2MinPU, ...
        'VariableNames', { ...
        'NodePhase', ...
        'Experiment2_MinVoltage_pu', ...
        'Experiment3_MinVoltage_pu', ...
        'E3_minus_E2_pu'});

    writetable(E2E3, ...
        fullfile(outputDir, ...
        "Experiment3_E2_vs_E3_VoltageComparison.csv"));

    figComp = figure( ...
        "Name", "Experiment 2 vs Experiment 3 voltages", ...
        "Color", "w", ...
        "Position", [140 80 1350 800]);

    x = 1:numel(commonLabels);

    plot(x, e2MinPU, "-o", ...
        "LineWidth", 1.3, ...
        "DisplayName", "Experiment 2 MPC");

    hold on;

    plot(x, e3MinPU, "-s", ...
        "LineWidth", 1.3, ...
        "DisplayName", "Experiment 3 MPC-CIL");

    yline(0.95, "--", ...
        "0.95 pu lower limit", ...
        "HandleVisibility", "off");

    hold off;

    grid on;
    box on;

    xticks(x);
    xticklabels(commonLabels);
    xtickangle(45);

    ylabel("Minimum RMS voltage (pu)");

    title("Experiment 2 vs Experiment 3: Minimum Voltage by Node-Phase");

    legend("Location", "best");

    saveAssessmentFigure(figComp, outputDir, ...
        "08_Exp3_E2_vs_E3_Minimum_Voltage", ...
        SAVE_PNG, SAVE_FIG);

else

    fprintf("\nExperiment 2 voltage summary not found.\n");
    fprintf("Automatic E2-vs-E3 voltage comparison was skipped.\n");
end

%% ========================================================================
% COMMAND WINDOW SUMMARY
% ========================================================================

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 3 SUMMARY\n");
fprintf("============================================================\n");

fprintf("\nRequired plots:\n");
fprintf("  1. Node 632 feeder active power              : CREATED\n");
fprintf("  2. All time-varying node-phase active powers: CREATED\n");
fprintf("  3. Node 634 A/B/C RMS voltages              : CREATED\n");
fprintf("  4. Other monitored RMS voltages             : CREATED\n");

if socPlotCreated
    fprintf("  5. Measured Node 646 battery SoC             : CREATED\n");
else
    fprintf("  5. Measured Node 646 battery SoC             : NOT CREATED - correct E3 log required\n");
end

fprintf("\nMeasured feeder statistics:\n");
fprintf("  Node 632 peak    : %.3f kW at %s\n", ...
    peakFeederKW, char(formatSimHour(peakFeederHour)));

fprintf("  Node 632 minimum : %.3f kW at %s\n", ...
    minFeederKW, char(formatSimHour(minFeederHour)));

fprintf("  Violating voltage node-phases: %d\n", ...
    height(violatingStats));

[lowestPU, lowestIdx] = min(voltageStats.Min_pu);

fprintf("  Lowest measured voltage: Node %s Phase %s = %.4f pu\n", ...
    char(voltageStats.Node(lowestIdx)), ...
    char(voltageStats.Phase(lowestIdx)), ...
    lowestPU);

if socPlotCreated && exist("socError", "var")

    fprintf("\nNode 646 SoC tracking:\n");

    fprintf("  Maximum absolute SoC error: %.3f percentage points\n", ...
        max(abs(socError)));

    fprintf("  Mean absolute SoC error   : %.3f percentage points\n", ...
        mean(abs(socError), "omitnan"));
end

fprintf("\nAll generated files are saved in:\n");
fprintf("  %s\n", outputDir);
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


function text = formatSimHour(simHour)

    if isnan(simHour)

        text = "N/A";
        return;
    end

    day = floor(simHour / 24) + 1;
    hourWithinDay = simHour - (day - 1) * 24;

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
