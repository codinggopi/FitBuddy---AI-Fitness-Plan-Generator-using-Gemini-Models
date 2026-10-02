from datetime import datetime, timedelta
from typing import Dict, Any


def generate_ics_calendar(plan: Dict[str, Any], user_name: str = "Athlete") -> str:
    """
    Generates an RFC 5545 compliant iCalendar (.ics) string for a 7-day routine.
    Allows athletes to import their personalized routine into Google Calendar,
    Apple Calendar, Outlook, and mobile calendar apps.
    """
    now = datetime.utcnow()
    dtstamp = now.strftime("%Y%m%dT%H%M%SZ")
    
    # Start schedule from tomorrow morning at 07:00 AM local time
    start_base = (now + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//FitBuddy AI//7-Day Workout Routine//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:FitBuddy - {user_name}'s Routine",
        "X-WR-TIMEZONE:UTC",
    ]

    day_index = 0
    for day_key, day_data in plan.items():
        event_date = start_base + timedelta(days=day_index)
        end_date = event_date + timedelta(minutes=50)

        dtstart = event_date.strftime("%Y%m%dT%H%M%SZ")
        dtend = end_date.strftime("%Y%m%dT%H%M%SZ")
        uid = f"fitbuddy-{event_date.strftime('%Y%m%d')}-{day_index}@fitbuddy.ai"

        focus = day_data.get("focus", f"Workout {day_key}")
        warmup = day_data.get("warmup", "")
        cooldown = day_data.get("cooldown", "")
        exercises = day_data.get("exercises", [])

        # Build clean description text
        desc_parts = [f"=== {day_key}: {focus} ==="]
        if warmup:
            desc_parts.append(f"Warmup: {warmup}")
        
        if exercises:
            desc_parts.append("Exercises:")
            for idx, ex in enumerate(exercises, 1):
                name = ex.get("name", "Exercise")
                sets = ex.get("sets", 3)
                reps = ex.get("reps", "10-12")
                notes = ex.get("notes", "")
                note_str = f" - {notes}" if notes else ""
                desc_parts.append(f"{idx}. {name}: {sets} sets x {reps}{note_str}")
        else:
            desc_parts.append("Rest and recovery day. Focus on hydration, stretching, and 8 hours of sleep.")

        if cooldown:
            desc_parts.append(f"Cooldown: {cooldown}")

        # Escape special characters for iCalendar format
        description = "\\n".join(desc_parts).replace(",", "\\,").replace(";", "\\;")
        summary = f"FitBuddy: {day_key} - {focus}".replace(",", "\\,")

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
            "END:VEVENT"
        ])

        day_index += 1

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
