# 🔌 SESHIS - EV Charging Session Analysis Tool

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey.svg)]()

> **SESHIS** (*Session Statistics*) is a powerful command-line tool for analyzing electric vehicle (EV) charging session data from PowerFlex API endpoints. It provides comprehensive insights into charging patterns, identifies problematic sessions, and generates visual reports to help optimize EV charging infrastructure performance.

## 🌟 Features

### 📊 **Comprehensive Analysis**
- **Empty Sessions Analysis**: Identify and analyze sessions with 0 kWh energy delivery
- **Microsessions Analysis**: Detect sessions with minimal energy delivery (configurable threshold)
- **Combined Reports**: Get holistic view of charging session quality
- **Daily Breakdowns**: Track performance trends over time

### 📈 **Visual Reporting**
- **Interactive Graphs**: Generate matplotlib charts showing daily percentages
- **Trend Analysis**: Visualize empty/micro session patterns over time
- **Professional Charts**: Publication-ready graphs with proper formatting

### 🛠️ **Flexible Configuration**
- **Multiple Date Ranges**: Today, last week, last month, or custom date ranges
- **Customizable Thresholds**: Set your own microsession energy thresholds
- **API Parameters**: Full control over sorting, pagination, and filtering
- **Debug Mode**: Comprehensive logging for troubleshooting

### 🚀 **Automation Ready**
- **No-Prompt Mode**: Use `--printsessions` for automated workflows
- **Conditional Outputs**: Control exactly what gets displayed
- **Script-Friendly**: Perfect for CI/CD pipelines and monitoring systems

---

## 📋 Prerequisites

### System Requirements
- **Python 3.6+**
- **macOS** or **Linux**
- **curl_device_manager.sh** script (for API authentication)

### Python Dependencies
```bash
pip install matplotlib
```

### External Dependencies
- `curl_device_manager.sh` - Custom script for PowerFlex API authentication
- Must be accessible in your PATH or same directory

---

## 🚀 Installation

1. **Clone or download** the script:
   ```bash
   wget https://your-repo/seshis.py
   chmod +x seshis.py
   ```

2. **Install Python dependencies**:
   ```bash
   pip install matplotlib
   ```

3. **Ensure curl_device_manager.sh is available**:
   ```bash
   # Should be in PATH or same directory
   which curl_device_manager.sh
   ```

---

## 💡 Usage

### Basic Syntax
```bash
python3 seshis.py [OPTIONS]
```

### 🎛️ Command Line Options

| Flag | Description | Example |
|------|-------------|---------|
| `--empty` | Analyze empty sessions (0 kWh) | `--empty` |
| `--micro` | Analyze microsessions (0 < kWh < threshold) | `--micro` |
| `--graph` | Generate and display visual charts | `--graph` |
| `--printsessions` | Auto-print session details (no prompts) | `--printsessions` |
| `--debug` | Enable comprehensive debug logging | `--debug` |

---

## 📖 Usage Examples

### 🔍 **Basic Analysis**

**Empty Sessions Only**
```bash
python3 seshis.py --empty
```
*Shows summary statistics and daily breakdown of sessions with 0 kWh delivery*

**Microsessions Only**
```bash
python3 seshis.py --micro
```
*Prompts for threshold (e.g., 1.0 kWh) and analyzes sessions below that threshold*

### 📊 **Combined Analysis**

**Complete Quality Report**
```bash
python3 seshis.py --empty --micro --graph
```
*Comprehensive analysis with visual charts showing both empty and micro sessions*

**Automation-Ready Report**
```bash
python3 seshis.py --empty --micro --printsessions
```
*Full analysis with automatic session detail output (no user prompts)*

### 🛠️ **Advanced Usage**

**Debug Mode**
```bash
python3 seshis.py --empty --micro --graph --debug
```
*Detailed logging showing API calls, data processing, and analysis steps*

**Raw Session Data**
```bash
python3 seshis.py
```
*Outputs raw JSON session data without analysis*

---

## 🖥️ Interactive Configuration

When you run the script, you'll be prompted for various configuration options:

### 🏢 **Account Settings**
```
Enter ACN (default: 0021): [YOUR_ACN]
Enter account (default: 16): [YOUR_ACCOUNT]
```

### 🔬 **Analysis Settings** *(if using --micro)*
```
Enter microsession threshold (kWh, e.g., 1.0): [THRESHOLD]
```

### ⚙️ **API Parameters**
```
Anonymize? (true/false, default: false): [true/false]
Include active sessions? (true/false, default: false): [true/false]
Sort by (default: session_start_time): [SORT_FIELD]
Sort order (ASC/DESC, default: DESC): [ASC/DESC]
Limit (default: 25): [NUMBER]
Page (default: 1): [NUMBER]
```

### 📅 **Date Range Selection**
```
Date range options:
1. Today
2. Last week
3. Last month
4. Custom (enter dates manually)
Choose date range (1-4, default: 1): [1-4]
```

---

## 📄 Sample Output

### 📊 Empty Sessions Analysis
```
📊 Total sessions returned: 1000 (filtered from 1000)
⚡ Sessions with 0 kWh delivered: 651 (65.1% of total)

📅 Daily breakdown:
- 2025-09-07: 188 empty / 271 total (69.4%)
- 2025-09-08: 91 empty / 169 total (53.8%)
- 2025-09-09: 150 empty / 216 total (69.4%)
- 2025-09-10: 154 empty / 236 total (65.3%)
- 2025-09-11: 68 empty / 108 total (63.0%)
```

### 🔬 Microsessions Analysis
```
📊 Total sessions returned: 1000 (filtered from 1000)
🔬 Microsessions (0 < kWh < 1.0): 3 (0.3% of total)

📅 Daily breakdown:
- 2025-09-07: 1 micro / 271 total (0.4%)
- 2025-09-08: 0 micro / 169 total (0.0%)
- 2025-09-09: 1 micro / 216 total (0.5%)
- 2025-09-10: 1 micro / 236 total (0.4%)
- 2025-09-11: 0 micro / 108 total (0.0%)
```

### 🎯 Combined Summary
```
==================================================
🔍 COMBINED SUMMARY
==================================================
📊 Total sessions analyzed: 1000
⚡ Empty sessions (0 kWh): 651 (65.1%)
🔬 Microsessions (0 < kWh < 1.0): 3 (0.3%)
🎯 Combined (empty + micro): 654 (65.4%)
✅ Normal sessions (>= 1.0 kWh): 346 (34.6%)
```

---

## 🎨 Visual Reports

When using the `--graph` flag, SESHIS generates professional matplotlib charts:

### 📈 **Chart Features**
- **Line plots** with data point markers
- **Percentage-based** Y-axis for easy comparison
- **Date-based** X-axis with proper formatting
- **Grid lines** for enhanced readability
- **Professional styling** ready for presentations

### 📊 **Chart Types**
1. **Daily Empty Session Percentage** - Tracks empty session trends
2. **Daily Microsession Percentage** - Shows low-energy session patterns

---

## 🛡️ Error Handling

SESHIS includes robust error handling for common issues:

### 🔗 **API Connection Issues**
- Validates curl_device_manager.sh availability
- Handles network timeouts and connection failures
- Provides clear error messages with debugging context

### 📝 **Data Format Issues**
- Handles both list and dict API response formats
- Validates JSON parsing and data structure
- Filters out malformed session records

### 🔢 **Input Validation**
- Validates numeric thresholds for microsession analysis
- Handles invalid date formats gracefully
- Provides user-friendly error messages

---

## 🧪 Debug Mode

Enable comprehensive logging with the `--debug` flag:

### 🔍 **Debug Information Includes**
- **Configuration**: All parsed command-line arguments
- **API Calls**: Complete URLs and curl commands
- **Data Processing**: JSON parsing, session extraction, filtering
- **Analysis Steps**: Detailed breakdown of calculations
- **Error Context**: Full error details with stack traces

### 💡 **Debug Example**
```bash
python3 seshis.py --empty --debug
```

```
🔧 Debug mode enabled
🔧 Arguments parsed: {'empty': True, 'micro': False, 'graph': False, 'printsessions': False, 'debug': True}
🔧 ACN: 0021, Account: 16
🔧 Date range: 2025-09-11 00:00:00 to 2025-09-11 21:22:57.123456
🔧 Timestamp range: 1726012800000 to 1726089777123
🔧 API URL: https://api.powerflex.io/v1/public/sessions/acn/0021?acc=16&...
🔧 Running: curl_device_manager.sh -s -X GET "..." -H "accept: application/json"
🔧 Raw API response length: 15432 characters
🔧 JSON parsed successfully, type: <class 'dict'>
🔧 Extracted 1000 sessions from 'rows' key
🔧 Starting empty sessions analysis...
🔧 Empty analysis - Total: 1000, Valid: 1000, Empty: 651
```

---

## 🔧 Troubleshooting

### ❌ **Common Issues**

**1. "curl_device_manager.sh not found"**
```bash
# Ensure the script is in your PATH or current directory
which curl_device_manager.sh
# Or place it in the same directory as seshis.py
```

**2. "Failed to parse JSON response"**
```bash
# Run with debug to see raw response
python3 seshis.py --empty --debug
```

**3. "Unexpected API response format"**
```bash
# API might have changed format - check with debug mode
python3 seshis.py --debug
```

**4. "matplotlib not found"**
```bash
pip install matplotlib
```

### 🔍 **Getting Help**
1. **Enable debug mode** with `--debug` for detailed logging
2. **Check API connectivity** by running without analysis flags
3. **Validate date ranges** - ensure they contain session data
4. **Verify authentication** - ensure curl_device_manager.sh works independently

---

## 📚 Flag Combination Guide

### 🎯 **Flag Combinations & Behaviors**

| Combination | Behavior | Use Case |
|-------------|----------|----------|
| `--empty` | Empty session analysis + daily breakdown + prompt for details | Basic empty session investigation |
| `--micro` | Microsession analysis + threshold input + daily breakdown + prompt | Basic microsession investigation |
| `--empty --micro` | Both analyses + combined summary + two prompts | Complete session quality assessment |
| `--empty --graph` | Empty analysis + chart display | Visual empty session trends |
| `--empty --printsessions` | Empty analysis + auto-print details (no prompt) | Automated empty session reporting |
| `--empty --micro --graph` | Full analysis + both charts | Complete visual quality report |
| `--empty --micro --printsessions` | Full analysis + auto-print details | Automated comprehensive reporting |
| `--empty --micro --graph --printsessions` | Complete analysis with all features | Maximum information output |
| `--debug` (with any combo) | Adds comprehensive debug logging | Troubleshooting and development |
| *(no flags)* | Raw JSON session dump | Data export and integration |

---

## 🔄 Workflow Examples

### 📊 **Daily Monitoring Workflow**
```bash
# Morning report - check overnight session quality
python3 seshis.py --empty --micro --graph > daily_report.log

# Extract specific problematic sessions for investigation
python3 seshis.py --empty --printsessions > empty_sessions.json
```

### 🔧 **Troubleshooting Workflow**
```bash
# Step 1: Check if API is working
python3 seshis.py --debug

# Step 2: Analyze specific issues with full debug info
python3 seshis.py --empty --micro --debug > debug_output.log

# Step 3: Extract session details for detailed analysis
python3 seshis.py --empty --micro --printsessions > detailed_sessions.json
```

### 📈 **Performance Analysis Workflow**
```bash
# Weekly trend analysis with graphs
python3 seshis.py --empty --micro --graph

# Month-to-month comparison
# (Run with date range option 3 - Last month)
python3 seshis.py --empty --micro --graph --printsessions
```

---

## 📝 API Reference

### 🔗 **PowerFlex Sessions API**

**Endpoint**: `https://api.powerflex.io/v1/public/sessions/acn/{acn}`

**Parameters**:
- `acc` - Account ID
- `anonymize` - Boolean for data anonymization
- `includeActive` - Include active/ongoing sessions
- `sortBy` - Field to sort by (default: session_start_time)
- `sortOrder` - ASC or DESC
- `limit` - Number of results per page
- `page` - Page number for pagination
- `date` - Date range filters (gte/lte with millisecond timestamps)

**Response Format**:
```json
{
  "rows": [
    {
      "session_id": "0021160501_2025-09-11...",
      "reporting_id": 477544158,
      "session_kwh": 5.3713,
      "session_start_time": 1757623500418,
      "session_end_time": 1757623500470,
      "status": "FINISHED",
      "user": "user@example.com",
      "vehicle": "2020 Tesla Model Y Performance AWD",
      "site": "Site Name",
      "cost_actual": 0.81,
      ...
    }
  ],
  "total_count": 1000,
  "page": 1,
  "limit": 25
}
```

---

## 🎁 Pro Tips

### 💡 **Performance Tips**
1. **Use smaller date ranges** for faster analysis of large datasets
2. **Increase limit parameter** to reduce API calls for comprehensive analysis
3. **Run without --graph** first to check data quality before generating charts
4. **Use --debug selectively** - it produces verbose output

### 🔧 **Automation Tips**
1. **Always use --printsessions** in scripts to avoid interactive prompts
2. **Pipe output to files** for further processing: `seshis.py --empty > report.txt`
3. **Combine with cron jobs** for regular monitoring
4. **Use specific date ranges** in automation rather than "today" for consistency

### 📊 **Analysis Tips**
1. **Start with --empty --micro** to get overview before diving deep
2. **Use custom date ranges** to analyze specific incidents or time periods
3. **Compare different thresholds** for microsession analysis to find optimal values
4. **Look for patterns** in daily breakdowns to identify systematic issues

---

## 🤝 Contributing

We welcome contributions! Here are ways you can help:

### 🐛 **Bug Reports**
- Use debug mode to capture detailed logs
- Include your command-line arguments and configuration
- Provide sample API responses (with sensitive data removed)

### ✨ **Feature Requests**
- Open an issue describing the desired functionality
- Include use cases and expected behavior
- Consider backward compatibility

### 🔧 **Development**
- Follow existing code style and patterns
- Add debug logging for new features
- Update documentation for new functionality

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PowerFlex API** - For providing the charging session data endpoints
- **matplotlib** - For excellent charting capabilities
- **Python Community** - For the robust ecosystem of tools and libraries

---

## 📞 Support

For support, please:
1. **Check this README** for common solutions
2. **Run with `--debug`** to gather diagnostic information
3. **Open an issue** with detailed information about your problem

---

*Made with ❤️ for the EV charging community*
