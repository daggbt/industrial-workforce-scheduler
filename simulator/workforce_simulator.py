import simpy
import pyomo.environ as pyo
import numpy as np
import pandas as pd
from typing import List
from collections import defaultdict

from config.settings import SIMULATION_SETTINGS, SHIFTS
from models.entities import Employee, Task
from utils.logger import setup_logger
from utils.helpers import get_shifts

logger = setup_logger()

class WorkforceSimulator:
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.employees = []
        self.tasks = []
        self.resources = {}
        self.historical_demand = pd.DataFrame()
        self.performance_metrics = defaultdict(list)

    def add_employee(self, employee: Employee):
        self.employees.append(employee)
        for skill in employee.skills:
            if skill not in self.resources:
                self.resources[skill] = simpy.Resource(self.env, capacity=1)

    def generate_schedule(self, horizon_days: int = 7):
        """Generate optimal staff schedule using Pyomo with CBC solver"""
        try:
            model = pyo.ConcreteModel()

            # Sets
            model.PERIODS = pyo.Set(initialize=range(24 * horizon_days))
            model.EMPLOYEES = pyo.Set(initialize=range(len(self.employees)))
            model.DAYS = pyo.Set(initialize=range(horizon_days))

            # Variables
            model.working = pyo.Var(model.EMPLOYEES, model.PERIODS, domain=pyo.Binary)

            # Objective
            model.objective = pyo.Objective(
                expr=sum(model.working[e,p] for e in model.EMPLOYEES for p in model.PERIODS),
                sense=pyo.minimize
            )

            # Constraints
            # 1. Daily working hours limit (8 hours per day)
            def daily_hours_rule(model, e, d):
                day_start = d * 24
                return sum(model.working[e,p] for p in range(day_start, day_start + 24)) <= 8
            model.daily_hours = pyo.Constraint(model.EMPLOYEES, model.DAYS, rule=daily_hours_rule)

            # 2. Minimum coverage (at least one employee working at all times)
            def coverage_rule(model, p):
                return sum(model.working[e,p] for e in model.EMPLOYEES) >= 1
            model.coverage = pyo.Constraint(model.PERIODS, rule=coverage_rule)

            # 3. Maximum consecutive working hours (8 hours)
            def consecutive_hours_rule(model, e, p):
                if p <= len(model.PERIODS) - 9:
                    return sum(model.working[e,t] for t in range(p, p + 9)) <= 8
                return pyo.Constraint.Skip
            model.consecutive_hours = pyo.Constraint(model.EMPLOYEES, model.PERIODS, rule=consecutive_hours_rule)

            # Solve
            solver = pyo.SolverFactory('cbc')
            results = solver.solve(model, tee=True)

            if (results.solver.status == pyo.SolverStatus.ok and
                results.solver.termination_condition == pyo.TerminationCondition.optimal):
                
                # Extract solution
                for e in model.EMPLOYEES:
                    schedule = []
                    for p in model.PERIODS:
                        if pyo.value(model.working[e,p]) > 0.5:
                            schedule.append(p)
                    self.employees[e].schedule = schedule
                logger.info("Schedule optimization completed successfully")
            else:
                logger.warning(f"Solver status: {results.solver.status}, Termination condition: {results.solver.termination_condition}")
                self._generate_fallback_schedule(horizon_days)

        except Exception as e:
            logger.error(f"Error in schedule generation: {str(e)}")
            self._generate_fallback_schedule(horizon_days)

    def _generate_fallback_schedule(self, horizon_days: int):
        """Generate a basic feasible schedule when optimization fails"""
        logger.info("Generating fallback schedule...")
        
        shifts = [
            (0, 8),   # Morning shift
            (8, 16),  # Day shift
            (16, 24)  # Night shift
        ]
        
        for e in range(len(self.employees)):
            schedule = []
            shift_index = e % len(shifts)
            shift_start, shift_end = shifts[shift_index]
            
            for day in range(horizon_days):
                if day % 2 == 0:  # Work every other day
                    for hour in range(shift_start, shift_end):
                        schedule.append(day * 24 + hour)
            
            self.employees[e].schedule = schedule
        
        logger.info("Fallback schedule generated successfully")

    def add_breaks(self):
        """Add breaks to each employee's schedule"""
        try:
            for employee in self.employees:
                shifts = self._get_shifts(employee.schedule)
                employee.breaks_taken = []
                
                for shift in shifts:
                    if len(shift) >= 6:  # Only add breaks for shifts 6 hours or longer
                        # Add break at middle of shift
                        mid_point = shift[len(shift) // 2]
                        employee.breaks_taken.append(mid_point)
            
            logger.info("Break assignment completed successfully")
            
        except Exception as e:
            logger.error(f"Error in break assignment: {str(e)}")

    def _get_shifts(self, schedule):
        """Helper function to group consecutive hours into shifts"""
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

    def print_schedule(self):
        """Print the schedule in a readable format"""
        print("\nSchedule Summary:")
        for i, employee in enumerate(self.employees):
            print(f"\nEmployee {i} (Skills: {', '.join(employee.skills)})")
            shifts = self._get_shifts(employee.schedule)
            for j, shift in enumerate(shifts):
                day = shift[0] // 24
                start_hour = shift[0] % 24
                end_hour = (shift[-1] % 24) + 1
                print(f"  Day {day}: {start_hour:02d}:00 - {end_hour:02d}:00")
            if employee.breaks_taken:
                break_times = [f"Day {b//24}, {b%24:02d}:00" for b in sorted(employee.breaks_taken)]
                print(f"  Breaks: {', '.join(break_times)}")