%% ECE4191 Module 3 - Experiment 1 (QP)
% ROBUST FULL ASSESSMENT / PRESENTATION PLOTTING SCRIPT
%
% This version avoids brittle exact Typhoon signal-name matching.
% It searches the actual CSV headers for the required node/phase signals and
% continues with a warning if a non-critical channel is missing, rather than
% stopping the whole script.
%
% Expected Experiment 1 files:
%   measured_activePower1.csv
%   measured_activePower2.csv
%   node632_probe1.csv
%   node634_rmsVoltage.csv
%   rmsVoltage1.csv
%   rmsVoltage2.csv
%   rmsVoltage3.csv
%
% Optional:
%   experiment1_qp_schedule*.csv
%       Used for the Node 646 measured SoC figure.
%
% Required Experiment 1 plots:
%   1. Feeder active power at Node 632
%   2. Active power at all monitored time-varying node-phase loads
%   3. Node 634 RMS voltage A/B/C with +/-5% limits about 277 V
%   4. RMS voltages at all other monitored feeder nodes with +/-5% limits
%      about 2401 V
%   5. Measured Node 646 battery SoC, if the controller CSV is present
%
% Additional assessment figures:
%   6. Worst minimum per-unit voltage by node-phase
%   7. Largest reverse active power by node-phase
%   8. Node contributions at measured feeder peak
%   9. Voltage profile at measured feeder peak
%
% Time mapping:
%   2 real seconds = 30 simulated minutes
%   96 real seconds = 1 simulated day
%   480 real seconds = 5 simulated days
%
% If Signal Analyzer started before the Raspberry Pi playback, modify
% PLAYBACK_START_REAL_S below.

clear;
clc;
close all;

%% ========================================================================
% USER SETTINGS
% ========================================================================

ACTIVE_POWER_FILES = [
    "measured_activePower1.csv"
    "measured_activePower2.csv"
];

FEEDER_POWER_FILE = "node632_probe1.csv";

VOLTAGE_FILES = [
    "node634_rmsVoltage.csv"
    "rmsVoltage1.csv"
    "rmsVoltage2.csv"
    "rmsVoltage3.csv"
];

% Optional schedule/log CSV. Leave blank for automatic detection.
SCHEDULE_FILE = "";

% Five-day QP playback.
PLAYBACK_START_REAL_S = 0.0;
PLAYBACK_DURATION_REAL_S = 480.0;
PLAYBACK_END_REAL_S = PLAYBACK_START_REAL_S + PLAYBACK_DURATION_REAL_S;

REAL_SECONDS_PER_DATA_STEP = 2.0;
SIM_HOURS_PER_DATA_STEP = 0.5;
SIM_HOURS_PER_REAL_SECOND = ...
    SIM_HOURS_PER_DATA_STEP / REAL_SECONDS_PER_DATA_STEP;

% First half-hour interval in the experiment.
SIM_FIRST_COMMAND_TIME = datetime(2013,1,7,0,30,0);

% Assessment voltage limits.
NOMINAL_634_V = 277.0;
NOMINAL_OTHER_V = 2401.0;

LOWER_634_V = 0.95 * NOMINAL_634_V;
UPPER_634_V = 1.05 * NOMINAL_634_V;

LOWER_OTHER_V = 0.95 * NOMINAL_OTHER_V;
UPPER_OTHER_V = 1.05 * NOMINAL_OTHER_V;

% Output settings.
SAVE_PNG = true;
SAVE_FIG = true;
OUTPUT_FOLDER = "Experiment1_Assessment_Output_Robust";

FONT_SIZE = 10;
LINE_WIDTH = 1.35;
LIMIT_LINE_WIDTH = 1.15;

%% ========================================================================
% DATA DIRECTORY
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
fprintf(" FIXED ROBUST ASSESSMENT ANALYSIS - 11 SEP VERSION\n");
fprintf("============================================================\n");
fprintf("Data folder       : %s\n", dataDir);
fprintf("Output folder     : %s\n", outputDir);
fprintf("Playback real time: %.2f to %.2f s\n", ...
    PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
fprintf("Playback length   : 5 simulated days\n\n");

%% ========================================================================
% LOAD ACTIVE-POWER CSVs
% ========================================================================

powerTables = cell(numel(ACTIVE_POWER_FILES), 1);

for k = 1:numel(ACTIVE_POWER_FILES)
    path = fullfile(dataDir, ACTIVE_POWER_FILES(k));
    powerTables{k} = readTyphoonCsv(path);
    powerTables{k} = cropByRealTime( ...
        powerTables{k}, ...
        PLAYBACK_START_REAL_S, ...
        PLAYBACK_END_REAL_S);
end

% Required monitored time-varying node-phase combinations available in the
% Experiment 1 exports.
requiredPowerChannels = [
    "611_C"
    "634_A"
    "634_B"
    "634_C"
    "645_B"
    "646_B"
    "652_A"
    "671_A"
    "671_B"
    "671_C"
    "675_A"
    "675_B"
    "675_C"
    "692_C"
];

powerSeries = struct();
missingPowerChannels = strings(0);

for k = 1:numel(requiredPowerChannels)
    canonical = requiredPowerChannels(k);

    [found, tableIndex, columnName] = ...
        findPowerSignal(powerTables, canonical);

    if ~found
        warning("Active-power channel %s was not found. Continuing without it.", canonical);
        missingPowerChannels(end+1) = canonical; %#ok<SAGROW>
        continue;
    end

    T = powerTables{tableIndex};
    field = "N" + canonical;

    powerSeries.(char(field)).realTime = T.("Time");
    powerSeries.(char(field)).simTime = realToSimTime( ...
        T.("Time"), ...
        PLAYBACK_START_REAL_S, ...
        SIM_FIRST_COMMAND_TIME, ...
        SIM_HOURS_PER_REAL_SECOND);

    % Typhoon P_measured exports are in watts.
    powerSeries.(char(field)).kW = T.(char(columnName)) / 1000.0;
    powerSeries.(char(field)).sourceColumn = columnName;

    fprintf("Power %-6s -> %s\n", canonical, columnName);
end

powerFields = string(fieldnames(powerSeries));

if isempty(powerFields)
    fprintf("\nNo monitored power channels were matched. CSV headers read were:\n");
    for tt = 1:numel(powerTables)
        fprintf("\n--- %s ---\n", ACTIVE_POWER_FILES(tt));
        disp(string(powerTables{tt}.Properties.VariableNames)');
    end
    error([ ...
        "No monitored active-power channels were found. " ...
        "Check that this FIXED script is being run with the Experiment 1 " ...
        "files measured_activePower1.csv and measured_activePower2.csv."]);
end

if ~isempty(missingPowerChannels)
    fprintf("\nWARNING: Missing active-power channels:\n  %s\n\n", ...
        strjoin(missingPowerChannels, ", "));
end

%% ========================================================================
% LOAD NODE 632 FEEDER POWER
% ========================================================================

PF = readTyphoonCsv(fullfile(dataDir, FEEDER_POWER_FILE));
PF = cropByRealTime( ...
    PF, ...
    PLAYBACK_START_REAL_S, ...
    PLAYBACK_END_REAL_S);

[found632, feederColumn] = findColumnContaining( ...
    string(PF.Properties.VariableNames), ...
    ["632", "Probe"]);

if ~found632
    error("Could not locate the Node 632 feeder-power probe column.");
end

feederRealTime = PF.("Time");
feederSimTime = realToSimTime( ...
    feederRealTime, ...
    PLAYBACK_START_REAL_S, ...
    SIM_FIRST_COMMAND_TIME, ...
    SIM_HOURS_PER_REAL_SECOND);

feederKW = PF.(char(feederColumn)) / 1000.0;

fprintf("Feeder power -> %s\n\n", feederColumn);

%% ========================================================================
% LOAD VOLTAGE CSVs
% ========================================================================

voltageTables = cell(numel(VOLTAGE_FILES), 1);

for k = 1:numel(VOLTAGE_FILES)
    path = fullfile(dataDir, VOLTAGE_FILES(k));
    voltageTables{k} = readTyphoonCsv(path);
    voltageTables{k} = cropByRealTime( ...
        voltageTables{k}, ...
        PLAYBACK_START_REAL_S, ...
        PLAYBACK_END_REAL_S);
end

voltageSeries = struct();

for t = 1:numel(voltageTables)
    T = voltageTables{t};
    names = string(T.Properties.VariableNames);

    for k = 1:numel(names)
        name = names(k);

        % Ignore metadata / exported limit traces. We calculate assessment
        % limits directly from the specified nominal voltages.
        if name == "Time" || ...
                contains(lower(name), "upperbound") || ...
                contains(lower(name), "lowerbound")
            continue;
        end

        token = regexp( ...
            char(name), ...
            '^Node\s+(\d+)\.V([123])_rms$', ...
            'tokens', ...
            'once');

        if isempty(token)
            continue;
        end

        node = string(token{1});
        phaseNumber = str2double(token{2});
        phaseLetters = 'ABC';
        phase = string(phaseLetters(phaseNumber));

        canonical = "N" + node + "_" + phase;

        % If the same channel appears twice, keep the first occurrence.
        if isfield(voltageSeries, char(canonical))
            continue;
        end

        voltageSeries.(char(canonical)).node = node;
        voltageSeries.(char(canonical)).phase = phase;
        voltageSeries.(char(canonical)).realTime = T.("Time");
        voltageSeries.(char(canonical)).simTime = realToSimTime( ...
            T.("Time"), ...
            PLAYBACK_START_REAL_S, ...
            SIM_FIRST_COMMAND_TIME, ...
            SIM_HOURS_PER_REAL_SECOND);
        voltageSeries.(char(canonical)).V = T.(char(name));
        voltageSeries.(char(canonical)).sourceColumn = name;

        if node == "634"
            voltageSeries.(char(canonical)).nominalV = NOMINAL_634_V;
            voltageSeries.(char(canonical)).lowerV = LOWER_634_V;
            voltageSeries.(char(canonical)).upperV = UPPER_634_V;
        else
            voltageSeries.(char(canonical)).nominalV = NOMINAL_OTHER_V;
            voltageSeries.(char(canonical)).lowerV = LOWER_OTHER_V;
            voltageSeries.(char(canonical)).upperV = UPPER_OTHER_V;
        end
    end
end

voltageFields = string(fieldnames(voltageSeries));

if isempty(voltageFields)
    error("No RMS-voltage channels were found in the supplied CSVs.");
end

fprintf("Voltage channels found: %d\n\n", numel(voltageFields));

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
    peakFeederKW, ...
    char(string(peakSimTime, "dd-MMM HH:mm"))));
legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);
formatDateAxis(gca);

saveAssessmentFigure( ...
    fig1, outputDir, ...
    "01_Exp1_Node632_Feeder_Active_Power", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 2 - REQUIRED: ALL MONITORED TIME-VARYING ACTIVE POWERS
% ========================================================================

nPower = numel(powerFields);

fig2 = figure( ...
    "Name", "Exp1 - time-varying active powers", ...
    "Color", "w", ...
    "Position", [20 20 1650 950]);

nCols = 4;
nRows = ceil(nPower / nCols);

tl2 = tiledlayout(nRows, nCols, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl2, ...
    "Experiment 1 (QP): Measured Active Power at Time-Varying Node-Phases", ...
    "FontWeight", "bold");

for k = 1:nPower
    field = powerFields(k);
    s = powerSeries.(char(field));

    nexttile;

    plot(s.simTime, s.kW, ...
        "LineWidth", LINE_WIDTH);

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

saveAssessmentFigure( ...
    fig2, outputDir, ...
    "02_Exp1_All_TimeVarying_NodePhase_Active_Powers", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 3 - REQUIRED: NODE 634 RMS VOLTAGES
% ========================================================================

node634Fields = voltageFields(startsWith(voltageFields, "N634_"));

if isempty(node634Fields)
    warning("No Node 634 voltage channels were found; Figure 3 cannot be produced.");
else
    fig3 = figure( ...
        "Name", "Exp1 - Node 634 RMS voltage", ...
        "Color", "w", ...
        "Position", [90 90 1250 650]);

    hold on;

    for k = 1:numel(node634Fields)
        f = node634Fields(k);
        s = voltageSeries.(char(f));

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
    subtitle("Nominal = 277 V; permitted range = 263.15 to 290.85 V");
    legend("Location", "best");
    set(gca, "FontSize", FONT_SIZE);
    formatDateAxis(gca);

    saveAssessmentFigure( ...
        fig3, outputDir, ...
        "03_Exp1_Node634_RMS_Voltages", ...
        SAVE_PNG, SAVE_FIG);
end

%% ========================================================================
% FIGURE 4 - REQUIRED: ALL OTHER MONITORED RMS VOLTAGES
% ========================================================================

otherFields = voltageFields(~startsWith(voltageFields, "N634_"));

otherNodes = strings(0);

for k = 1:numel(otherFields)
    s = voltageSeries.(char(otherFields(k)));
    otherNodes(end+1) = s.node; %#ok<SAGROW>
end

otherNodes = unique(otherNodes, "stable");

if isempty(otherNodes)
    warning("No non-634 voltage channels were found; Figure 4 cannot be produced.");
else
    nNodes = numel(otherNodes);

    fig4 = figure( ...
        "Name", "Exp1 - other monitored RMS voltages", ...
        "Color", "w", ...
        "Position", [10 10 1700 1000]);

    nCols = 4;
    nRows = ceil(nNodes / nCols);

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
            s = voltageSeries.(char(otherFields(k)));

            if s.node == node
                fieldsThisNode(end+1) = otherFields(k); %#ok<SAGROW>
            end
        end

        for k = 1:numel(fieldsThisNode)
            f = fieldsThisNode(k);
            s = voltageSeries.(char(f));

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

    saveAssessmentFigure( ...
        fig4, outputDir, ...
        "04_Exp1_All_Other_Monitored_RMS_Voltages", ...
        SAVE_PNG, SAVE_FIG);
end

%% ========================================================================
% FIGURE 5 - REQUIRED IF SCHEDULE CSV IS AVAILABLE: NODE 646 SOC
% ========================================================================

scheduleFile = resolveScheduleFile( ...
    dataDir, ...
    SCHEDULE_FILE, ...
    ["experiment1_qp_schedule*.csv", "*qp*schedule*.csv"]);

if strlength(scheduleFile) > 0

    S = readtable(scheduleFile, ...
        "VariableNamingRule", "preserve", ...
        "TextType", "string");

    scheduleNames = string(S.Properties.VariableNames);

    if ismember("soc646_measured_pct", scheduleNames)

        nRows = min(height(S), 240);
        S = S(1:nRows,:);

        if all(ismember(["date_label","profile_time"], ...
                string(S.Properties.VariableNames)))

            socTime = datetime( ...
                string(S.("date_label")) + " " + ...
                string(S.("profile_time")), ...
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

        if ismember("soc_predicted_pct", ...
                string(S.Properties.VariableNames))

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

        saveAssessmentFigure( ...
            fig5, outputDir, ...
            "05_Exp1_Node646_Measured_SoC", ...
            SAVE_PNG, SAVE_FIG);

        fprintf("Node 646 SoC schedule found: %s\n\n", scheduleFile);

    else
        warning("Schedule CSV found, but soc646_measured_pct is absent.");
    end

else
    warning('%s', [ ...
        'No Experiment 1 QP schedule CSV was found. ' ...
        'Figure 5 (Node 646 measured SoC) was skipped.']);
end

%% ========================================================================
% Q1-Q3: VOLTAGE VIOLATIONS
% ========================================================================

voltageRows = table();
voltageEventRows = table();

for k = 1:numel(voltageFields)

    f = voltageFields(k);
    s = voltageSeries.(char(f));

    values = s.V;
    under = values < s.lowerV;
    over = values > s.upperV;
    violates = under | over;

    [minV, iMin] = min(values);
    [maxV, iMax] = max(values);

    minPU = minV / s.nominalV;
    maxPU = maxV / s.nominalV;

    if any(violates)

        badIdx = find(violates);
        firstViolation = s.simTime(badIdx(1));
        lastViolation = s.simTime(badIdx(end));

        underMagnitude = max(0, s.lowerV - minV);
        overMagnitude = max(0, maxV - s.upperV);

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

        intervals = logicalIntervals(violates);

        for q = 1:height(intervals)

            iStart = intervals.StartIndex(q);
            iEnd = intervals.EndIndex(q);

            eventType = "MIXED";

            if all(under(iStart:iEnd))
                eventType = "UNDER";
            elseif all(over(iStart:iEnd))
                eventType = "OVER";
            end

            eventRow = table( ...
                s.node, ...
                s.phase, ...
                eventType, ...
                s.simTime(iStart), ...
                s.simTime(iEnd), ...
                'VariableNames', { ...
                'Node','Phase','Type','StartTime','EndTime'});

            voltageEventRows = [voltageEventRows; eventRow]; %#ok<AGROW>
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
        s.node, ...
        s.phase, ...
        s.nominalV, ...
        minV, ...
        minPU, ...
        maxV, ...
        maxPU, ...
        any(under), ...
        any(over), ...
        sum(under), ...
        sum(over), ...
        firstViolation, ...
        lastViolation, ...
        worstType, ...
        worstV, ...
        worstTime, ...
        limitV, ...
        worstMagnitude, ...
        'VariableNames', { ...
        'Node','Phase','Nominal_V', ...
        'Min_V','Min_pu','Max_V','Max_pu', ...
        'UnderVoltage','OverVoltage', ...
        'UnderSamples','OverSamples', ...
        'FirstViolation','LastViolation', ...
        'WorstType','WorstVoltage_V','WorstTime', ...
        'RelevantLimit_V','ViolationMagnitude_V'});

    voltageRows = [voltageRows; newRow]; %#ok<AGROW>
end

violTable = voltageRows( ...
    voltageRows.UnderVoltage | voltageRows.OverVoltage, :);

writetable( ...
    voltageRows, ...
    fullfile(outputDir, "Experiment1_AllVoltageStatistics.csv"));

writetable( ...
    violTable, ...
    fullfile(outputDir, "Experiment1_VoltageViolations.csv"));

if ~isempty(voltageEventRows)

    writetable( ...
        voltageEventRows, ...
        fullfile(outputDir, ...
        "Experiment1_VoltageViolationIntervals.csv"));
end

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 Q1-Q3 - VOLTAGE VIOLATIONS\n");
fprintf("============================================================\n");

if isempty(violTable)

    fprintf("Q1: No monitored node-phase violates the +/-5%% limits.\n");

else

    violatingNodes = unique(violTable.Node, "stable");

    fprintf("Q1 - Nodes with voltage violations:\n");
    fprintf("  %s\n", ...
        strjoin("Node " + violatingNodes, ", "));

    fprintf("\nQ2/Q3 - Timing and worst violation by node-phase:\n");

    for r = 1:height(violTable)

        fprintf([ ...
            "  Node %s Phase %s: %s; worst %.2f V at %s; " ...
            "limit %.2f V; violation %.2f V.\n"], ...
            violTable.Node(r), ...
            violTable.Phase(r), ...
            violTable.WorstType(r), ...
            violTable.WorstVoltage_V(r), ...
            formatTimestamp(violTable.WorstTime(r)), ...
            violTable.RelevantLimit_V(r), ...
            violTable.ViolationMagnitude_V(r));
    end
end

%% ========================================================================
% FIGURE 6 - WORST MINIMUM PER-UNIT VOLTAGE
% ========================================================================

labelsVoltage = "N" + voltageRows.Node + "-" + voltageRows.Phase;

[minPUSorted, orderV] = sort( ...
    voltageRows.Min_pu, ...
    "ascend");

labelsSorted = labelsVoltage(orderV);

fig6 = figure( ...
    "Name", "Exp1 - worst minimum voltage", ...
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
title("Experiment 1 (QP): Worst Minimum Voltage by Node-Phase");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure( ...
    fig6, outputDir, ...
    "06_Exp1_Worst_Minimum_Voltage_Summary", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% Q4-Q6: REVERSE ACTIVE POWER FLOW
% ========================================================================

reverseRows = table();
reverseEventRows = table();

for k = 1:numel(powerFields)

    field = powerFields(k);
    s = powerSeries.(char(field));

    parts = split(field, "_");
    node = erase(parts(1), "N");
    phase = parts(2);

    reverseMask = s.kW < 0;

    if any(reverseMask)

        [minKW, minIdx] = min(s.kW);
        badIdx = find(reverseMask);

        firstReverse = s.simTime(badIdx(1));
        lastReverse = s.simTime(badIdx(end));
        worstTime = s.simTime(minIdx);

        intervals = logicalIntervals(reverseMask);

        for q = 1:height(intervals)

            iStart = intervals.StartIndex(q);
            iEnd = intervals.EndIndex(q);

            eventRow = table( ...
                string(node), ...
                string(phase), ...
                s.simTime(iStart), ...
                s.simTime(iEnd), ...
                'VariableNames', { ...
                'Node','Phase','StartTime','EndTime'});

            reverseEventRows = [reverseEventRows; eventRow]; %#ok<AGROW>
        end

    else

        minKW = min(s.kW);
        firstReverse = NaT;
        lastReverse = NaT;
        worstTime = NaT;
    end

    newRow = table( ...
        string(node), ...
        string(phase), ...
        any(reverseMask), ...
        minKW, ...
        firstReverse, ...
        lastReverse, ...
        worstTime, ...
        'VariableNames', { ...
        'Node','Phase','ReverseFlow','MinimumPower_kW', ...
        'FirstReverseFlow','LastReverseFlow','WorstReverseTime'});

    reverseRows = [reverseRows; newRow]; %#ok<AGROW>
end

reverseTable = reverseRows(reverseRows.ReverseFlow, :);

writetable( ...
    reverseRows, ...
    fullfile(outputDir, "Experiment1_AllActivePowerStatistics.csv"));

writetable( ...
    reverseTable, ...
    fullfile(outputDir, "Experiment1_ReversePowerFlow.csv"));

if ~isempty(reverseEventRows)

    writetable( ...
        reverseEventRows, ...
        fullfile(outputDir, ...
        "Experiment1_ReversePowerFlowIntervals.csv"));
end

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 Q4-Q6 - REVERSE POWER FLOW\n");
fprintf("============================================================\n");

if isempty(reverseTable)

    fprintf("Q4: No monitored node-phase exhibits reverse active power flow.\n");

else

    reverseNodes = unique(reverseTable.Node, "stable");

    fprintf("Q4 - Nodes with reverse active power flow:\n");
    fprintf("  %s\n", ...
        strjoin("Node " + reverseNodes, ", "));

    fprintf("\nQ5/Q6 - Largest reverse flow by node-phase:\n");

    for r = 1:height(reverseTable)

        fprintf([ ...
            "  Node %s Phase %s: minimum %.2f kW at %s.\n"], ...
            reverseTable.Node(r), ...
            reverseTable.Phase(r), ...
            reverseTable.MinimumPower_kW(r), ...
            formatTimestamp(reverseTable.WorstReverseTime(r)));
    end
end

%% ========================================================================
% FIGURE 7 - LARGEST REVERSE FLOW SUMMARY
% ========================================================================

[minPowerSorted, orderP] = sort( ...
    reverseRows.MinimumPower_kW, ...
    "ascend");

labelsPower = ...
    "N" + reverseRows.Node + "-" + reverseRows.Phase;
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
title("Experiment 1 (QP): Largest Reverse Active-Power Flow");
subtitle("Negative active power indicates reverse power flow");
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure( ...
    fig7, outputDir, ...
    "07_Exp1_Reverse_Power_Flow_Summary", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% Q7-Q10: FEEDER PEAK AND NODE CONTRIBUTIONS
% ========================================================================

contribRows = table();

for k = 1:numel(powerFields)

    field = powerFields(k);
    s = powerSeries.(char(field));

    pAtPeak = interp1( ...
        s.realTime, ...
        s.kW, ...
        peakRealTime, ...
        "linear", ...
        "extrap");

    parts = split(field, "_");
    node = erase(parts(1), "N");
    phase = parts(2);

    newRow = table( ...
        string(node), ...
        string(phase), ...
        pAtPeak, ...
        'VariableNames', { ...
        'Node','Phase','PowerAtFeederPeak_kW'});

    contribRows = [contribRows; newRow]; %#ok<AGROW>
end

nodesMeasured = unique(contribRows.Node, "stable");
nodeTotals = zeros(numel(nodesMeasured), 1);

for n = 1:numel(nodesMeasured)

    nodeTotals(n) = sum( ...
        contribRows.PowerAtFeederPeak_kW( ...
        contribRows.Node == nodesMeasured(n)), ...
        "omitnan");
end

[nodeTotalsSorted, orderNode] = sort( ...
    nodeTotals, ...
    "descend");

nodesSorted = nodesMeasured(orderNode);

peakContributionTable = table( ...
    nodesSorted, ...
    nodeTotalsSorted, ...
    100 * nodeTotalsSorted / peakFeederKW, ...
    'VariableNames', { ...
    'Node','MeasuredContribution_kW','ShareOfFeederPeak_pct'});

writetable( ...
    peakContributionTable, ...
    fullfile(outputDir, ...
    "Experiment1_PeakLoad_NodeContributions.csv"));

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 Q7-Q10 - FEEDER PEAK\n");
fprintf("============================================================\n");

fprintf("Q7 - Highest feeder net load occurs at:\n");
fprintf("  %s\n", formatTimestamp(peakSimTime));

fprintf("\nQ8 - Peak measured feeder net load:\n");
fprintf("  %.3f kW (%.3f MW)\n", ...
    peakFeederKW, ...
    peakFeederKW / 1000);

fprintf("\nQ9 - Measurement method:\n");
fprintf([ ...
    "  Node 632 is at the feeder head. The Typhoon Power Meter measures\n" ...
    "  three-phase feeder active power and Node 632.Probe1 records it.\n" ...
    "  Peak feeder net load is the maximum measured Probe1 value.\n"]);

fprintf("\nQ10 - Measured node contributions at feeder peak:\n");
disp(peakContributionTable);

%% ========================================================================
% FIGURE 8 - NODE CONTRIBUTIONS AT FEEDER PEAK
% ========================================================================

fig8 = figure( ...
    "Name", "Exp1 - node contributions at feeder peak", ...
    "Color", "w", ...
    "Position", [140 100 1150 650]);

bar( ...
    categorical("Node " + nodesSorted, "Node " + nodesSorted), ...
    nodeTotalsSorted);

grid on;
box on;
ylabel("Measured active-power contribution (kW)");
xlabel("Node");
title("Experiment 1 (QP): Node Contributions at Measured Feeder Peak");
subtitle(sprintf("Node 632 peak = %.1f kW at %s", ...
    peakFeederKW, ...
    char(string(peakSimTime, "dd-MMM HH:mm"))));
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure( ...
    fig8, outputDir, ...
    "08_Exp1_Node_Contributions_At_Feeder_Peak", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% FIGURE 9 - VOLTAGE PROFILE AT FEEDER PEAK
% ========================================================================

peakVoltageRows = table();

for k = 1:numel(voltageFields)

    f = voltageFields(k);
    s = voltageSeries.(char(f));

    vAtPeak = interp1( ...
        s.realTime, ...
        s.V, ...
        peakRealTime, ...
        "linear", ...
        "extrap");

    puAtPeak = vAtPeak / s.nominalV;

    status = "within";

    if puAtPeak < 0.95
        status = "UNDER";
    elseif puAtPeak > 1.05
        status = "OVER";
    end

    newRow = table( ...
        s.node, ...
        s.phase, ...
        vAtPeak, ...
        puAtPeak, ...
        status, ...
        'VariableNames', { ...
        'Node','Phase','VoltageAtPeak_V','VoltageAtPeak_pu','Status'});

    peakVoltageRows = [peakVoltageRows; newRow]; %#ok<AGROW>
end

writetable( ...
    peakVoltageRows, ...
    fullfile(outputDir, ...
    "Experiment1_Voltages_At_Feeder_Peak.csv"));

[peakPUSorted, orderPeakV] = sort( ...
    peakVoltageRows.VoltageAtPeak_pu, ...
    "ascend");

peakLabels = ...
    "N" + peakVoltageRows.Node + "-" + peakVoltageRows.Phase;
peakLabels = peakLabels(orderPeakV);

fig9 = figure( ...
    "Name", "Exp1 - voltage profile at feeder peak", ...
    "Color", "w", ...
    "Position", [150 80 1250 800]);

barh(categorical(peakLabels, peakLabels), peakPUSorted);
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
title("Experiment 1 (QP): Feeder Voltage Profile at Peak Net Load");
subtitle(sprintf("Peak %.1f kW at %s", ...
    peakFeederKW, ...
    char(string(peakSimTime, "dd-MMM HH:mm"))));
set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure( ...
    fig9, outputDir, ...
    "09_Exp1_Voltage_Profile_At_Feeder_Peak", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% PRESENTATION SUMMARY
% ========================================================================

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 PRESENTATION SUMMARY\n");
fprintf("============================================================\n");

fprintf("Peak feeder power : %.3f MW at %s\n", ...
    peakFeederKW / 1000, ...
    formatTimestamp(peakSimTime));

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

    [worstReverse, worstReverseIdx] = min( ...
        reverseTable.MinimumPower_kW);

    fprintf([ ...
        "Largest reverse flow: %.2f kW at " ...
        "Node %s Phase %s (%s)\n"], ...
        worstReverse, ...
        reverseTable.Node(worstReverseIdx), ...
        reverseTable.Phase(worstReverseIdx), ...
        formatTimestamp( ...
        reverseTable.WorstReverseTime(worstReverseIdx)));

else
    fprintf("Reverse-flow nodes: none\n");
end

fprintf("Top peak contributor: Node %s = %.2f kW (%.2f%%)\n", ...
    peakContributionTable.Node(1), ...
    peakContributionTable.MeasuredContribution_kW(1), ...
    peakContributionTable.ShareOfFeederPeak_pct(1));

fprintf("\nAll figures and tables saved to:\n  %s\n", outputDir);

if ~isempty(missingPowerChannels)
    fprintf("\nChannels not found and therefore omitted:\n  %s\n", ...
        strjoin(missingPowerChannels, ", "));
end

fprintf("============================================================\n");


%% ========================================================================
% LOCAL FUNCTIONS
% ========================================================================

function T = readTyphoonCsv(path)

    assert(isfile(path), ...
        "Required file not found: %s", path);

    T = readtable( ...
        path, ...
        "VariableNamingRule", "preserve");

    assert( ...
        ismember("Time", string(T.Properties.VariableNames)), ...
        "Typhoon CSV does not contain a Time column: %s", path);
end


function T = cropByRealTime(T, startS, endS)

    mask = ...
        T.("Time") >= startS & ...
        T.("Time") <= endS;

    T = T(mask,:);

    assert(~isempty(T), ...
        "No samples remain after cropping to %.2f-%.2f seconds.", ...
        startS, endS);
end


function simTime = realToSimTime( ...
    realTime, ...
    startRealS, ...
    firstCommandTime, ...
    hoursPerRealSecond)

    simTime = ...
        firstCommandTime + ...
        hours((realTime - startRealS) * hoursPerRealSecond);
end


function [found, tableIndex, columnName] = ...
    findPowerSignal(powerTables, canonical)

    found = false;
    tableIndex = NaN;
    columnName = "";

    parts = split(string(canonical), "_");
    node = parts(1);
    phase = parts(2);

    for t = 1:numel(powerTables)

        names = string(powerTables{t}.Properties.VariableNames);

        % Only inspect measured-power columns belonging to this node.
        nodeMask = ...
            contains(lower(names), ...
                lower("Time Varying Load " + node)) & ...
            contains(lower(names), "p_measured");

        candidates = names(nodeMask);

        if isempty(candidates)
            continue;
        end

        % Single-phase node exports. There should only be one P_measured
        % channel for these nodes, so use it directly.
        if any(node == ["611","645","646","652","692"])
            if numel(candidates) == 1
                found = true;
                tableIndex = t;
                columnName = candidates(1);
                return;
            end

            % Node 692 assessment channel is Phase C.
            if node == "692"
                mask = contains(lower(candidates), "loadc.p_measured");
                if any(mask)
                    found = true;
                    tableIndex = t;
                    columnName = candidates(find(mask,1));
                    return;
                end
            end
        end

        % Node 634 encodes phase in Master PulseA/B/C.
        if node == "634"

            pattern = lower("Master Pulse" + phase + ".P_measured");
            mask = contains(lower(candidates), pattern);

            if any(mask)
                found = true;
                tableIndex = t;
                columnName = candidates(find(mask,1));
                return;
            end
        end

        % Node 675 uses loadA/loadB/loadC.
        if node == "675"

            pattern = lower("load" + phase + ".P_measured");
            mask = contains(lower(candidates), pattern);

            if any(mask)
                found = true;
                tableIndex = t;
                columnName = candidates(find(mask,1));
                return;
            end
        end

        % Node 671 uses A, A1, A2 for physical phases A, B, C.
        if node == "671"

            if phase == "A"
                pattern = "loada.p_measured";
            elseif phase == "B"
                pattern = "loada1.p_measured";
            else
                pattern = "loada2.p_measured";
            end

            mask = contains(lower(candidates), pattern);

            if any(mask)
                found = true;
                tableIndex = t;
                columnName = candidates(find(mask,1));
                return;
            end
        end
    end
end


function [found, columnName] = ...
    findColumnContaining(names, requiredPieces)

    found = false;
    columnName = "";

    names = string(names);
    mask = true(size(names));

    for k = 1:numel(requiredPieces)
        mask = ...
            mask & ...
            contains(lower(names), lower(requiredPieces(k)));
    end

    idx = find(mask, 1);

    if ~isempty(idx)
        found = true;
        columnName = names(idx);
    end
end


function label = canonicalPowerLabel(field)

    parts = split(string(field), "_");

    if numel(parts) == 2
        label = ...
            "Node " + ...
            erase(parts(1), "N") + ...
            " Phase " + ...
            parts(2);
    else
        label = string(field);
    end
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


function pathOut = resolveScheduleFile( ...
    folder, requested, patterns)

    if strlength(requested) > 0

        candidate = fullfile(folder, requested);

        if isfile(candidate)
            pathOut = string(candidate);
        else
            warning("Requested schedule CSV not found: %s", candidate);
            pathOut = "";
        end

        return;
    end

    candidates = strings(0);
    dates = [];

    for p = 1:numel(patterns)

        d = dir(fullfile(folder, patterns(p)));

        for k = 1:numel(d)

            candidates(end+1) = ...
                string(fullfile(d(k).folder, d(k).name)); %#ok<AGROW>

            dates(end+1) = d(k).datenum; %#ok<AGROW>
        end
    end

    if isempty(candidates)
        pathOut = "";
        return;
    end

    [candidates, ia] = unique(candidates, "stable");
    dates = dates(ia);

    [~, idx] = max(dates);
    pathOut = candidates(idx);
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


function saveAssessmentFigure( ...
    fig, ...
    outputDir, ...
    baseName, ...
    savePng, ...
    saveFig)

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
