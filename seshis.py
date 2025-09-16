#!/usr/bin/env python3
import argparse
import subprocess
import json
from datetime import datetime
import matplotlib.pyplot as plt
import threading
import time
import sys
import csv
import os

# Try to import reportlab for PDF functionality
try:
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

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

def export_to_csv(sessions, filename, debug=False):
    """Export session data to CSV file"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'session_id', 'user', 'session_kwh', 'created_at', 'updated_at', 
                'duration_seconds', 'duration_formatted', 'avg_amperage', 'performance_rating',
                'parking_space', 'pfid', 'authorization_source', 'status',
                'session_start_time', 'session_end_time', 'reporting_id', 'site', 'vehicle', 'cost_actual'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for session in sessions:
                # Calculate duration and performance metrics
                created_at = session.get("created_at", "")
                updated_at = session.get("updated_at", "")
                session_kwh = session.get("session_kwh", 0)
                
                duration_seconds = 0
                duration_formatted = "N/A"
                avg_amperage = 0
                performance_rating = "Unknown"
                
                if created_at and updated_at:
                    try:
                        start_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        duration_seconds = (end_dt - start_dt).total_seconds()
                        
                        # Format duration
                        if duration_seconds < 60:
                            duration_formatted = f"{duration_seconds:.0f}s"
                        elif duration_seconds < 3600:
                            minutes = duration_seconds / 60
                            duration_formatted = f"{minutes:.1f}m"
                        else:
                            hours = duration_seconds / 3600
                            duration_formatted = f"{hours:.1f}h"
                        
                        # Calculate average amperage and performance rating
                        if session_kwh > 0 and duration_seconds > 0:
                            duration_hours = duration_seconds / 3600
                            avg_power_watts = (session_kwh * 1000) / duration_hours
                            avg_amperage = avg_power_watts / 208
                            
                            if avg_amperage >= 16:
                                performance_rating = "High"
                            elif avg_amperage >= 8:
                                performance_rating = "Medium"
                            else:
                                performance_rating = "Low"
                        else:
                            performance_rating = "Poor"
                            
                    except (ValueError, TypeError):
                        pass
                
                # Prepare row data
                row = {
                    'session_id': session.get('session_id', ''),
                    'user': session.get('user', ''),
                    'session_kwh': session_kwh,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'duration_seconds': duration_seconds,
                    'duration_formatted': duration_formatted,
                    'avg_amperage': round(avg_amperage, 2) if avg_amperage > 0 else 0,
                    'performance_rating': performance_rating,
                    'parking_space': session.get('parking_space', ''),
                    'pfid': session.get('pfid', ''),
                    'authorization_source': session.get('authorization_source', ''),
                    'status': session.get('status', ''),
                    'session_start_time': session.get('session_start_time', ''),
                    'session_end_time': session.get('session_end_time', ''),
                    'reporting_id': session.get('reporting_id', ''),
                    'site': session.get('site', ''),
                    'vehicle': session.get('vehicle', ''),
                    'cost_actual': session.get('cost_actual', '')
                }
                
                writer.writerow(row)
            
        if debug:
            print(f"🔧 CSV exported successfully: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
        return False

def export_to_pdf(sessions, filename, analysis_type="user", specific_user=None, debug=False):
    """Export session data to PDF file with color coding"""
    try:
        # Create PDF document in landscape orientation
        doc = SimpleDocTemplate(filename, pagesize=landscape(letter), 
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                   alignment=TA_CENTER, fontSize=16, spaceAfter=12)
        subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], 
                                      alignment=TA_CENTER, fontSize=12, spaceAfter=8)
        normal_style = styles['Normal']
        
        # Story elements
        story = []
        
        # Extract site information and date range from sessions
        site_name = "Unknown Site"
        site_location = "Unknown Location"
        date_range_str = "No sessions"
        
        if sessions:
            site_name = sessions[0].get("site", "Unknown Site")
            site_location = sessions[0].get("site_location", "Unknown Location")
            
            # Calculate date range from session data
            earliest_date = None
            latest_date = None
            
            for session in sessions:
                created_at = session.get("created_at", "")
                if created_at:
                    try:
                        session_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if earliest_date is None or session_date < earliest_date:
                            earliest_date = session_date
                        if latest_date is None or session_date > latest_date:
                            latest_date = session_date
                    except (ValueError, TypeError):
                        continue
            
            # Format date range
            if earliest_date and latest_date:
                if earliest_date.date() == latest_date.date():
                    # Same day
                    date_range_str = f"Date: {earliest_date.strftime('%Y-%m-%d')}"
                else:
                    # Date range
                    date_range_str = f"Date Range: {earliest_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}"
        
        # Add simple header without logo
        story.append(Paragraph(f"EV Charging Session Report", title_style))
        story.append(Paragraph(f"Site: {site_name} | Location: {site_location}", subtitle_style))
        story.append(Paragraph(f"{date_range_str}", normal_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 12))
        
        # Check for logo file for later use
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pf.jpg")
        if not os.path.exists(logo_path):
            logo_path = None
            if debug:
                print(f"🔧 Logo not found at: {logo_path}")
        elif debug:
            print(f"🔧 Using logo: {logo_path}")
        
        if analysis_type == "user":
            # Group sessions by user
            user_sessions = {}
            for session in sessions:
                user = session.get("user") or "null"
                if user not in user_sessions:
                    user_sessions[user] = []
                user_sessions[user].append(session)
            
            # Add logo before analysis section if available
            if logo_path and os.path.exists(logo_path):
                try:
                    # Center the logo
                    logo_img = Image(logo_path, width=2*inch, height=1.2*inch)
                    logo_img.hAlign = 'CENTER'
                    story.append(logo_img)
                    story.append(Spacer(1, 12))
                    if debug:
                        print(f"🔧 Logo added to PDF")
                except Exception as e:
                    if debug:
                        print(f"🔧 Failed to add logo: {e}")
            
            # Add summary
            if specific_user:
                story.append(Paragraph(f"User Session Analysis for: {specific_user}", subtitle_style))
            else:
                story.append(Paragraph(f"User Session Analysis - Total Users: {len(user_sessions)}", subtitle_style))
            story.append(Spacer(1, 12))
            
            # Process each user
            for user, user_session_list in sorted(user_sessions.items(), key=lambda x: x[0] or "null"):
                # User header
                user_header = f"User: {user} (Total sessions: {len(user_session_list)})"
                story.append(Paragraph(user_header, styles['Heading3']))
                
                # Skip session details for null user
                if user == "null":
                    story.append(Spacer(1, 12))
                    continue
                
                # Create session rows
                session_rows = []
                for i, session in enumerate(user_session_list, 1):
                    row_text, color = format_session_for_pdf(session, i)
                    session_rows.append([Paragraph(row_text, normal_style)])
                
                # Create table with color coding
                if session_rows:
                    table = Table(session_rows, colWidths=[10*inch])
                    table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                 ('FONTSIZE', (0, 0), (-1, -1), 9),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 6)]
                    
                    # Add color coding to rows
                    for idx, session in enumerate(user_session_list):
                        _, color = format_session_for_pdf(session, idx + 1)
                        if color == 'green':
                            table_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.lightgreen))
                        elif color == 'orange':
                            table_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.orange))
                        elif color == 'red':
                            table_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.lightcoral))
                    
                    table.setStyle(TableStyle(table_style))
                    story.append(table)
                
                story.append(Spacer(1, 12))
        
        else:  # empty or micro analysis
            # Add logo before analysis section if available
            if logo_path and os.path.exists(logo_path):
                try:
                    # Center the logo
                    logo_img = Image(logo_path, width=2*inch, height=1.2*inch)
                    logo_img.hAlign = 'CENTER'
                    story.append(logo_img)
                    story.append(Spacer(1, 12))
                    if debug:
                        print(f"🔧 Logo added to PDF")
                except Exception as e:
                    if debug:
                        print(f"🔧 Failed to add logo: {e}")
            
            story.append(Paragraph(f"Session Analysis - {analysis_type.title()} Sessions", subtitle_style))
            story.append(Paragraph(f"Total sessions: {len(sessions)}", normal_style))
            story.append(Spacer(1, 12))
            
            # Create session rows
            session_rows = []
            for i, session in enumerate(sessions, 1):
                row_text, color = format_session_for_pdf(session, i)
                session_rows.append([Paragraph(row_text, normal_style)])
            
            # Create table with color coding
            if session_rows:
                table = Table(session_rows, colWidths=[10*inch])
                table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                             ('FONTSIZE', (0, 0), (-1, -1), 9),
                             ('LEFTPADDING', (0, 0), (-1, -1), 6),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 6)]
                
                # Add color coding to rows
                for idx, session in enumerate(sessions):
                    _, color = format_session_for_pdf(session, idx + 1)
                    if color == 'green':
                        table_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.lightgreen))
                    elif color == 'orange':
                        table_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.orange))
                    elif color == 'red':
                        table_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.lightcoral))
                
                table.setStyle(TableStyle(table_style))
                story.append(table)
        
        # Build PDF
        doc.build(story)
        
        if debug:
            print(f"🔧 PDF exported successfully: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting PDF: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False

def format_session_for_pdf(session, session_num):
    """Format a session for PDF display with color determination"""
    # Extract session data
    session_kwh = session.get("session_kwh", 0)
    session_id = session.get("session_id", "unknown")
    pfid = session.get("pfid", "N/A")
    parking_space = session.get("parking_space", "N/A")
    evse_type = session.get("evse_type", "N/A")
    created_at = session.get("created_at", "")
    updated_at = session.get("updated_at", "")
    
    # Parse dates and calculate duration
    start_time = "N/A"
    end_time = "N/A"
    duration_str = "N/A"
    color = "red"  # Default to red
    
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
            
            # Calculate average amperage for color coding
            if session_kwh > 0 and duration_seconds > 0:
                duration_hours = duration_seconds / 3600
                avg_power_watts = (session_kwh * 1000) / duration_hours
                avg_amperage = avg_power_watts / 208
                
                if avg_amperage >= 16:
                    color = "green"
                elif avg_amperage >= 8:
                    color = "orange"
                else:
                    color = "red"
            
        except (ValueError, TypeError):
            pass
    
    # Format the session line
    session_text = (f"Session {session_num}: PFID: {pfid} / Parking Space: {parking_space} / "
                   f"START: {start_time} / END: {end_time} / DURATION: {duration_str} / "
                   f"{session_kwh} kWh / {session_id} / EVSE: {evse_type}")
    
    return session_text, color

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
    parser.add_argument("--csv", action="store_true", help="Export session data to CSV file (requires analysis flag, incompatible with --graph)")
    parser.add_argument("--pdf", action="store_true", help="Export session data to PDF file (requires analysis flag, incompatible with --graph)")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    args = parser.parse_args()

    # Validate flag combinations
    if (args.csv or args.pdf) and args.graph:
        print("❌ Error: --csv/--pdf and --graph flags are incompatible")
        return
    
    if (args.csv or args.pdf) and not (args.empty or args.micro or args.user):
        print("❌ Error: --csv/--pdf requires at least one analysis flag (--empty, --micro, or --user)")
        return
    
    if args.csv and args.pdf:
        print("❌ Error: --csv and --pdf flags cannot be used together")
        return
    
    if args.pdf and not REPORTLAB_AVAILABLE:
        print("❌ Error: PDF export requires reportlab library")
        print("📍 Install with: pip install reportlab")
        return
    
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
        for user, user_session_list in sorted(user_sessions.items(), key=lambda x: x[0] or "null"):
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
    
    # Export functionality (CSV or PDF)
    if args.csv or args.pdf:
        # Generate timestamp for filename
        now = datetime.now()
        file_extension = "csv" if args.csv else "pdf"
        filename = f"{now.strftime('%Y_%m_%d_%H%M%S')}.{file_extension}"
        
        # Determine which sessions to export based on analysis flags
        sessions_to_export = []
        analysis_type = "user"
        specific_user = None
        
        if args.user:
            # For user analysis, export all valid sessions with user data
            valid_sessions = [s for s in sessions if isinstance(s, dict)]
            analysis_type = "user"
            
            if args.user != "all":
                # Filter to specific user
                sessions_to_export = [s for s in valid_sessions if s.get("user", "null") == args.user]
                specific_user = args.user
                if args.debug:
                    print(f"🔧 Filtered {len(sessions_to_export)} sessions for user: {args.user}")
            else:
                # Export all user sessions
                sessions_to_export = valid_sessions
                if args.debug:
                    print(f"🔧 Exporting {len(sessions_to_export)} sessions for all users")
        
        elif args.empty or args.micro:
            # For empty/micro analysis, export the relevant sessions
            valid_sessions = [s for s in sessions if isinstance(s, dict)]
            
            if args.empty and args.micro:
                # Export both empty and micro sessions
                sessions_to_export = [s for s in valid_sessions 
                                    if s.get("session_kwh", 0) == 0 or 
                                    (0 < s.get("session_kwh", 0) < micro_threshold)]
                analysis_type = "empty_and_micro"
            elif args.empty:
                # Export only empty sessions
                sessions_to_export = [s for s in valid_sessions if s.get("session_kwh", 0) == 0]
                analysis_type = "empty"
            elif args.micro:
                # Export only micro sessions
                sessions_to_export = [s for s in valid_sessions 
                                    if 0 < s.get("session_kwh", 0) < micro_threshold]
                analysis_type = "micro"
            
            if args.debug:
                print(f"🔧 Exporting {len(sessions_to_export)} sessions for {analysis_type} analysis")
        
        # Export to CSV or PDF
        if sessions_to_export:
            if args.csv:
                success = export_to_csv(sessions_to_export, filename, args.debug)
            else:  # PDF
                success = export_to_pdf(sessions_to_export, filename, analysis_type, specific_user, args.debug)
            
            if success:
                export_type = "CSV" if args.csv else "PDF"
                print(f"✅ {export_type} exported successfully: {filename}")
                print(f"📊 {len(sessions_to_export)} sessions exported")
            else:
                export_type = "CSV" if args.csv else "PDF"
                print(f"❌ Failed to export {export_type} file")
        else:
            print(f"⚠️  No sessions to export based on current filters")
    
    # If no analysis flags are used, just print all sessions
    if not args.empty and not args.micro and not args.user:
        if args.debug:
            print(f"🔧 No analysis flags provided, outputting raw {len(sessions)} sessions...")
        print(json.dumps(sessions, indent=2))

if __name__ == "__main__":
    main()
