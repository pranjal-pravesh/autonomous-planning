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
        # For now, only define move action to get basic functionality working
        # self._define_load_action()
        # self._define_unload_action()
        self._define_move_action()
    
    def _define_load_action(self):
        """
        Define the load action: load(r, c, c', p, d)
        
        Robot r loads container c from pile p at dock d, where c' is the container
        that c is currently on top of (or nil if c is at the bottom).
        """
        # Parameters
        r = Parameter("r", self.domain.Robot)
        c = Parameter("c", self.domain.Container)
        c_prime = Parameter("c'", self.domain.Container)
        p = Parameter("p", self.domain.Pile)
        d = Parameter("d", self.domain.Dock)
        
        # Preconditions
        preconditions = [
            # Pile p is at dock d
            self.domain.at(p, d),
            # Robot r is at dock d
            Equals(self.domain.loc(r), d),
            # Robot r is not carrying anything
            Equals(self.domain.cargo(r), self.domain.nil_container),
            # Container c is on top of pile p
            Equals(self.domain.top(p), c),
            # Container c is on top of c' (or nil if at bottom)
            Equals(self.domain.pos(c), c_prime),
            # Container c is in pile p
            Equals(self.domain.pile(c), p)
        ]
        
        # Create action
        load_action = InstantaneousAction("load", r=self.domain.Robot, c=self.domain.Container, c_prime=self.domain.Container, p=self.domain.Pile, d=self.domain.Dock)
        
        # Add preconditions
        for precondition in preconditions:
            load_action.add_precondition(precondition)
        
        # Add effects
        load_action.add_effect(self.domain.cargo(r), c)
        load_action.add_effect(self.domain.pile(c), self.domain.nil_pile)
        load_action.add_effect(self.domain.pos(c), r)
        load_action.add_effect(self.domain.top(p), c_prime)
        
        self.actions.append(load_action)
    
    def _define_unload_action(self):
        """
        Define the unload action: unload(r, c, c', p, d)
        
        Robot r unloads container c onto pile p at dock d, placing it on top of c'
        (or at the bottom if c' is nil).
        """
        # Parameters
        r = Parameter("r", self.domain.Robot)
        c = Parameter("c", self.domain.Container)
        c_prime = Parameter("c'", self.domain.Container)
        p = Parameter("p", self.domain.Pile)
        d = Parameter("d", self.domain.Dock)
        
        # Preconditions
        preconditions = [
            # Pile p is at dock d
            self.domain.at(p, d),
            # Robot r is at dock d
            Equals(self.domain.loc(r), d),
            # Robot r is carrying container c
            Equals(self.domain.cargo(r), c),
            # Container c is currently on robot r
            Equals(self.domain.pos(c), r),
            # Container c' is currently on top of pile p (or nil if pile is empty)
            Equals(self.domain.top(p), c_prime)
        ]
        
        # Create action
        unload_action = InstantaneousAction("unload", r=self.domain.Robot, c=self.domain.Container, c_prime=self.domain.Container, p=self.domain.Pile, d=self.domain.Dock)
        
        # Add preconditions
        for precondition in preconditions:
            unload_action.add_precondition(precondition)
        
        # Add effects
        unload_action.add_effect(self.domain.cargo(r), self.domain.nil_container)
        unload_action.add_effect(self.domain.pile(c), p)
        unload_action.add_effect(self.domain.pos(c), c_prime)
        unload_action.add_effect(self.domain.top(p), c)
        
        self.actions.append(unload_action)
    
    def _define_move_action(self):
        """
        Define the move action: move(r, d, d')
        
        Robot r moves from dock d to adjacent dock d'.
        """
        # Create action first
        move_action = InstantaneousAction("move", r=self.domain.Robot, d=self.domain.Dock, d_prime=self.domain.Dock)
        
        # Get parameters from the action
        r = move_action.parameter("r")
        d = move_action.parameter("d")
        d_prime = move_action.parameter("d_prime")
        
        # Add preconditions using proper fluent expressions
        move_action.add_precondition(self.domain.adjacent(d, d_prime))
        move_action.add_precondition(Equals(self.domain.loc(r), d))
        move_action.add_precondition(Not(self.domain.occupied(d_prime)))
        
        # Add effects
        move_action.add_effect(self.domain.loc(r), d_prime)
        move_action.add_effect(self.domain.occupied(d), False)
        move_action.add_effect(self.domain.occupied(d_prime), True)
        
        self.actions.append(move_action)
    
    def get_actions(self) -> List[InstantaneousAction]:
        """Return all defined actions."""
        return self.actions