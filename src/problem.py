"""
Problem setup and initial state for the logistics domain.
Creates planning problems with different goals for testing.
"""

from unified_planning.shortcuts import *
from typing import Dict, List, Any
from .domain import LogisticsDomain
from .actions import LogisticsActions


class LogisticsProblem:
    """Problem setup for the logistics domain."""
    
    def __init__(self):
        self.domain = LogisticsDomain()
        self.actions = LogisticsActions(self.domain)
        self.problem = None
    
    def create_problem(self, name: str = "logistics_problem") -> Problem:
        """Create a basic problem with the domain and initial state."""
        # Create problem
        self.problem = Problem(name)
        
        # Add types
        self.problem.add_objects(self.domain.objects)
        
        # Add fluents
        for fluent in self.domain.fluents + self.domain.static_fluents:
            self.problem.add_fluent(fluent, default_initial_value=False)
        
        # Add actions
        for action in self.actions.get_actions():
            self.problem.add_action(action)
        
        # Set initial state
        initial_state = self.domain.get_initial_state()
        for fluent, value in initial_state.items():
            self.problem.set_initial_value(fluent, value)
        
        return self.problem
    
    def add_goal(self, goal_expression) -> None:
        """Add a goal to the current problem."""
        if self.problem is None:
            raise ValueError("Problem not created yet. Call create_problem() first.")
        self.problem.add_goal(goal_expression)
    
    def create_robot_location_goal(self, robot, dock) -> None:
        """Create a goal to move a robot to a specific dock."""
        goal = Equals(self.domain.loc(robot), dock)
        self.add_goal(goal)
    
    def create_container_pile_goal(self, container, pile) -> None:
        """Create a goal to move a container to a specific pile."""
        goal = Equals(self.domain.pile(container), pile)
        self.add_goal(goal)
    
    def create_container_position_goal(self, container, position) -> None:
        """Create a goal to move a container to a specific position."""
        goal = Equals(self.domain.pos(container), position)
        self.add_goal(goal)
    
    def create_complex_goal(self, goals: List[Any]) -> None:
        """Create a complex goal with multiple conditions."""
        if len(goals) == 1:
            self.add_goal(goals[0])
        else:
            # Combine multiple goals with AND
            combined_goal = goals[0]
            for goal in goals[1:]:
                combined_goal = And(combined_goal, goal)
            self.add_goal(combined_goal)
    
    def get_problem(self) -> Problem:
        """Return the current problem."""
        if self.problem is None:
            raise ValueError("Problem not created yet. Call create_problem() first.")
        return self.problem
    
    def reset_problem(self) -> None:
        """Reset the problem to start fresh."""
        self.problem = None


# Predefined example problems
class ExampleProblems:
    """Collection of example problems for testing."""
    
    def __init__(self):
        self.problem_setup = LogisticsProblem()
    
    def problem_1_move_robot(self) -> Problem:
        """Problem 1: Move robot r1 to dock d3."""
        problem = self.problem_setup.create_problem("move_robot_r1_to_d3")
        self.problem_setup.create_robot_location_goal(self.problem_setup.domain.r1, self.problem_setup.domain.d3)
        return problem
    
    def problem_2_move_container(self) -> Problem:
        """Problem 2: Move container c1 to pile p2."""
        problem = self.problem_setup.create_problem("move_container_c1_to_p2")
        self.problem_setup.create_container_pile_goal(self.problem_setup.domain.c1, self.problem_setup.domain.p2)
        return problem
    
    def problem_3_complex_goal(self) -> Problem:
        """Problem 3: Move r1 to d3 AND move c1 to p2."""
        problem = self.problem_setup.create_problem("complex_goal")
        goals = [
            Equals(self.problem_setup.domain.loc(self.problem_setup.domain.r1), self.problem_setup.domain.d3),
            Equals(self.problem_setup.domain.pile(self.problem_setup.domain.c1), self.problem_setup.domain.p2)
        ]
        self.problem_setup.create_complex_goal(goals)
        return problem
    
    def problem_4_swap_containers(self) -> Problem:
        """Problem 4: Swap positions of c1 and c3."""
        problem = self.problem_setup.create_problem("swap_containers")
        goals = [
            Equals(self.problem_setup.domain.pile(self.problem_setup.domain.c1), self.problem_setup.domain.p2),
            Equals(self.problem_setup.domain.pile(self.problem_setup.domain.c3), self.problem_setup.domain.p1)
        ]
        self.problem_setup.create_complex_goal(goals)
        return problem
    
    def get_all_problems(self) -> Dict[str, Problem]:
        """Return all example problems."""
        return {
            "move_robot": self.problem_1_move_robot(),
            "move_container": self.problem_2_move_container(),
            "complex_goal": self.problem_3_complex_goal(),
            "swap_containers": self.problem_4_swap_containers()
        }
