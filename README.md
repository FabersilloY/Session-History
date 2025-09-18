# 🔌 SESHIS - EV Charging Session Analysis Tool

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey.svg)]()

> **SESHIS** (*Session Statistics*) is a powerful command-line tool for analyzing electric vehicle (EV) charging session data from PowerFlex API endpoints. It provides comprehensive insights into charging patterns, identifies problematic sessions, analyzes user behavior, tracks unclaimed sessions, and generates professional visual reports to help optimize EV charging infrastructure performance.

## 🌟 Key Features Overview

### 📊 **What SESHIS Can Do For You**
- **Identify Problem Sessions**: Find empty sessions (0 kWh) and microsessions (very low energy delivery)
- **Analyze User Behavior**: See how different users interact with your charging stations
- **Track Unclaimed Sessions**: Monitor sessions where users didn't scan QR codes first
- **Generate Professional Reports**: Create PDF reports and CSV exports for stakeholders
- **Visualize Trends**: Generate charts to spot patterns over time
- **Performance Analysis**: Automatically calculate charging performance metrics

### 🔓 **NEW: Unclaimed Sessions Tracking**
One of the most important features is tracking **unclaimed sessions** - these are sessions where someone plugged in their vehicle without scanning the QR code with the app first. These sessions help identify:
- User education opportunities
- Signage effectiveness issues  
- Sites that may need better QR code visibility
- Potential revenue loss from untracked usage

## 🚀 Quick Start Guide

### Most Common Use Cases

**1. Daily Site Health Check**
```bash
python3 seshis.py --all --pdf
```
*Generates a comprehensive PDF report showing all users, all session types, and unclaimed sessions*

**2. Export Data for Spreadsheet Analysis**
```bash
python3 seshis.py --all --csv
```
*Exports complete session data to a timestamped CSV file*

**3. Quick Problem Session Overview**
```bash
python3 seshis.py --empty --micro
```
*Shows summary of empty and microsession issues with statistics*

**4. User Performance Analysis**
```bash
python3 seshis.py --user
```
*Color-coded analysis of all users including unclaimed sessions*

---

## 📋 Prerequisites

### What You Need
- **Python 3.6+**
- **curl_device_manager.sh** script (for PowerFlex API authentication)
- **matplotlib** (`pip install matplotlib`) - for charts
- **reportlab** (`pip install reportlab`) - for PDF reports (optional)

### Quick Setup
```bash
# Install dependencies
pip install matplotlib reportlab

# Ensure authentication script is available
which curl_device_manager.sh
```

---

## 💡 Command Line Options

| Flag | What It Does | Example |
|------|-------------|---------|
| `--empty` | Find sessions with 0 kWh delivered | `--empty` |
| `--micro` | Find sessions with very low energy (you set threshold) | `--micro` |
| `--user` | Analyze sessions by user (optional: specify email) | `--user` or `--user john@example.com` |
| `--all` | **NEW!** Complete analysis of all session types by user | `--all --pdf` |
| `--csv` | Export data to spreadsheet file | `--empty --csv` |
| `--pdf` | Generate professional PDF report | `--user --pdf` |
| `--graph` | Show visual charts | `--empty --graph` |
| `--advanced` | Enable all configuration options | `--advanced` |
| `--debug` | Show detailed technical information | `--debug` |

### ⚠️ Important Flag Rules
- Export flags (`--csv`, `--pdf`) require at least one analysis flag
- Can't use `--csv` and `--pdf` together (run separately)  
- Can't use exports with `--graph` (run separately)
- Use double dashes: `--pdf` not `-pdf`

---

## 📖 Real-World Usage Examples

### 🏢 **Daily Operations**

**Morning Site Report**
```bash
python3 seshis.py --all --pdf
```
*Perfect for daily management reports - shows everything in one professional document*

**Quick Health Check**
```bash
python3 seshis.py --user
```
*Fast overview of user activity with color-coded performance and unclaimed sessions*

**Problem Investigation**
```bash
python3 seshis.py --empty --micro --debug
```
*Detailed analysis when you need to investigate site issues*

### 📊 **Data Analysis & Reporting**

**Export for Spreadsheet Work**
```bash
python3 seshis.py --all --csv
```
*Complete dataset for Excel/Google Sheets analysis*

**Weekly Trend Analysis**
```bash
python3 seshis.py --empty --micro --graph
```
*Visual charts showing session quality trends over time*

**User-Specific Investigation**
```bash
python3 seshis.py --user problematic.user@domain.com --pdf
```
*Detailed report for specific user issues*

### 🔧 **Troubleshooting**

**Site Performance Deep Dive**
```bash
python3 seshis.py --all --debug
```
*Comprehensive analysis with technical details*

**Unclaimed Sessions Focus**
```bash
python3 seshis.py --user
# Look at the "🔓 UNCLAIMED SESSIONS" section at the bottom
```
*Specifically monitor sessions without QR code scans*

---

## 🔓 Understanding Unclaimed Sessions

### What Are Unclaimed Sessions?
Unclaimed sessions appear when someone:
1. Plugs in their vehicle
2. **Doesn't scan the QR code** with the app first
3. Charging happens but isn't linked to a user account

### Why They Matter
- **Revenue Impact**: Untracked usage may not be properly billed
- **User Experience**: Indicates users aren't following proper procedures
- **Site Issues**: High unclaimed percentages might mean poor signage or QR code visibility
- **Education Opportunities**: Shows where user training is needed

### How SESHIS Helps
- **Always Visible**: Unclaimed sessions appear at the bottom of every user analysis
- **Clear Statistics**: Shows breakdown of empty, micro, and normal unclaimed sessions
- **Export Ready**: Unclaimed sessions are properly labeled in CSV and PDF exports
- **Performance Analysis**: Same color-coded performance metrics applied

---

## 🎨 Understanding Color-Coded Performance

When you see session details, they're color-coded based on charging performance:

- **🟢 Green [NORMAL-HIGH]**: ≥16A average - Excellent charging
- **🟡 Orange [NORMAL-MED]**: 8-15.9A average - Good charging  
- **🔴 Red [NORMAL-LOW]**: <8A average - Poor performance, investigate
- **🔴 Red [EMPTY]**: 0 kWh - Failed sessions
- **🟡 Orange [MICRO]**: Very low energy - Partial sessions

### What This Tells You
- **Lots of Red**: Potential hardware issues or user behavior problems
- **Lots of Green**: Site is performing well
- **Mixed Colors**: Normal variation, but trends matter

---

## 📄 Sample Output Explained

### User Analysis Output
```bash
👥 User Session Summary:
📊 Total unique users: 15

User: john.doe@example.com (85.7% normal sessions)
    Total sessions: 7
    Empty sessions (0 kWh): 1 (14.3%)
    Normal sessions (>= 1.0 kWh): 6 (85.7%)

    Showing 7 sessions:
    Session 1: START: 2025-09-15 08:30:15 / END: 2025-09-15 12:45:22 / DURATION: 4.3h / 8.5 kWh / session_id_123 [NORMAL-MED]

🔓 UNCLAIMED SESSIONS (25.0% normal sessions)
    These are sessions where users plugged in without scanning the QR code first
    Total sessions: 12
    Empty sessions (0 kWh): 8 (66.7%)
    Normal sessions (>= 1.0 kWh): 3 (25.0%)
    
    Showing 12 unclaimed sessions:
    Session 1: START: 2025-09-15 14:20:10 / END: 2025-09-15 14:20:45 / DURATION: 35.0s / 0 kWh / session_id_456 [EMPTY]
```

### What This Means
- **john.doe@example.com**: Good user with mostly successful sessions
- **Unclaimed Sessions**: 12 sessions without QR scans, mostly failed (empty)
- **Action Needed**: High empty rate in unclaimed suggests signage or hardware issues

---

## 📊 Export Options Explained

### CSV Export (`--csv`)
**Best For**: Detailed data analysis, spreadsheet work, automated processing

**What You Get**:
- Timestamped filename (2025_09_18_143022.csv)
- All session fields (duration, performance, user info, etc.)
- Unclaimed sessions clearly labeled as "🔓 UNCLAIMED SESSIONS"
- Ready for Excel/Google Sheets

**Example**:
```bash
python3 seshis.py --all --csv
# Creates: 2025_09_18_143022.csv with complete data
```

### PDF Export (`--pdf`)
**Best For**: Professional reports, management presentations, record keeping

**What You Get**:
- Professional landscape layout
- Color-coded sessions (Green/Orange/Red indicators)
- Site branding (if pf.jpg logo exists)
- Unclaimed sessions with explanatory text
- User grouping with statistics

**Example**:
```bash
python3 seshis.py --all --pdf
# Creates: 2025_09_18_143022.pdf with professional report
```

---

## 🔧 Configuration Options

### Basic Setup
When you run the script, you'll be prompted for:

```
Enter ACN (default: 0021): [Press enter for default]
Enter account (default: 16): [Press enter for default]
```

### Date Range Selection
```
Date range options:
1. Today
2. Last week  
3. Last month
4. Custom (enter dates manually)
Choose date range (1-4, default: 1): [Choose option]
```

### Analysis-Specific Options

**For Microsession Analysis (`--micro`)**:
```
Enter microsession threshold (kWh, e.g., 1.0): 1.0
```
*Sessions below this threshold are considered "micro"*

**For Advanced Mode (`--advanced`)**:
Enables additional API configuration options for power users.

---

## 🚨 Troubleshooting Common Issues

### "unrecognized arguments: -pdf"
**Problem**: Using single dash instead of double dash
**Solution**: Use `--pdf` not `-pdf`

### "curl_device_manager.sh not found"
**Problem**: Authentication script not in PATH
**Solution**: Place script in same directory as seshis.py or add to PATH

### "PDF export requires reportlab library"
**Problem**: Missing PDF dependency
**Solution**: `pip install reportlab`

### "--csv/--pdf requires at least one analysis flag"
**Problem**: Trying to export without analysis
**Solution**: Use `--empty`, `--micro`, `--user`, or `--all` with export flags

### Script outputs raw JSON after export
**Problem**: This was a bug that's been fixed
**Solution**: Update to latest version - script should stop after showing "📊 X sessions exported"

---

## 📈 Team Workflows

### For Site Managers
**Daily Report**:
```bash
python3 seshis.py --all --pdf
```
*One-stop comprehensive site health report*

### For Data Analysts  
**Full Data Export**:
```bash
python3 seshis.py --all --csv
```
*Complete dataset for detailed analysis*

### For Operations Teams
**Problem Investigation**:
```bash
python3 seshis.py --empty --micro --debug
python3 seshis.py --user problematic.user@domain.com
```
*Targeted analysis for specific issues*

### For Executive Reporting
**Monthly Summary**:
```bash
# Set date range to "Last month" when prompted
python3 seshis.py --all --pdf
```
*Professional monthly performance report*

---

## 🎯 Key Metrics to Monitor

### Session Quality Metrics
- **Empty Session %**: Should be <20% (high percentages indicate hardware issues)
- **Microsession %**: Should be <5% (high percentages indicate user behavior issues)
- **Normal Session %**: Should be >75% (indicates healthy site operation)

### User Behavior Metrics
- **Unclaimed Session %**: Should be <30% (high percentages indicate user education needs)
- **Users with High Empty Rates**: May need individual support
- **Performance Distribution**: Most sessions should be green/orange, not red

### Site Performance Indicators
- **Average Session Duration**: Varies by use case but consistency matters
- **Performance Color Distribution**: More green/orange than red
- **Daily Trends**: Consistent patterns vs. sudden changes

---

## 🔄 Recommended Monitoring Schedule

### Daily (5 minutes)
```bash
python3 seshis.py --user
```
*Quick health check and unclaimed session review*

### Weekly (15 minutes)
```bash
python3 seshis.py --all --pdf
python3 seshis.py --empty --micro --graph
```
*Comprehensive report + trend analysis*

### Monthly (30 minutes)
```bash
python3 seshis.py --all --csv
# Analyze in spreadsheet for deeper insights
```
*Full data export for detailed analysis*

### As-Needed Troubleshooting
```bash
python3 seshis.py --all --debug
```
*When investigating specific issues*

---

## 🆕 What's New in Latest Version

### Major New Features
- **🔓 Unclaimed Sessions**: Dedicated tracking and analysis
- **📊 --all Flag**: Complete site analysis in one command
- **🎨 Enhanced PDF Reports**: Better layout with unclaimed session explanations
- **⚡ Fixed Export Issues**: Script properly stops after exports
- **🏷️ Better Labeling**: Clear identification of unclaimed sessions

### Improvements
- **Better Error Messages**: More helpful troubleshooting information
- **Improved Export Organization**: Clearer separation of session types
- **Enhanced Documentation**: This comprehensive README
- **Color-Coded Consistency**: Same performance indicators across all features

---

## 💡 Pro Tips for Teams

### For New Users
1. **Start with `--all --pdf`** - gives you complete overview
2. **Pay attention to unclaimed sessions** - they're often overlooked but important
3. **Use color coding** - red sessions need investigation
4. **Export to CSV for detailed analysis** - easier than working with terminal output

### For Power Users
1. **Use `--debug` for troubleshooting** - shows exactly what's happening
2. **Combine with cron jobs** for automated reporting
3. **Use custom date ranges** for incident investigation
4. **Export separate analysis types** when you need specific datasets

### For Managers
1. **`--all --pdf` for stakeholder reports** - professional and comprehensive
2. **Monitor unclaimed session percentages** - indicates user experience quality
3. **Track trends over time** - sudden changes indicate issues
4. **Use CSV exports for executive dashboards** - easier to integrate with other tools

---

## 📞 Getting Help

### Quick Self-Help
1. **Read the error message carefully** - they're designed to be helpful
2. **Run with `--debug`** - shows detailed information about what went wrong
3. **Check flag combinations** - some flags can't be used together
4. **Verify file permissions** - especially for exports

### Common Solutions
- **Authentication issues**: Check curl_device_manager.sh
- **Export problems**: Verify dependencies (matplotlib, reportlab)
- **Flag errors**: Use double dashes (`--pdf` not `-pdf`)
- **No data**: Check date ranges and API connectivity

---

*Made with ❤️ for the EV charging community by the PowerFlex team*

---

## 📚 Appendix: Complete Flag Reference

### Analysis Flags
- `--empty`: Analyze 0 kWh sessions
- `--micro`: Analyze low-energy sessions (with threshold)
- `--user`: Analyze by user (with optional email filter)
- `--all`: Complete analysis of all session types

### Export Flags  
- `--csv`: Export to spreadsheet format
- `--pdf`: Export to professional report format

### Utility Flags
- `--graph`: Generate visual charts
- `--advanced`: Enable all configuration options  
- `--printsessions`: Auto-print details (for automation)
- `--debug`: Show technical information

### Usage Rules
- Export flags require analysis flags
- Can't combine `--csv` and `--pdf`
- Can't combine exports with `--graph`
- Use double dashes for all flags
