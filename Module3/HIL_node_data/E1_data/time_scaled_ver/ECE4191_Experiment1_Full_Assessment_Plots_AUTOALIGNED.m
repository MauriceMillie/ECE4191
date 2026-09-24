%% ECE4191 Module 3 - Experiment 1 (QP)
% EXACT-DATA ASSESSMENT PLOTTING SCRIPT
%
% Built specifically for the Experiment 1 files supplied:
%   experiment1_qp_schedule_20260911_160042.csv
%   measured_activePower1.csv
%   measured_activePower2.csv
%   node632_probe1.csv
%   node634_rmsVoltage.csv
%   rmsVoltage1.csv
%   rmsVoltage2.csv
%   rmsVoltage3.csv
%
% The script produces the five required Experiment 1 plots:
%   1) Node 632 measured feeder active power
%   2) Measured active power at all time-varying node-phases
%   3) Node 634 RMS voltages A/B/C with +/-5% limits
%   4) RMS voltages at all other monitored nodes with +/-5% limits
%   5) Measured Node 646 battery SoC
%
% It also creates assessment-support figures/tables for:
%   - voltage violations
%   - reverse active power flow
%   - feeder peak time/magnitude
%   - node contributions at feeder peak
%   - feeder voltage profile at feeder peak
%
% AUTOMATIC PANEL TIME ALIGNMENT
% ------------------------------
% The HIL playback uses:
%       2 real seconds = 30 simulated minutes
%
% Experiment 1 therefore lasts:
%       240 steps x 2 real s/step = 480 real seconds
%
% The HIL/SCADA panels were exported sequentially while the simulation was
% still live. Therefore each CSV can have a different total recording
% length. In addition, the recording contains "priming" / dummy data before
% the Raspberry Pi playback actually began.
%
% This version AUTOMATICALLY:
%   1) inspects the Time column of every required HIL panel CSV;
%   2) identifies the first-exported panel as the one with the EARLIEST
%      final Time value (shortest elapsed recording duration);
%   3) uses that earliest final Time as the common end of the valid run;
%   4) subtracts the known 480 s Experiment 1 playback duration to infer the
%      true controller/playback start;
%   5) crops EVERY panel CSV to the same inferred playback window; and
%   6) remaps that window to the schedule time axis beginning at
%      07-Jan-2013 00:00.
%
% IMPORTANT:
% Alignment uses the CSV Time values, NOT row counts. This matters because
% different exported panels can contain different effective logging
% intervals even when the panel update rate was configured as 1000 ms.
%
% The first schedule entry is the interval ENDING at 00:30. Therefore the
% continuous HIL playback begins 30 minutes before the first schedule label.

clear;
clc;
close all;

%% ========================================================================
% USER SETTINGS
% ========================================================================

% Automatic alignment is recommended for the sequential HIL panel exports.
AUTO_ALIGN_PANEL_EXPORTS = true;

% SCADA/panel update setting used during the interview.
% This is retained as a diagnostic/reference value. The script uses each
% CSV's actual Time column for alignment rather than assuming one sample
% per second.
PANEL_UPDATE_RATE_S = 1.0;     % 1000 ms

% Manual fallback only, used if AUTO_ALIGN_PANEL_EXPORTS = false.
MANUAL_PLAYBACK_START_REAL_S = 0.0;

REAL_SECONDS_PER_STEP = 2.0;
SIM_MINUTES_PER_STEP = 30.0;

% Five days x 48 half-hour steps.
N_PLAYBACK_STEPS = 240;
PLAYBACK_DURATION_REAL_S = N_PLAYBACK_STEPS * REAL_SECONDS_PER_STEP;

% These are calculated automatically below after all panel CSVs have been
% inspected. They are left as NaN here to prevent accidental use of t = 0.
PLAYBACK_START_REAL_S = NaN;
PLAYBACK_END_REAL_S = NaN;

% Required voltage limits.
NOMINAL_634_V = 277.0;
NOMINAL_OTHER_V = 2401.0;

LOWER_634_V = 0.95 * NOMINAL_634_V;       % 263.15 V
UPPER_634_V = 1.05 * NOMINAL_634_V;       % 290.85 V

LOWER_OTHER_V = 0.95 * NOMINAL_OTHER_V;   % 2280.95 V
UPPER_OTHER_V = 1.05 * NOMINAL_OTHER_V;   % 2521.05 V

SAVE_PNG = true;
SAVE_FIG = true;
OUTPUT_FOLDER = "Experiment1_Assessment_Output_Final";

FONT_SIZE = 10;
LINE_WIDTH = 1.25;
LIMIT_LINE_WIDTH = 1.15;

%% ========================================================================
% LOCATE FILES
% ========================================================================

scriptPath = mfilename("fullpath");

if strlength(scriptPath) == 0
    dataDir = pwd;
else
    dataDir = fileparts(scriptPath);
end

scheduleFile = resolveCsv(dataDir, [ ...
    "experiment1_qp_schedule_20260911_160042.csv", ...
    "experiment1_qp_schedule*.csv"]);

powerFile1 = resolveCsv(dataDir, [ ...
    "measured_activePower1.csv", ...
    "measured_activePower1.csv", ...
    "*activePower1*.csv"]);

powerFile2 = resolveCsv(dataDir, [ ...
    "measured_activePower2.csv", ...
    "measured_activePower2.csv", ...
    "*activePower2*.csv"]);

feederFile = resolveCsv(dataDir, [ ...
    "node632_probe1.csv", ...
    "node632_probe1.csv", ...
    "*node632*probe1*.csv"]);

node634VoltageFile = resolveCsv(dataDir, [ ...
    "node634_rmsVoltage.csv", ...
    "node634_rmsVoltage.csv", ...
    "*634*rmsVoltage*.csv"]);

voltageFile1 = resolveCsv(dataDir, [ ...
    "rmsVoltage1.csv", ...
    "rmsVoltage1.csv", ...
    "*rmsVoltage1*.csv"]);

voltageFile2 = resolveCsv(dataDir, [ ...
    "rmsVoltage2.csv", ...
    "rmsVoltage2.csv", ...
    "*rmsVoltage2*.csv"]);

voltageFile3 = resolveCsv(dataDir, [ ...
    "rmsVoltage3.csv", ...
    "rmsVoltage3.csv", ...
    "*rmsVoltage3*.csv"]);

outputDir = fullfile(dataDir, OUTPUT_FOLDER);

if ~isfolder(outputDir)
    mkdir(outputDir);
end

fprintf("============================================================\n");
fprintf(" ECE4191 MODULE 3 - EXPERIMENT 1 (QP)\n");
fprintf(" HEADER-SAFE EXACT-DATA ASSESSMENT ANALYSIS\n");
fprintf("============================================================\n");
fprintf("Schedule     : %s\n", scheduleFile);
fprintf("Power file 1 : %s\n", powerFile1);
fprintf("Power file 2 : %s\n", powerFile2);
fprintf("Node 632     : %s\n", feederFile);
fprintf("Node 634 V   : %s\n", node634VoltageFile);
fprintf("Voltage 1    : %s\n", voltageFile1);
fprintf("Voltage 2    : %s\n", voltageFile2);
fprintf("Voltage 3    : %s\n", voltageFile3);
fprintf("Output folder: %s\n\n", outputDir);

%% ========================================================================
% LOAD SCHEDULE / BUILD SIMULATED TIME REFERENCE
% ========================================================================

S = readtable(scheduleFile, ...
    "VariableNamingRule", "preserve", ...
    "TextType", "string");

requiredScheduleColumns = [ ...
    "step", ...
    "date_label", ...
    "profile_time", ...
    "pbat_aggregate_kw", ...
    "soc_predicted_pct", ...
    "soc646_measured_pct"];

assert(all(ismember(requiredScheduleColumns, ...
    string(S.Properties.VariableNames))), ...
    "The QP schedule is missing one or more required columns.");

assert(height(S) >= N_PLAYBACK_STEPS, ...
    "Expected at least %d schedule rows; found %d.", ...
    N_PLAYBACK_STEPS, height(S));

S = S(1:N_PLAYBACK_STEPS, :);

scheduleTime = datetime( ...
    string(S.("date_label")) + " " + string(S.("profile_time")), ...
    "InputFormat", "d-MMM-yy H:mm", ...
    "Locale", "en_US");

% The first schedule value is an interval-ending value at 00:30.
simPlaybackStart = scheduleTime(1) - minutes(SIM_MINUTES_PER_STEP);

fprintf("Schedule rows   : %d\n", height(S));
fprintf("Simulated start : %s\n", ...
    char(string(simPlaybackStart, "dd-MMM-yyyy HH:mm")));
fprintf("Simulated end   : %s\n\n", ...
    char(string(scheduleTime(end), "dd-MMM-yyyy HH:mm")));

%% ========================================================================
% AUTOMATIC ALIGNMENT OF SEQUENTIALLY EXPORTED HIL PANEL DATA
% ========================================================================

% Only the full Experiment 1 assessment panel exports are used here.
% Do NOT include the toy-QP CSVs in this alignment calculation.
panelFiles = [ ...
    string(powerFile1); ...
    string(powerFile2); ...
    string(feederFile); ...
    string(node634VoltageFile); ...
    string(voltageFile1); ...
    string(voltageFile2); ...
    string(voltageFile3)];

panelLabels = [ ...
    "Active Power 1"; ...
    "Active Power 2"; ...
    "Node 632 Feeder Power"; ...
    "Node 634 RMS Voltage"; ...
    "RMS Voltage 1"; ...
    "RMS Voltage 2"; ...
    "RMS Voltage 3"];

panelAlignment = inspectPanelExports(panelFiles, panelLabels);

% The first panel exported should have the earliest final timestamp because
% all panels began recording from the same simulation start but were saved
% sequentially while the simulation remained live.
[commonPanelEndS, anchorIdx] = min(panelAlignment.EndTime_s);

if AUTO_ALIGN_PANEL_EXPORTS

    PLAYBACK_END_REAL_S = commonPanelEndS;
    PLAYBACK_START_REAL_S = ...
        PLAYBACK_END_REAL_S - PLAYBACK_DURATION_REAL_S;

else

    PLAYBACK_START_REAL_S = MANUAL_PLAYBACK_START_REAL_S;
    PLAYBACK_END_REAL_S = ...
        PLAYBACK_START_REAL_S + PLAYBACK_DURATION_REAL_S;
end

% Verify that every panel actually contains the inferred common window.
if any(panelAlignment.StartTime_s > PLAYBACK_START_REAL_S + 1e-9)

    error([ ...
        "At least one HIL panel begins after the inferred playback start. " ...
        "Automatic alignment cannot safely create a common window."]);
end

if any(panelAlignment.EndTime_s < PLAYBACK_END_REAL_S - 1e-9)

    error([ ...
        "At least one HIL panel ends before the inferred common playback " ...
        "end. Automatic alignment cannot safely create a common window."]);
end

% Estimate how much priming/dummy recording preceded the actual playback.
commonRecordingStartS = min(panelAlignment.StartTime_s);
primingRealSeconds = ...
    PLAYBACK_START_REAL_S - commonRecordingStartS;

simMinutesPerRealSecond = ...
    SIM_MINUTES_PER_STEP / REAL_SECONDS_PER_STEP;

primingSimHours = ...
    primingRealSeconds * simMinutesPerRealSecond / 60.0;

panelAlignment.IsAlignmentAnchor = ...
    (1:height(panelAlignment))' == anchorIdx;

alignmentCsv = fullfile( ...
    outputDir, ...
    "Experiment1_Panel_Time_Alignment.csv");

writetable(panelAlignment, alignmentCsv);

fprintf("============================================================\n");
fprintf(" AUTOMATIC HIL PANEL ALIGNMENT\n");
fprintf("============================================================\n");
fprintf("Configured panel update rate : %.3f s (%g ms)\n", ...
    PANEL_UPDATE_RATE_S, PANEL_UPDATE_RATE_S * 1000);
fprintf("Known playback duration      : %.3f real s\n", ...
    PLAYBACK_DURATION_REAL_S);
fprintf("Alignment anchor             : %s\n", ...
    char(panelAlignment.Panel(anchorIdx)));
fprintf("Anchor final Time            : %.3f s\n", ...
    commonPanelEndS);
fprintf("Inferred playback start      : %.3f s\n", ...
    PLAYBACK_START_REAL_S);
fprintf("Common playback end          : %.3f s\n", ...
    PLAYBACK_END_REAL_S);
fprintf("Discarded priming data       : %.3f real s\n", ...
    primingRealSeconds);
fprintf("Equivalent simulated offset  : %.3f h\n\n", ...
    primingSimHours);

fprintf("Panel timing diagnostics:\n");
disp(panelAlignment(:, { ...
    'Panel','Samples','StartTime_s','EndTime_s', ...
    'Duration_s','MedianSampleInterval_s','IsAlignmentAnchor'}));

fprintf('%s', [ ...
    'NOTE: The script aligns by Time values rather than row count. ' ...
    'This is intentional because the exported panel CSVs can have ' ...
    'different sampling intervals.\n\n']);

%% ========================================================================
% LOAD HIL ACTIVE POWER DATA
% ========================================================================

P1 = readTyphoonCsv(powerFile1);
P2 = readTyphoonCsv(powerFile2);
PF = readTyphoonCsv(feederFile);

P1 = cropRealTime(P1, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
P2 = cropRealTime(P2, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);
PF = cropRealTime(PF, PLAYBACK_START_REAL_S, PLAYBACK_END_REAL_S);

% Header-safe column mapping for the supplied Experiment 1 exports.
%
% WHY THIS USES COLUMN POSITIONS:
% Some MATLAB versions truncate long table variable names to namelengthmax
% characters. The Typhoon active-power headers are 64-86 characters long,
% so exact string matching can fail even though the CSV is correct.
%
% The uploaded Signal Analyzer exports have a fixed, verified column order:
%
% measured_activePower1:
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
% measured_activePower2:
%   1 Time
%   2 671-A
%   3 675-B
%   4 671-B
%   5 671-C
%   6 675-A
%   7 675-C
%
% Using numeric column positions completely avoids MATLAB header truncation
% and duplicate-name modification.

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
        "Active-power CSV %d has only %d columns; expected column %d for %s.", ...
        sourceNumber, width(T), columnIndex, field);

    powerSeries.(char(field)).realTime = T.("Time");
    powerSeries.(char(field)).simTime = hilToSimTime( ...
        T.("Time"), ...
        PLAYBACK_START_REAL_S, ...
        simPlaybackStart, ...
        REAL_SECONDS_PER_STEP, ...
        SIM_MINUTES_PER_STEP);

    % Typhoon active-power exports are in W.
    powerSeries.(char(field)).kW = T{:, columnIndex} / 1000.0;

    % Keep whatever MATLAB imported the header as, for diagnostics only.
    powerSeries.(char(field)).column = ...
        string(T.Properties.VariableNames{columnIndex});
end

powerFields = string(fieldnames(powerSeries));

% Node 632 feeder power.
assert(ismember("Node 632.Probe1", string(PF.Properties.VariableNames)), ...
    "Node 632.Probe1 was not found in the feeder-power CSV.");

feederRealTime = PF.("Time");
feederSimTime = hilToSimTime( ...
    feederRealTime, ...
    PLAYBACK_START_REAL_S, ...
    simPlaybackStart, ...
    REAL_SECONDS_PER_STEP, ...
    SIM_MINUTES_PER_STEP);

feederKW = PF.("Node 632.Probe1") / 1000.0;

%% ========================================================================
% LOAD HIL RMS VOLTAGE DATA
% ========================================================================

V634 = readTyphoonCsv(node634VoltageFile);
V1 = readTyphoonCsv(voltageFile1);
V2 = readTyphoonCsv(voltageFile2);
V3 = readTyphoonCsv(voltageFile3);

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

        if name == "Time" || name == "UpperBound" || name == "LowerBound"
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

        % Keep first occurrence if duplicated between exports.
        if isfield(voltageSeries, char(field))
            continue;
        end

        voltageSeries.(char(field)).node = node;
        voltageSeries.(char(field)).phase = phase;
        voltageSeries.(char(field)).realTime = T.("Time");
        voltageSeries.(char(field)).simTime = hilToSimTime( ...
            T.("Time"), ...
            PLAYBACK_START_REAL_S, ...
            simPlaybackStart, ...
            REAL_SECONDS_PER_STEP, ...
            SIM_MINUTES_PER_STEP);

        voltageSeries.(char(field)).V = T.(char(name));
        voltageSeries.(char(field)).column = name;

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

fprintf("Active-power channels loaded: %d\n", numel(powerFields));
fprintf("RMS-voltage channels loaded : %d\n\n", numel(voltageFields));

%% ========================================================================
% REQUIRED FIGURE 1 - NODE 632 FEEDER ACTIVE POWER
% ========================================================================

[peakFeederKW, peakIdx] = max(feederKW);
[minFeederKW, minIdx] = min(feederKW);

peakFeederTime = feederSimTime(peakIdx);
minFeederTime = feederSimTime(minIdx);
peakFeederRealTime = feederRealTime(peakIdx);

fig1 = figure( ...
    "Name", "Experiment 1 - Node 632 feeder active power", ...
    "Color", "w", ...
    "Position", [80 80 1250 650]);

plot(feederSimTime, feederKW, ...
    "LineWidth", 1.6, ...
    "DisplayName", "Measured Node 632 feeder power");

hold on;

yline(0, "-", ...
    "0 kW", ...
    "HandleVisibility", "off");

plot(peakFeederTime, peakFeederKW, "o", ...
    "MarkerSize", 8, ...
    "LineWidth", 1.4, ...
    "DisplayName", sprintf("Peak %.1f kW", peakFeederKW));

plot(minFeederTime, minFeederKW, "s", ...
    "MarkerSize", 8, ...
    "LineWidth", 1.4, ...
    "DisplayName", sprintf("Minimum %.1f kW", minFeederKW));

hold off;
grid on;
box on;

xlabel("Simulated date/time");
ylabel("Measured feeder active power (kW)");
title("Experiment 1 (QP): Measured Feeder Active Power at Node 632");
subtitle(sprintf("Peak %.1f kW | Minimum %.1f kW", ...
    peakFeederKW, minFeederKW));

legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);
formatDateAxis(gca);

saveAssessmentFigure(fig1, outputDir, ...
    "01_Exp1_Node632_Feeder_Active_Power", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 2 - ALL TIME-VARYING NODE-PHASE ACTIVE POWERS
% ========================================================================

fig2 = figure( ...
    "Name", "Experiment 1 - node-phase active powers", ...
    "Color", "w", ...
    "Position", [20 20 1700 950]);

tl2 = tiledlayout(4,4, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl2, ...
    "Experiment 1 (QP): Measured Active Power at Time-Varying Node-Phases", ...
    "FontWeight", "bold");

for k = 1:numel(powerFields)

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

    title(powerFieldLabel(field));
    ylabel("kW");

    set(gca, "FontSize", 8);
    formatDateAxis(gca);
end

xlabel(tl2, "Simulated date/time");

saveAssessmentFigure(fig2, outputDir, ...
    "02_Exp1_All_TimeVarying_NodePhase_Active_Powers", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 3 - NODE 634 RMS VOLTAGES
% ========================================================================

node634Fields = voltageFields(startsWith(voltageFields, "N634_"));

assert(numel(node634Fields) == 3, ...
    "Expected three Node 634 voltage phases; found %d.", ...
    numel(node634Fields));

fig3 = figure( ...
    "Name", "Experiment 1 - Node 634 RMS voltage", ...
    "Color", "w", ...
    "Position", [90 90 1250 650]);

hold on;

for k = 1:numel(node634Fields)

    f = node634Fields(k);
    s = voltageSeries.(char(f));

    plot(s.simTime, s.V, ...
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

hold off;
grid on;
box on;

xlabel("Simulated date/time");
ylabel("RMS line-to-ground voltage (V)");
title("Experiment 1 (QP): Node 634 RMS Voltages");
subtitle("Nominal = 277 V; permitted range = 263.15-290.85 V");

legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);
formatDateAxis(gca);

saveAssessmentFigure(fig3, outputDir, ...
    "03_Exp1_Node634_RMS_Voltages", ...
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
    "Name", "Experiment 1 - all other monitored RMS voltages", ...
    "Color", "w", ...
    "Position", [10 10 1750 1000]);

nCols = 4;
nRows = ceil(numel(otherNodes) / nCols);

tl4 = tiledlayout(nRows, nCols, ...
    "TileSpacing", "compact", ...
    "Padding", "compact");

title(tl4, ...
    "Experiment 1 (QP): RMS Voltages at All Other Monitored Feeder Nodes", ...
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

        plot(s.simTime, s.V, ...
            "LineWidth", 1.0, ...
            "DisplayName", "Phase " + s.phase);
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
    "04_Exp1_All_Other_Monitored_RMS_Voltages", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% REQUIRED FIGURE 5 - NODE 646 MEASURED BATTERY SOC
% ========================================================================

socMeasured = double(S.("soc646_measured_pct"));
socPredicted = double(S.("soc_predicted_pct"));

fig5 = figure( ...
    "Name", "Experiment 1 - Node 646 battery SoC", ...
    "Color", "w", ...
    "Position", [100 100 1250 650]);

plot(scheduleTime, socMeasured, ...
    "LineWidth", 1.7, ...
    "DisplayName", "Measured Node 646 SoC");

hold on;

plot(scheduleTime, socPredicted, "--", ...
    "LineWidth", 1.2, ...
    "DisplayName", "QP predicted SoC");

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
    "05_Exp1_Node646_Measured_SoC", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% Q1-Q3 - VOLTAGE VIOLATION ANALYSIS
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
        worstTime = s.simTime(iMin);
        worstLimit = s.lowerV;
        worstMagnitude = underMagnitude;

    elseif overMagnitude > 0

        worstType = "OVER";
        worstVoltage = maxV;
        worstTime = s.simTime(iMax);
        worstLimit = s.upperV;
        worstMagnitude = overMagnitude;

    else

        worstType = "NONE";
        worstVoltage = NaN;
        worstTime = NaT;
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
        worstTime, ...
        worstLimit, ...
        worstMagnitude, ...
        'VariableNames', { ...
        'Node','Phase','Nominal_V', ...
        'Min_V','Min_pu','Max_V','Max_pu', ...
        'UnderVoltage','OverVoltage', ...
        'WorstType','WorstVoltage_V','WorstTime', ...
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

        intervalRow = table( ...
            s.node, ...
            s.phase, ...
            type, ...
            s.simTime(iStart), ...
            s.simTime(iEnd), ...
            'VariableNames', { ...
            'Node','Phase','Type','StartTime','EndTime'});

        voltageIntervals = [voltageIntervals; intervalRow]; %#ok<AGROW>
    end
end

violatingStats = voltageStats( ...
    voltageStats.UnderVoltage | voltageStats.OverVoltage, :);

writetable(voltageStats, ...
    fullfile(outputDir, "Experiment1_AllVoltageStatistics.csv"));

writetable(violatingStats, ...
    fullfile(outputDir, "Experiment1_VoltageViolations.csv"));

if ~isempty(voltageIntervals)
    writetable(voltageIntervals, ...
        fullfile(outputDir, "Experiment1_VoltageViolationIntervals.csv"));
end

%% ========================================================================
% Q4-Q6 - REVERSE ACTIVE POWER FLOW ANALYSIS
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
    [maximumKW, iMaximum] = max(s.kW);

    if any(reverse)
        largestReverseTime = s.simTime(iMinimum);
    else
        largestReverseTime = NaT;
    end

    newRow = table( ...
        node, ...
        phase, ...
        any(reverse), ...
        minimumKW, ...
        maximumKW, ...
        largestReverseTime, ...
        'VariableNames', { ...
        'Node','Phase','ReverseFlow', ...
        'MinimumPower_kW','MaximumPower_kW','WorstReverseTime'});

    powerStats = [powerStats; newRow]; %#ok<AGROW>

    intervals = logicalIntervals(reverse);

    for q = 1:height(intervals)

        iStart = intervals.StartIndex(q);
        iEnd = intervals.EndIndex(q);

        intervalRow = table( ...
            node, ...
            phase, ...
            s.simTime(iStart), ...
            s.simTime(iEnd), ...
            'VariableNames', { ...
            'Node','Phase','StartTime','EndTime'});

        reverseIntervals = [reverseIntervals; intervalRow]; %#ok<AGROW>
    end
end

reverseStats = powerStats(powerStats.ReverseFlow, :);

writetable(powerStats, ...
    fullfile(outputDir, "Experiment1_AllActivePowerStatistics.csv"));

writetable(reverseStats, ...
    fullfile(outputDir, "Experiment1_ReversePowerFlow.csv"));

if ~isempty(reverseIntervals)
    writetable(reverseIntervals, ...
        fullfile(outputDir, "Experiment1_ReversePowerFlowIntervals.csv"));
end

%% ========================================================================
% EXTRA FIGURE 6 - WORST MINIMUM VOLTAGE BY NODE-PHASE
% ========================================================================

[sortedMinPU, orderVoltage] = sort(voltageStats.Min_pu, "ascend");

voltageLabels = ...
    "N" + voltageStats.Node + "-" + voltageStats.Phase;

voltageLabels = voltageLabels(orderVoltage);

fig6 = figure( ...
    "Name", "Experiment 1 - minimum voltage summary", ...
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
title("Experiment 1 (QP): Worst Minimum Voltage by Node-Phase");

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig6, outputDir, ...
    "06_Exp1_Worst_Minimum_Voltage_Summary", ...
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
    "Name", "Experiment 1 - reverse power summary", ...
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
title("Experiment 1 (QP): Largest Reverse Active Power by Node-Phase");
subtitle("Negative values indicate reverse active power flow");

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig7, outputDir, ...
    "07_Exp1_Reverse_Power_Flow_Summary", ...
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
    "Experiment1_PeakLoad_NodeContributions.csv"));

%% ========================================================================
% EXTRA FIGURE 8 - NODE CONTRIBUTIONS AT FEEDER PEAK
% ========================================================================

fig8 = figure( ...
    "Name", "Experiment 1 - node contributions at peak", ...
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
title("Experiment 1 (QP): Node Contributions at Measured Feeder Peak");
subtitle(sprintf("Node 632 feeder peak = %.1f kW at %s", ...
    peakFeederKW, ...
    char(string(peakFeederTime, "dd-MMM HH:mm"))));

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig8, outputDir, ...
    "08_Exp1_Node_Contributions_At_Feeder_Peak", ...
    SAVE_PNG, SAVE_FIG);

%% ========================================================================
% EXTRA FIGURE 9 - FEEDER VOLTAGE PROFILE AT PEAK LOAD
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
    "Experiment1_Voltages_At_Feeder_Peak.csv"));

[sortedPeakPU, orderPeak] = sort( ...
    peakVoltageRows.VoltageAtPeak_pu, "ascend");

peakLabels = ...
    "N" + peakVoltageRows.Node + "-" + peakVoltageRows.Phase;

peakLabels = peakLabels(orderPeak);

fig9 = figure( ...
    "Name", "Experiment 1 - voltage profile at peak", ...
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
title("Experiment 1 (QP): Feeder Voltage Profile at Peak Net Load");
subtitle(sprintf("Peak %.1f kW at %s", ...
    peakFeederKW, ...
    char(string(peakFeederTime, "dd-MMM HH:mm"))));

set(gca, "FontSize", FONT_SIZE);

saveAssessmentFigure(fig9, outputDir, ...
    "09_Exp1_Voltage_Profile_At_Feeder_Peak", ...
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

        intervalRow = table( ...
            feederSimTime(iStart), ...
            feederSimTime(iEnd), ...
            'VariableNames', {'StartTime','EndTime'});

        feederReverseOutput = ...
            [feederReverseOutput; intervalRow]; %#ok<AGROW>
    end

    writetable(feederReverseOutput, ...
        fullfile(outputDir, ...
        "Experiment1_Node632_ReverseFlowIntervals.csv"));
end

%% ========================================================================
% COMMAND-WINDOW ASSESSMENT SUMMARY
% ========================================================================

fprintf("\n============================================================\n");
fprintf(" EXPERIMENT 1 ASSESSMENT SUMMARY\n");
fprintf("============================================================\n");

% Q1-Q3
fprintf("\nQ1 - Nodes violating voltage limits:\n");

if isempty(violatingStats)

    fprintf("  None.\n");

else

    violatingNodes = unique(violatingStats.Node, "stable");
    fprintf("  %s\n", strjoin("Node " + violatingNodes, ", "));

    fprintf("\nQ2/Q3 - Worst violation by affected node-phase:\n");

    for r = 1:height(violatingStats)

        fmtViolation = [ ...
            '  Node %s Phase %s: %s, worst %.2f V ' ...
            '(%.4f pu) at %s; %.2f V beyond limit.\n'];

        fprintf(fmtViolation, ...
            char(violatingStats.Node(r)), ...
            char(violatingStats.Phase(r)), ...
            char(violatingStats.WorstType(r)), ...
            violatingStats.WorstVoltage_V(r), ...
            violatingStats.WorstVoltage_V(r) / ...
                violatingStats.Nominal_V(r), ...
            char(formatTimestamp(violatingStats.WorstTime(r))), ...
            violatingStats.ViolationMagnitude_V(r));
    end
end

% Q4-Q6
fprintf("\nQ4 - Nodes exhibiting reverse active power flow:\n");

if isempty(reverseStats)

    fprintf("  None.\n");

else

    reverseNodes = unique(reverseStats.Node, "stable");
    fprintf("  %s\n", strjoin("Node " + reverseNodes, ", "));

    fprintf("\nQ5/Q6 - Largest reverse flow by affected node-phase:\n");

    for r = 1:height(reverseStats)

        fmtReverse = ...
            '  Node %s Phase %s: %.2f kW at %s.\n';

        fprintf(fmtReverse, ...
            char(reverseStats.Node(r)), ...
            char(reverseStats.Phase(r)), ...
            reverseStats.MinimumPower_kW(r), ...
            char(formatTimestamp(reverseStats.WorstReverseTime(r))));
    end
end

% Q7-Q9
fprintf("\nQ7 - Highest total feeder net load occurs at:\n");
fprintf("  %s\n", formatTimestamp(peakFeederTime));

fprintf("\nQ8 - Peak feeder net load:\n");
fprintf("  %.3f kW (%.3f MW)\n", ...
    peakFeederKW, peakFeederKW / 1000);

fprintf("\nQ9 - Peak-load measurement method:\n");
fprintf('%s', [ ...
    '  The feeder-head active power is measured at Node 632 using\n' ...
    '  Node 632.Probe1. The peak feeder net load is the maximum value\n' ...
    '  of that measured signal over the five-day Experiment 1 playback.\n']);

% Q10
fprintf("\nQ10 - Node contributions at measured feeder peak:\n");
disp(peakContributionTable);

% Useful diagnostics.
fprintf("\nAdditional diagnostics:\n");
fprintf("  Minimum Node 632 feeder power : %.3f kW at %s\n", ...
    minFeederKW, formatTimestamp(minFeederTime));

fprintf("  Node 632 samples below 0 kW  : %d of %d\n", ...
    sum(feederReverse), numel(feederReverse));

fprintf("  Measured Node 646 SoC range  : %.2f%% to %.2f%%\n", ...
    min(socMeasured), max(socMeasured));

[lowestPU, lowestIdx] = min(voltageStats.Min_pu);

fprintf("  Lowest measured feeder voltage: Node %s Phase %s = %.4f pu\n", ...
    voltageStats.Node(lowestIdx), ...
    voltageStats.Phase(lowestIdx), ...
    lowestPU);

fprintf("\nNOTE FOR Q1 AND Q10:\n");
fprintf('%s', [ ...
    '  The assessment also asks for comparison with Module 1.\n' ...
    '  This script analyses Experiment 1 only; add Module 1 data for the\n' ...
    '  quantitative no-control comparison.\n']);

fprintf("\nFigures and CSV summaries saved to:\n  %s\n", outputDir);
fprintf("============================================================\n");

%% ========================================================================
% LOCAL FUNCTIONS
% ========================================================================

function pathOut = resolveCsv(folder, candidates)

    pathOut = "";

    % Exact names first.
    for k = 1:numel(candidates)

        candidate = string(candidates(k));

        if ~contains(candidate, "*")

            p = fullfile(folder, candidate);

            if isfile(p)
                pathOut = string(p);
                return;
            end
        end
    end

    % Wildcard fallback.
    for k = 1:numel(candidates)

        candidate = string(candidates(k));

        if contains(candidate, "*")

            d = dir(fullfile(folder, candidate));

            if ~isempty(d)

                % Use newest matching file.
                [~, idx] = max([d.datenum]);

                pathOut = string(fullfile( ...
                    d(idx).folder, d(idx).name));

                return;
            end
        end
    end

    error("Could not locate required CSV. Tried: %s", ...
        strjoin(candidates, ", "));
end


function info = inspectPanelExports(panelFiles, panelLabels)

    nFiles = numel(panelFiles);

    Samples = zeros(nFiles,1);
    StartTime_s = zeros(nFiles,1);
    EndTime_s = zeros(nFiles,1);
    Duration_s = zeros(nFiles,1);
    MedianSampleInterval_s = NaN(nFiles,1);

    for k = 1:nFiles

        T = readTyphoonCsv(panelFiles(k));

        t = double(T.("Time"));
        t = t(isfinite(t));

        assert(~isempty(t), ...
            "No finite Time samples found in:\n%s", ...
            panelFiles(k));

        t = sort(t(:));

        Samples(k) = numel(t);
        StartTime_s(k) = t(1);
        EndTime_s(k) = t(end);
        Duration_s(k) = t(end) - t(1);

        if numel(t) > 1

            dt = diff(t);
            dt = dt(dt > 0 & isfinite(dt));

            if ~isempty(dt)
                MedianSampleInterval_s(k) = median(dt);
            end
        end
    end

    info = table( ...
        panelLabels(:), ...
        panelFiles(:), ...
        Samples, ...
        StartTime_s, ...
        EndTime_s, ...
        Duration_s, ...
        MedianSampleInterval_s, ...
        'VariableNames', { ...
        'Panel', ...
        'File', ...
        'Samples', ...
        'StartTime_s', ...
        'EndTime_s', ...
        'Duration_s', ...
        'MedianSampleInterval_s'});
end


function T = readTyphoonCsv(path)

    T = readtable(path, ...
        "VariableNamingRule", "preserve");

    assert(ismember("Time", ...
        string(T.Properties.VariableNames)), ...
        "File does not contain a Time column:\n%s", path);
end


function T = cropRealTime(T, startS, endS)

    mask = ...
        T.("Time") >= startS & ...
        T.("Time") <= endS;

    T = T(mask,:);

    assert(~isempty(T), ...
        "No samples remain after cropping to %.2f-%.2f s.", ...
        startS, endS);
end


function simTime = hilToSimTime( ...
    realTime, ...
    startRealS, ...
    simStart, ...
    realSecondsPerStep, ...
    simMinutesPerStep)

    minutesPerRealSecond = ...
        simMinutesPerStep / realSecondsPerStep;

    simTime = simStart + ...
        minutes((realTime - startRealS) * minutesPerRealSecond);
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

        exportgraphics(fig, ...
            fullfile(outputDir, baseName + ".png"), ...
            "Resolution", 300);
    end

    if saveFig

        savefig(fig, ...
            fullfile(outputDir, baseName + ".fig"));
    end
end
