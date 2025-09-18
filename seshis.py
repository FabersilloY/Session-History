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

def export_to_pdf(sessions, filename, analysis_type="user", specific_user=None, micro_threshold=None, debug=False):
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
        
        # Add color legend
        legend_style = ParagraphStyle('Legend', parent=styles['Normal'], fontSize=10, spaceAfter=6)
        story.append(Paragraph("<b>Status Legend:</b>", legend_style))
        story.append(Paragraph('<font color="#00AA00">■■■</font> High Performance (≥16A avg) | <font color="#FF8800">■■■</font> Medium Performance (8-16A avg) | <font color="#CC0000">■■■</font> Low/Poor Performance (<8A avg)', legend_style))
        story.append(Spacer(1, 12))
        
        # Check for logo file for later use
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pf.jpg")
        if not os.path.exists(logo_path):
            logo_path = None
            if debug:
                print(f"🔧 Logo not found at: {logo_path}")
        elif debug:
            print(f"🔧 Using logo: {logo_path}")
        
        if analysis_type == "user" or analysis_type.startswith("user_with_") or analysis_type == "all_sessions":
            # Group sessions by user
            user_sessions = {}
            for session in sessions:
                user = session.get("user") or "🔓 UNCLAIMED SESSIONS"
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
            analysis_title = "User Session Analysis"
            if analysis_type.startswith("user_with_"):
                # Extract the filter types from the analysis_type
                filter_part = analysis_type.replace("user_with_", "")
                filter_types = filter_part.replace("+", " + ")
                analysis_title = f"User Session Analysis with {filter_types} sessions"
            elif analysis_type == "all_sessions":
                analysis_title = "Complete User Session Analysis (All Session Types)"
            
            if specific_user:
                story.append(Paragraph(f"{analysis_title} for: {specific_user}", subtitle_style))
            else:
                story.append(Paragraph(f"{analysis_title} - Total Users: {len(user_sessions)}", subtitle_style))
            story.append(Spacer(1, 12))
            
            # Process each user
            for user, user_session_list in sorted(user_sessions.items(), key=lambda x: x[0] or "null"):
                # Calculate session statistics for user
                empty_count = sum(1 for s in user_session_list if s.get("session_kwh", 0) == 0)
                micro_count = 0
                if analysis_type.startswith("user_with_") and "micro" in analysis_type and micro_threshold:
                    micro_count = sum(1 for s in user_session_list 
                                    if 0 < s.get("session_kwh", 0) < micro_threshold)
                
                total_sessions = len(user_session_list)
                normal_count = total_sessions - empty_count - micro_count
                normal_percentage = (normal_count / total_sessions * 100) if total_sessions > 0 else 0
                
                # User header with percentage
                if analysis_type.startswith("user_with_") or analysis_type == "all_sessions":
                    user_header = f"User: {user} ({normal_percentage:.1f}% normal sessions, Total: {total_sessions})"
                    # Add breakdown for all_sessions type
                    if analysis_type == "all_sessions":
                        user_header += f"\nEmpty: {empty_count} | Micro: {micro_count} | Normal: {normal_count}"
                else:
                    user_header = f"User: {user} (Total sessions: {total_sessions})"
                story.append(Paragraph(user_header, styles['Heading3']))
                
                # Add explanation for unclaimed sessions
                if user == "🔓 UNCLAIMED SESSIONS":
                    story.append(Paragraph("These are sessions where users plugged in without scanning the QR code first.", normal_style))
                    story.append(Spacer(1, 6))
                
                # Create session rows (show all sessions for all_sessions type)
                session_rows = []
                sessions_to_show_pdf = user_session_list  # Show all sessions for all_sessions type
                
                for i, session in enumerate(sessions_to_show_pdf, 1):
                    row_text, color = format_session_for_pdf(session, i)
                    # Create paragraph with colored status indicator
                    colored_paragraph = create_colored_session_paragraph(row_text, color, normal_style)
                    session_rows.append([colored_paragraph])
                
                # Create table without background color coding
                if session_rows:
                    table = Table(session_rows, colWidths=[10*inch])
                    table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                 ('FONTSIZE', (0, 0), (-1, -1), 9),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 6)]
                    
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
                # Create paragraph with colored status indicator
                colored_paragraph = create_colored_session_paragraph(row_text, color, normal_style)
                session_rows.append([colored_paragraph])
            
            # Create table without background color coding
            if session_rows:
                table = Table(session_rows, colWidths=[10*inch])
                table_style = [('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                             ('FONTSIZE', (0, 0), (-1, -1), 9),
                             ('LEFTPADDING', (0, 0), (-1, -1), 6),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 6)]
                
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

def create_colored_session_paragraph(session_text, color, base_style):
    """Create a paragraph with a colored status indicator at the beginning"""
    # Define color mapping for the status indicators
    color_map = {
        'green': '#00AA00',    # Green for high performance
        'orange': '#FF8800',   # Orange for medium performance  
        'red': '#CC0000'       # Red for low/poor performance
    }
    
    # Get the hex color, default to red if unknown
    hex_color = color_map.get(color, '#CC0000')
    
    # Create a colored square/box indicator using HTML-like formatting
    # The ■ symbol creates a solid square that we can color
    colored_indicator = f'<font color="{hex_color}">■■■</font>'
    
    # Combine the colored indicator with the session text
    formatted_text = f'{colored_indicator} {session_text}'
    
    # Return a Paragraph with the formatted text
    return Paragraph(formatted_text, base_style)

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
    parser.add_argument("--all", action="store_true", help="Show all sessions (empty, micro, and normal) grouped by user (requires --pdf or --csv)")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    args = parser.parse_args()

    # Validate flag combinations
    if (args.csv or args.pdf) and args.graph:
        print("❌ Error: --csv/--pdf and --graph flags are incompatible")
        return
    
    if args.all and not (args.csv or args.pdf):
        print("❌ Error: --all flag requires --csv or --pdf")
        return
    
    if args.all and (args.empty or args.micro or args.user):
        print("❌ Error: --all flag cannot be used with --empty, --micro, or --user flags")
        return
    
    if (args.csv or args.pdf) and not (args.empty or args.micro or args.user or args.all):
        print("❌ Error: --csv/--pdf requires at least one analysis flag (--empty, --micro, --user, or --all)")
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
        combined_mode = args.empty or args.micro
        if combined_mode:
            mode_desc = []
            if args.empty:
                mode_desc.append("empty")
            if args.micro:
                mode_desc.append("micro")
            mode_str = " + ".join(mode_desc)
            
            if args.user == "all":
                print(f"\n👥 User Session Summary with {mode_str} sessions:")
                print(f"📊 Total unique users: {len(user_sessions)}")
            else:
                print(f"\n👥 User Session Summary for {args.user} with {mode_str} sessions:")
        else:
            if args.user == "all":
                print(f"\n👥 User Session Summary:")
                print(f"📊 Total unique users: {len(user_sessions)}")
            else:
                print(f"\n👥 User Session Summary for: {args.user}")
        
        # Separate unclaimed sessions from regular users
        unclaimed_sessions = user_sessions.pop("null", [])
        
        # Process each user's sessions (excluding unclaimed)
        for user, user_session_list in sorted(user_sessions.items(), key=lambda x: x[0] or "null"):
            # Calculate session categories for this user
            empty_count = 0
            micro_count = 0
            normal_count = 0
            
            for session in user_session_list:
                session_kwh = session.get("session_kwh", 0)
                if session_kwh == 0:
                    empty_count += 1
                elif args.micro and micro_threshold and 0 < session_kwh < micro_threshold:
                    micro_count += 1
                else:
                    normal_count += 1
            
            total_sessions = len(user_session_list)
            normal_percentage = (normal_count / total_sessions * 100) if total_sessions > 0 else 0
            
            # Display user header with percentage of normal sessions
            print(f"\nUser: {user} ({normal_percentage:.1f}% normal sessions)")
            print(f"    Total sessions: {total_sessions}")
            
            if combined_mode:
                if args.empty:
                    print(f"    Empty sessions (0 kWh): {empty_count} ({(empty_count/total_sessions*100) if total_sessions else 0:.1f}%)")
                if args.micro:
                    print(f"    Microsessions (0 < kWh < {micro_threshold}): {micro_count} ({(micro_count/total_sessions*100) if total_sessions else 0:.1f}%)")
                print(f"    Normal sessions (>= {micro_threshold if args.micro else '0'} kWh): {normal_count} ({normal_percentage:.1f}%)")
            
            # Filter sessions to show based on flags
            sessions_to_show = []
            if combined_mode:
                for session in user_session_list:
                    session_kwh = session.get("session_kwh", 0)
                    show_session = False
                    
                    if args.empty and session_kwh == 0:
                        show_session = True
                    if args.micro and micro_threshold and 0 < session_kwh < micro_threshold:
                        show_session = True
                    
                    if show_session:
                        sessions_to_show.append(session)
            else:
                # Show all sessions if not in combined mode
                sessions_to_show = user_session_list
            
            # Display session details
            if sessions_to_show:
                print(f"\n    Showing {len(sessions_to_show)} sessions:")
                for i, session in enumerate(sessions_to_show, 1):
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
                    session_type = ""
                    
                    if session_kwh == 0:
                        color_code = "\033[91m"  # Red for empty sessions
                        session_type = " [EMPTY]"
                    elif args.micro and micro_threshold and 0 < session_kwh < micro_threshold:
                        color_code = "\033[93m"  # Orange for microsessions
                        session_type = " [MICRO]"
                    elif created_at and updated_at and session_kwh > 0:
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
                                    session_type = " [NORMAL-HIGH]"
                                elif avg_amperage >= 8:
                                    color_code = "\033[93m"  # Orange/Yellow
                                    session_type = " [NORMAL-MED]"
                                else:
                                    color_code = "\033[91m"  # Red
                                    session_type = " [NORMAL-LOW]"
                            else:
                                color_code = "\033[91m"  # Red for zero duration
                                session_type = " [DURATION-ERROR]"
                        except (ValueError, TypeError, ZeroDivisionError):
                            color_code = "\033[91m"  # Red for calculation errors
                            session_type = " [CALC-ERROR]"
                    else:
                        color_code = "\033[91m"  # Red for missing data
                        session_type = " [DATA-ERROR]"
                    
                    session_line = f"    Session {i}: START: {start_time} / END: {end_time} / DURATION: {duration_str} / {session_kwh} kWh / {session_id}{session_type}"
                    print(f"{color_code}{session_line}{reset_code}")
        
        # Always show unclaimed sessions at the bottom if they exist
        if unclaimed_sessions:
            # Calculate session categories for unclaimed sessions
            empty_count = 0
            micro_count = 0
            normal_count = 0
            
            for session in unclaimed_sessions:
                session_kwh = session.get("session_kwh", 0)
                if session_kwh == 0:
                    empty_count += 1
                elif args.micro and micro_threshold and 0 < session_kwh < micro_threshold:
                    micro_count += 1
                else:
                    normal_count += 1
            
            total_sessions = len(unclaimed_sessions)
            normal_percentage = (normal_count / total_sessions * 100) if total_sessions > 0 else 0
            
            # Display unclaimed sessions header
            print(f"\n🔓 UNCLAIMED SESSIONS ({normal_percentage:.1f}% normal sessions)")
            print(f"    These are sessions where users plugged in without scanning the QR code first")
            print(f"    Total sessions: {total_sessions}")
            
            if combined_mode:
                if args.empty:
                    print(f"    Empty sessions (0 kWh): {empty_count} ({(empty_count/total_sessions*100) if total_sessions else 0:.1f}%)")
                if args.micro:
                    print(f"    Microsessions (0 < kWh < {micro_threshold}): {micro_count} ({(micro_count/total_sessions*100) if total_sessions else 0:.1f}%)")
                print(f"    Normal sessions (>= {micro_threshold if args.micro else '0'} kWh): {normal_count} ({normal_percentage:.1f}%)")
            
            # Filter unclaimed sessions to show based on flags
            sessions_to_show = []
            if combined_mode:
                for session in unclaimed_sessions:
                    session_kwh = session.get("session_kwh", 0)
                    show_session = False
                    
                    if args.empty and session_kwh == 0:
                        show_session = True
                    if args.micro and micro_threshold and 0 < session_kwh < micro_threshold:
                        show_session = True
                    
                    if show_session:
                        sessions_to_show.append(session)
            else:
                # Show all unclaimed sessions if not in combined mode
                sessions_to_show = unclaimed_sessions
            
            # Display unclaimed session details
            if sessions_to_show:
                print(f"\n    Showing {len(sessions_to_show)} unclaimed sessions:")
                for i, session in enumerate(sessions_to_show, 1):
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
                    color_code = ""
                    reset_code = "\033[0m"
                    session_type = ""
                    
                    if session_kwh == 0:
                        color_code = "\033[91m"  # Red for empty sessions
                        session_type = " [EMPTY]"
                    elif args.micro and micro_threshold and 0 < session_kwh < micro_threshold:
                        color_code = "\033[93m"  # Orange for microsessions
                        session_type = " [MICRO]"
                    elif created_at and updated_at and session_kwh > 0:
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
                                    session_type = " [NORMAL-HIGH]"
                                elif avg_amperage >= 8:
                                    color_code = "\033[93m"  # Orange/Yellow
                                    session_type = " [NORMAL-MED]"
                                else:
                                    color_code = "\033[91m"  # Red
                                    session_type = " [NORMAL-LOW]"
                            else:
                                color_code = "\033[91m"  # Red for zero duration
                                session_type = " [DURATION-ERROR]"
                        except (ValueError, TypeError, ZeroDivisionError):
                            color_code = "\033[91m"  # Red for calculation errors
                            session_type = " [CALC-ERROR]"
                    else:
                        color_code = "\033[91m"  # Red for missing data
                        session_type = " [DATA-ERROR]"
                    
                    session_line = f"    Session {i}: START: {start_time} / END: {end_time} / DURATION: {duration_str} / {session_kwh} kWh / {session_id}{session_type}"
                    print(f"{color_code}{session_line}{reset_code}")
    
    # All sessions summary (like user mode but shows all session types)
    if args.all:
        if args.debug:
            print(f"🔧 Starting all sessions analysis...")
        
        # Filter out non-dictionary items before processing
        valid_sessions = [s for s in sessions if isinstance(s, dict)]
        
        # Group sessions by user
        user_sessions = {}
        for session in valid_sessions:
            user = session.get("user") or "null"
            if user not in user_sessions:
                user_sessions[user] = []
            user_sessions[user].append(session)
        
        # Display header
        print(f"\n👥 Complete User Session Analysis (All Session Types):")
        print(f"📊 Total unique users: {len(user_sessions)}")
        print(f"📊 Total sessions: {len(valid_sessions)}")
        
        # We need micro_threshold for categorization, but it might not be set
        # Set a default threshold for categorization purposes
        display_micro_threshold = 1.0  # Default threshold for display
        
        # Separate unclaimed sessions from regular users
        unclaimed_sessions = user_sessions.pop("null", [])
        
        # Process each user's sessions (excluding unclaimed)
        for user, user_session_list in sorted(user_sessions.items(), key=lambda x: x[0] or "null"):
            # Calculate session categories for this user
            empty_count = 0
            micro_count = 0
            normal_count = 0
            
            for session in user_session_list:
                session_kwh = session.get("session_kwh", 0)
                if session_kwh == 0:
                    empty_count += 1
                elif 0 < session_kwh < display_micro_threshold:
                    micro_count += 1
                else:
                    normal_count += 1
            
            total_sessions = len(user_session_list)
            normal_percentage = (normal_count / total_sessions * 100) if total_sessions > 0 else 0
            
            # Display user header with percentage of normal sessions
            print(f"\nUser: {user} ({normal_percentage:.1f}% normal sessions)")
            print(f"    Total sessions: {total_sessions}")
            print(f"    Empty sessions (0 kWh): {empty_count} ({(empty_count/total_sessions*100) if total_sessions else 0:.1f}%)")
            print(f"    Microsessions (0 < kWh < {display_micro_threshold}): {micro_count} ({(micro_count/total_sessions*100) if total_sessions else 0:.1f}%)")
            print(f"    Normal sessions (>= {display_micro_threshold} kWh): {normal_count} ({normal_percentage:.1f}%)")
            
            # Display all session details
            print(f"\n    All sessions for {user}:")
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
                
                # Calculate average amperage for color coding and session type
                color_code = ""
                reset_code = "\033[0m"
                session_type = ""
                
                if session_kwh == 0:
                    color_code = "\033[91m"  # Red for empty sessions
                    session_type = " [EMPTY]"
                elif 0 < session_kwh < display_micro_threshold:
                    color_code = "\033[93m"  # Orange for microsessions
                    session_type = " [MICRO]"
                elif created_at and updated_at and session_kwh > 0:
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
                                session_type = " [NORMAL-HIGH]"
                            elif avg_amperage >= 8:
                                color_code = "\033[93m"  # Orange/Yellow
                                session_type = " [NORMAL-MED]"
                            else:
                                color_code = "\033[91m"  # Red
                                session_type = " [NORMAL-LOW]"
                        else:
                            color_code = "\033[91m"  # Red for zero duration
                            session_type = " [DURATION-ERROR]"
                    except (ValueError, TypeError, ZeroDivisionError):
                        color_code = "\033[91m"  # Red for calculation errors
                        session_type = " [CALC-ERROR]"
                else:
                    color_code = "\033[91m"  # Red for missing data
                    session_type = " [DATA-ERROR]"
                
                session_line = f"    Session {i}: START: {start_time} / END: {end_time} / DURATION: {duration_str} / {session_kwh} kWh / {session_id}{session_type}"
                print(f"{color_code}{session_line}{reset_code}")
        
        # Always show unclaimed sessions at the bottom if they exist
        if unclaimed_sessions:
            # Calculate session categories for unclaimed sessions
            empty_count = 0
            micro_count = 0
            normal_count = 0
            
            for session in unclaimed_sessions:
                session_kwh = session.get("session_kwh", 0)
                if session_kwh == 0:
                    empty_count += 1
                elif 0 < session_kwh < display_micro_threshold:
                    micro_count += 1
                else:
                    normal_count += 1
            
            total_sessions = len(unclaimed_sessions)
            normal_percentage = (normal_count / total_sessions * 100) if total_sessions > 0 else 0
            
            # Display unclaimed sessions header
            print(f"\n🔓 UNCLAIMED SESSIONS ({normal_percentage:.1f}% normal sessions)")
            print(f"    These are sessions where users plugged in without scanning the QR code first")
            print(f"    Total sessions: {total_sessions}")
            print(f"    Empty sessions (0 kWh): {empty_count} ({(empty_count/total_sessions*100) if total_sessions else 0:.1f}%)")
            print(f"    Microsessions (0 < kWh < {display_micro_threshold}): {micro_count} ({(micro_count/total_sessions*100) if total_sessions else 0:.1f}%)")
            print(f"    Normal sessions (>= {display_micro_threshold} kWh): {normal_count} ({normal_percentage:.1f}%)")
            
            # Display all unclaimed session details
            print(f"\n    All unclaimed sessions:")
            for i, session in enumerate(unclaimed_sessions, 1):
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
                
                # Calculate average amperage for color coding and session type
                color_code = ""
                reset_code = "\033[0m"
                session_type = ""
                
                if session_kwh == 0:
                    color_code = "\033[91m"  # Red for empty sessions
                    session_type = " [EMPTY]"
                elif 0 < session_kwh < display_micro_threshold:
                    color_code = "\033[93m"  # Orange for microsessions
                    session_type = " [MICRO]"
                elif created_at and updated_at and session_kwh > 0:
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
                                session_type = " [NORMAL-HIGH]"
                            elif avg_amperage >= 8:
                                color_code = "\033[93m"  # Orange/Yellow
                                session_type = " [NORMAL-MED]"
                            else:
                                color_code = "\033[91m"  # Red
                                session_type = " [NORMAL-LOW]"
                        else:
                            color_code = "\033[91m"  # Red for zero duration
                            session_type = " [DURATION-ERROR]"
                    except (ValueError, TypeError, ZeroDivisionError):
                        color_code = "\033[91m"  # Red for calculation errors
                        session_type = " [CALC-ERROR]"
                else:
                    color_code = "\033[91m"  # Red for missing data
                    session_type = " [DATA-ERROR]"
                
                session_line = f"    Session {i}: START: {start_time} / END: {end_time} / DURATION: {duration_str} / {session_kwh} kWh / {session_id}{session_type}"
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
        
        if args.all:
            # For --all flag, export all valid sessions with user analysis
            valid_sessions = [s for s in sessions if isinstance(s, dict)]
            sessions_to_export = valid_sessions
            analysis_type = "all_sessions"
            
            if args.debug:
                print(f"🔧 Exporting all {len(sessions_to_export)} sessions")
        
        elif args.user:
            # For user analysis, determine which sessions to export based on combined flags
            valid_sessions = [s for s in sessions if isinstance(s, dict)]
            analysis_type = "user"
            
            # Apply user filter first
            if args.user != "all":
                # Filter to specific user
                user_filtered_sessions = [s for s in valid_sessions if s.get("user", "null") == args.user]
                specific_user = args.user
                if args.debug:
                    print(f"🔧 Filtered to {len(user_filtered_sessions)} sessions for user: {args.user}")
            else:
                # Use all user sessions
                user_filtered_sessions = valid_sessions
                if args.debug:
                    print(f"🔧 Using {len(user_filtered_sessions)} sessions for all users")
            
            # Apply empty/micro filters if specified
            if args.empty or args.micro:
                sessions_to_export = []
                for session in user_filtered_sessions:
                    session_kwh = session.get("session_kwh", 0)
                    include_session = False
                    
                    if args.empty and session_kwh == 0:
                        include_session = True
                    if args.micro and micro_threshold and 0 < session_kwh < micro_threshold:
                        include_session = True
                    
                    if include_session:
                        sessions_to_export.append(session)
                
                # Update analysis type to reflect combined filtering
                mode_desc = []
                if args.empty:
                    mode_desc.append("empty")
                if args.micro:
                    mode_desc.append("micro")
                analysis_type = f"user_with_{'+'.join(mode_desc)}"
                
                if args.debug:
                    print(f"🔧 Combined filtering resulted in {len(sessions_to_export)} sessions")
            else:
                # Export all user sessions without additional filtering
                sessions_to_export = user_filtered_sessions
                if args.debug:
                    print(f"🔧 Exporting {len(sessions_to_export)} sessions without additional filtering")
        
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
                success = export_to_pdf(sessions_to_export, filename, analysis_type, specific_user, micro_threshold, args.debug)
            
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
    if not args.empty and not args.micro and not args.user and not args.all:
        if args.debug:
            print(f"🔧 No analysis flags provided, outputting raw {len(sessions)} sessions...")
        print(json.dumps(sessions, indent=2))

if __name__ == "__main__":
    main()
