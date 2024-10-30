import simpy
from simulator.workforce_simulator import WorkforceSimulator
from visualization.visualizer import ScheduleVisualizer
from models.entities import Employee
from config.settings import SKILLS_MATRIX
from utils.logger import setup_logger

logger = setup_logger()

def main():
    try:
        # Initialize simulation environment
        env = simpy.Environment()
        simulator = WorkforceSimulator(env)
        
        # Add employees
        for i, skills in enumerate(SKILLS_MATRIX):
            simulator.add_employee(Employee(id=i, skills=skills))
        
        # Generate schedule
        simulator.generate_schedule()
        
        # Add breaks
        simulator.add_breaks()
        
        # Create visualizer and generate outputs
        visualizer = ScheduleVisualizer(simulator)
        visualizer.generate_all_visualizations()
        
        logger.info("Schedule generation and visualization complete!")
        logger.info("The following files have been generated in the schedule_output directory:")
        logger.info("1. schedule_gantt.html - Interactive Gantt chart of the schedule")
        logger.info("2. coverage_heatmap.png - Heatmap showing staff coverage")
        logger.info("3. skill_coverage.png - Line chart showing skill coverage by hour")
        logger.info("4. schedule_report.xlsx - Detailed Excel report of the schedule")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())