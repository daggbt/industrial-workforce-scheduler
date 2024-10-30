from typing import List
from datetime import datetime, timedelta

def get_shifts(schedule: List[int]) -> List[List[int]]:
    """Group consecutive hours into shifts"""
    if not schedule:
        return []
        
    shifts = []
    current_shift = [schedule[0]]
    
    for hour in schedule[1:]:
        if hour == current_shift[-1] + 1:
            current_shift.append(hour)
        else:
            shifts.append(current_shift)
            current_shift = [hour]
    
    if current_shift:
        shifts.append(current_shift)
    return shifts

def hours_to_datetime(hours: int, start_date: str) -> datetime:
    """Convert hour number to datetime"""
    base_date = datetime.strptime(start_date, '%Y-%m-%d')
    return base_date + timedelta(hours=hours)