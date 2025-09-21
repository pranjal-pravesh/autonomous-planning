"""
Domain definition for Example 2.3 - Logistics domain with robots, docks, containers, and piles.
Based on Figure 2.3 from "Automated Planning and Acting" by Ghallab, Nau, and Traverso.
"""

from unified_planning.shortcuts import *
from typing import Dict, Set, Tuple


class LogisticsDomain:
    """Logistics domain with robots, docks, containers, and piles."""
    
    def __init__(self):
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
        # Robots
        self.r1 = Object("r1", self.Robot)
        self.r2 = Object("r2", self.Robot)
        
        # Docks
        self.d1 = Object("d1", self.Dock)
        self.d2 = Object("d2", self.Dock)
        self.d3 = Object("d3", self.Dock)
        
        # Containers
        self.c1 = Object("c1", self.Container)
        self.c2 = Object("c2", self.Container)
        self.c3 = Object("c3", self.Container)
        
        # Piles
        self.p1 = Object("p1", self.Pile)
        self.p2 = Object("p2", self.Pile)
        self.p3 = Object("p3", self.Pile)
        
        # Special objects
        self.nil_container = Object("nil_container", self.Container)
        self.nil_pile = Object("nil_pile", self.Pile)
        
        # All objects list
        self.objects = [
            self.r1, self.r2,
            self.d1, self.d2, self.d3,
            self.c1, self.c2, self.c3,
            self.p1, self.p2, self.p3,
            self.nil_container, self.nil_pile
        ]
    
    def _setup_fluents(self):
        """Define the state variables (fluents) for the domain."""
        # Robot state
        self.cargo = Fluent("cargo", self.Container, robot=self.Robot)
        self.loc = Fluent("loc", self.Dock, robot=self.Robot)
        
        # Dock state
        self.occupied = Fluent("occupied", BoolType(), dock=self.Dock)
        
        # Container state
        self.pos = Fluent("pos", self.Container, container=self.Container)
        self.pile = Fluent("pile", self.Pile, container=self.Container)
        
        # Pile state
        self.top = Fluent("top", self.Container, pile=self.Pile)
        
        # All fluents list
        self.fluents = [
            self.cargo, self.loc, self.occupied,
            self.pos, self.pile, self.top
        ]
    
    def _setup_static_relations(self):
        """Define static relations (rigid properties)."""
        # Adjacent docks (triangular network: d1-d2-d3-d1)
        self.adjacent = Fluent("adjacent", BoolType(), dock1=self.Dock, dock2=self.Dock)
        
        # Pile locations
        self.at = Fluent("at", BoolType(), pile=self.Pile, dock=self.Dock)
        
        # All static fluents
        self.static_fluents = [self.adjacent, self.at]
    
    def get_initial_state(self) -> Dict[Fluent, object]:
        """
        Return the initial state from Figure 2.3 (state s0).
        
        Initial configuration:
        - r1 at d1, r2 at d2
        - d1 occupied, d2 occupied, d3 free
        - p1 at d1 with c1 on top of c2
        - p2 at d2 with c3
        - p3 at d2, empty
        """
        return {
            # Robot cargo (both empty initially)
            self.cargo(self.r1): self.nil_container,
            self.cargo(self.r2): self.nil_container,
            
            # Robot locations
            self.loc(self.r1): self.d1,
            self.loc(self.r2): self.d2,
            
            # Dock occupancy
            self.occupied(self.d1): True,
            self.occupied(self.d2): True,
            self.occupied(self.d3): False,
            
            # Container positions
            self.pos(self.c1): self.c2,  # c1 is on top of c2
            self.pos(self.c2): self.nil_container,  # c2 is at bottom of pile
            self.pos(self.c3): self.nil_container,  # c3 is at bottom of its pile
            
            # Container piles
            self.pile(self.c1): self.p1,
            self.pile(self.c2): self.p1,
            self.pile(self.c3): self.p2,
            
            # Pile tops
            self.top(self.p1): self.c1,  # c1 is on top of p1
            self.top(self.p2): self.c3,  # c3 is on top of p2
            self.top(self.p3): self.nil_container,  # p3 is empty
            
            # Static relations - adjacent docks (triangular network)
            self.adjacent(self.d1, self.d2): True,
            self.adjacent(self.d2, self.d1): True,
            self.adjacent(self.d2, self.d3): True,
            self.adjacent(self.d3, self.d2): True,
            self.adjacent(self.d3, self.d1): True,
            self.adjacent(self.d1, self.d3): True,
            
            # Static relations - pile locations
            self.at(self.p1, self.d1): True,
            self.at(self.p2, self.d2): True,
            self.at(self.p3, self.d2): True,
        }
    
    def get_domain_objects(self) -> Dict[str, list]:
        """Return organized domain objects for problem creation."""
        return {
            "robots": [self.r1, self.r2],
            "docks": [self.d1, self.d2, self.d3],
            "containers": [self.c1, self.c2, self.c3],
            "piles": [self.p1, self.p2, self.p3],
            "all_objects": self.objects
        }
