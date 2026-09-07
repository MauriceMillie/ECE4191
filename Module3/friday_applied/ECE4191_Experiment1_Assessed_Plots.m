%% ECE4191 Module 3 - Experiment 1 (QP) assessed plots
% This script is designed for the 5-day Experiment 1 playback.
%
% Place this .m file in the same folder as:
%   1) the Experiment 1 Raspberry Pi schedule/log CSV
%      (contains pbat_aggregate_kw, grid_actual_calculated_kw,
%       soc646_measured_pct, etc.)
%
% and, when exported from Typhoon HIL / Signal Analyzer:
%   2) the Experiment 1 measured active-power CSV
%      (ideally columns named p_<node>_<phase>_W)
%   3) the Experiment 1 measured RMS-voltage CSV
%      (ideally columns named v_<node>_<phase>_rms_V)
%
% The script automatically searches the current folder for compatible CSVs.
%
% REQUIRED ASSESSMENT FIGURES PRODUCED WHEN THE MEASURED CSVs ARE PRESENT:
%   Figure 1 - measured feeder active power at Node 632
%   Figure 2 - measured active power at all time-varying node-phases
%   Figure 3 - Node 634 RMS voltages, +/-5% of 277 V
%   Figure 4 - all other monitored RMS voltages, +/-5% of 2401 V
%   Figure 5 - measured Node 646 battery SoC
%
% EXTRA USEFUL FIGURES:
%   Figure 6 - aggregate QP battery command
%   Figure 7 - no-battery baseline vs QP-controlled feeder power estimate
%
% It also prints assessment-oriented numerical summaries:
%   - voltage violations and worst values
%   - reverse active-power flow and worst reverse flow
%   - peak feeder active power and time
%   - largest node contributions at the feeder peak
%
% IMPORTANT:
% The Raspberry Pi schedule CSV does NOT contain measured feeder voltages or
% measured node powers. Figures 1-4 require the HIL measurement exports.
% The controller-side "grid_actual_calculated_kw" is plotted separately as
% an estimate and is NOT relabelled as the measured Node-632 feeder power.

clear;
clc;
close all;

%% ------------------------------------------------------------------------
% User settings
% -------------------------------------------------------------------------

% Leave these empty ("") to auto-detect compatible CSVs in this folder.
SCHEDULE_FILE = "";
POWER_FILE    = "";
VOLTAGE_FILE  = "";

SAVE_PNG = true;
SAVE_FIG = true;
OUTPUT_FOLDER = "Experiment1_Assessed_Plots";

% Voltage limits required by the Module 3 assessment.
NOMINAL_634_V = 277;
NOMINAL_OTHER_V = 2401;

LOWER_634_V  = 0.95 * NOMINAL_634_V;
UPPER_634_V  = 1.05 * NOMINAL_634_V;

LOWER_OTHER_V = 0.95 * NOMINAL_OTHER_V;
UPPER_OTHER_V = 1.05 * NOMINAL_OTHER_V;

% Plot presentation.
LINE_WIDTH = 1.35;
LIMIT_LINE_WIDTH = 1.25;
FONT_SIZE = 10;

%% ------------------------------------------------------------------------
% Locate files
% -------------------------------------------------------------------------

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

scheduleFile = resolveCsv( ...
    dataDir, SCHEDULE_FILE, ...
    ["soc646_measured_pct", "pbat_aggregate_kw", "grid_actual_calculated_kw"]);

powerFile = resolveCsvOptional( ...
    dataDir, POWER_FILE, ...
    ["step"], "p_");

voltageFile = resolveCsvOptional( ...
    dataDir, VOLTAGE_FILE, ...
    ["step"], "v_");

fprintf("============================================================\n");
fprintf(" ECE4191 MODULE 3 - EXPERIMENT 1 ASSESSED PLOTS\n");
fprintf("============================================================\n");
fprintf("Schedule file : %s\n", scheduleFile);

if strlength(powerFile) > 0
    fprintf("Power file    : %s\n", powerFile);
else
    fprintf("Power file    : NOT FOUND\n");
end

if strlength(voltageFile) > 0
    fprintf("Voltage file  : %s\n", voltageFile);
else
    fprintf("Voltage file  : NOT FOUND\n");
end

fprintf("Output folder : %s\n\n", outputDir);

if strlength(powerFile) == 0
    fprintf("NOTE: No measured p_*_W CSV was detected. The schedule CSV will NOT\n");
    fprintf("      be used as a substitute for measured HIL active-power data.\n\n");
end

if strlength(voltageFile) == 0
    fprintf("NOTE: No measured v_*_rms_V CSV was detected.\n\n");
end

%% ------------------------------------------------------------------------
% Read the Raspberry Pi Experiment 1 schedule/log
% -------------------------------------------------------------------------

S = readtable(scheduleFile, ...
    "VariableNamingRule", "preserve", ...
    "TextType", "string");

requiredSchedule = [ ...
    "step", "date_label", "profile_time", ...
    "p_load_actual_total_kw", "p_pv_actual_total_kw", ...
    "baseline_grid_actual_kw", "pbat_aggregate_kw", ...
    "grid_actual_calculated_kw", ...
    "soc_predicted_pct", "soc646_measured_pct"];

assert(all(ismember(requiredSchedule, string(S.Properties.VariableNames))), ...
    "The selected schedule CSV does not have the expected Experiment 1 columns.");

assert(height(S) == 240, ...
    "Experiment 1 should contain 240 samples (5 days x 48 half-hour intervals).");

timeS = buildTimeVector(S);
stepS = S.("step");

%% ------------------------------------------------------------------------
% FIGURE 5 (available from the uploaded schedule CSV):
% measured Node 646 State of Charge
% -------------------------------------------------------------------------

fig5 = figure( ...
    "Name", "Experiment 1 - Node 646 SoC", ...
    "Color", "w", ...
    "Position", [100 100 1200 620]);

plot(timeS, S.("soc646_measured_pct"), ...
    "LineWidth", 1.8, ...
    "DisplayName", "Measured SoC");
hold on;

plot(timeS, S.("soc_predicted_pct"), "--", ...
    "LineWidth", 1.2, ...
    "DisplayName", "QP predicted SoC");

yline(0, ":", "0%", "HandleVisibility", "off");
yline(100, ":", "100%", "HandleVisibility", "off");

hold off;
grid on;
box on;

xlabel("Playback date and time");
ylabel("Battery state of charge (%)");
title("Experiment 1 (QP): Node 646 Battery State of Charge");
legend("Location", "best");
ylim([-3 103]);
set(gca, "FontSize", FONT_SIZE);
formatTimeAxis(gca);

saveAssessmentFigure(fig5, outputDir, ...
    "05_Exp1_Node646_Measured_SoC", SAVE_PNG, SAVE_FIG);

%% ------------------------------------------------------------------------
% EXTRA FIGURE 6: aggregate battery schedule
% -------------------------------------------------------------------------

fig6 = figure( ...
    "Name", "Experiment 1 - Aggregate battery schedule", ...
    "Color", "w", ...
    "Position", [110 110 1200 620]);

plot(timeS, S.("pbat_aggregate_kw"), "LineWidth", 1.5);
hold on;
yline(0, "-", "HandleVisibility", "off");
hold off;

grid on;
box on;
xlabel("Playback date and time");
ylabel("Aggregate battery power (kW)");
title("Experiment 1 (QP): Aggregate Battery Schedule");
subtitle("Positive = discharge, negative = charge");
set(gca, "FontSize", FONT_SIZE);
formatTimeAxis(gca);

saveAssessmentFigure(fig6, outputDir, ...
    "06_Exp1_Aggregate_Battery_Schedule", SAVE_PNG, SAVE_FIG);

%% ------------------------------------------------------------------------
% EXTRA FIGURE 7: controller-side feeder power calculation
% -------------------------------------------------------------------------

fig7 = figure( ...
    "Name", "Experiment 1 - Calculated feeder power", ...
    "Color", "w", ...
    "Position", [120 120 1200 650]);

plot(timeS, S.("baseline_grid_actual_kw"), ...
    "LineWidth", 1.2, ...
    "DisplayName", "No-battery baseline (calculated)");
hold on;

plot(timeS, S.("grid_actual_calculated_kw"), ...
    "LineWidth", 1.6, ...
    "DisplayName", "QP-controlled grid power (calculated)");

yline(0, "-", "HandleVisibility", "off");
hold off;

grid on;
box on;
xlabel("Playback date and time");
ylabel("Calculated feeder grid power (kW)");
title("Experiment 1 (QP): Controller-Side Feeder Power Calculation");
subtitle("Diagnostic only - use measured Node 632 power for the assessed feeder-power plot");
legend("Location", "best");
set(gca, "FontSize", FONT_SIZE);
formatTimeAxis(gca);

saveAssessmentFigure(fig7, outputDir, ...
    "07_Exp1_Calculated_Feeder_Power_Diagnostic", SAVE_PNG, SAVE_FIG);

%% ------------------------------------------------------------------------
% Read measured active-power data, if present
% -------------------------------------------------------------------------

P = table();
timeP = datetime.empty();
powerVars = strings(0);
powerDataKW = [];
powerLabels = strings(0);

if strlength(powerFile) > 0
    P = readtable(powerFile, ...
        "VariableNamingRule", "preserve", ...
        "TextType", "string");

    timeP = buildCompatibleTimeVector(P, S);

    varNamesP = string(P.Properties.VariableNames);
    powerVars = varNamesP(startsWith(varNamesP, "p_") & endsWith(varNamesP, "_W"));

    if isempty(powerVars)
        warning("No p_* active-power measurement columns were found in %s.", powerFile);
    else
        powerData = P{:, cellstr(powerVars)};
        powerDataKW = convertPowerColumnsToKW(powerData, powerVars);
    end
end

%% ------------------------------------------------------------------------
% REQUIRED FIGURE 1:
% measured feeder active power at Node 632
% -------------------------------------------------------------------------

if ~isempty(powerVars)
    is632 = contains(powerVars, "632");

    if any(is632)
        feederVars = powerVars(is632);
        feederData = powerDataKW(:, is632);

        % If several Node-632 phase channels exist, sum them to obtain total
        % feeder active power. If there is one total signal, use it directly.
        if size(feederData, 2) == 1
            feederKW = feederData(:, 1);
            feederDescription = makePowerLabel(feederVars(1));
        else
            feederKW = sum(feederData, 2, "omitnan");
            feederDescription = "Sum of measured Node 632 phase powers";
        end

        fig1 = figure( ...
            "Name", "Experiment 1 - Node 632 feeder active power", ...
            "Color", "w", ...
            "Position", [90 90 1200 620]);

        plot(timeP, feederKW, "LineWidth", 1.65);
        hold on;
        yline(0, "-", "HandleVisibility", "off");
        hold off;

        grid on;
        box on;
        xlabel("Playback date and time");
        ylabel("Measured feeder active power (kW)");
        title("Experiment 1 (QP): Measured Feeder Active Power at Node 632");
        subtitle(feederDescription);
        set(gca, "FontSize", FONT_SIZE);
        formatTimeAxis(gca);

        saveAssessmentFigure(fig1, outputDir, ...
            "01_Exp1_Node632_Measured_Feeder_Active_Power", SAVE_PNG, SAVE_FIG);

        % Assessment summary: peak feeder load.
        [peakFeederKW, peakIdx] = max(feederKW);
        [minFeederKW, minIdx] = min(feederKW);

        fprintf("\n--- ASSESSED: NODE 632 FEEDER ACTIVE POWER ---\n");
        fprintf("Peak feeder active power: %.3f kW at %s\n", ...
            peakFeederKW, formatTimestamp(timeP(peakIdx)));
        fprintf("Minimum feeder active power: %.3f kW at %s\n", ...
            minFeederKW, formatTimestamp(timeP(minIdx)));

    else
        warning('%s', [ ...
            'Measured power CSV was found, but no Node-632 power column was found. ' ...
            'Figure 1 cannot be produced until the Node 632 feeder active-power ' ...
            'signal is exported from the HIL Signal Analyzer.']);
    end
else
    warning('%s', [ ...
        'No measured active-power CSV was found. Required Figures 1 and 2 ' ...
        'cannot yet be produced.']);
end

%% ------------------------------------------------------------------------
% REQUIRED FIGURE 2:
% measured active power at all time-varying node-phase loads
% -------------------------------------------------------------------------

if ~isempty(powerVars)
    % Exclude Node 632 because it is the feeder measurement, not one of the
    % time-varying load node-phase plots.
    loadMask = ~contains(powerVars, "632");
    loadVars = powerVars(loadMask);
    loadDataKW = powerDataKW(:, loadMask);

    if ~isempty(loadVars)
        nTraces = numel(loadVars);
        nCols = 4;
        nRows = ceil(nTraces / nCols);

        fig2 = figure( ...
            "Name", "Experiment 1 - all time-varying active powers", ...
            "Color", "w", ...
            "Position", [40 40 1550 900]);

        tl2 = tiledlayout(nRows, nCols, ...
            "TileSpacing", "compact", ...
            "Padding", "compact");

        title(tl2, ...
            "Experiment 1 (QP): Measured Active Power at Time-Varying Node-Phases", ...
            "FontWeight", "bold");

        ax2 = gobjects(nTraces, 1);

        for k = 1:nTraces
            ax2(k) = nexttile;
            plot(timeP, loadDataKW(:, k), "LineWidth", LINE_WIDTH);
            hold on;
            yline(0, "-", "HandleVisibility", "off");
            hold off;
            grid on;
            box on;
            title(makePowerLabel(loadVars(k)), "Interpreter", "none");
            ylabel("kW");
            set(gca, "FontSize", 8);
            formatTimeAxis(gca);
        end

        linkaxes(ax2, "x");
        xlabel(tl2, "Playback date and time");

        saveAssessmentFigure(fig2, outputDir, ...
            "02_Exp1_All_TimeVarying_NodePhase_Active_Powers", SAVE_PNG, SAVE_FIG);

        % Reverse-power-flow assessment summary.
        fprintf("\n--- ASSESSED: REVERSE ACTIVE POWER FLOW ---\n");
        reverseFound = false;

        for k = 1:nTraces
            reverseIdx = find(loadDataKW(:, k) < 0);

            if ~isempty(reverseIdx)
                reverseFound = true;
                [worstReverse, localIdx] = min(loadDataKW(reverseIdx, k));
                worstIdx = reverseIdx(localIdx);

                fprintf("%s: reverse flow occurs; most negative = %.3f kW at %s\n", ...
                    makePowerLabel(loadVars(k)), ...
                    worstReverse, ...
                    formatTimestamp(timeP(worstIdx)));
            end
        end

        if ~reverseFound
            fprintf("No reverse active-power flow detected in the measured node channels.\n");
        end

        % Top measured node contributions at the Node-632 peak, if available.
        is632 = contains(powerVars, "632");
        if any(is632)
            feederData = powerDataKW(:, is632);
            if size(feederData, 2) == 1
                feederKW_forPeak = feederData(:, 1);
            else
                feederKW_forPeak = sum(feederData, 2, "omitnan");
            end
            [~, peakIdx] = max(feederKW_forPeak);

            contributions = loadDataKW(peakIdx, :);
            [sortedValues, order] = sort(contributions, "descend");

            fprintf("\nLargest measured node-phase contributions at feeder peak (%s):\n", ...
                formatTimestamp(timeP(peakIdx)));

            topN = min(5, numel(order));
            for rank = 1:topN
                fprintf("  %d. %-22s %9.3f kW\n", ...
                    rank, ...
                    makePowerLabel(loadVars(order(rank))), ...
                    sortedValues(rank));
            end
        end
    end
end

%% ------------------------------------------------------------------------
% Read measured RMS-voltage data, if present
% -------------------------------------------------------------------------

V = table();
timeV = datetime.empty();
voltageVars = strings(0);
voltageData = [];
voltageLabels = strings(0);

if strlength(voltageFile) > 0
    V = readtable(voltageFile, ...
        "VariableNamingRule", "preserve", ...
        "TextType", "string");

    timeV = buildCompatibleTimeVector(V, S);

    varNamesV = string(V.Properties.VariableNames);
    voltageVars = varNamesV(startsWith(varNamesV, "v_") & endsWith(varNamesV, "_rms_V"));

    if isempty(voltageVars)
        warning("No v_* RMS-voltage measurement columns were found in %s.", voltageFile);
    else
        voltageData = V{:, cellstr(voltageVars)};
    end
end

%% ------------------------------------------------------------------------
% REQUIRED FIGURE 3:
% Node 634 RMS voltages, phases A/B/C, +/-5% of 277 V
% -------------------------------------------------------------------------

if ~isempty(voltageVars)
    is634 = contains(voltageVars, "v_634_");

    if any(is634)
        vars634 = voltageVars(is634);
        data634 = voltageData(:, is634);

        fig3 = figure( ...
            "Name", "Experiment 1 - Node 634 RMS voltage", ...
            "Color", "w", ...
            "Position", [100 100 1200 650]);

        plot(timeV, data634, "LineWidth", 1.5);
        hold on;

        yline(UPPER_634_V, "--", ...
            sprintf("+5%% limit = %.2f V", UPPER_634_V), ...
            "LineWidth", LIMIT_LINE_WIDTH, ...
            "HandleVisibility", "off");

        yline(LOWER_634_V, "--", ...
            sprintf("-5%% limit = %.2f V", LOWER_634_V), ...
            "LineWidth", LIMIT_LINE_WIDTH, ...
            "HandleVisibility", "off");

        hold off;
        grid on;
        box on;

        xlabel("Playback date and time");
        ylabel("Measured RMS line-to-ground voltage (V)");
        title("Experiment 1 (QP): Node 634 RMS Voltages");
        subtitle("Nominal = 277 V; limits = +/-5%");
        legend(arrayfun(@makeVoltageLabel, vars634), ...
            "Location", "best", ...
            "Interpreter", "none");

        set(gca, "FontSize", FONT_SIZE);
        formatTimeAxis(gca);

        saveAssessmentFigure(fig3, outputDir, ...
            "03_Exp1_Node634_RMS_Voltages", SAVE_PNG, SAVE_FIG);
    else
        warning("No Node 634 voltage channels were found in the measured voltage CSV.");
    end
end

%% ------------------------------------------------------------------------
% REQUIRED FIGURE 4:
% all other monitored RMS voltages, +/-5% of 2401 V
% -------------------------------------------------------------------------

if ~isempty(voltageVars)
    is634 = contains(voltageVars, "v_634_");
    otherVars = voltageVars(~is634);
    otherData = voltageData(:, ~is634);

    if ~isempty(otherVars)
        nTraces = numel(otherVars);
        nCols = 4;
        nRows = ceil(nTraces / nCols);

        fig4 = figure( ...
            "Name", "Experiment 1 - other feeder RMS voltages", ...
            "Color", "w", ...
            "Position", [25 25 1600 950]);

        tl4 = tiledlayout(nRows, nCols, ...
            "TileSpacing", "compact", ...
            "Padding", "compact");

        title(tl4, ...
            "Experiment 1 (QP): RMS Voltages at All Other Monitored Node-Phases", ...
            "FontWeight", "bold");

        ax4 = gobjects(nTraces, 1);

        for k = 1:nTraces
            ax4(k) = nexttile;

            plot(timeV, otherData(:, k), ...
                "LineWidth", LINE_WIDTH);

            hold on;
            yline(UPPER_OTHER_V, "--", ...
                "LineWidth", LIMIT_LINE_WIDTH, ...
                "HandleVisibility", "off");
            yline(LOWER_OTHER_V, "--", ...
                "LineWidth", LIMIT_LINE_WIDTH, ...
                "HandleVisibility", "off");
            hold off;

            grid on;
            box on;
            title(makeVoltageLabel(otherVars(k)), "Interpreter", "none");
            ylabel("V");
            set(gca, "FontSize", 8);
            formatTimeAxis(gca);
        end

        linkaxes(ax4, "x");
        xlabel(tl4, "Playback date and time");

        saveAssessmentFigure(fig4, outputDir, ...
            "04_Exp1_Other_Monitored_RMS_Voltages", SAVE_PNG, SAVE_FIG);
    end

    %% --------------------------------------------------------------------
    % Assessment-oriented voltage violation summary
    % ---------------------------------------------------------------------

    fprintf("\n--- ASSESSED: VOLTAGE VIOLATIONS ---\n");

    violationFound = false;

    for k = 1:numel(voltageVars)
        varName = voltageVars(k);
        values = voltageData(:, k);

        if contains(varName, "v_634_")
            lowerLimit = LOWER_634_V;
            upperLimit = UPPER_634_V;
            nominal = NOMINAL_634_V;
        else
            lowerLimit = LOWER_OTHER_V;
            upperLimit = UPPER_OTHER_V;
            nominal = NOMINAL_OTHER_V;
        end

        lowIdx = find(values < lowerLimit);
        highIdx = find(values > upperLimit);

        if ~isempty(lowIdx) || ~isempty(highIdx)
            violationFound = true;
            fprintf("\n%s\n", makeVoltageLabel(varName));

            if ~isempty(lowIdx)
                [worstLow, localIdx] = min(values(lowIdx));
                idx = lowIdx(localIdx);

                fprintf("  UNDER-VOLTAGE: worst %.3f V at %s\n", ...
                    worstLow, formatTimestamp(timeV(idx)));
                fprintf("    %.3f V below lower limit %.3f V (%.3f%% of nominal)\n", ...
                    lowerLimit - worstLow, ...
                    lowerLimit, ...
                    100 * (worstLow - nominal) / nominal);
            end

            if ~isempty(highIdx)
                [worstHigh, localIdx] = max(values(highIdx));
                idx = highIdx(localIdx);

                fprintf("  OVER-VOLTAGE: worst %.3f V at %s\n", ...
                    worstHigh, formatTimestamp(timeV(idx)));
                fprintf("    %.3f V above upper limit %.3f V (+%.3f%% of nominal)\n", ...
                    worstHigh - upperLimit, ...
                    upperLimit, ...
                    100 * (worstHigh - nominal) / nominal);
            end
        end
    end

    if ~violationFound
        fprintf("No RMS-voltage violations detected.\n");
    end

else
    warning('%s', [ ...
        'No measured voltage CSV was found. Required Figures 3 and 4 and ' ...
        'voltage-violation assessment results cannot yet be produced.']);
end

%% ------------------------------------------------------------------------
% Schedule-based numerical information available now
% -------------------------------------------------------------------------

fprintf("\n--- EXPERIMENT 1 QP SCHEDULE / SOC INFORMATION ---\n");

[calcPeakKW, calcPeakIdx] = max(S.("grid_actual_calculated_kw"));
[calcMinimumKW, calcMinIdx] = min(S.("grid_actual_calculated_kw"));

fprintf("Controller-side calculated peak grid power: %.3f kW at %s\n", ...
    calcPeakKW, formatTimestamp(timeS(calcPeakIdx)));

fprintf("Controller-side calculated minimum grid power: %.3f kW at %s\n", ...
    calcMinimumKW, formatTimestamp(timeS(calcMinIdx)));

fprintf("Aggregate battery command range: %.3f to %.3f kW\n", ...
    min(S.("pbat_aggregate_kw")), max(S.("pbat_aggregate_kw")));

fprintf("Measured Node 646 SoC range: %.3f%% to %.3f%%\n", ...
    min(S.("soc646_measured_pct")), max(S.("soc646_measured_pct")));

socError = S.("soc646_measured_pct") - S.("soc_predicted_pct");

socMeasured = S.("soc646_measured_pct");
socPredicted = S.("soc_predicted_pct");

fprintf("Final measured Node 646 SoC: %.3f%%\n", ...
    socMeasured(end));

fprintf("Final predicted Node 646 SoC: %.3f%%\n", ...
    socPredicted(end));

fprintf("Final measured-predicted SoC difference: %.3f percentage points\n", ...
    socError(end));

fprintf("\nPlots saved in:\n  %s\n", outputDir);

if strlength(powerFile) == 0 || strlength(voltageFile) == 0
    fprintf("\n");
    fprintf("NOTE: The Experiment 1 schedule CSV alone is not sufficient for all\n");
    fprintf("five required assessed plots. Export the measured Node-632/node active\n");
    fprintf("powers and RMS voltages from HIL SCADA / Signal Analyzer, place the\n");
    fprintf("CSV files beside this MATLAB script, and rerun it.\n");
end

fprintf("============================================================\n");


%% ========================================================================
% Local functions
% ========================================================================

function pathOut = resolveCsv(dataDir, requested, requiredColumns)

    if strlength(requested) > 0
        candidate = fullfile(dataDir, requested);
        assert(isfile(candidate), "Could not find requested CSV: %s", candidate);

        T = readtable(candidate, ...
            "VariableNamingRule", "preserve", ...
            "TextType", "string");

        assert(all(ismember(requiredColumns, string(T.Properties.VariableNames))), ...
            "Requested CSV does not contain the required columns.");

        pathOut = string(candidate);
        return;
    end

    files = dir(fullfile(dataDir, "*.csv"));

    for k = 1:numel(files)
        candidate = fullfile(files(k).folder, files(k).name);

        try
            opts = detectImportOptions(candidate, "VariableNamingRule", "preserve");
            names = string(opts.VariableNames);

            if all(ismember(requiredColumns, names))
                pathOut = string(candidate);
                return;
            end
        catch
        end
    end

    error("Could not auto-detect the Experiment 1 schedule CSV in %s.", dataDir);
end


function pathOut = resolveCsvOptional(dataDir, requested, requiredColumns, prefix)

    pathOut = "";

    if strlength(requested) > 0
        candidate = fullfile(dataDir, requested);

        if ~isfile(candidate)
            warning("Requested optional CSV not found: %s", candidate);
            return;
        end

        pathOut = string(candidate);
        return;
    end

    files = dir(fullfile(dataDir, "*.csv"));

    for k = 1:numel(files)
        candidate = fullfile(files(k).folder, files(k).name);

        try
            opts = detectImportOptions(candidate, "VariableNamingRule", "preserve");
            names = string(opts.VariableNames);

            hasRequired = all(ismember(requiredColumns, names));

            if prefix == "p_"
                % Measured active-power logger/export columns are p_*_W.
                % This deliberately excludes controller schedule columns such
                % as p_load_actual_total_kw and pbat_aggregate_kw.
                hasPrefix = any(startsWith(names, "p_") & endsWith(names, "_W"));
            elseif prefix == "v_"
                % Measured RMS-voltage logger/export columns are v_*_rms_V.
                hasPrefix = any(startsWith(names, "v_") & endsWith(names, "_rms_V"));
            else
                hasPrefix = any(startsWith(names, prefix));
            end

            if hasRequired && hasPrefix
                pathOut = string(candidate);
                return;
            end
        catch
        end
    end
end


function time = buildTimeVector(T)

    required = ["date_label", "profile_time"];

    assert(all(ismember(required, string(T.Properties.VariableNames))), ...
        "CSV must contain date_label and profile_time columns.");

    time = datetime( ...
        string(T.("date_label")) + " " + string(T.("profile_time")), ...
        "InputFormat", "d-MMM-yy H:mm", ...
        "Locale", "en_US");
end


function time = buildCompatibleTimeVector(T, scheduleTable)

    names = string(T.Properties.VariableNames);

    if all(ismember(["date_label", "profile_time"], names))
        time = buildTimeVector(T);
        return;
    end

    if ismember("step", names) && height(T) == height(scheduleTable)
        time = buildTimeVector(scheduleTable);
        return;
    end

    if height(T) == height(scheduleTable)
        warning('%s', [ ...
            'Measurement file has no date_label/profile_time metadata. ' ...
            'Using the Experiment 1 schedule time axis because row counts match.']);
        time = buildTimeVector(scheduleTable);
        return;
    end

    error('%s', [ ...
        'Could not construct a time vector for a measurement CSV. ' ...
        'Provide date_label/profile_time columns or a 240-row file aligned ' ...
        'with the Experiment 1 schedule.']);
end


function dataKW = convertPowerColumnsToKW(data, variableNames)

    dataKW = data;

    for k = 1:numel(variableNames)
        name = variableNames(k);

        % Existing ECE4191 measurement logger names measured powers *_W.
        if endsWith(name, "_W")
            dataKW(:, k) = data(:, k) / 1000;
        else
            % If the exported variable is not explicitly labelled in W,
            % preserve its value rather than guessing a conversion.
            warning("Power column %s has no _W suffix; plotted without unit conversion.", name);
        end
    end
end


function label = makePowerLabel(varName)

    text = char(varName);

    token = regexp(text, ...
        '^p_(\d+)_([ABC])(?:_.*)?$', ...
        'tokens', 'once');

    if ~isempty(token)
        label = string(sprintf("Node %s Phase %s", token{1}, token{2}));
        return;
    end

    token = regexp(text, ...
        '^p_(\d+)(?:_.*)?$', ...
        'tokens', 'once');

    if ~isempty(token)
        label = string(sprintf("Node %s", token{1}));
        return;
    end

    label = string(varName);
end


function label = makeVoltageLabel(varName)

    text = char(varName);

    token = regexp(text, ...
        '^v_(\d+)_([ABC])(?:_.*)?$', ...
        'tokens', 'once');

    if ~isempty(token)
        label = string(sprintf("Node %s Phase %s", token{1}, token{2}));
    else
        label = string(varName);
    end
end


function formatTimeAxis(ax)

    if isempty(ax.XLim)
        return;
    end

    ax.XGrid = "on";
    ax.YGrid = "on";

    try
        xtickformat(ax, "dd-MMM");
    catch
    end

    ax.XTickLabelRotation = 30;
end


function text = formatTimestamp(t)
    text = char(string(t, "dd-MMM-yyyy HH:mm"));
end


function saveAssessmentFigure(fig, outputDir, baseName, savePng, saveFig)

    if savePng
        exportgraphics(fig, ...
            fullfile(outputDir, baseName + ".png"), ...
            "Resolution", 300);
    end

    if saveFig
        savefig(fig, fullfile(outputDir, baseName + ".fig"));
    end
end
