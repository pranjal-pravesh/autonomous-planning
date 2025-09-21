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
        Simplified capacity system with boolean fluents.
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
        
        # LIFO constraint for piles - robot can only pick up the top container
        pickup_action.add_precondition(self.domain.container_on_top_of_pile(container, pile))
        
        # Capacity constraint: robot must have available capacity
        # Robot can pick up if it has any free slot (not all slots occupied)
        pickup_action.add_precondition(
            Or(
                And(self.domain.robot_can_carry_1(robot), Not(self.domain.robot_has_container_1(robot))),
                And(self.domain.robot_can_carry_2(robot), Not(self.domain.robot_has_container_2(robot))),
                And(self.domain.robot_can_carry_3(robot), Not(self.domain.robot_has_container_3(robot)))
            )
        )
        
        # Weight constraint: robot must have weight capacity for the container
        # Define all valid weight combinations explicitly
        pickup_action.add_precondition(
            Or(
                # Pick up 2t container when robot has 0t (total 2t <= capacity)
                And(self.domain.container_weight_2(container), self.domain.robot_weight_0(robot)),
                # Pick up 2t container when robot has 2t (total 4t <= capacity)
                And(self.domain.container_weight_2(container), self.domain.robot_weight_2(robot)),
                # Pick up 2t container when robot has 4t (total 6t <= capacity)
                And(self.domain.container_weight_2(container), self.domain.robot_weight_4(robot)),
                # Pick up 4t container when robot has 0t (total 4t <= capacity)
                And(self.domain.container_weight_4(container), self.domain.robot_weight_0(robot)),
                # Pick up 4t container when robot has 2t (total 6t <= capacity)
                And(self.domain.container_weight_4(container), self.domain.robot_weight_2(robot)),
                # Pick up 6t container when robot has 0t (total 6t <= capacity)
                And(self.domain.container_weight_6(container), self.domain.robot_weight_0(robot)),
            )
        )
        
        # Add effects
        pickup_action.add_effect(self.domain.robot_carrying(robot, container), True)
        pickup_action.add_effect(self.domain.container_in_pile(container, pile), False)
        
        # Update robot load tracking - assign container to first available slot (LIFO loading)
        # Slot 1 first (if available)
        pickup_action.add_effect(
            self.domain.container_in_robot_slot_1(robot, container),
            True,
            condition=And(
                self.domain.robot_can_carry_1(robot), 
                Not(self.domain.robot_has_container_1(robot))
            )
        )
        pickup_action.add_effect(
            self.domain.robot_has_container_1(robot), 
            True,
            condition=And(
                self.domain.robot_can_carry_1(robot), 
                Not(self.domain.robot_has_container_1(robot))
            )
        )
        
        # Slot 2 second (if slot 1 occupied and slot 2 available)
        pickup_action.add_effect(
            self.domain.container_in_robot_slot_2(robot, container),
            True,
            condition=And(
                self.domain.robot_can_carry_2(robot), 
                Not(self.domain.robot_has_container_2(robot)),
                self.domain.robot_has_container_1(robot)
            )
        )
        pickup_action.add_effect(
            self.domain.robot_has_container_2(robot), 
            True,
            condition=And(
                self.domain.robot_can_carry_2(robot), 
                Not(self.domain.robot_has_container_2(robot)),
                self.domain.robot_has_container_1(robot)
            )
        )
        
        # Slot 3 third (if slots 1&2 occupied and slot 3 available)
        pickup_action.add_effect(
            self.domain.container_in_robot_slot_3(robot, container),
            True,
            condition=And(
                self.domain.robot_can_carry_3(robot), 
                Not(self.domain.robot_has_container_3(robot)),
                self.domain.robot_has_container_1(robot),
                self.domain.robot_has_container_2(robot)
            )
        )
        pickup_action.add_effect(
            self.domain.robot_has_container_3(robot), 
            True,
            condition=And(
                self.domain.robot_can_carry_3(robot), 
                Not(self.domain.robot_has_container_3(robot)),
                self.domain.robot_has_container_1(robot),
                self.domain.robot_has_container_2(robot)
            )
        )
        
        # Update robot_free status - robot is free only if no containers
        pickup_action.add_effect(
            self.domain.robot_free(robot), 
            False,
            condition=Or(
                self.domain.robot_has_container_1(robot),
                self.domain.robot_has_container_2(robot),
                self.domain.robot_has_container_3(robot)
            )
        )
        
        # Update robot weight levels - define all weight combinations explicitly
        # Pick up 2t container when robot has 0t -> robot now has 2t
        pickup_action.add_effect(self.domain.robot_weight_0(robot), False, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_0(robot)))
        pickup_action.add_effect(self.domain.robot_weight_2(robot), True, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_0(robot)))
        
        # Pick up 2t container when robot has 2t -> robot now has 4t
        pickup_action.add_effect(self.domain.robot_weight_2(robot), False, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_2(robot)))
        pickup_action.add_effect(self.domain.robot_weight_4(robot), True, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_2(robot)))
        
        # Pick up 2t container when robot has 4t -> robot now has 6t
        pickup_action.add_effect(self.domain.robot_weight_4(robot), False, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_4(robot)))
        pickup_action.add_effect(self.domain.robot_weight_6(robot), True, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_4(robot)))
        
        # Pick up 4t container when robot has 0t -> robot now has 4t
        pickup_action.add_effect(self.domain.robot_weight_0(robot), False, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_0(robot)))
        pickup_action.add_effect(self.domain.robot_weight_4(robot), True, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_0(robot)))
        
        # Pick up 4t container when robot has 2t -> robot now has 6t
        pickup_action.add_effect(self.domain.robot_weight_2(robot), False, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_2(robot)))
        pickup_action.add_effect(self.domain.robot_weight_6(robot), True, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_2(robot)))
        
        # Pick up 6t container when robot has 0t -> robot now has 6t
        pickup_action.add_effect(self.domain.robot_weight_0(robot), False, 
                                condition=And(self.domain.container_weight_6(container), self.domain.robot_weight_0(robot)))
        pickup_action.add_effect(self.domain.robot_weight_6(robot), True, 
                                condition=And(self.domain.container_weight_6(container), self.domain.robot_weight_0(robot)))
        
        # Update pile stacking - remove container from top
        pickup_action.add_effect(self.domain.container_on_top_of_pile(container, pile), False)
        
        # Update stacking relationships when picking up
        # If this container was on top of another, update the new top
        # Get all containers dynamically from domain objects
        domain_objects = self.domain.get_domain_objects()
        containers = domain_objects["containers"]
        
        for other_container in containers:
            if other_container != container:
                # If other_container was under this container, it becomes the new top
                pickup_action.add_effect(
                    self.domain.container_on_top_of_pile(other_container, pile),
                    True,
                    condition=self.domain.container_under_in_pile(other_container, container, pile)
                )
                # Remove the under relationship
                pickup_action.add_effect(
                    self.domain.container_under_in_pile(other_container, container, pile),
                    False,
                    condition=self.domain.container_under_in_pile(other_container, container, pile)
                )
        
        self.actions.append(pickup_action)
    
    def _define_putdown_action(self):
        """
        Define the putdown action: putdown(r, c, p, d)
        
        Robot r puts down container c onto pile p at dock d.
        Simplified capacity system.
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
        
        # LIFO constraint: Robot can only put down container from the top slot
        # Can only putdown if this specific container is in the topmost occupied slot
        putdown_action.add_precondition(
            Or(
                # Container is in slot 3 (top slot - always can putdown)
                self.domain.container_in_robot_slot_3(robot, container),
                # Container is in slot 2 AND slot 3 is empty (slot 2 is now top)
                And(
                    self.domain.container_in_robot_slot_2(robot, container),
                    Not(self.domain.robot_has_container_3(robot))
                ),
                # Container is in slot 1 AND slots 2&3 are empty (slot 1 is now top)
                And(
                    self.domain.container_in_robot_slot_1(robot, container),
                    Not(self.domain.robot_has_container_2(robot)),
                    Not(self.domain.robot_has_container_3(robot))
                )
            )
        )
        
        # Add effects
        putdown_action.add_effect(self.domain.robot_carrying(robot, container), False)
        putdown_action.add_effect(self.domain.container_in_pile(container, pile), True)
        
        # Update robot load tracking - clear the specific container from its slot
        # Clear the specific container-slot relationship
        putdown_action.add_effect(self.domain.container_in_robot_slot_1(robot, container), False)
        putdown_action.add_effect(self.domain.container_in_robot_slot_2(robot, container), False)
        putdown_action.add_effect(self.domain.container_in_robot_slot_3(robot, container), False)
        
        # Update slot occupancy flags
        putdown_action.add_effect(
            self.domain.robot_has_container_3(robot), 
            False,
            condition=self.domain.container_in_robot_slot_3(robot, container)
        )
        
        putdown_action.add_effect(
            self.domain.robot_has_container_2(robot), 
            False,
            condition=self.domain.container_in_robot_slot_2(robot, container)
        )
        
        putdown_action.add_effect(
            self.domain.robot_has_container_1(robot), 
            False,
            condition=self.domain.container_in_robot_slot_1(robot, container)
        )
        
        # Update robot_free status - robot is free if no containers
        putdown_action.add_effect(
            self.domain.robot_free(robot), 
            True,
            condition=And(
                Not(self.domain.robot_has_container_1(robot)),
                Not(self.domain.robot_has_container_2(robot)),
                Not(self.domain.robot_has_container_3(robot))
            )
        )
        
        # Update robot weight levels - define all weight combinations explicitly
        # Put down 2t container when robot has 2t -> robot now has 0t
        putdown_action.add_effect(self.domain.robot_weight_2(robot), False, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_2(robot)))
        putdown_action.add_effect(self.domain.robot_weight_0(robot), True, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_2(robot)))
        
        # Put down 2t container when robot has 4t -> robot now has 2t
        putdown_action.add_effect(self.domain.robot_weight_4(robot), False, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_4(robot)))
        putdown_action.add_effect(self.domain.robot_weight_2(robot), True, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_4(robot)))
        
        # Put down 2t container when robot has 6t -> robot now has 4t
        putdown_action.add_effect(self.domain.robot_weight_6(robot), False, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_6(robot)))
        putdown_action.add_effect(self.domain.robot_weight_4(robot), True, 
                                condition=And(self.domain.container_weight_2(container), self.domain.robot_weight_6(robot)))
        
        # Put down 4t container when robot has 4t -> robot now has 0t
        putdown_action.add_effect(self.domain.robot_weight_4(robot), False, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_4(robot)))
        putdown_action.add_effect(self.domain.robot_weight_0(robot), True, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_4(robot)))
        
        # Put down 4t container when robot has 6t -> robot now has 2t
        putdown_action.add_effect(self.domain.robot_weight_6(robot), False, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_6(robot)))
        putdown_action.add_effect(self.domain.robot_weight_2(robot), True, 
                                condition=And(self.domain.container_weight_4(container), self.domain.robot_weight_6(robot)))
        
        # Put down 6t container when robot has 6t -> robot now has 0t
        putdown_action.add_effect(self.domain.robot_weight_6(robot), False, 
                                condition=And(self.domain.container_weight_6(container), self.domain.robot_weight_6(robot)))
        putdown_action.add_effect(self.domain.robot_weight_0(robot), True, 
                                condition=And(self.domain.container_weight_6(container), self.domain.robot_weight_6(robot)))
        
        # Update pile stacking - this container becomes the new top
        putdown_action.add_effect(self.domain.container_on_top_of_pile(container, pile), True)
        
        # Update stacking relationships when putting down
        # Find what was previously on top and put this container on top of it
        # Get all containers dynamically from domain objects
        domain_objects = self.domain.get_domain_objects()
        containers = domain_objects["containers"]
        
        for other_container in containers:
            if other_container != container:
                # If other_container was on top, it's no longer on top
                putdown_action.add_effect(
                    self.domain.container_on_top_of_pile(other_container, pile),
                    False,
                    condition=self.domain.container_on_top_of_pile(other_container, pile)
                )
                # This container is now on top of the other container
                putdown_action.add_effect(
                    self.domain.container_under_in_pile(other_container, container, pile),
                    True,
                    condition=self.domain.container_on_top_of_pile(other_container, pile)
                )
        
        self.actions.append(putdown_action)
    
    def get_actions(self) -> List[InstantaneousAction]:
        """Return all defined actions."""
        return self.actions