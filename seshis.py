#!/usr/bin/env python3
import argparse
import subprocess
import json
from datetime import datetime
import matplotlib.pyplot as plt
import threading
import time
import sys

class ProgressSpinner:
    def __init__(self, message="Loading"):
        self.message = message
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.running = False
        self.thread = None
    
    def _spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f"\r{self.spinner_chars[i % len(self.spinner_chars)]} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, success_message=""):
        self.running = False
        if self.thread:
            self.thread.join()
        if success_message:
            sys.stdout.write(f"\r✅ {success_message}\n")
        else:
            sys.stdout.write(f"\r")
        sys.stdout.flush()

def run_command(cmd, debug=False, show_progress=True):
    if debug:
        print(f"🔧 Running: {cmd}")
    
    # Start progress spinner for non-debug mode
    spinner = None
    if show_progress and not debug:
        spinner = ProgressSpinner("Fetching session data from PowerFlex API")
        spinner.start()
    
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Stop spinner on completion
        if spinner:
            if result.returncode == 0:
                spinner.stop("Session data retrieved successfully")
            else:
                spinner.stop("API request failed")
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return None
        return result.stdout
        
    except Exception as e:
        if spinner:
            spinner.stop("API request failed")
        print(f"❌ Error executing command: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--empty", action="store_true", help="Show empty session summary (0 kWh)")
    parser.add_argument("--micro", action="store_true", help="Show microsession summary (0 < kWh < threshold)")
    parser.add_argument("--graph", action="store_true", help="Generate and display graphs")
    parser.add_argument("--printsessions", action="store_true", help="Print session details without prompting")
    parser.add_argument("--user", nargs="?", const="all", help="Generate summary of sessions per user (optionally specify email address for specific user)")
    parser.add_argument("--advanced", action="store_true", help="Enable advanced prompts for anonymization, active sessions, sorting options")
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
    
    # Advanced options - only prompt if --advanced flag is used
    if args.advanced:
        anonymize = input("Anonymize? (true/false, default: false): ") or "false"
        include_active = input("Include active sessions? (true/false, default: false): ") or "false"
        sort_by = input("Sort by (default: session_start_time): ") or "session_start_time"
        sort_order = input("Sort order (ASC/DESC, default: DESC): ") or "DESC"
    else:
        # Use default values when --advanced is not specified
        anonymize = "false"
        include_active = "false"
        sort_by = "session_start_time"
        sort_order = "DESC"
        if args.debug:
            print(f"🔧 Using default advanced options: anonymize={anonymize}, include_active={include_active}, sort_by={sort_by}, sort_order={sort_order}")
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
        
        # Extract site name from first valid session
        site_name = "Unknown Site"
        if valid_sessions:
            site_name = valid_sessions[0].get("site", "Unknown Site")
            if args.debug:
                print(f"🔧 Extracted site name: {site_name}")
        
        print(f"🏢 Site: {site_name}")
        print(f"📊 Total sessions analyzed: {total_sessions}")
        print(f"⚡ Empty sessions (0 kWh): {empty_count} ({(empty_count/total_sessions*100) if total_sessions else 0:.1f}%)")
        print(f"🔬 Microsessions (0 < kWh < {micro_threshold}): {micro_count} ({(micro_count/total_sessions*100) if total_sessions else 0:.1f}%)")
        print(f"🎯 Combined (empty + micro): {combined_count} ({(combined_count/total_sessions*100) if total_sessions else 0:.1f}%)")
        
        # Show breakdown by energy ranges
        normal_sessions = total_sessions - combined_count
        print(f"✅ Normal sessions (>= {micro_threshold} kWh): {normal_sessions} ({(normal_sessions/total_sessions*100) if total_sessions else 0:.1f}%)")

    # User session summary
    if args.user:
        if args.debug:
            print(f"🔧 Starting user session analysis (filter: {args.user})...")
        
        # Filter out non-dictionary items before processing
        valid_sessions = [s for s in sessions if isinstance(s, dict)]
        
        # Group sessions by user
        user_sessions = {}
        for session in valid_sessions:
            user = session.get("user") or "null"
            if user not in user_sessions:
                user_sessions[user] = []
            user_sessions[user].append(session)
        
        # Filter to specific user if email address provided
        if args.user != "all":
            specific_user = args.user
            if specific_user in user_sessions:
                user_sessions = {specific_user: user_sessions[specific_user]}
                if args.debug:
                    print(f"🔧 Filtered to specific user: {specific_user} with {len(user_sessions[specific_user])} sessions")
            else:
                print(f"\n⚠️  User '{specific_user}' not found in session data.")
                print(f"📊 Available users: {', '.join(sorted(user_sessions.keys()))}")
                return
        
        # Display header based on mode
        if args.user == "all":
            print(f"\n👥 User Session Summary:")
            print(f"📊 Total unique users: {len(user_sessions)}")
        else:
            print(f"\n👥 User Session Summary for: {args.user}")
        
        # Process each user's sessions
        for user, user_session_list in sorted(user_sessions.items()):
            print(f"\nUser: {user}")
            print(f"    Total sessions: {len(user_session_list)}")
            
            # For null user, just show count without details
            if user == "null":
                continue
            
            # Display session details for non-null users
            for i, session in enumerate(user_session_list, 1):
                session_kwh = session.get("session_kwh", 0)
                session_id = session.get("session_id", "unknown")
                
                # Parse dates and calculate duration
                created_at = session.get("created_at", "")
                updated_at = session.get("updated_at", "")
                
                start_time = "N/A"
                end_time = "N/A"
                duration_str = "N/A"
                
                if created_at and updated_at:
                    try:
                        # Parse ISO format dates
                        start_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        
                        # Format dates as YYYY-MM-DD HH:MM:SS
                        start_time = start_dt.strftime("%Y-%m-%d %H:%M:%S")
                        end_time = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Calculate duration
                        duration_seconds = (end_dt - start_dt).total_seconds()
                        
                        if duration_seconds < 60:
                            duration_str = f"{duration_seconds:.0f}s"
                        elif duration_seconds < 3600:
                            minutes = duration_seconds / 60
                            duration_str = f"{minutes:.1f}m"
                        else:
                            hours = duration_seconds / 3600
                            duration_str = f"{hours:.1f}h"
                            
                    except (ValueError, TypeError) as e:
                        if args.debug:
                            print(f"🔧 Error parsing dates for session {session_id}: {e}")
                
                # Calculate average amperage for color coding
                # Using P = V * I, so I = P / V
                # Average power = kWh / hours, then convert to watts
                # Assuming 208V as mentioned
                color_code = ""
                reset_code = "\033[0m"
                
                if created_at and updated_at and session_kwh > 0:
                    try:
                        duration_hours = duration_seconds / 3600
                        if duration_hours > 0:
                            # Calculate average power in watts
                            avg_power_watts = (session_kwh * 1000) / duration_hours
                            # Calculate average amperage at 208V
                            avg_amperage = avg_power_watts / 208
                            
                            if args.debug:
                                print(f"    🔧 Session {i} calculations: {duration_hours:.2f}h, {avg_power_watts:.1f}W, {avg_amperage:.1f}A")
                            
                            # Color coding based on amperage
                            if avg_amperage >= 16:
                                color_code = "\033[92m"  # Green
                            elif avg_amperage >= 8:
                                color_code = "\033[93m"  # Orange/Yellow
                            else:
                                color_code = "\033[91m"  # Red
                        else:
                            color_code = "\033[91m"  # Red for zero duration
                    except (ValueError, TypeError, ZeroDivisionError):
                        color_code = "\033[91m"  # Red for calculation errors
                else:
                    color_code = "\033[91m"  # Red for missing data or zero kWh
                
                session_line = f"    Session {i}: START: {start_time} / END: {end_time} / DURATION: {duration_str} / {session_kwh} kWh / {session_id}"
                print(f"{color_code}{session_line}{reset_code}")
    
    # If no analysis flags are used, just print all sessions
    if not args.empty and not args.micro and not args.user:
        if args.debug:
            print(f"🔧 No analysis flags provided, outputting raw {len(sessions)} sessions...")
        print(json.dumps(sessions, indent=2))

if __name__ == "__main__":
    main()
