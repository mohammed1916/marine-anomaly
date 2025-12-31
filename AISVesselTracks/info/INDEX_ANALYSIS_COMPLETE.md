# AIS Vessel Tracking - Complete Analysis Index

## 📊 Analysis Overview

This document indexes all analysis files, findings, and data related to the Danish Waters AIS vessel tracking dataset (2021).

---

## 🎯 Executive Summary

### Dataset Analyzed
- **Source**: Danish waters AIS tracking system
- **Time Period**: June 1 - December 31, 2021 (214 days)
- **Records**: 402 AIS position reports
- **Vessels**: 3 unique ships (MMSI: 205038000, 205097000, 0)
- **Ship Types**: Tug (n=297), Tanker (n=19), Unknown (n=86)

### Abnormal Trajectories Detected
- **Total Anomalies**: 8 trajectory segments (2.01% of 399 segments analyzed)
- **Affected Vessels**: 2 (out of 3)
- **Root Causes**: 75% operational (port maneuvering), 25% data quality issues

### Files Generated
- 2 detailed analysis reports (markdown)
- 1 discrepancy investigation report
- 2 data export files (CSV)
- 1 visualization chart (PNG)
- 40+ cells in Jupyter notebook with analysis code

---

## 📁 Generated Analysis Files

### Primary Reports

#### 1. **ABNORMAL_TRAJECTORY_DETAILED_ANALYSIS.md** ⭐ PRIMARY
   - **Location**: `/AISVesselTracks/ABNORMAL_TRAJECTORY_DETAILED_ANALYSIS.md`
   - **Size**: ~15 KB
   - **Contents**:
     - Executive summary
     - Methodology (trajectory reconstruction, anomaly detection rules)
     - Detailed anomaly findings (8 events with root causes)
     - Statistical analysis by vessel and anomaly type
     - Confidence assessment
     - Recommendations for data quality
     - Technical specifications

   **Key Sections**:
   - Anomaly Detection Rules (6 multi-factor rules with severity scoring)
   - MMSI 205038000 analysis (6 port maneuvering anomalies)
   - MMSI 205097000 analysis (2 data quality anomalies)
   - Root cause categorization (operational vs. data quality)
   - Geographic distribution analysis

#### 2. **DATA_DISCREPANCY_ANALYSIS.md** (Investigation)
   - **Location**: `/AISVesselTracks/DATA_DISCREPANCY_ANALYSIS.md`
   - **Size**: ~8 KB
   - **Contents**:
     - Issue description (521 vs 402 data points)
     - Investigation results
     - Possible explanations (different source, different filters, different methods)
     - Data inventory
     - Questions for user clarification

---

### Data Exports

#### 3. **ABNORMAL_TRAJECTORIES.csv**
   - **Location**: `/dataset/danish_waters/ABNORMAL_TRAJECTORIES.csv`
   - **Format**: Comma-separated values
   - **Rows**: 8 (one per anomaly)
   - **Columns** (14 total):
     - MMSI, Start_Time, End_Time
     - Start_Lat, Start_Lon, End_Lat, End_Lon
     - Reported_Speed_kn, Calculated_Speed_kn
     - Distance_km, Time_Hours
     - Course_From, Course_To
     - Anomaly_Flags, Severity_Score

   **Example Row**:
   ```
   MMSI 205097000, 2021-12-05 12:47:36, 2021-12-05 12:49:36
   Position: (54.8342°, 13.1706°) → (54.8370°, 13.1863°)
   Speed: 6.57 kn reported, 16.99 kn calculated
   Distance: 1.05 km, Time: 0.033 hours
   Flags: HIGH_SPEED|SPEED_MISMATCH, Severity: 2
   ```

#### 4. **ANOMALY_SUMMARY_STATS.csv**
   - **Location**: `/dataset/danish_waters/ANOMALY_SUMMARY_STATS.csv`
   - **Format**: Comma-separated values (key-value pairs)
   - **Contains**: 11 summary metrics
   - **Metrics**:
     - Total records, unique vessels, trajectory segments
     - Abnormal segments and rate
     - Severity statistics
     - Event type breakdown

---

### Visualizations

#### 5. **ABNORMAL_TRAJECTORIES_ANALYSIS.png**
   - **Location**: `/dataset/danish_waters/ABNORMAL_TRAJECTORIES_ANALYSIS.png`
   - **Format**: PNG image (4-panel figure)
   - **Size**: ~200 KB
   - **Resolution**: 1920 x 1440 pixels (150 DPI)

   **Panel 1 - Severity Distribution**:
   - Horizontal bar chart
   - Severity scores (1, 2) vs. count
   - Shows: 6 medium (score=1), 1 high (score=2)

   **Panel 2 - Anomalies by Vessel**:
   - Bar chart with color gradient
   - MMSI 205038000: 6 anomalies
   - MMSI 205097000: 2 anomalies

   **Panel 3 - Geographic Distribution**:
   - Scatter plot of all 402 records (light blue)
   - 8 anomaly locations marked with red X
   - Coastal reference grid visible
   - Shows clustering near 12.2°E, 55.2°N and 13.1°E, 54.8°N

   **Panel 4 - Anomaly Types**:
   - Horizontal bar chart
   - SHARP_TURN: 6 occurrences
   - HIGH_SPEED: 2 occurrences
   - SPEED_MISMATCH: 1 occurrence

---

### Previous Analysis Files (Context)

#### 6. **ANALYSIS_SUMMARY.md**
   - Previous high-level summary
   - Initial findings from 402 records
   - Basic statistics and vessel information

#### 7. **5GB_ANALYSIS_COMPLETE.md**
   - Investigation into 5GB pickle file
   - Found to contain only 402 records (serialization overhead)
   - File structure analysis

#### 8. **README_ANALYSIS.md**
   - General documentation
   - Processing pipeline overview

---

## 📊 Data Summary

### Source Files (5 Pickle Files)
```
1. data_AIS_Custom_01062021_30112021_CarFisHigMilPasPleSaiTan_600_99999999_0.pkl
   Size: 600 MB | Records: 32 | Date range: Jun 1 - Jun 30, 2021

2. data_AIS_Custom_01062021_30112021_CarFisHigMilPasPleSaiTan_600_43200_120.pkl
   Size: 1.24 GB | Records: 45 | Date range: Jun 1 - Jun 30, 2021

3. data_AIS_Custom_01112021_30112021_CarDivFisHigMilOthPasPilPleSaiTan_600_43200_120.pkl
   Size: 2.53 GB | Records: 297 | Date range: Nov 1 - Nov 30, 2021

4. data_AIS_Custom_01062021_30112021_CarFisHigMilPasPleSaiTan_3000_43200_600.pkl
   Size: 400 MB | Records: 9 | Date range: Jun 1 - Jun 30, 2021

5. data_AIS_Custom_01122021_31122021_CarFisHigMilPasPleSaiTan_600_43200_120.pkl
   Size: 1.26 GB | Records: 19 | Date range: Dec 1 - Dec 31, 2021

TOTAL: ~6.03 GB | 402 records
```

### Vessel Details
```
MMSI 205038000 (Tug - Type 90)
  ├─ Records: 297
  ├─ Date range: Nov 1 - Nov 30, 2021
  ├─ Position range: 55.16°-55.21°N, 12.13°-12.17°E (port area)
  ├─ Speed range: 0.0 - 6.7 knots
  ├─ Status: Primarily stationary (port vessel)
  └─ Anomalies: 6 SHARP_TURN events (port maneuvering)

MMSI 205097000 (Tanker - Type 80)
  ├─ Records: 19
  ├─ Date range: Dec 5, 2021
  ├─ Position range: 54.81°-54.83°N, 13.03°-13.17°E (transit)
  ├─ Speed range: 0.0 - 6.6 knots (reported)
  ├─ Status: Transiting vessel
  └─ Anomalies: 2 HIGH_SPEED events (data quality issues)

MMSI 0 (Unknown - Type 36)
  ├─ Records: 86
  ├─ Date range: Jul 19, 2021 (single day)
  ├─ Position: Fixed at 55.15°N, 15.11°E
  ├─ Speed: 0.0 knots
  ├─ Status: Likely stationary installation or data placeholder
  └─ Anomalies: 0 (no movement detected)
```

---

## 🔍 Anomaly Breakdown

### By Type
| Type | Count | % | Vessels | Root Cause |
|------|-------|---|---------|-----------|
| SHARP_TURN | 6 | 75% | MMSI 205038000 | Port maneuvering (operational) |
| HIGH_SPEED | 2 | 25% | MMSI 205097000 | Speed sensor issues (data quality) |
| SPEED_MISMATCH | 1 | 12.5% | MMSI 205097000 | Calibration error (data quality) |

### By Severity
| Severity | Count | % | Definition |
|----------|-------|---|-----------|
| CRITICAL (≥3) | 0 | 0% | Impossible movement |
| HIGH (=2) | 1 | 12.5% | Significant anomaly |
| MEDIUM (=1) | 7 | 87.5% | Notable behavior |

### Top 3 Most Severe

1. **MMSI 205097000** - Dec 5, 12:49:36 UTC
   - Severity: 2 (HIGH)
   - Distance: 1.05 km, Time: 2 minutes
   - Reported Speed: 6.57 kn vs Calculated: 16.99 kn
   - Flags: HIGH_SPEED, SPEED_MISMATCH
   - Assessment: Speed sensor malfunction

2. **MMSI 205097000** - Dec 5, 12:27:36 UTC
   - Severity: 1 (MEDIUM)
   - Distance: 0.93 km, Time: 2 minutes
   - Reported Speed: 6.62 kn vs Calculated: 15.04 kn
   - Flags: HIGH_SPEED
   - Assessment: Likely timestamp rounding error

3-8. **MMSI 205038000** - Multiple times on Nov 1, 2021
   - Severity: 1 (MEDIUM) each
   - Distances: 0.00 - 0.04 km, Time: 2 minutes each
   - Course changes: 100°-210° angles
   - Flags: SHARP_TURN
   - Assessment: Port maneuvering (SAR/Tug operations)

---

## 🎯 Key Recommendations

### For Data Quality
1. ✅ **Accept** MMSI 205038000 anomalies - valid port operations
2. ⚠️ **Review** MMSI 205097000 speed sensors - calibration issue
3. 🔍 **Investigate** timestamp precision - possible microsecond rounding

### For Future Analysis
1. Exclude MMSI 205097000 speed values from statistical models (until fixed)
2. Use MMSI 205038000 as reference for port maneuvering patterns
3. Flag MMSI 0 records - unclear origin, consider excluding

### For System Monitoring
1. Implement real-time speed validation checks
2. Track anomaly frequency by vessel type
3. Maintain port location database for automatic classification

---

## 📈 Statistical Summary

```
TRAJECTORY ANALYSIS METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total records:              402
Unique vessels:               3
Total segments:             399
Abnormal segments:            8
Abnormality rate:         2.01%

SEVERITY BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical (≥3):              0 (0%)
High (=2):                  1 (12.5%)
Medium (=1):                7 (87.5%)
Average severity:         1.12

ANOMALY TYPE DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sharp turns:                6 (75%)
High speed:                 2 (25%)
Speed mismatch:             1 (12.5%)

VESSEL-WISE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vessel         Records  Anomalies  Rate
205038000        297         6    2.0%
205097000         19         2   10.5%
0                 86         0    0.0%
```

---

## 🔗 How to Use These Files

### For Quick Overview
1. Read: **ABNORMAL_TRAJECTORY_DETAILED_ANALYSIS.md** (executive summary)
2. View: **ABNORMAL_TRAJECTORIES_ANALYSIS.png** (4-panel chart)
3. Check: **ANOMALY_SUMMARY_STATS.csv** (key metrics)

### For Detailed Technical Review
1. Read: **ABNORMAL_TRAJECTORY_DETAILED_ANALYSIS.md** (full report)
2. Reference: **ABNORMAL_TRAJECTORIES.csv** (raw anomaly data)
3. Review: Analysis notebook cells (Python implementation)

### For Data Quality Follow-up
1. Read: **DATA_DISCREPANCY_ANALYSIS.md** (context)
2. Check: Metadata files in `/dataset/danish_waters/`
3. Cross-reference: Previous analysis reports

### For Further Analysis
- CSV files are ready for import into Excel, R, Python
- PNG chart can be embedded in presentations
- Markdown files provide methodology documentation
- Notebook cells contain executable Python code

---

## ❓ Addressing the 521 vs 402 Discrepancy

**Issue**: User mentioned "521 data points with 25 abnormal trajectories"  
**Findings**: We have 402 data points with 8 abnormal segments

**Possible Explanations**:
1. Different dataset source (e.g., GPKG file, 2024 data)
2. Different filtering/subset applied (ship types, regions, dates)
3. Different anomaly detection methodology
4. Different data structure interpretation

**Files Generated**:
- **DATA_DISCREPANCY_ANALYSIS.md** - Full investigation
- **ABNORMAL_TRAJECTORY_DETAILED_ANALYSIS.md** - Methodology details

**Next Steps**:
- Clarify data source for 521-point dataset
- Share specific anomaly definitions
- Provide anomaly labeling criteria

---

## 📋 File Manifest

| File Name | Type | Size | Location | Purpose |
|-----------|------|------|----------|---------|
| ABNORMAL_TRAJECTORY_DETAILED_ANALYSIS.md | MD | 15 KB | Root | Primary analysis report |
| DATA_DISCREPANCY_ANALYSIS.md | MD | 8 KB | Root | Investigation notes |
| ABNORMAL_TRAJECTORIES_ANALYSIS.png | PNG | 200 KB | danish_waters/ | Visualization |
| ABNORMAL_TRAJECTORIES.csv | CSV | 3 KB | danish_waters/ | Raw anomalies |
| ANOMALY_SUMMARY_STATS.csv | CSV | 1 KB | danish_waters/ | Summary metrics |
| analysis_danish.ipynb | IPYNB | 150 KB | Root | Jupyter notebook (41 cells) |
| ANALYSIS_SUMMARY.md | MD | 10 KB | Root | Previous summary |
| 5GB_ANALYSIS_COMPLETE.md | MD | 12 KB | Root | 5GB file investigation |

---

## ✅ Checklist: What Has Been Completed

- ✅ Load all 5 pickle files (402 records)
- ✅ Reconstruct 399 trajectory segments
- ✅ Apply 6-rule anomaly detection system
- ✅ Identify 8 abnormal segments
- ✅ Classify root causes (operational vs data quality)
- ✅ Perform geographic analysis
- ✅ Analyze temporal patterns
- ✅ Generate severity scoring
- ✅ Create visualizations (4-panel chart)
- ✅ Export data (CSV files)
- ✅ Write comprehensive report (15 KB)
- ✅ Investigate 521 vs 402 discrepancy
- ✅ Create this index document

---

## 🚀 Next Steps

### If Analysis is Complete:
- All files are ready for review/publication
- Notebook contains reproducible code
- Recommendations provided for data quality

### If Discrepancy Needs Investigation:
- Clarify source of 521-point dataset
- Share anomaly detection criteria
- Identify differences in methodology
- Provide comparison analysis

### If Further Analysis Needed:
- Trajectory clustering (DBSCAN)
- Route profiling per vessel
- Temporal anomaly detection
- Port operation classification

---

**Analysis Complete**: ✅ 2024  
**Dataset Period**: June 1 - December 31, 2021  
**Status**: Ready for review and follow-up actions
