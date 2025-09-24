"""
Domain definition for Example 2.3 - Logistics domain with robots, docks, containers, and piles.
Based on Figure 2.3 from "Automated Planning and Acting" by Ghallab, Nau, and Traverso.
"""

from unified_planning.shortcuts import *
from typing import Dict, Set, Tuple


class LogisticsDomain:
    """Logistics domain with robots, docks, containers, and piles."""
    
    def __init__(self, scale: str = "small", auto_objects: bool = False):
        """
        Initialize logistics domain.
        
        Args:
            scale: "small" for basic 3-dock scenario, "large" for 8-dock scenario
            auto_objects: if True, create default objects for the chosen scale; if False, do not create any objects
        """
        self.scale = scale
        self._auto_objects = auto_objects
        self._setup_types()
        if self._auto_objects:
            self._setup_objects()
        else:
            # When objects are not auto-created, keep an empty objects list for compatibility
            self.objects = []
        self._setup_fluents()
        self._setup_static_relations()

    def assign_objects(self, objects_dict: Dict[str, list]) -> None:
        """Assign externally-created objects for demos.
        
        Expected keys: 'robots', 'docks', 'containers', 'piles', 'all_objects'.
        Only the presence of 'containers' is required by current actions.
        """
        if not isinstance(objects_dict, dict):
            raise ValueError("assign_objects expects a dictionary of object lists")
        self._assigned_objects = objects_dict
        # Keep a flat list for compatibility where 'objects' is referenced
        self.objects = objects_dict.get("all_objects", [])
    
    def _setup_types(self):
        """Define the types for the domain."""
        # Basic types
        self.Robot = UserType("Robot")
        self.Dock = UserType("Dock") 
        self.Container = UserType("Container")
        self.Pile = UserType("Pile")
    
    def _setup_objects(self):
        """Object creation removed. Demos should create their own objects and use assign_objects()."""
        raise NotImplementedError("Object creation removed. Use assign_objects() in your demo to provide objects.")
    
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
        
        # Container weight system (boolean weight levels approach)
        self.container_weight_2 = Fluent("container_weight_2", BoolType(), container=self.Container)
        self.container_weight_4 = Fluent("container_weight_4", BoolType(), container=self.Container)
        self.container_weight_6 = Fluent("container_weight_6", BoolType(), container=self.Container)
        
        # Robot weight level system (boolean approach for numerical weights)
        self.robot_weight_0 = Fluent("robot_weight_0", BoolType(), robot=self.Robot)
        self.robot_weight_2 = Fluent("robot_weight_2", BoolType(), robot=self.Robot)
        self.robot_weight_4 = Fluent("robot_weight_4", BoolType(), robot=self.Robot)
        self.robot_weight_6 = Fluent("robot_weight_6", BoolType(), robot=self.Robot)
        self.robot_weight_8 = Fluent("robot_weight_8", BoolType(), robot=self.Robot)
        self.robot_weight_10 = Fluent("robot_weight_10", BoolType(), robot=self.Robot)
        
        # Robot capacity levels
        self.robot_capacity_5 = Fluent("robot_capacity_5", BoolType(), robot=self.Robot)
        self.robot_capacity_6 = Fluent("robot_capacity_6", BoolType(), robot=self.Robot)
        self.robot_capacity_8 = Fluent("robot_capacity_8", BoolType(), robot=self.Robot)
        self.robot_capacity_10 = Fluent("robot_capacity_10", BoolType(), robot=self.Robot)
        
        # Pile state
        self.pile_at_dock = Fluent("pile_at_dock", BoolType(), pile=self.Pile, dock=self.Dock)
        
        # All fluents list
        self.fluents = [
            self.robot_at, self.robot_carrying, self.robot_free,
            self.robot_can_carry_1, self.robot_can_carry_2, self.robot_can_carry_3,
            self.robot_has_container_1, self.robot_has_container_2, self.robot_has_container_3,
            self.container_in_robot_slot_1, self.container_in_robot_slot_2, self.container_in_robot_slot_3,
            self.container_in_pile, self.container_on_top_of_pile, self.container_under_in_pile,
            self.container_weight_2, self.container_weight_4, self.container_weight_6,
            self.robot_weight_0, self.robot_weight_2, self.robot_weight_4, self.robot_weight_6, self.robot_weight_8, self.robot_weight_10,
            self.robot_capacity_5, self.robot_capacity_6, self.robot_capacity_8, self.robot_capacity_10,
            self.pile_at_dock
        ]
    
    def _setup_static_relations(self):
        """Define static relations (rigid properties)."""
        # Adjacent docks
        self.adjacent = Fluent("adjacent", BoolType(), dock1=self.Dock, dock2=self.Dock)
        
        # All static fluents
        self.static_fluents = [self.adjacent]
    
    def get_domain_objects(self) -> Dict[str, list]:
        """Return organized domain objects for problem creation."""
        if hasattr(self, "_assigned_objects") and self._assigned_objects:
            return self._assigned_objects
        raise ValueError("No domain objects available. Call assign_objects() in your demo to provide objects.")
