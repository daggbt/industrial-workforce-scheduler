import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

from config.settings import VISUALIZATION_SETTINGS
from utils.helpers import get_shifts, hours_to_datetime
from utils.logger import setup_logger

logger = setup_logger()

class ScheduleVisualizer:
    def __init__(self, simulator):
        self.simulator = simulator
        self.output_dir = VISUALIZATION_SETTINGS['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)

    def create_gantt_chart(self):
        """Create a Gantt chart of the schedule using plotly"""
        df_list = []
        
        for i, employee in enumerate(self.simulator.employees):
            shifts = self.simulator._get_shifts(employee.schedule)
            for shift in shifts:
                start_time = datetime(2024, 1, 1) + timedelta(hours=shift[0])
                end_time = datetime(2024, 1, 1) + timedelta(hours=shift[-1] + 1)
                
                df_list.append({
                    'Employee': f'Employee {i} ({", ".join(employee.skills)})',
                    'Start': start_time,
                    'Finish': end_time,
                    'Task': 'Working'
                })
                
            # Add breaks
            for break_time in employee.breaks_taken:
                break_start = datetime(2024, 1, 1) + timedelta(hours=break_time)
                break_end = break_start + timedelta(hours=1)
                df_list.append({
                    'Employee': f'Employee {i} ({", ".join(employee.skills)})',
                    'Start': break_start,
                    'Finish': break_end,
                    'Task': 'Break'
                })

        df = pd.DataFrame(df_list)
        
        fig = ff.create_gantt(df, 
                            group_tasks=True,
                            show_colorbar=True,
                            index_col='Employee',
                            title='Employee Schedule Gantt Chart',
                            height=400)
        
        # Update layout
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Employee',
            showlegend=True
        )
        
        # Save the plot
        fig.write_html(os.path.join(self.output_dir, 'schedule_gantt.html'))

    def create_coverage_heatmap(self):
        """Create a heatmap showing staff coverage by day and hour"""
        coverage_matrix = np.zeros((7, 24))
        
        for employee in self.simulator.employees:
            for hour in employee.schedule:
                day = hour // 24
                hour_of_day = hour % 24
                if day < 7:  # Only consider first week
                    coverage_matrix[day, hour_of_day] += 1

        plt.figure(figsize=(15, 6))
        sns.heatmap(coverage_matrix, 
                   cmap='YlOrRd',
                   xticklabels=range(24),
                   yticklabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                   cbar_kws={'label': 'Number of Employees'})
        
        plt.title('Staff Coverage Heatmap')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'coverage_heatmap.png'))
        plt.close()

    def create_skill_coverage_chart(self):
        """Create a chart showing skill coverage by hour"""
        skill_coverage = defaultdict(lambda: np.zeros(24))
        all_skills = set()
        
        for employee in self.simulator.employees:
            all_skills.update(employee.skills)
            shifts = self.simulator._get_shifts(employee.schedule)
            
            for shift in shifts:
                for hour in shift:
                    hour_of_day = hour % 24
                    for skill in employee.skills:
                        skill_coverage[skill][hour_of_day] += 1

        # Create plot
        plt.figure(figsize=(15, 6))
        for skill in all_skills:
            plt.plot(range(24), skill_coverage[skill], label=skill, marker='o')
            
        plt.title('Skill Coverage by Hour of Day')
        plt.xlabel('Hour of Day')
        plt.ylabel('Number of Employees with Skill')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'skill_coverage.png'))
        plt.close()

    def generate_excel_report(self):
        """Generate a detailed Excel report of the schedule"""
        writer = pd.ExcelWriter(os.path.join(self.output_dir, 'schedule_report.xlsx'), engine='xlsxwriter')
        
        # Employee Schedule Sheet
        schedule_data = []
        for i, employee in enumerate(self.simulator.employees):
            shifts = self.simulator._get_shifts(employee.schedule)
            for shift in shifts:
                day = shift[0] // 24
                start_hour = shift[0] % 24
                end_hour = (shift[-1] % 24) + 1
                schedule_data.append({
                    'Employee ID': i,
                    'Skills': ', '.join(employee.skills),
                    'Day': day,
                    'Start Hour': f'{start_hour:02d}:00',
                    'End Hour': f'{end_hour:02d}:00',
                    'Shift Length': len(shift)
                })
        
        schedule_df = pd.DataFrame(schedule_data)
        schedule_df.to_excel(writer, sheet_name='Schedules', index=False)
        
        # Break Schedule Sheet
        break_data = []
        for i, employee in enumerate(self.simulator.employees):
            for break_time in sorted(employee.breaks_taken):
                break_data.append({
                    'Employee ID': i,
                    'Day': break_time // 24,
                    'Break Time': f'{break_time % 24:02d}:00'
                })
        
        break_df = pd.DataFrame(break_data)
        break_df.to_excel(writer, sheet_name='Breaks', index=False)
        
        # Coverage Summary Sheet
        coverage_data = self._generate_coverage_summary()
        coverage_df = pd.DataFrame(coverage_data)
        coverage_df.to_excel(writer, sheet_name='Coverage Summary', index=False)
        
        writer.close()

    def _generate_coverage_summary(self):
        """Generate coverage statistics"""
        hours = range(24)
        days = range(7)
        
        coverage_data = []
        for day in days:
            for hour in hours:
                staff_count = sum(1 for emp in self.simulator.employees 
                                if day * 24 + hour in emp.schedule)
                
                skills_present = set()
                for emp in self.simulator.employees:
                    if day * 24 + hour in emp.schedule:
                        skills_present.update(emp.skills)
                
                coverage_data.append({
                    'Day': day,
                    'Hour': hour,
                    'Staff Count': staff_count,
                    'Skills Available': ', '.join(skills_present)
                })
        
        return coverage_data

    def generate_all_visualizations(self):
        """Generate all visualizations and reports"""
        logger.info("Generating visualizations and reports...")
        self.create_gantt_chart()
        self.create_coverage_heatmap()
        self.create_skill_coverage_chart()
        self.generate_excel_report()
        logger.info(f"Output files have been saved to: {self.output_dir}/")
