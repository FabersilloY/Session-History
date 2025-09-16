# 🔌 SESHIS - EV Charging Session Analysis Tool

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey.svg)]()

> **SESHIS** (*Session Statistics*) is a powerful command-line tool for analyzing electric vehicle (EV) charging session data from PowerFlex API endpoints. It provides comprehensive insights into charging patterns, identifies problematic sessions, analyzes user behavior, and generates visual reports to help optimize EV charging infrastructure performance.

## 🌟 Features

### 📊 **Comprehensive Analysis**
- **Empty Sessions Analysis**: Identify and analyze sessions with 0 kWh energy delivery
- **Microsessions Analysis**: Detect sessions with minimal energy delivery (configurable threshold)
- **User Session Analysis**: Analyze sessions grouped by user with detailed session information and performance metrics
- **Combined Reports**: Get holistic view of charging session quality
- **Daily Breakdowns**: Track performance trends over time

### 📈 **Visual Reporting**
- **Interactive Graphs**: Generate matplotlib charts showing daily percentages
- **Color-Coded Performance**: Visual indicators for session quality (Green/Orange/Red)
- **Trend Analysis**: Visualize empty/micro session patterns over time
- **Professional Charts**: Publication-ready graphs with proper formatting

### 🛠️ **Flexible Configuration**
- **Multiple Date Ranges**: Today, last week, last month, or custom date ranges
- **Customizable Thresholds**: Set your own microsession energy thresholds
- **User Filtering**: Analyze all users or focus on specific email addresses
- **Streamlined Interface**: Use `--advanced` flag for full control or simplified defaults
- **API Parameters**: Full control over sorting, pagination, and filtering
- **Debug Mode**: Comprehensive logging for troubleshooting

### 🚀 **Automation Ready**
- **No-Prompt Mode**: Use `--printsessions` for automated workflows
- **Streamlined Mode**: Default mode skips advanced prompts for faster execution
- **Conditional Outputs**: Control exactly what gets displayed
- **Color-Coded Results**: Visual performance indicators for quick assessment
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
| `--user` | Analyze sessions per user (optional: specify email) | `--user` or `--user user@example.com` |
| `--advanced` | Enable advanced prompts (anonymize, sorting, etc.) | `--advanced` |
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

**User Session Analysis**
```bash
python3 seshis.py --user
```
*Shows all users and their sessions with detailed information including duration and performance*

**Specific User Analysis**
```bash
python3 seshis.py --user vera.combatvet@gmail.com
```
*Shows only sessions for the specified user with color-coded performance indicators*

### 📊 **Combined Analysis**

**Complete Quality Report**
```bash
python3 seshis.py --empty --micro --graph
```
*Comprehensive analysis with visual charts showing both empty and micro sessions*

**User Performance Overview**
```bash
python3 seshis.py --user --debug
```
*Color-coded user analysis with performance calculations and debug information*

**Automation-Ready Report**
```bash
python3 seshis.py --empty --micro --printsessions
```
*Full analysis with automatic session detail output (no user prompts)*

### 🛠️ **Advanced Usage**

**Advanced Configuration Mode**
```bash
python3 seshis.py --user --advanced
```
*Enables all configuration prompts for full control over API parameters*

**Debug Mode**
```bash
python3 seshis.py --empty --micro --graph --debug
```
*Detailed logging showing API calls, data processing, and analysis steps*

**Multi-User Performance Analysis**
```bash
python3 seshis.py --user --graph --debug
```
*Color-coded user analysis with performance calculations and debug information*

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

**Default Mode** *(streamlined - uses defaults)*:
```
Limit (default: 25): [NUMBER]
Page (default: 1): [NUMBER]
```
*Automatically uses: anonymize=false, includeActive=false, sortBy=session_start_time, sortOrder=DESC*

**Advanced Mode** *(when using --advanced flag)*:
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
🏢 Site: Downtown Charging Hub
📊 Total sessions analyzed: 1000
⚡ Empty sessions (0 kWh): 651 (65.1%)
🔬 Microsessions (0 < kWh < 1.0): 3 (0.3%)
🎯 Combined (empty + micro): 654 (65.4%)
✅ Normal sessions (>= 1.0 kWh): 346 (34.6%)
```

### 👥 User Session Analysis
```
👥 User Session Summary:
📊 Total unique users: 15

User: null
    Total sessions: 42

User: vera.combatvet@gmail.com
    Total sessions: 8
    Session 1: START: 2025-09-15 07:12:27 / END: 2025-09-15 07:13:13 / DURATION: 46.0s / 0.0221 kWh / 0101110106_2025-09-12...
    Session 2: START: 2025-09-12 16:16:48 / END: 2025-09-13 00:44:54 / DURATION: 8.5h / 12.763 kWh / 0101110102_2025-08-20...
    ...

User: john.doe@example.com
    Total sessions: 3
    Session 1: START: 2025-08-20 19:29:13 / END: 2025-08-21 00:21:03 / DURATION: 4.9h / 12.76309 kWh / 0101110102_2025-08-20...
    ...
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

### 🎨 **Color-Coded Session Analysis**

When using the `--user` flag, sessions are displayed with color coding based on charging performance:

- **🟢 Green**: High performance sessions (≥16A average) - Optimal charging
- **🟡 Orange**: Medium performance sessions (8-15.9A average) - Acceptable charging  
- **🔴 Red**: Poor performance sessions (<8A average) - Potential issues

**Performance Calculation**: 
- Average Power = `kWh ÷ duration (hours)`
- Average Amperage = `watts ÷ 208V`
- Color assigned based on calculated amperage vs. minimum 8A fallback rate

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
- **Performance Metrics**: Amperage calculations for user sessions
- **Error Context**: Full error details with stack traces

### 💡 **Debug Example**
```bash
python3 seshis.py --user --debug
```

```
🔧 Debug mode enabled
🔧 Arguments parsed: {'user': 'all', 'empty': False, 'micro': False, 'advanced': False, 'graph': False, 'printsessions': False, 'debug': True}
🔧 ACN: 0021, Account: 16
🔧 Using default advanced options: anonymize=false, include_active=false, sort_by=session_start_time, sort_order=DESC
🔧 Date range: 2025-09-16 00:00:00 to 2025-09-16 21:22:57.123456
🔧 Starting user session analysis (filter: all)...
🔧 Session 1 calculations: 8.47h, 2.6W, 0.01A
🔧 Session 2 calculations: 4.90h, 2603.2W, 12.5A
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

**3. "User 'email@domain.com' not found"**
```bash
# Run --user without email to see available users
python3 seshis.py --user
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
| `--empty` | Empty session analysis + daily breakdown | Basic empty session investigation |
| `--micro` | Microsession analysis + threshold input | Basic microsession investigation |
| `--user` | All users session analysis + color-coded performance | User behavior and performance analysis |
| `--user email@domain.com` | Single user analysis + color-coded sessions | Individual user troubleshooting |
| `--advanced` | Enables all configuration prompts | Full API parameter control |
| `--empty --micro` | Both analyses + combined summary | Complete session quality assessment |
| `--empty --graph` | Empty analysis + chart display | Visual empty session trends |
| `--user --advanced` | User analysis + full configuration options | Advanced user performance analysis |
| `--empty --printsessions` | Empty analysis + auto-print details | Automated empty session reporting |
| `--user --debug` | User analysis + performance calculations shown | User performance troubleshooting |
| `--debug` (with any combo) | Adds comprehensive debug logging | Troubleshooting and development |
| *(no flags)* | Raw JSON session dump | Data export and integration |

---

## 🔄 Workflow Examples

### 📊 **Daily Monitoring Workflow**
```bash
# Morning report - check overnight session quality
python3 seshis.py --empty --micro --graph > daily_report.log

# User performance overview with color coding
python3 seshis.py --user > user_performance.log

# Extract specific problematic sessions for investigation
python3 seshis.py --empty --printsessions > empty_sessions.json
```

### 🔧 **Troubleshooting Workflow**
```bash
# Step 1: Check if API is working
python3 seshis.py --debug

# Step 2: Identify problematic users
python3 seshis.py --user > user_overview.log

# Step 3: Deep dive into specific user issues
python3 seshis.py --user problematic.user@domain.com --debug

# Step 4: Analyze specific issues with full debug info
python3 seshis.py --empty --micro --debug > debug_output.log
```

### 📈 **Performance Analysis Workflow**
```bash
# Weekly trend analysis with graphs
python3 seshis.py --empty --micro --graph

# User performance analysis with color coding
python3 seshis.py --user --advanced

# Individual user deep dive
python3 seshis.py --user frequent.user@domain.com --debug

# Month-to-month comparison
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
      "created_at": "2025-09-15T07:12:27.381Z",
      "updated_at": "2025-09-15T07:13:13.838Z",
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
1. **Skip --advanced flag** in automation to use streamlined defaults
2. **Always use --printsessions** in scripts to avoid interactive prompts
3. **Use --user for performance monitoring** without additional prompts
4. **Pipe output to files** for further processing: `seshis.py --empty > report.txt`
5. **Combine with cron jobs** for regular monitoring
6. **Use specific date ranges** in automation rather than "today" for consistency

### 📊 **Analysis Tips**
1. **Start with --user** to identify problematic users and patterns
2. **Use color coding** to quickly spot performance issues (red = investigate)
3. **Start with --empty --micro** to get overview before diving deep
4. **Use custom date ranges** to analyze specific incidents or time periods
5. **Compare different thresholds** for microsession analysis to find optimal values
6. **Look for patterns** in daily breakdowns to identify systematic issues
7. **Use --debug with --user** to see amperage calculations for performance analysis

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

## 🆕 Recent Updates

### Version 2.0 Features
- **🔥 User Analysis**: New `--user` flag for per-user session analysis
- **🎨 Color Coding**: Performance-based color indicators (Green/Orange/Red)
- **⚡ Performance Metrics**: Automatic amperage calculation and assessment
- **🚀 Streamlined UX**: `--advanced` flag for simplified daily usage
- **📊 Enhanced Details**: Session start/end times with duration calculation
- **🔍 Smart Filtering**: Filter to specific users or analyze all users
- **⏱️ Duration Intelligence**: Smart duration formatting (seconds/minutes/hours)

---

*Made with ❤️ for the EV charging community*
