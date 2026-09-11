%% ECE4191 Module 3 - Experiment 1 (QP)
% FULL ASSESSMENT / PRESENTATION PLOTTING SCRIPT
%
% This script is tailored to the native Typhoon Signal Analyzer exports:
%
%   measured_activePower1.csv
%   measured_activePower2.csv
%   node632_probe1.csv
%   node634_rmsVoltage.csv
%   rmsVoltage1.csv
%   rmsVoltage2.csv
%   rmsVoltage3.csv
%
% It produces the five required Experiment 1 plots where data are available,
% plus extra presentation figures and console/table summaries aimed directly
% at the Experiment 1 oral assessment questions.
%
% Required plots:
%   1. Feeder active power at Node 632
%   2. Active power at all monitored time-varying node-phase loads
%   3. Node 634 RMS voltages (A/B/C) with +/-5% limits around 277 V
%   4. RMS voltages at all other monitored nodes with +/-5% limits around 2401 V
%   5. Measured Node 646 battery SoC (loaded from experiment1_qp_schedule*.csv
%      if that schedule CSV is present in the same folder)
%
% Extra assessment figures:
%   6. Worst minimum per-unit voltage by node-phase
%   7. Largest reverse active power by node-phase
%   8. Node contributions at the measured feeder peak
%   9. Feeder voltage profile at the measured peak-load instant
%
% Console + CSV outputs answer:
%   Q1  Which nodes violate voltage bounds?
%   Q2  When do voltage violations occur?
%   Q3  Worst-case voltage violation for each violating node/node-phase
%   Q4  Which nodes exhibit reverse active power flow?
%   Q5  When does reverse active power flow occur?
%   Q6  Largest reverse flow for each affected node/node-phase
%   Q7  When is total feeder net load highest?
%   Q8  What is the peak feeder net load?
%   Q9  How is peak feeder net load measured?
%   Q10 Which nodes contribute most to feeder peak load?
%
% IMPORTANT TIME MAPPING
% ----------------------
% The Raspberry Pi playback used:
%   2 real seconds = 30 simulated minutes
% so:
%   96 real seconds = 1 simulated day.
%
% The first command corresponds to the 0:30 interval-ending dataset value.
% If your Signal Analyzer recording started before/after the controller
% playback, adjust PLAYBACK_START_REAL_S below.
%
% The uploaded data cover slightly more than 480 real seconds. This script
% crops to the 5-day Experiment 1 playback window by default.

clear;
clc;
close all;

%% ========================================================================
% USER SETTINGS
% ========================================================================

% Native Typhoon CSV filenames.
ACTIVE_POWER_FILE_1 = "measured_activePower1.csv";
ACTIVE_POWER_FILE_2 = "measured_activePower2.csv";
FEEDER_POWER_FILE   = "node632_probe1.csv";

NODE634_VOLTAGE_FILE = "node634_rmsVoltage.csv";
RMS_VOLTAGE_FILE_1   = "rmsVoltage1.csv";
RMS_VOLTAGE_FILE_2   = "rmsVoltage2.csv";
RMS_VOLTAGE_FILE_3   = "rmsVoltage3.csv";

% Real-time capture window corresponding to the 5-day playback.
PLAYBACK_START_REAL_S = 0.0;
PLAYBACK_DURATION_REAL_S = 480.0;
PLAYBACK_END_REAL_S = PLAYBACK_START_REAL_S + PLAYBACK_DURATION_REAL_S;

% Simulation-time mapping.
REAL_SECONDS_PER_DATA_STEP = 2.0;
SIM_HOURS_PER_DATA_STEP = 0.5;
SIM_HOURS_PER_REAL_SECOND = SIM_HOURS_PER_DATA_STEP / REAL_SECONDS_PER_DATA_STEP;

% First playback command corresponds to 7-Jan-2013 00:30.
SIM_FIRST_COMMAND_TIME = datetime(2013,1,7,0,30,0);

% Assessment voltage limits.
NOMINAL_634_V = 277.0;
NOMINAL_OTHER_V = 2401.0;

LOWER_634_V = 0.95 * NOMINAL_634_V;
UPPER_634_V = 1.05 * NOMINAL_634_V;

LOWER_OTHER_V = 0.95 * NOMINAL_OTHER_V;
UPPER_OTHER_V = 1.05 * NOMINAL_OTHER_V;

% Save settings.
SAVE_PNG = true;
SAVE_FIG = true;
OUTPUT_FOLDER = "Experiment1_Assessment_Output";

% Figure formatting.
FONT_SIZE = 10;
LINE_WIDTH = 1.35;
LIMIT_LINE_WIDTH = 1.15;

%% ========================================================================
% FIND DATA DIRECTORY / CREATE OUTPUT FOLDER
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

fprintf("============================================================\n");
fprintf(" ECE4191 MODULE 3 - EXPERIMENT 1 (QP)\n");
fprintf(" FULL ASSESSMENT ANALYSIS\n");
fprintf("============================================================\n");
fprintf("Data folder       : %s\n", dataDir);
fprintf("Output folder     : %s\n", outputDir);
fprintf("Playback real time: %.2f to %.2f s\n", ...
    PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
fprintf("Playback length   : 5 simulated days\n\n");

%% ========================================================================
% LOAD NATIVE TYPHOON ACTIVE-POWER DATA
% ========================================================================

P1 = readTyphoonCsv(fullfile(dataDir, ACTIVE_POWER_FILE_1));
P2 = readTyphoonCsv(fullfile(dataDir, ACTIVE_POWER_FILE_2));
PF = readTyphoonCsv(fullfile(dataDir, FEEDER_POWER_FILE));

P1 = cropByRealTime(P1, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
P2 = cropByRealTime(P2, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
PF = cropByRealTime(PF, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);

% Canonical mapping for the uploaded Typhoon signal names.
% Power is exported in W and converted to kW below.
powerMap = {
    "N611_C", "Time Varying Load 611.Single phase time-varying load1.P_measured";
    "N634_A", "Time Varying Load 634.Single phase time-varying load with the Master PulseA.P_measured";
    "N634_B", "Time Varying Load 634.Single phase time-varying load with the Master PulseB.P_measured";
    "N634_C", "Time Varying Load 634.Single phase time-varying load with the Master PulseC.P_measured";
    "N645_B", "Time Varying Load 645.Single phase time-varying load645.P_measured";
    "N646_B", "Time Varying Load 646.Single phase time-varying load646.P_measured";
    "N652_A", "Time Varying Load 652.Single phase time-varying load652.P_measured";
    "N692_C", "Time Varying Load 692.Single phase time-varying loadC.P_measured";
    "N671_A", "Time Varying Load 671.Single phase time-varying loadA.P_measured";
    "N671_B", "Time Varying Load 671.Single phase time-varying loadA1.P_measured";
    "N671_C", "Time Varying Load 671.Single phase time-varying loadA2.P_measured";
    "N675_A", "Time Varying Load 675.Single phase time-varying loadA.P_measured";
    "N675_B", "Time Varying Load 675.Single phase time-varying loadB.P_measured";
    "N675_C", "Time Varying Load 675.Single phase time-varying loadC.P_measured"
};

% Extract the 14 measured node-phase channels.
powerSeries = struct();

for k = 1:size(powerMap,1)
    canonical = powerMap{k,1};
    signal = powerMap{k,2};

    if ismember(string(signal), string(P1.Properties.VariableNames))
        src = P1;
    elseif ismember(string(signal), string(P2.Properties.VariableNames))
        src = P2;
    else
        error("Required active-power signal not found: %s", signal);
    end

    powerSeries.(canonical).realTime = src.("Time");
    powerSeries.(canonical).simTime = realToSimTime( ...
        src.("Time"), PLAYBACK_START_REAL_S, SIM_FIRST_COMMAND_TIME, ...
        SIM_HOURS_PER_REAL_SECOND);
    powerSeries.(canonical).kW = src.(signal) / 1000.0;
end

% Feeder power at Node 632.
assert(ismember("Node 632.Probe1", PF.Properties.VariableNames), ...
    "node632_probe1.csv does not contain 'Node 632.Probe1'.");

feederRealTime = PF.("Time");
feederSimTime = realToSimTime( ...
    feederRealTime, PLAYBACK_START_REAL_S, SIM_FIRST_COMMAND_TIME, ...
    SIM_HOURS_PER_REAL_SECOND);
feederKW = PF.("Node 632.Probe1") / 1000.0;

%% ========================================================================
% LOAD NATIVE TYPHOON RMS-VOLTAGE DATA
% ========================================================================

V634 = readTyphoonCsv(fullfile(dataDir, NODE634_VOLTAGE_FILE));
V1   = readTyphoonCsv(fullfile(dataDir, RMS_VOLTAGE_FILE_1));
V2   = readTyphoonCsv(fullfile(dataDir, RMS_VOLTAGE_FILE_2));
V3   = readTyphoonCsv(fullfile(dataDir, RMS_VOLTAGE_FILE_3));

V634 = cropByRealTime(V634, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
V1   = cropByRealTime(V1,   PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
V2   = cropByRealTime(V2,   PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
V3   = cropByRealTime(V3,   PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);

% Build a single canonical voltage structure.
voltageSeries = struct();

voltageSources = {V634, V1, V2, V3};

for f = 1:numel(voltageSources)
    T = voltageSources{f};
    names = string(T.Properties.VariableNames);

    for k = 1:numel(names)
        name = names(k);

        if name == "Time" || name == "UpperBound" || name == "LowerBound"
            continue;
        end

        token = regexp(char(name), ...
            '^Node\s+(\d+)\.V([123])_rms$', ...
            'tokens', 'once');

        if isempty(token)
            continue;
        end

        node = token{1};
        phaseNumber = str2double(token{2});
        phaseLetters = 'ABC';
        phase = string(phaseLetters(phaseNumber));

        canonical = sprintf("N%s_%s", node, phase);

        voltageSeries.(canonical).node = string(node);
        voltageSeries.(canonical).phase = string(phase);
        voltageSeries.(canonical).realTime = T.("Time");
        voltageSeries.(canonical).simTime = realToSimTime( ...
            T.("Time"), PLAYBACK_START_REAL_S, SIM_FIRST_COMMAND_TIME, ...
            SIM_HOURS_PER_REAL_SECOND);
        voltageSeries.(canonical).V = T.(char(name));

        if node == "634"
            voltageSeries.(canonical).nominalV = NOMINAL_634_V;
            voltageSeries.(canonical).lowerV = LOWER_634_V;
            voltageSeries.(canonical).upperV = UPPER_634_V;
        else
            voltageSeries.(canonical).nominalV = NOMINAL_OTHER_V;
            voltageSeries.(canonical).lowerV = LOWER_OTHER_V;
            voltageSeries.(canonical).upperV = UPPER_OTHER_V;
        end
    end
end

voltageFields = string(fieldnames(voltageSeries));

%% ========================================================================
% FIGURE 1 - REQUIRED: FEEDER ACTIVE POWER AT NODE 632
% ========================================================================

[peakFeederKW, peakIdx] = max(feederKW);
[minFeederKW, minIdx] = min(feederKW);

peakRealTime = feederRealTime(peakIdx);
peakSimTime = feederSimTime(peakIdx);

fig1 = figure( ...
    "Name", "Exp1 - Node 632 feeder active power", ...
    "Color", "w", ...
    "Position", [80 80 1250 650]);

plot(feederSimTime, feederKW, ...
    "LineWidth", 1.6, ...
    "DisplayName", "Node 632 measured feeder power");
hold on;

plot(peakSimTime, peakFeederKW, "o", ...
    "MarkerSize", 8, ...
    "LineWidth", 1.5, ...
    "DisplayName", sprintf("Peak = %.1f kW", peakFeederKW));

yline(0, "-", "HandleVisibility", "off");
hold off;

grid on;
box on;
xlabel("Simulated date/time");
ylabel("Measured feeder active power (kW)");
title("Experiment 1 (QP): Measured Feeder Active Power at Node 632");
subtitle(sprintf("Peak %.1f kW at %s", ...
    peakFeederKW, char(string(peakSimTime, "dd-MMM HH:mm"))));
legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);
formatDateAxis(gca);

saveAssessmentFigure(fig1, outputDir, ...
    "01_Exp1_Node632_Feeder_Active_Power", SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 2 - REQUIRED: ALL TIME-VARYING NODE-PHASE ACTIVE POWERS
% ========================================================================

powerFields = string(fieldnames(powerSeries));
nPower = numel(powerFields);

fig2 = figure( ...
    "Name", "Exp1 - all time-varying active powers", ...
    "Color", "w", ...
    "Position", [20 20 1650 950]);

tl2 = tiledlayout(4,4, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl2, ...
    "Experiment 1 (QP): Measured Active Power at Time-Varying Node-Phases", ...
    "FontWeight", "bold");

for k = 1:nPower
    field = powerFields(k);
    s = powerSeries.(field);

    nexttile;
    plot(s.simTime, s.kW, "LineWidth", LINE_WIDTH);
    hold on;
    yline(0, "-", "HandleVisibility", "off");
    hold off;

    grid on;
    box on;
    title(canonicalPowerLabel(field));
    ylabel("kW");
    set(gca, "FontSize", 8);
    formatDateAxis(gca);
end

xlabel(tl2, "Simulated date/time");

saveAssessmentFigure(fig2, outputDir, ...
    "02_Exp1_All_TimeVarying_NodePhase_Active_Powers", SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 3 - REQUIRED: NODE 634 RMS VOLTAGES
% ========================================================================

node634Fields = voltageFields(startsWith(voltageFields, "N634_"));

fig3 = figure( ...
    "Name", "Exp1 - Node 634 RMS voltage", ...
    "Color", "w", ...
    "Position", [90 90 1250 650]);

hold on;

for k = 1:numel(node634Fields)
    f = node634Fields(k);
    s = voltageSeries.(f);

    plot(s.simTime, s.V, ...
        "LineWidth", 1.5, ...
        "DisplayName", sprintf("Phase %s", s.phase));
end

yline(LOWER_634_V, "--", ...
    sprintf("-5%% = %.2f V", LOWER_634_V), ...
    "LineWidth", LIMIT_LINE_WIDTH, ...
    "HandleVisibility", "off");

yline(UPPER_634_V, "--", ...
    sprintf("+5%% = %.2f V", UPPER_634_V), ...
    "LineWidth", LIMIT_LINE_WIDTH, ...
    "HandleVisibility", "off");

hold off;
grid on;
box on;
xlabel("Simulated date/time");
ylabel("RMS line-to-ground voltage (V)");
title("Experiment 1 (QP): Node 634 RMS Voltages");
subtitle("Nominal = 277 V, permitted range = 263.15 to 290.85 V");
legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);
formatDateAxis(gca);

saveAssessmentFigure(fig3, outputDir, ...
    "03_Exp1_Node634_RMS_Voltages", SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 4 - REQUIRED: ALL OTHER MONITORED RMS VOLTAGES
% Grouped by node, with phases overlaid.
% ========================================================================

otherFields = voltageFields(~startsWith(voltageFields, "N634_"));

otherNodes = strings(0);

for k = 1:numel(otherFields)
    otherNodes(end+1) = voltageSeries.(otherFields(k)).node; %#ok<SAGROW>
end

otherNodes = unique(otherNodes, "stable");
nNodes = numel(otherNodes);

fig4 = figure( ...
    "Name", "Exp1 - other monitored RMS voltages", ...
    "Color", "w", ...
    "Position", [10 10 1700 1000]);

nCols = 4;
nRows = ceil(nNodes/nCols);

tl4 = tiledlayout(nRows, nCols, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl4, ...
    "Experiment 1 (QP): RMS Voltages at All Other Monitored Feeder Nodes", ...
    "FontWeight", "bold");

for n = 1:nNodes
    node = otherNodes(n);
    nexttile;
    hold on;

    fieldsThisNode = strings(0);

    for k = 1:numel(otherFields)
        if voltageSeries.(otherFields(k)).node == node
            fieldsThisNode(end+1) = otherFields(k); %#ok<SAGROW>
        end
    end

    for k = 1:numel(fieldsThisNode)
        f = fieldsThisNode(k);
        s = voltageSeries.(f);

        plot(s.simTime, s.V, ...
            "LineWidth", 1.05, ...
            "DisplayName", sprintf("Phase %s", s.phase));
    end

    yline(LOWER_OTHER_V, "--", ...
        "LineWidth", 0.9, ...
        "HandleVisibility", "off");
    yline(UPPER_OTHER_V, "--", ...
        "LineWidth", 0.9, ...
        "HandleVisibility", "off");

    hold off;
    grid on;
    box on;

    title("Node " + node);
    ylabel("V");
    legend("Location", "best", "FontSize", 7);
    set(gca, "FontSize", 8);
    formatDateAxis(gca);
end

xlabel(tl4, "Simulated date/time");

saveAssessmentFigure(fig4, outputDir, ...
    "04_Exp1_All_Other_Monitored_RMS_Voltages", SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 5 - REQUIRED IF SCHEDULE CSV IS PRESENT:
% NODE 646 MEASURED BATTERY SOC
% ========================================================================

scheduleFile = findNewestFile(dataDir, "experiment1_qp_schedule*.csv");

if strlength(scheduleFile) > 0
    S = readtable(scheduleFile, ...
        "VariableNamingRule", "preserve", ...
        "TextType", "string");

    if ismember("soc646_measured_pct", string(S.Properties.VariableNames))

        if all(ismember(["date_label","profile_time"], ...
                string(S.Properties.VariableNames)))

            socTime = datetime( ...
                string(S.("date_label")) + " " + string(S.("profile_time")), ...
                "InputFormat", "d-MMM-yy H:mm", ...
                "Locale", "en_US");
        else
            socTime = SIM_FIRST_COMMAND_TIME + ...
                minutes((0:height(S)-1)' * 30);
        end

        socMeasured = S.("soc646_measured_pct");

        fig5 = figure( ...
            "Name", "Exp1 - Node 646 measured SoC", ...
            "Color", "w", ...
            "Position", [100 100 1250 650]);

        plot(socTime, socMeasured, ...
            "LineWidth", 1.7, ...
            "DisplayName", "Measured Node 646 SoC");
        hold on;

        if ismember("soc_predicted_pct", string(S.Properties.VariableNames))
            plot(socTime, S.("soc_predicted_pct"), "--", ...
                "LineWidth", 1.2, ...
                "DisplayName", "QP predicted SoC");
        end

        yline(0, ":", "HandleVisibility", "off");
        yline(100, ":", "HandleVisibility", "off");
        hold off;

        grid on;
        box on;
        xlabel("Simulated date/time");
        ylabel("Battery State of Charge (%)");
        title("Experiment 1 (QP): Node 646 Battery State of Charge");
        legend("Location", "best");
        ylim([-2 102]);
        set(gca, "FontSize", FONT_SIZE);
        formatDateAxis(gca);

        saveAssessmentFigure(fig5, outputDir, ...
            "05_Exp1_Node646_Measured_SoC", SAVE_PNG, SAVE_FIG);

        fprintf("Node 646 SoC schedule found: %s\n\n", scheduleFile);
    else
        warning("Schedule CSV found, but no soc646_measured_pct column exists.");
    end
else
    warning('%s', [ ...
        'No experiment1_qp_schedule*.csv was found. ' ...
        'Required Figure 5 (Node 646 measured SoC) was not produced.']);
end

%% ========================================================================
% ASSESSMENT Q1-Q3: VOLTAGE VIOLATIONS
% ========================================================================

voltageRows = table();

for k = 1:numel(voltageFields)
    f = voltageFields(k);
    s = voltageSeries.(f);

    values = s.V;
    under = values < s.lowerV;
    over  = values > s.upperV;
    violates = under | over;

    [minV, iMin] = min(values);
    [maxV, iMax] = max(values);

    minPU = minV / s.nominalV;
    maxPU = maxV / s.nominalV;

    if any(violates)
        badIdx = find(violates);
        firstIdx = badIdx(1);
        lastIdx  = badIdx(end);

        firstViolation = s.simTime(firstIdx);
        lastViolation  = s.simTime(lastIdx);

        % Worst deviation outside a limit.
        underMagnitude = max(0, s.lowerV - minV);
        overMagnitude  = max(0, maxV - s.upperV);

        if underMagnitude >= overMagnitude
            worstType = "UNDER";
            worstV = minV;
            worstTime = s.simTime(iMin);
            limitV = s.lowerV;
            worstMagnitude = underMagnitude;
        else
            worstType = "OVER";
            worstV = maxV;
            worstTime = s.simTime(iMax);
            limitV = s.upperV;
            worstMagnitude = overMagnitude;
        end
    else
        firstViolation = NaT;
        lastViolation = NaT;
        worstType = "NONE";
        worstV = NaN;
        worstTime = NaT;
        limitV = NaN;
        worstMagnitude = 0;
    end

    newRow = table( ...
        s.node, s.phase, s.nominalV, minV, minPU, maxV, maxPU, ...
        any(under), any(over), sum(under), sum(over), ...
        firstViolation, lastViolation, worstType, worstV, ...
        worstTime, limitV, worstMagnitude, ...
        'VariableNames', { ...
        'Node','Phase','Nominal_V','Min_V','Min_pu','Max_V','Max_pu', ...
        'UnderVoltage','OverVoltage','UnderSamples','OverSamples', ...
        'FirstViolation','LastViolation','WorstType','WorstVoltage_V', ...
        'WorstTime','RelevantLimit_V','ViolationMagnitude_V'});

    voltageRows = [voltageRows; newRow]; %#ok<AGROW>
end

violTable = voltageRows( ...
    voltageRows.UnderVoltage | voltageRows.OverVoltage, :);

writetable(voltageRows, ...
    fullfile(outputDir, "Experiment1_AllVoltageStatistics.csv"));

writetable(violTable, ...
    fullfile(outputDir, "Experiment1_VoltageViolations.csv"));

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 ORAL QUESTIONS - VOLTAGE\n");
fprintf("============================================================\n");

if isempty(violTable)
    fprintf("Q1: No monitored node-phase violates the +/-5%% voltage limits.\n");
else
    violatingNodes = unique(violTable.Node, "stable");

    fprintf("Q1 - Nodes with voltage violations:\n");
    fprintf("  %s\n", strjoin("Node " + violatingNodes, ", "));

    fprintf("\nQ2/Q3 - Timing and worst-case voltage violations:\n");

    for r = 1:height(violTable)
        fprintf([ ...
            "  Node %s Phase %s: %s; worst %.2f V at %s, " ...
            "limit %.2f V, violation %.2f V.\n"], ...
            violTable.Node(r), ...
            violTable.Phase(r), ...
            violTable.WorstType(r), ...
            violTable.WorstVoltage_V(r), ...
            formatTimestamp(violTable.WorstTime(r)), ...
            violTable.RelevantLimit_V(r), ...
            violTable.ViolationMagnitude_V(r));

        fprintf("      Violation window in capture: %s to %s\n", ...
            formatTimestamp(violTable.FirstViolation(r)), ...
            formatTimestamp(violTable.LastViolation(r)));
    end
end

%% ========================================================================
% FIGURE 6 - WORST MINIMUM PER-UNIT VOLTAGE
% Strong presentation figure for Q1-Q3.
% ========================================================================

labelsVoltage = "N" + voltageRows.Node + "-" + voltageRows.Phase;

[minPUSorted, orderV] = sort(voltageRows.Min_pu, "ascend");
labelsSorted = labelsVoltage(orderV);

fig6 = figure( ...
    "Name", "Exp1 - worst minimum voltage summary", ...
    "Color", "w", ...
    "Position", [120 80 1250 800]);

barh(categorical(labelsSorted, labelsSorted), minPUSorted);
hold on;
xline(0.95, "--", "0.95 pu lower limit", ...
    "LineWidth", 1.3);
xline(1.05, "--", "1.05 pu upper limit", ...
    "LineWidth", 1.3);
hold off;

grid on;
box on;
xlabel("Minimum measured RMS voltage (pu)");
ylabel("Node-phase");
title("Experiment 1 (QP): Worst Minimum Voltage at Each Monitored Node-Phase");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig6, outputDir, ...
    "06_Exp1_Worst_Minimum_Voltage_Summary", SAVE_PNG, SAVE_FIG);

%% ========================================================================
% ASSESSMENT Q4-Q6: REVERSE ACTIVE POWER FLOW
% ========================================================================

reverseRows = table();

for k = 1:nPower
    field = powerFields(k);
    s = powerSeries.(field);

    nodePhase = split(field, "_");
    node = erase(nodePhase(1), "N");
    phase = nodePhase(2);

    reverseMask = s.kW < 0;

    if any(reverseMask)
        [minKW, minIdx] = min(s.kW);
        badIdx = find(reverseMask);

        firstReverse = s.simTime(badIdx(1));
        lastReverse  = s.simTime(badIdx(end));
        worstTime = s.simTime(minIdx);
    else
        minKW = min(s.kW);
        firstReverse = NaT;
        lastReverse = NaT;
        worstTime = NaT;
    end

    newRow = table( ...
        string(node), string(phase), any(reverseMask), minKW, ...
        firstReverse, lastReverse, worstTime, ...
        'VariableNames', { ...
        'Node','Phase','ReverseFlow','MinimumPower_kW', ...
        'FirstReverseFlow','LastReverseFlow','WorstReverseTime'});

    reverseRows = [reverseRows; newRow]; %#ok<AGROW>
end

reverseTable = reverseRows(reverseRows.ReverseFlow, :);

writetable(reverseRows, ...
    fullfile(outputDir, "Experiment1_AllActivePowerStatistics.csv"));

writetable(reverseTable, ...
    fullfile(outputDir, "Experiment1_ReversePowerFlow.csv"));

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 ORAL QUESTIONS - REVERSE POWER FLOW\n");
fprintf("============================================================\n");

if isempty(reverseTable)
    fprintf("Q4: No monitored node-phase exhibits reverse active power flow.\n");
else
    reverseNodes = unique(reverseTable.Node, "stable");

    fprintf("Q4 - Nodes exhibiting reverse active power flow:\n");
    fprintf("  %s\n", strjoin("Node " + reverseNodes, ", "));

    fprintf("\nQ5/Q6 - Timing and largest reverse flow by node-phase:\n");

    for r = 1:height(reverseTable)
        fprintf([ ...
            "  Node %s Phase %s: minimum %.2f kW at %s; " ...
            "reverse-flow window %s to %s.\n"], ...
            reverseTable.Node(r), ...
            reverseTable.Phase(r), ...
            reverseTable.MinimumPower_kW(r), ...
            formatTimestamp(reverseTable.WorstReverseTime(r)), ...
            formatTimestamp(reverseTable.FirstReverseFlow(r)), ...
            formatTimestamp(reverseTable.LastReverseFlow(r)));
    end
end

%% ========================================================================
% FIGURE 7 - LARGEST REVERSE ACTIVE POWER BY NODE-PHASE
% ========================================================================

[minPowerSorted, orderP] = sort(reverseRows.MinimumPower_kW, "ascend");
labelsPower = "N" + reverseRows.Node + "-" + reverseRows.Phase;
labelsPower = labelsPower(orderP);

fig7 = figure( ...
    "Name", "Exp1 - reverse active power summary", ...
    "Color", "w", ...
    "Position", [130 80 1250 750]);

barh(categorical(labelsPower, labelsPower), minPowerSorted);
hold on;
xline(0, "-", "0 kW");
hold off;

grid on;
box on;
xlabel("Minimum measured active power (kW)");
ylabel("Node-phase");
title("Experiment 1 (QP): Largest Reverse Active-Power Flow by Node-Phase");
subtitle("Negative active power indicates reverse power flow");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig7, outputDir, ...
    "07_Exp1_Reverse_Power_Flow_Summary", SAVE_PNG, SAVE_FIG);

%% ========================================================================
% ASSESSMENT Q7-Q10: FEEDER PEAK AND NODE CONTRIBUTIONS
% ========================================================================

% Interpolate every node-phase active-power trace at the measured Node 632
% peak time, then sum phases by physical node.
contribRows = table();

for k = 1:nPower
    field = powerFields(k);
    s = powerSeries.(field);

    pAtPeak = interp1( ...
        s.realTime, s.kW, peakRealTime, ...
        "linear", "extrap");

    parts = split(field, "_");
    node = erase(parts(1), "N");
    phase = parts(2);

    newRow = table( ...
        string(node), string(phase), pAtPeak, ...
        'VariableNames', {'Node','Phase','PowerAtFeederPeak_kW'});

    contribRows = [contribRows; newRow]; %#ok<AGROW>
end

nodesMeasured = unique(contribRows.Node, "stable");
nodeTotals = zeros(numel(nodesMeasured),1);

for n = 1:numel(nodesMeasured)
    nodeTotals(n) = sum( ...
        contribRows.PowerAtFeederPeak_kW( ...
        contribRows.Node == nodesMeasured(n)), ...
        "omitnan");
end

[nodeTotalsSorted, orderNode] = sort(nodeTotals, "descend");
nodesSorted = nodesMeasured(orderNode);

peakContributionTable = table( ...
    nodesSorted, nodeTotalsSorted, ...
    100 * nodeTotalsSorted / peakFeederKW, ...
    'VariableNames', {'Node','MeasuredContribution_kW','ShareOfFeederPeak_pct'});

writetable(peakContributionTable, ...
    fullfile(outputDir, "Experiment1_PeakLoad_NodeContributions.csv"));

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 ORAL QUESTIONS - FEEDER PEAK\n");
fprintf("============================================================\n");

fprintf("Q7 - Highest total feeder net load occurs at:\n");
fprintf("  %s\n", formatTimestamp(peakSimTime));

fprintf("\nQ8 - Peak measured feeder net load:\n");
fprintf("  %.3f kW (%.3f MW)\n", peakFeederKW, peakFeederKW/1000);

fprintf("\nQ9 - Measurement method:\n");
fprintf([ ...
    "  Node 632 is at the feeder head. The Typhoon Power Meter measures\n" ...
    "  three-phase active power and Probe1 logs the measured feeder active\n" ...
    "  power. Peak feeder net load is the maximum of Node 632.Probe1.\n"]);

fprintf("\nQ10 - Measured node contributions at the feeder peak:\n");
disp(peakContributionTable);

fprintf([ ...
    "NOTE: The Module 1 comparison part of Q1 and Q10 requires your\n" ...
    "Module 1 no-control data. This script reports Experiment 1 itself.\n"]);

%% ========================================================================
% FIGURE 8 - NODE CONTRIBUTIONS AT MEASURED FEEDER PEAK
% ========================================================================

fig8 = figure( ...
    "Name", "Exp1 - node contributions at feeder peak", ...
    "Color", "w", ...
    "Position", [140 100 1150 650]);

bar(categorical("Node " + nodesSorted, "Node " + nodesSorted), ...
    nodeTotalsSorted);

grid on;
box on;
ylabel("Measured active-power contribution (kW)");
xlabel("Node");
title("Experiment 1 (QP): Node Contributions at Measured Feeder Peak");
subtitle(sprintf("Node 632 feeder peak = %.1f kW at %s", ...
    peakFeederKW, char(string(peakSimTime, "dd-MMM HH:mm"))));
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig8, outputDir, ...
    "08_Exp1_Node_Contributions_At_Feeder_Peak", SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 9 - VOLTAGE PROFILE AT FEEDER PEAK
% Useful for explaining how the peak-load period affects feeder voltage.
% ========================================================================

peakVoltageRows = table();

for k = 1:numel(voltageFields)
    f = voltageFields(k);
    s = voltageSeries.(f);

    vAtPeak = interp1( ...
        s.realTime, s.V, peakRealTime, ...
        "linear", "extrap");

    puAtPeak = vAtPeak / s.nominalV;

    newRow = table( ...
        s.node, s.phase, vAtPeak, puAtPeak, ...
        'VariableNames', {'Node','Phase','VoltageAtPeak_V','VoltageAtPeak_pu'});

    peakVoltageRows = [peakVoltageRows; newRow]; %#ok<AGROW>
end

[peakPUSorted, orderPeakV] = sort(peakVoltageRows.VoltageAtPeak_pu, "ascend");
peakLabels = "N" + peakVoltageRows.Node + "-" + peakVoltageRows.Phase;
peakLabels = peakLabels(orderPeakV);

fig9 = figure( ...
    "Name", "Exp1 - voltage profile at feeder peak", ...
    "Color", "w", ...
    "Position", [150 80 1250 800]);

barh(categorical(peakLabels, peakLabels), peakPUSorted);
hold on;
xline(0.95, "--", "0.95 pu lower limit", "LineWidth", 1.2);
xline(1.05, "--", "1.05 pu upper limit", "LineWidth", 1.2);
hold off;

grid on;
box on;
xlabel("RMS voltage at feeder peak (pu)");
ylabel("Node-phase");
title("Experiment 1 (QP): Feeder Voltage Profile at Peak Net Load");
subtitle(sprintf("Peak %.1f kW at %s", ...
    peakFeederKW, char(string(peakSimTime, "dd-MMM HH:mm"))));
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig9, outputDir, ...
    "09_Exp1_Voltage_Profile_At_Feeder_Peak", SAVE_PNG, SAVE_FIG);

writetable(peakVoltageRows, ...
    fullfile(outputDir, "Experiment1_Voltages_At_Feeder_Peak.csv"));

%% ========================================================================
% SHORT PRESENTATION SUMMARY
% ========================================================================

fprintf("\n============================================================\n");
fprintf(" PRESENTATION SUMMARY\n");
fprintf("============================================================\n");
fprintf("Peak feeder power : %.3f MW at %s\n", ...
    peakFeederKW/1000, formatTimestamp(peakSimTime));

if ~isempty(violTable)
    violatingNodes = unique(violTable.Node, "stable");
    fprintf("Voltage violations: %s\n", ...
        strjoin("Node " + violatingNodes, ", "));

    [~, worstIdx] = max(violTable.ViolationMagnitude_V);
    fprintf("Worst violation : Node %s Phase %s, %.2f V at %s\n", ...
        violTable.Node(worstIdx), ...
        violTable.Phase(worstIdx), ...
        violTable.WorstVoltage_V(worstIdx), ...
        formatTimestamp(violTable.WorstTime(worstIdx)));
else
    fprintf("Voltage violations: none\n");
end

if ~isempty(reverseTable)
    reverseNodes = unique(reverseTable.Node, "stable");
    fprintf("Reverse-flow nodes: %s\n", ...
        strjoin("Node " + reverseNodes, ", "));

    [worstReverse, worstReverseIdx] = min(reverseTable.MinimumPower_kW);
    fprintf("Largest reverse flow: %.2f kW at Node %s Phase %s (%s)\n", ...
        worstReverse, ...
        reverseTable.Node(worstReverseIdx), ...
        reverseTable.Phase(worstReverseIdx), ...
        formatTimestamp(reverseTable.WorstReverseTime(worstReverseIdx)));
else
    fprintf("Reverse-flow nodes: none\n");
end

fprintf("Top peak contributor: Node %s = %.2f kW (%.2f%% of feeder peak)\n", ...
    peakContributionTable.Node(1), ...
    peakContributionTable.MeasuredContribution_kW(1), ...
    peakContributionTable.ShareOfFeederPeak_pct(1));

fprintf("\nAll figures and tables saved to:\n  %s\n", outputDir);
fprintf("============================================================\n");


%% ========================================================================
% LOCAL FUNCTIONS
% ========================================================================

function T = readTyphoonCsv(path)
    assert(isfile(path), "Required file not found: %s", path);

    T = readtable(path, ...
        "VariableNamingRule", "preserve");

    assert(ismember("Time", string(T.Properties.VariableNames)), ...
        "Typhoon CSV does not contain a Time column: %s", path);
end


function T = cropByRealTime(T, startS, endS)
    mask = T.("Time") >= startS & T.("Time") <= endS;
    T = T(mask,:);

    assert(~isempty(T), ...
        "No samples remain after cropping to %.2f-%.2f s.", ...
        startS, endS);
end


function simTime = realToSimTime(realTime, startRealS, firstCommandTime, hoursPerRealSecond)
    simTime = firstCommandTime + ...
        hours((realTime - startRealS) * hoursPerRealSecond);
end


function label = canonicalPowerLabel(field)
    parts = split(string(field), "_");

    if numel(parts) == 2
        label = "Node " + erase(parts(1), "N") + " Phase " + parts(2);
    else
        label = string(field);
    end
end


function pathOut = findNewestFile(folder, pattern)
    d = dir(fullfile(folder, pattern));

    if isempty(d)
        pathOut = "";
        return;
    end

    [~, idx] = max([d.datenum]);
    pathOut = string(fullfile(d(idx).folder, d(idx).name));
end


function formatDateAxis(ax)
    try
        xtickformat(ax, "dd-MMM HH:mm");
    catch
    end

    ax.XTickLabelRotation = 30;
    ax.XGrid = "on";
    ax.YGrid = "on";
end


function text = formatTimestamp(t)
    if isnat(t)
        text = "N/A";
    else
        text = char(string(t, "dd-MMM-yyyy HH:mm"));
    end
end


function saveAssessmentFigure(fig, outputDir, baseName, savePng, saveFig)
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
