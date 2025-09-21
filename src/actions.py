"""
Action definitions for the logistics domain.
Implements load, unload, and move actions with proper preconditions and effects.
"""

from unified_planning.shortcuts import *
from typing import List
from .domain import LogisticsDomain


class LogisticsActions:
    """Action definitions for the logistics domain."""
    
    def __init__(self, domain: LogisticsDomain):
        self.domain = domain
        self.actions = []
        self._define_actions()
    
    def _define_actions(self):
        """Define all actions in the domain."""
        self._define_move_action()
        self._define_pickup_action()
        self._define_putdown_action()
    
    
    def _define_move_action(self):
        """
        Define the move action: move(r, d, d')
        
        Robot r moves from dock d to adjacent dock d'.
        """
        # Create action first
        move_action = InstantaneousAction("move", robot=self.domain.Robot, from_dock=self.domain.Dock, to_dock=self.domain.Dock)
        
        # Get parameters from the action
        robot = move_action.parameter("robot")
        from_dock = move_action.parameter("from_dock")
        to_dock = move_action.parameter("to_dock")
        
        # Add preconditions using boolean fluents
        move_action.add_precondition(self.domain.robot_at(robot, from_dock))
        move_action.add_precondition(self.domain.adjacent(from_dock, to_dock))
        
        # Add effects
        move_action.add_effect(self.domain.robot_at(robot, from_dock), False)
        move_action.add_effect(self.domain.robot_at(robot, to_dock), True)
        
        self.actions.append(move_action)
    
    def _define_pickup_action(self):
        """
        Define the pickup action: pickup(r, c, p, d)
        
        Robot r picks up container c from pile p at dock d.
        """
        pickup_action = InstantaneousAction("pickup", robot=self.domain.Robot, container=self.domain.Container, pile=self.domain.Pile, dock=self.domain.Dock)
        
        # Get parameters
        robot = pickup_action.parameter("robot")
        container = pickup_action.parameter("container")
        pile = pickup_action.parameter("pile")
        dock = pickup_action.parameter("dock")
        
        # Add preconditions
        pickup_action.add_precondition(self.domain.robot_at(robot, dock))
        pickup_action.add_precondition(self.domain.pile_at_dock(pile, dock))
        pickup_action.add_precondition(self.domain.container_in_pile(container, pile))
        pickup_action.add_precondition(self.domain.robot_free(robot))
        
        # Add effects
        pickup_action.add_effect(self.domain.robot_carrying(robot, container), True)
        pickup_action.add_effect(self.domain.robot_free(robot), False)
        pickup_action.add_effect(self.domain.container_in_pile(container, pile), False)
        
        self.actions.append(pickup_action)
    
    def _define_putdown_action(self):
        """
        Define the putdown action: putdown(r, c, p, d)
        
        Robot r puts down container c onto pile p at dock d.
        """
        putdown_action = InstantaneousAction("putdown", robot=self.domain.Robot, container=self.domain.Container, pile=self.domain.Pile, dock=self.domain.Dock)
        
        # Get parameters
        robot = putdown_action.parameter("robot")
        container = putdown_action.parameter("container")
        pile = putdown_action.parameter("pile")
        dock = putdown_action.parameter("dock")
        
        # Add preconditions
        putdown_action.add_precondition(self.domain.robot_at(robot, dock))
        putdown_action.add_precondition(self.domain.pile_at_dock(pile, dock))
        putdown_action.add_precondition(self.domain.robot_carrying(robot, container))
        
        # Add effects
        putdown_action.add_effect(self.domain.robot_carrying(robot, container), False)
        putdown_action.add_effect(self.domain.robot_free(robot), True)
        putdown_action.add_effect(self.domain.container_in_pile(container, pile), True)
        
        self.actions.append(putdown_action)
    
    def get_actions(self) -> List[InstantaneousAction]:
        """Return all defined actions."""
        return self.actions