SIMULATION_SETTINGS = {
    'horizon_days': 7,
    'max_hours_per_day': 8,
    'max_hours_per_week': 40,
    'min_rest_hours': 12,
    'min_staff_per_shift': 1
}

VISUALIZATION_SETTINGS = {
    'output_dir': 'schedule_output',
    'plot_width': 15,
    'plot_height': 6,
    'start_date': '2024-01-01'
}

SHIFTS = [
    (0, 8),    # Morning shift
    (8, 16),   # Day shift
    (16, 24)   # Night shift
]

SKILLS_MATRIX = [
    ['operator', 'maintenance'],
    ['operator'],
    ['maintenance', 'quality'],
    ['operator', 'quality']
]