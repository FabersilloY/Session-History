#!/usr/bin/env python3
import argparse
import subprocess
import json
from datetime import datetime
import matplotlib.pyplot as plt

def run_command(cmd, debug=False):
    if debug:
        print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return None
    return result.stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--empty", action="store_true", help="Show empty session summary (0 kWh)")
    parser.add_argument("--micro", action="store_true", help="Show microsession summary (0 < kWh < threshold)")
    parser.add_argument("--graph", action="store_true", help="Generate and display graphs")
    parser.add_argument("--printsessions", action="store_true", help="Print session details without prompting")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    args = parser.parse_args()

    # Interactive inputs
    if args.debug:
        print("🔧 Debug mode enabled")
        print(f"🔧 Arguments parsed: {vars(args)}")
    
    acn = input("Enter ACN (default: 0021): ") or "0021"
    acc = input("Enter account (default: 16): ") or "16"
    
    if args.debug:
        print(f"🔧 ACN: {acn}, Account: {acc}")
    
    # Get microsession threshold if --micro flag is used
    micro_threshold = None
    if args.micro:
        if args.debug:
            print("🔧 Microsession analysis requested, getting threshold...")
        while True:
            try:
                micro_threshold = float(input("Enter microsession threshold (kWh, e.g., 1.0): "))
                if micro_threshold > 0:
                    if args.debug:
                        print(f"🔧 Microsession threshold set to: {micro_threshold} kWh")
                    break
                else:
                    print("Threshold must be greater than 0")
            except ValueError:
                print("Please enter a valid number")
    anonymize = input("Anonymize? (true/false, default: false): ") or "false"
    include_active = input("Include active sessions? (true/false, default: false): ") or "false"
    sort_by = input("Sort by (default: session_start_time): ") or "session_start_time"
    sort_order = input("Sort order (ASC/DESC, default: DESC): ") or "DESC"
    limit = input("Limit (default: 25): ") or "25"
    page = input("Page (default: 1): ") or "1"

    print("\nDate range options:")
    print("1. Today")
    print("2. Last week")
    print("3. Last month")
    print("4. Custom (enter dates manually)")
    date_choice = input("Choose date range (1-4, default: 1): ") or "1"

    now = datetime.now()
    if date_choice == "1":
        start_date = datetime(now.year, now.month, now.day)
        end_date = now
    elif date_choice == "2":
        from datetime import timedelta
        start_date = now - timedelta(days=7)
        end_date = now
    elif date_choice == "3":
        from datetime import timedelta
        start_date = now - timedelta(days=30)
        end_date = now
    else:
        start_input = input("Enter start date (YYYY-MM-DD): ")
        end_input = input("Enter end date (YYYY-MM-DD): ")
        start_date = datetime.strptime(start_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_input, "%Y-%m-%d")

    start_ms = int(start_date.timestamp() * 1000)
    end_ms = int(end_date.timestamp() * 1000)
    
    if args.debug:
        print(f"🔧 Date range: {start_date} to {end_date}")
        print(f"🔧 Timestamp range: {start_ms} to {end_ms}")

    url = (
        f"https://api.powerflex.io/v1/public/sessions/acn/{acn}"
        f"?acc={acc}&anonymize={anonymize}&includeActive={include_active}"
        f"&sortBy={sort_by}&sortOrder={sort_order}&limit={limit}&page={page}"
        f"&date=gte%3A{start_ms}&date=lte%3A{end_ms}"
    )
    
    if args.debug:
        print(f"🔧 API URL: {url}")

    cmd = f'curl_device_manager.sh -s -X GET "{url}" -H "accept: application/json" -H "Content-Type: application/json"'
    output = run_command(cmd, debug=args.debug)
    if not output:
        return

    if args.debug:
        print(f"🔧 Raw API response length: {len(output) if output else 0} characters")
        print(f"🔧 Raw response preview: {output[:200] if output else 'None'}{'...' if output and len(output) > 200 else ''}")
    
    try:
        data = json.loads(output)
        if args.debug:
            print(f"🔧 JSON parsed successfully, type: {type(data)}")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        if args.debug:
            print(f"🔧 Raw response that failed to parse: {output}")
        return

    # Handle API response format - extract sessions from 'rows' key if present
    if isinstance(data, dict) and 'rows' in data:
        sessions = data['rows']
        if args.debug:
            print(f"🔧 Extracted {len(sessions)} sessions from 'rows' key")
            if isinstance(data, dict):
                print(f"🔧 Additional keys in response: {list(data.keys())}")
    elif isinstance(data, list):
        sessions = data
        if args.debug:
            print(f"🔧 Using direct list response with {len(sessions)} items")
    else:
        print(f"❌ Unexpected API response format. Expected a list or dict with 'rows' key, but got: {type(data).__name__}")
        if args.debug:
            print(f"🔧 Full response content: {data}")
        else:
            print(f"Response content: {data}")
        return

    if args.empty:
        if args.debug:
            print("🔧 Starting empty sessions analysis...")
        total_sessions = len(sessions)
        # Filter out non-dictionary items before processing
        valid_sessions = [s for s in sessions if isinstance(s, dict)]
        empty_sessions = sum(1 for s in valid_sessions if s.get("session_kwh", 0) == 0)
        
        if args.debug:
            print(f"🔧 Empty analysis - Total: {total_sessions}, Valid: {len(valid_sessions)}, Empty: {empty_sessions}")

        print(f"\n📊 Total sessions returned: {len(valid_sessions)} (filtered from {total_sessions})")
        print(f"⚡ Sessions with 0 kWh delivered: {empty_sessions} ({(empty_sessions/len(valid_sessions)*100) if valid_sessions else 0:.1f}% of total)")

        # Daily breakdown
        daily_counts = {}
        for session in valid_sessions:
            session_date = datetime.fromtimestamp(session['session_start_time'] / 1000).date()
            if session_date not in daily_counts:
                daily_counts[session_date] = {"empty": 0, "total": 0}
            daily_counts[session_date]["total"] += 1
            if session.get("session_kwh", 0) == 0:
                daily_counts[session_date]["empty"] += 1

        print("\n📅 Daily breakdown:")
        dates = []
        percentages = []
        for date in sorted(daily_counts.keys()):
            total = daily_counts[date]["total"]
            empty = daily_counts[date]["empty"]
            if total > 0:
                percentage = (empty / total) * 100
                print(f"- {date}: {empty} empty / {total} total ({percentage:.1f}%)")
                dates.append(date)
                percentages.append(percentage)

        # Plot line chart only if --graph flag is used
        if dates and args.graph:
            plt.figure(figsize=(10, 5))
            plt.plot(dates, percentages, marker="o")
            plt.title("Daily empty session percentage")
            plt.xlabel("Date")
            plt.ylabel("Empty sessions (%)")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        # Print sessions only if --printsessions flag is used
        if args.printsessions:
            empty_sessions_list = [s for s in valid_sessions if s.get("session_kwh", 0) == 0]
            print(f"\n📋 Empty sessions details ({len(empty_sessions_list)} sessions):")
            print(json.dumps(empty_sessions_list, indent=2))

    
    if args.micro:
        if args.debug:
            print(f"🔧 Starting microsessions analysis (threshold: {micro_threshold} kWh)...")
        total_sessions = len(sessions)
        # Filter out non-dictionary items before processing
        valid_sessions = [s for s in sessions if isinstance(s, dict)]
        micro_sessions = sum(1 for s in valid_sessions if 0 < s.get("session_kwh", 0) < micro_threshold)
        
        if args.debug:
            print(f"🔧 Micro analysis - Total: {total_sessions}, Valid: {len(valid_sessions)}, Micro: {micro_sessions}")

        print(f"\n📊 Total sessions returned: {len(valid_sessions)} (filtered from {total_sessions})")
        print(f"🔬 Microsessions (0 < kWh < {micro_threshold}): {micro_sessions} ({(micro_sessions/len(valid_sessions)*100) if valid_sessions else 0:.1f}% of total)")

        # Daily breakdown
        daily_counts = {}
        for session in valid_sessions:
            session_date = datetime.fromtimestamp(session['session_start_time'] / 1000).date()
            if session_date not in daily_counts:
                daily_counts[session_date] = {"micro": 0, "total": 0}
            daily_counts[session_date]["total"] += 1
            if 0 < session.get("session_kwh", 0) < micro_threshold:
                daily_counts[session_date]["micro"] += 1

        print("\n📅 Daily breakdown:")
        dates = []
        percentages = []
        for date in sorted(daily_counts.keys()):
            total = daily_counts[date]["total"]
            micro = daily_counts[date]["micro"]
            if total > 0:
                percentage = (micro / total) * 100
                print(f"- {date}: {micro} micro / {total} total ({percentage:.1f}%)")
                dates.append(date)
                percentages.append(percentage)

        # Plot line chart only if --graph flag is used
        if dates and args.graph:
            plt.figure(figsize=(10, 5))
            plt.plot(dates, percentages, marker="o")
            plt.title(f"Daily microsession percentage (< {micro_threshold} kWh)")
            plt.xlabel("Date")
            plt.ylabel("Microsessions (%)")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        # Print sessions only if --printsessions flag is used
        if args.printsessions:
            micro_sessions_list = [s for s in valid_sessions if 0 < s.get("session_kwh", 0) < micro_threshold]
            print(f"\n📋 Microsessions details ({len(micro_sessions_list)} sessions):")
            print(json.dumps(micro_sessions_list, indent=2))
    
    # Combined summary if both flags are used
    if args.empty and args.micro:
        if args.debug:
            print("🔧 Generating combined summary...")
        print("\n" + "="*50)
        print("🔍 COMBINED SUMMARY")
        print("="*50)
        
        total_sessions = len([s for s in sessions if isinstance(s, dict)])
        valid_sessions = [s for s in sessions if isinstance(s, dict)]
        empty_count = sum(1 for s in valid_sessions if s.get("session_kwh", 0) == 0)
        micro_count = sum(1 for s in valid_sessions if 0 < s.get("session_kwh", 0) < micro_threshold)
        combined_count = empty_count + micro_count
        
        print(f"📊 Total sessions analyzed: {total_sessions}")
        print(f"⚡ Empty sessions (0 kWh): {empty_count} ({(empty_count/total_sessions*100) if total_sessions else 0:.1f}%)")
        print(f"🔬 Microsessions (0 < kWh < {micro_threshold}): {micro_count} ({(micro_count/total_sessions*100) if total_sessions else 0:.1f}%)")
        print(f"🎯 Combined (empty + micro): {combined_count} ({(combined_count/total_sessions*100) if total_sessions else 0:.1f}%)")
        
        # Show breakdown by energy ranges
        normal_sessions = total_sessions - combined_count
        print(f"✅ Normal sessions (>= {micro_threshold} kWh): {normal_sessions} ({(normal_sessions/total_sessions*100) if total_sessions else 0:.1f}%)")

    # If no analysis flags are used, just print all sessions
    if not args.empty and not args.micro:
        if args.debug:
            print(f"🔧 No analysis flags provided, outputting raw {len(sessions)} sessions...")
        print(json.dumps(sessions, indent=2))

if __name__ == "__main__":
    main()
