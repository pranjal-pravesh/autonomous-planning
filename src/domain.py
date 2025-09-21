"""
Domain definition for Example 2.3 - Logistics domain with robots, docks, containers, and piles.
Based on Figure 2.3 from "Automated Planning and Acting" by Ghallab, Nau, and Traverso.
"""

from unified_planning.shortcuts import *
from typing import Dict, Set, Tuple


class LogisticsDomain:
    """Logistics domain with robots, docks, containers, and piles."""
    
    def __init__(self, scale: str = "small"):
        """
        Initialize logistics domain.
        
        Args:
            scale: "small" for basic 3-dock scenario, "large" for 8-dock scenario
        """
        self.scale = scale
        self._setup_types()
        self._setup_objects()
        self._setup_fluents()
        self._setup_static_relations()
    
    def _setup_types(self):
        """Define the types for the domain."""
        # Basic types
        self.Robot = UserType("Robot")
        self.Dock = UserType("Dock") 
        self.Container = UserType("Container")
        self.Pile = UserType("Pile")
    
    def _setup_objects(self):
        """Define the objects in the domain."""
        if self.scale == "small":
            self._setup_small_objects()
        elif self.scale == "large":
            self._setup_large_objects()
        else:
            raise ValueError(f"Unknown scale: {self.scale}")
    
    def _setup_small_objects(self):
        """Setup objects for small-scale (3-dock) scenario."""
        # Robots with different capacities
        self.r1 = Object("r1", self.Robot)  # Capacity 1
        self.r2 = Object("r2", self.Robot)  # Capacity 2
        self.r3 = Object("r3", self.Robot)  # Capacity 3
        
        # Docks
        self.d1 = Object("d1", self.Dock)
        self.d2 = Object("d2", self.Dock)
        self.d3 = Object("d3", self.Dock)
        
        # Containers
        self.c1 = Object("c1", self.Container)
        self.c2 = Object("c2", self.Container)
        self.c3 = Object("c3", self.Container)
        self.c4 = Object("c4", self.Container)
        self.c5 = Object("c5", self.Container)
        
        # Piles
        self.p1 = Object("p1", self.Pile)
        self.p2 = Object("p2", self.Pile)
        self.p3 = Object("p3", self.Pile)
        
        # Special objects
        self.nil_container = Object("nil_container", self.Container)
        self.nil_pile = Object("nil_pile", self.Pile)
        
        # All objects list
        self.objects = [
            self.r1, self.r2, self.r3,
            self.d1, self.d2, self.d3,
            self.c1, self.c2, self.c3, self.c4, self.c5,
            self.p1, self.p2, self.p3,
            self.nil_container, self.nil_pile
        ]
    
    def _setup_large_objects(self):
        """Setup objects for large-scale (8-dock) scenario."""
        # 3 robots with different capacities
        self.r1 = Object("r1", self.Robot)  # Capacity 1
        self.r2 = Object("r2", self.Robot)  # Capacity 2
        self.r3 = Object("r3", self.Robot)  # Capacity 3
        
        # 8 docks
        self.d1 = Object("d1", self.Dock)
        self.d2 = Object("d2", self.Dock)
        self.d3 = Object("d3", self.Dock)
        self.d4 = Object("d4", self.Dock)
        self.d5 = Object("d5", self.Dock)
        self.d6 = Object("d6", self.Dock)
        self.d7 = Object("d7", self.Dock)
        self.d8 = Object("d8", self.Dock)
        
        # 15 containers
        self.c1 = Object("c1", self.Container)
        self.c2 = Object("c2", self.Container)
        self.c3 = Object("c3", self.Container)
        self.c4 = Object("c4", self.Container)
        self.c5 = Object("c5", self.Container)
        self.c6 = Object("c6", self.Container)
        self.c7 = Object("c7", self.Container)
        self.c8 = Object("c8", self.Container)
        self.c9 = Object("c9", self.Container)
        self.c10 = Object("c10", self.Container)
        self.c11 = Object("c11", self.Container)
        self.c12 = Object("c12", self.Container)
        self.c13 = Object("c13", self.Container)
        self.c14 = Object("c14", self.Container)
        self.c15 = Object("c15", self.Container)
        
        # 12 piles (unequal distribution per dock)
        self.p1 = Object("p1", self.Pile)   # d1
        self.p2 = Object("p2", self.Pile)   # d1
        self.p3 = Object("p3", self.Pile)   # d2
        self.p4 = Object("p4", self.Pile)   # d3
        self.p5 = Object("p5", self.Pile)   # d3
        self.p6 = Object("p6", self.Pile)   # d3
        self.p7 = Object("p7", self.Pile)   # d4
        self.p8 = Object("p8", self.Pile)   # d5
        self.p9 = Object("p9", self.Pile)   # d5
        self.p10 = Object("p10", self.Pile) # d6
        self.p11 = Object("p11", self.Pile) # d7
        self.p12 = Object("p12", self.Pile) # d8
        self.p13 = Object("p13", self.Pile) # d6 (additional)
        self.p14 = Object("p14", self.Pile) # d7 (additional)
        self.p15 = Object("p15", self.Pile) # d8 (additional)
        
        # Special objects
        self.nil_container = Object("nil_container", self.Container)
        self.nil_pile = Object("nil_pile", self.Pile)
        
        # All objects list
        self.objects = [
            self.r1, self.r2, self.r3,  # 3 robots
            self.d1, self.d2, self.d3, self.d4, self.d5, self.d6, self.d7, self.d8,  # 8 docks
            self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8, 
            self.c9, self.c10, self.c11, self.c12, self.c13,  # 13 containers (c14, c15 removed)
            self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, 
            self.p9, self.p10, self.p11, self.p12, self.p13, self.p14, self.p15,  # 15 piles
            self.nil_container, self.nil_pile
        ]
    
    def _setup_fluents(self):
        """Define the state variables (fluents) for the domain."""
        # Robot state (boolean fluents for PDDL compatibility)
        self.robot_at = Fluent("robot_at", BoolType(), robot=self.Robot, dock=self.Dock)
        self.robot_carrying = Fluent("robot_carrying", BoolType(), robot=self.Robot, container=self.Container)
        self.robot_free = Fluent("robot_free", BoolType(), robot=self.Robot)
        
        # Robot capacity system (simplified with boolean fluents)
        self.robot_can_carry_1 = Fluent("robot_can_carry_1", BoolType(), robot=self.Robot)
        self.robot_can_carry_2 = Fluent("robot_can_carry_2", BoolType(), robot=self.Robot)
        self.robot_can_carry_3 = Fluent("robot_can_carry_3", BoolType(), robot=self.Robot)
        
        # Robot load tracking (simplified)
        self.robot_has_container_1 = Fluent("robot_has_container_1", BoolType(), robot=self.Robot)
        self.robot_has_container_2 = Fluent("robot_has_container_2", BoolType(), robot=self.Robot)
        self.robot_has_container_3 = Fluent("robot_has_container_3", BoolType(), robot=self.Robot)
        
        # Track which specific container is in each slot (for LIFO enforcement)
        self.container_in_robot_slot_1 = Fluent("container_in_robot_slot_1", BoolType(), robot=self.Robot, container=self.Container)
        self.container_in_robot_slot_2 = Fluent("container_in_robot_slot_2", BoolType(), robot=self.Robot, container=self.Container)
        self.container_in_robot_slot_3 = Fluent("container_in_robot_slot_3", BoolType(), robot=self.Robot, container=self.Container)
        
        # Container state
        self.container_in_pile = Fluent("container_in_pile", BoolType(), container=self.Container, pile=self.Pile)
        self.container_on_top_of_pile = Fluent("container_on_top_of_pile", BoolType(), container=self.Container, pile=self.Pile)
        self.container_under_in_pile = Fluent("container_under_in_pile", BoolType(), container=self.Container, other_container=self.Container, pile=self.Pile)
        
        # Pile state
        self.pile_at_dock = Fluent("pile_at_dock", BoolType(), pile=self.Pile, dock=self.Dock)
        
        # All fluents list
        self.fluents = [
            self.robot_at, self.robot_carrying, self.robot_free,
            self.robot_can_carry_1, self.robot_can_carry_2, self.robot_can_carry_3,
            self.robot_has_container_1, self.robot_has_container_2, self.robot_has_container_3,
            self.container_in_robot_slot_1, self.container_in_robot_slot_2, self.container_in_robot_slot_3,
            self.container_in_pile, self.container_on_top_of_pile, self.container_under_in_pile,
            self.pile_at_dock
        ]
    
    def _setup_static_relations(self):
        """Define static relations (rigid properties)."""
        # Adjacent docks
        self.adjacent = Fluent("adjacent", BoolType(), dock1=self.Dock, dock2=self.Dock)
        
        # All static fluents
        self.static_fluents = [self.adjacent]
    
    def get_initial_state(self) -> Dict[Fluent, object]:
        """Return the initial state based on scale."""
        if self.scale == "small":
            return self._get_small_initial_state()
        elif self.scale == "large":
            return self._get_large_initial_state()
        else:
            raise ValueError(f"Unknown scale: {self.scale}")
    
    def _get_small_initial_state(self) -> Dict[Fluent, object]:
        """
        Return the initial state for small-scale scenario.
        
        Initial configuration:
        - r1 at d1 (capacity 1), r2 at d2 (capacity 2), r3 at d3 (capacity 3)
        - p1 at d1 with c1, c2
        - p2 at d2 with c3
        - p3 at d2, empty
        """
        return {
            # Robot locations
            self.robot_at(self.r1, self.d1): True,
            self.robot_at(self.r2, self.d1): True,
            self.robot_at(self.r3, self.d2): True,
            
            # Robot capacities (simplified boolean system)
            self.robot_can_carry_1(self.r1): True,   # r1 can carry 1 container
            self.robot_can_carry_2(self.r1): False,  # r1 cannot carry 2 containers
            self.robot_can_carry_3(self.r1): False,  # r1 cannot carry 3 containers
            
            self.robot_can_carry_1(self.r2): True,   # r2 can carry 1 container
            self.robot_can_carry_2(self.r2): True,   # r2 can carry 2 containers
            self.robot_can_carry_3(self.r2): False,  # r2 cannot carry 3 containers
            
            self.robot_can_carry_1(self.r3): True,   # r3 can carry 1 container
            self.robot_can_carry_2(self.r3): True,   # r3 can carry 2 containers
            self.robot_can_carry_3(self.r3): True,   # r3 can carry 3 containers
            
            # Robot load tracking (all start empty)
            self.robot_has_container_1(self.r1): False,
            self.robot_has_container_2(self.r1): False,
            self.robot_has_container_3(self.r1): False,
            
            self.robot_has_container_1(self.r2): False,
            self.robot_has_container_2(self.r2): False,
            self.robot_has_container_3(self.r2): False,
            
            self.robot_has_container_1(self.r3): False,
            self.robot_has_container_2(self.r3): False,
            self.robot_has_container_3(self.r3): False,
            
            self.robot_free(self.r1): True,
            self.robot_free(self.r2): True,
            self.robot_free(self.r3): True,
            
            # Container piles with proper stacking
            # Pile p1: c1 at bottom, c2, c3, c4, c5 stacked on top
            self.container_in_pile(self.c1, self.p1): True,
            self.container_in_pile(self.c2, self.p1): True,
            self.container_in_pile(self.c3, self.p1): True,
            self.container_in_pile(self.c4, self.p1): True,
            self.container_in_pile(self.c5, self.p1): True,
            self.container_on_top_of_pile(self.c5, self.p1): True,  # c5 is on top
            self.container_under_in_pile(self.c4, self.c5, self.p1): True,  # c4 is under c5
            self.container_under_in_pile(self.c3, self.c4, self.p1): True,  # c3 is under c4
            self.container_under_in_pile(self.c2, self.c3, self.p1): True,  # c2 is under c3
            self.container_under_in_pile(self.c1, self.c2, self.p1): True,  # c1 is under c2
            
            # Pile locations - each dock has 1 pile
            self.pile_at_dock(self.p1, self.d1): True,
            self.pile_at_dock(self.p2, self.d2): True,
            self.pile_at_dock(self.p3, self.d3): True,
            
            # Static relations - adjacent docks (triangular network)
            self.adjacent(self.d1, self.d2): True,
            self.adjacent(self.d2, self.d1): True,
            self.adjacent(self.d2, self.d3): True,
            self.adjacent(self.d3, self.d2): True,
            self.adjacent(self.d3, self.d1): True,
            self.adjacent(self.d1, self.d3): True,
        }
    
    def _get_large_initial_state(self) -> Dict[Fluent, object]:
        """
        Return the initial state for large-scale scenario.
        
        Initial configuration:
        - r1 at d1, r2 at d3, r3 at d5
        - Complex distribution across 8 docks with 12 piles
        """
        return {
            # Robot locations
            self.robot_at(self.r1, self.d1): True,
            self.robot_at(self.r2, self.d3): True,
            self.robot_at(self.r3, self.d5): True,
            
            # Robot capacities (simplified boolean system) - Large scale: 2 robots cap 3, 1 robot cap 2
            self.robot_can_carry_1(self.r1): True,   # r1 can carry 1 container
            self.robot_can_carry_2(self.r1): True,   # r1 can carry 2 containers
            self.robot_can_carry_3(self.r1): True,   # r1 can carry 3 containers
            
            self.robot_can_carry_1(self.r2): True,   # r2 can carry 1 container
            self.robot_can_carry_2(self.r2): True,   # r2 can carry 2 containers
            self.robot_can_carry_3(self.r2): True,   # r2 can carry 3 containers
            
            self.robot_can_carry_1(self.r3): True,   # r3 can carry 1 container
            self.robot_can_carry_2(self.r3): True,   # r3 can carry 2 containers
            self.robot_can_carry_3(self.r3): False,  # r3 cannot carry 3 containers
            
            # Robot load tracking (all start empty)
            self.robot_has_container_1(self.r1): False,
            self.robot_has_container_2(self.r1): False,
            self.robot_has_container_3(self.r1): False,
            
            self.robot_has_container_1(self.r2): False,
            self.robot_has_container_2(self.r2): False,
            self.robot_has_container_3(self.r2): False,
            
            self.robot_has_container_1(self.r3): False,
            self.robot_has_container_2(self.r3): False,
            self.robot_has_container_3(self.r3): False,
            
            self.robot_free(self.r1): True,
            self.robot_free(self.r2): True,
            self.robot_free(self.r3): True,
            
            # Initialize robot slot tracking for all robots and all containers (all empty initially)
            # Robot r1 slots
            self.container_in_robot_slot_1(self.r1, self.c1): False,
            self.container_in_robot_slot_1(self.r1, self.c2): False,
            self.container_in_robot_slot_1(self.r1, self.c3): False,
            self.container_in_robot_slot_1(self.r1, self.c4): False,
            self.container_in_robot_slot_1(self.r1, self.c5): False,
            self.container_in_robot_slot_1(self.r1, self.c6): False,
            self.container_in_robot_slot_1(self.r1, self.c7): False,
            self.container_in_robot_slot_1(self.r1, self.c8): False,
            self.container_in_robot_slot_1(self.r1, self.c9): False,
            self.container_in_robot_slot_1(self.r1, self.c10): False,
            self.container_in_robot_slot_1(self.r1, self.c11): False,
            self.container_in_robot_slot_1(self.r1, self.c12): False,
            self.container_in_robot_slot_1(self.r1, self.c13): False,
            
            self.container_in_robot_slot_2(self.r1, self.c1): False,
            self.container_in_robot_slot_2(self.r1, self.c2): False,
            self.container_in_robot_slot_2(self.r1, self.c3): False,
            self.container_in_robot_slot_2(self.r1, self.c4): False,
            self.container_in_robot_slot_2(self.r1, self.c5): False,
            self.container_in_robot_slot_2(self.r1, self.c6): False,
            self.container_in_robot_slot_2(self.r1, self.c7): False,
            self.container_in_robot_slot_2(self.r1, self.c8): False,
            self.container_in_robot_slot_2(self.r1, self.c9): False,
            self.container_in_robot_slot_2(self.r1, self.c10): False,
            self.container_in_robot_slot_2(self.r1, self.c11): False,
            self.container_in_robot_slot_2(self.r1, self.c12): False,
            self.container_in_robot_slot_2(self.r1, self.c13): False,
            
            self.container_in_robot_slot_3(self.r1, self.c1): False,
            self.container_in_robot_slot_3(self.r1, self.c2): False,
            self.container_in_robot_slot_3(self.r1, self.c3): False,
            self.container_in_robot_slot_3(self.r1, self.c4): False,
            self.container_in_robot_slot_3(self.r1, self.c5): False,
            self.container_in_robot_slot_3(self.r1, self.c6): False,
            self.container_in_robot_slot_3(self.r1, self.c7): False,
            self.container_in_robot_slot_3(self.r1, self.c8): False,
            self.container_in_robot_slot_3(self.r1, self.c9): False,
            self.container_in_robot_slot_3(self.r1, self.c10): False,
            self.container_in_robot_slot_3(self.r1, self.c11): False,
            self.container_in_robot_slot_3(self.r1, self.c12): False,
            self.container_in_robot_slot_3(self.r1, self.c13): False,
            
            # Robot r2 slots
            self.container_in_robot_slot_1(self.r2, self.c1): False,
            self.container_in_robot_slot_1(self.r2, self.c2): False,
            self.container_in_robot_slot_1(self.r2, self.c3): False,
            self.container_in_robot_slot_1(self.r2, self.c4): False,
            self.container_in_robot_slot_1(self.r2, self.c5): False,
            self.container_in_robot_slot_1(self.r2, self.c6): False,
            self.container_in_robot_slot_1(self.r2, self.c7): False,
            self.container_in_robot_slot_1(self.r2, self.c8): False,
            self.container_in_robot_slot_1(self.r2, self.c9): False,
            self.container_in_robot_slot_1(self.r2, self.c10): False,
            self.container_in_robot_slot_1(self.r2, self.c11): False,
            self.container_in_robot_slot_1(self.r2, self.c12): False,
            self.container_in_robot_slot_1(self.r2, self.c13): False,
            
            self.container_in_robot_slot_2(self.r2, self.c1): False,
            self.container_in_robot_slot_2(self.r2, self.c2): False,
            self.container_in_robot_slot_2(self.r2, self.c3): False,
            self.container_in_robot_slot_2(self.r2, self.c4): False,
            self.container_in_robot_slot_2(self.r2, self.c5): False,
            self.container_in_robot_slot_2(self.r2, self.c6): False,
            self.container_in_robot_slot_2(self.r2, self.c7): False,
            self.container_in_robot_slot_2(self.r2, self.c8): False,
            self.container_in_robot_slot_2(self.r2, self.c9): False,
            self.container_in_robot_slot_2(self.r2, self.c10): False,
            self.container_in_robot_slot_2(self.r2, self.c11): False,
            self.container_in_robot_slot_2(self.r2, self.c12): False,
            self.container_in_robot_slot_2(self.r2, self.c13): False,
            
            self.container_in_robot_slot_3(self.r2, self.c1): False,
            self.container_in_robot_slot_3(self.r2, self.c2): False,
            self.container_in_robot_slot_3(self.r2, self.c3): False,
            self.container_in_robot_slot_3(self.r2, self.c4): False,
            self.container_in_robot_slot_3(self.r2, self.c5): False,
            self.container_in_robot_slot_3(self.r2, self.c6): False,
            self.container_in_robot_slot_3(self.r2, self.c7): False,
            self.container_in_robot_slot_3(self.r2, self.c8): False,
            self.container_in_robot_slot_3(self.r2, self.c9): False,
            self.container_in_robot_slot_3(self.r2, self.c10): False,
            self.container_in_robot_slot_3(self.r2, self.c11): False,
            self.container_in_robot_slot_3(self.r2, self.c12): False,
            self.container_in_robot_slot_3(self.r2, self.c13): False,
            
            # Robot r3 slots (capacity 2 robot - no slot 3)
            self.container_in_robot_slot_1(self.r3, self.c1): False,
            self.container_in_robot_slot_1(self.r3, self.c2): False,
            self.container_in_robot_slot_1(self.r3, self.c3): False,
            self.container_in_robot_slot_1(self.r3, self.c4): False,
            self.container_in_robot_slot_1(self.r3, self.c5): False,
            self.container_in_robot_slot_1(self.r3, self.c6): False,
            self.container_in_robot_slot_1(self.r3, self.c7): False,
            self.container_in_robot_slot_1(self.r3, self.c8): False,
            self.container_in_robot_slot_1(self.r3, self.c9): False,
            self.container_in_robot_slot_1(self.r3, self.c10): False,
            self.container_in_robot_slot_1(self.r3, self.c11): False,
            self.container_in_robot_slot_1(self.r3, self.c12): False,
            self.container_in_robot_slot_1(self.r3, self.c13): False,
            
            self.container_in_robot_slot_2(self.r3, self.c1): False,
            self.container_in_robot_slot_2(self.r3, self.c2): False,
            self.container_in_robot_slot_2(self.r3, self.c3): False,
            self.container_in_robot_slot_2(self.r3, self.c4): False,
            self.container_in_robot_slot_2(self.r3, self.c5): False,
            self.container_in_robot_slot_2(self.r3, self.c6): False,
            self.container_in_robot_slot_2(self.r3, self.c7): False,
            self.container_in_robot_slot_2(self.r3, self.c8): False,
            self.container_in_robot_slot_2(self.r3, self.c9): False,
            self.container_in_robot_slot_2(self.r3, self.c10): False,
            self.container_in_robot_slot_2(self.r3, self.c11): False,
            self.container_in_robot_slot_2(self.r3, self.c12): False,
            self.container_in_robot_slot_2(self.r3, self.c13): False,
            
            # r3 has no slot 3 (capacity 2 robot)
            self.container_in_robot_slot_3(self.r3, self.c1): False,
            self.container_in_robot_slot_3(self.r3, self.c2): False,
            self.container_in_robot_slot_3(self.r3, self.c3): False,
            self.container_in_robot_slot_3(self.r3, self.c4): False,
            self.container_in_robot_slot_3(self.r3, self.c5): False,
            self.container_in_robot_slot_3(self.r3, self.c6): False,
            self.container_in_robot_slot_3(self.r3, self.c7): False,
            self.container_in_robot_slot_3(self.r3, self.c8): False,
            self.container_in_robot_slot_3(self.r3, self.c9): False,
            self.container_in_robot_slot_3(self.r3, self.c10): False,
            self.container_in_robot_slot_3(self.r3, self.c11): False,
            self.container_in_robot_slot_3(self.r3, self.c12): False,
            self.container_in_robot_slot_3(self.r3, self.c13): False,
            
            # Pile-dock relationships - Central dock d1 has many piles, others have single piles
            # Dock 1: 8 piles (central dock)
            self.pile_at_dock(self.p1, self.d1): True,
            self.pile_at_dock(self.p2, self.d1): True,
            self.pile_at_dock(self.p3, self.d1): True,
            self.pile_at_dock(self.p4, self.d1): True,
            self.pile_at_dock(self.p5, self.d1): True,
            self.pile_at_dock(self.p6, self.d1): True,
            self.pile_at_dock(self.p7, self.d1): True,
            self.pile_at_dock(self.p8, self.d1): True,
            # Dock 2: 1 pile
            self.pile_at_dock(self.p9, self.d2): True,
            # Dock 3: 1 pile
            self.pile_at_dock(self.p10, self.d3): True,
            # Dock 4: 1 pile
            self.pile_at_dock(self.p11, self.d4): True,
            # Dock 5: 1 pile
            self.pile_at_dock(self.p12, self.d5): True,
            # Dock 6: 1 pile
            self.pile_at_dock(self.p13, self.d6): True,
            # Dock 7: 1 pile
            self.pile_at_dock(self.p14, self.d7): True,
            # Dock 8: 1 pile
            self.pile_at_dock(self.p15, self.d8): True,
            
            # Initial container distribution - ALL containers at central dock d1
            # Dock 1, Pile p1: c1, c2, c3
            self.container_in_pile(self.c1, self.p1): True,
            self.container_in_pile(self.c2, self.p1): True,
            self.container_in_pile(self.c3, self.p1): True,
            
            # Dock 1, Pile p2: c4, c5
            self.container_in_pile(self.c4, self.p2): True,
            self.container_in_pile(self.c5, self.p2): True,
            
            # Dock 1, Pile p3: c6, c7
            self.container_in_pile(self.c6, self.p3): True,
            self.container_in_pile(self.c7, self.p3): True,
            
            # Dock 1, Pile p4: c8
            self.container_in_pile(self.c8, self.p4): True,
            
            # Dock 1, Pile p5: c9, c10
            self.container_in_pile(self.c9, self.p5): True,
            self.container_in_pile(self.c10, self.p5): True,
            
            # Dock 1, Pile p6: c11
            self.container_in_pile(self.c11, self.p6): True,
            
            # Dock 1, Pile p7: c12
            self.container_in_pile(self.c12, self.p7): True,
            
            # Dock 1, Pile p8: c13
            self.container_in_pile(self.c13, self.p8): True,
            
            # Dock 5, Pile p9: empty (c14, c15 removed)
            # self.container_in_pile(self.c14, self.p9): True,  # Removed
            # self.container_in_pile(self.c15, self.p9): True,  # Removed
            
            # Complex network connectivity
            self.adjacent(self.d1, self.d2): True,
            self.adjacent(self.d1, self.d3): True,
            self.adjacent(self.d1, self.d5): True,
            self.adjacent(self.d2, self.d1): True,
            self.adjacent(self.d2, self.d3): True,
            self.adjacent(self.d2, self.d4): True,
            self.adjacent(self.d2, self.d6): True,
            self.adjacent(self.d3, self.d1): True,
            self.adjacent(self.d3, self.d2): True,
            self.adjacent(self.d3, self.d4): True,
            self.adjacent(self.d3, self.d5): True,
            self.adjacent(self.d4, self.d2): True,
            self.adjacent(self.d4, self.d3): True,
            self.adjacent(self.d4, self.d5): True,
            self.adjacent(self.d4, self.d6): True,
            self.adjacent(self.d5, self.d1): True,
            self.adjacent(self.d5, self.d3): True,
            self.adjacent(self.d5, self.d4): True,
            self.adjacent(self.d5, self.d6): True,
            self.adjacent(self.d5, self.d7): True,
            self.adjacent(self.d6, self.d2): True,
            self.adjacent(self.d6, self.d4): True,
            self.adjacent(self.d6, self.d5): True,
            self.adjacent(self.d6, self.d7): True,
            self.adjacent(self.d6, self.d8): True,
            self.adjacent(self.d7, self.d5): True,
            self.adjacent(self.d7, self.d6): True,
            self.adjacent(self.d7, self.d8): True,
            self.adjacent(self.d8, self.d6): True,
            self.adjacent(self.d8, self.d7): True,
        }
    
    def get_domain_objects(self) -> Dict[str, list]:
        """Return organized domain objects for problem creation."""
        if self.scale == "small":
            return {
                "robots": [self.r1, self.r2, self.r3],
                "docks": [self.d1, self.d2, self.d3],
                "containers": [self.c1, self.c2, self.c3, self.c4, self.c5],
                "piles": [self.p1, self.p2, self.p3],
                "all_objects": self.objects
            }
        elif self.scale == "large":
            return {
                "robots": [self.r1, self.r2, self.r3],
                "docks": [self.d1, self.d2, self.d3, self.d4, self.d5, self.d6, self.d7, self.d8],
                "containers": [self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8, 
                              self.c9, self.c10, self.c11, self.c12, self.c13],
                "piles": [self.p1, self.p2, self.p3, self.p4, self.p5, self.p6, self.p7, self.p8, 
                         self.p9, self.p10, self.p11, self.p12, self.p13, self.p14, self.p15],
                "all_objects": self.objects
            }
        else:
            raise ValueError(f"Unknown scale: {self.scale}")
