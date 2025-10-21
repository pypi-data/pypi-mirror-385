from __future__ import annotations
from ostk import astrodynamics as OpenSpaceToolkitAstrodynamicsPy
from ostk.astrodynamics import Access
from ostk.astrodynamics import Dynamics
from ostk.astrodynamics import EventCondition
from ostk.astrodynamics import GuidanceLaw
from ostk.astrodynamics import RootSolver
from ostk.astrodynamics import Trajectory
from ostk.astrodynamics import access
from ostk.astrodynamics import conjunction
from ostk.astrodynamics import converters
from ostk.astrodynamics import data
from ostk.astrodynamics import dynamics
from ostk.astrodynamics import eclipse
from ostk.astrodynamics import estimator
from ostk.astrodynamics import event_condition
import ostk.astrodynamics.flight
from ostk.astrodynamics import flight
from ostk.astrodynamics import guidance_law
from ostk.astrodynamics import pytrajectory
from ostk.astrodynamics import solver
from ostk.astrodynamics import trajectory
from ostk.astrodynamics.trajectory import State as PyState
from ostk import core as OpenSpaceToolkitCorePy
from ostk.core import container
from ostk.core import filesystem
from ostk.core import type
import ostk.core.type
from ostk import io as OpenSpaceToolkitIOPy
from ostk.io import URL
from ostk.io import ip
from ostk import mathematics as OpenSpaceToolkitMathematicsPy
from ostk.mathematics import curve_fitting
from ostk.mathematics import geometry
import ostk.mathematics.geometry.d3.transformation.rotation
from ostk.mathematics import object
from ostk import physics as OpenSpaceToolkitPhysicsPy
import ostk.physics
from ostk.physics import Environment
from ostk.physics import Manager
from ostk.physics import Unit
import ostk.physics.coordinate
from ostk.physics import coordinate
from ostk.physics import environment
from ostk.physics import time
import ostk.physics.time
from ostk.physics import unit
from ostk import simulation as OpenSpaceToolkitSimulationPy
import typing
from . import component
__all__ = ['Access', 'Component', 'ComponentConfiguration', 'ComponentHolder', 'Dynamics', 'Entity', 'Environment', 'EventCondition', 'GuidanceLaw', 'Manager', 'OpenSpaceToolkitAstrodynamicsPy', 'OpenSpaceToolkitCorePy', 'OpenSpaceToolkitIOPy', 'OpenSpaceToolkitMathematicsPy', 'OpenSpaceToolkitPhysicsPy', 'OpenSpaceToolkitSimulationPy', 'PyState', 'RootSolver', 'Satellite', 'SatelliteConfiguration', 'Simulator', 'SimulatorConfiguration', 'Trajectory', 'URL', 'Unit', 'access', 'component', 'conjunction', 'container', 'converters', 'coordinate', 'curve_fitting', 'data', 'dynamics', 'eclipse', 'environment', 'estimator', 'event_condition', 'filesystem', 'flight', 'geometry', 'guidance_law', 'ip', 'object', 'pytrajectory', 'solver', 'time', 'trajectory', 'type', 'unit']
class Component(Entity, ComponentHolder):
    """
    
                    Simulation component representing any part of a space system.
    
                    Component is the base class for all simulation objects like assemblies, sensors,
                    actuators, and controllers. It provides hierarchical structure, geometry attachment,
                    and reference frame management.
                
    """
    class Type:
        """
        
                        Enumeration of component types.
        
                        Defines the classification of components within the simulation.
                    
        
        Members:
        
          Undefined : 
                            Undefined type.
                        
        
          Assembly : 
                            Structural assembly or subsystem.
                        
        
          Controller : 
                            Control system component.
                        
        
          Sensor : 
                            Sensing or measurement device.
                        
        
          Actuator : 
                            Actuation device (thrusters, reaction wheels, etc.).
                        
        
          Other : 
                            Other component type.
                        
        """
        Actuator: typing.ClassVar[Component.Type]  # value = <Type.Actuator: 4>
        Assembly: typing.ClassVar[Component.Type]  # value = <Type.Assembly: 1>
        Controller: typing.ClassVar[Component.Type]  # value = <Type.Controller: 2>
        Other: typing.ClassVar[Component.Type]  # value = <Type.Other: 5>
        Sensor: typing.ClassVar[Component.Type]  # value = <Type.Sensor: 3>
        Undefined: typing.ClassVar[Component.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Component.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Assembly': <Type.Assembly: 1>, 'Controller': <Type.Controller: 2>, 'Sensor': <Type.Sensor: 3>, 'Actuator': <Type.Actuator: 4>, 'Other': <Type.Other: 5>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    @staticmethod
    def configure(configuration: typing.Any, parent_component: Component) -> Component:
        """
                            Create a component from configuration.
        
                            Args:
                                configuration (ComponentConfiguration): The component configuration.
                                parent_component (Component): The parent component.
        
                            Returns:
                                Component: The configured component.
        
                            Example:
                                >>> config = ComponentConfiguration(
                                ...     id="sensor-1",
                                ...     name="Star Tracker",
                                ...     type=Component.Type.Sensor
                                ... )
                                >>> component = Component.configure(config, parent)
        """
    @staticmethod
    def string_from_type(type: typing.Any) -> ostk.core.type.String:
        """
                            Convert component type to string.
        
                            Args:
                                type (Component.Type): The component type.
        
                            Returns:
                                str: String representation of the type.
        
                            Example:
                                >>> Component.string_from_type(Component.Type.Sensor)
                                'Sensor'
        """
    @staticmethod
    def undefined() -> Component:
        """
                            Create an undefined component.
        
                            Returns:
                                Component: An undefined component.
        
                            Example:
                                >>> component = Component.undefined()
                                >>> component.is_defined()
                                False
        """
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, type: typing.Any, tags: list[ostk.core.type.String], geometries: list[...], components: list[Component], parent: ComponentHolder, frame: ostk.physics.coordinate.Frame, simulator: Simulator) -> None:
        """
                            Create a Component instance.
        
                            Args:
                                id (str): The unique component identifier.
                                name (str): The component name.
                                type (Component.Type): The component type (Assembly, Sensor, etc.).
                                tags (list[str]): Array of classification tags.
                                geometries (list[Geometry]): Array of geometry objects.
                                components (list[Component]): Array of child components.
                                parent (ComponentHolder): The parent component holder.
                                frame (Frame): The component reference frame.
                                simulator (Simulator): Reference to the parent simulator.
        
                            Returns:
                                Component: The component instance.
        
                            Example:
                                >>> component = Component(
                                ...     id="sensor-1",
                                ...     name="Star Tracker",
                                ...     type=Component.Type.Sensor,
                                ...     tags=["attitude"],
                                ...     geometries=[],
                                ...     components=[],
                                ...     parent=satellite,
                                ...     frame=frame,
                                ...     simulator=sim
                                ... )
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_frame(self) -> ostk.physics.coordinate.Frame:
        """
                            Access the component's reference frame.
        
                            Returns:
                                Frame: The component frame.
        
                            Example:
                                >>> frame = component.access_frame()
                                >>> position = frame.get_origin_in(gcrf)
        """
    def access_geometry_with_name(self, name: ostk.core.type.String) -> ...:
        """
                            Access a geometry object by name.
        
                            Args:
                                name (str): The geometry name.
        
                            Returns:
                                Geometry: The geometry with the specified name.
        
                            Example:
                                >>> geometry = component.access_geometry_with_name("solar-panel")
        """
    def access_simulator(self) -> Simulator:
        """
                            Access the parent simulator.
        
                            Returns:
                                Simulator: The parent simulator.
        
                            Example:
                                >>> simulator = component.access_simulator()
                                >>> instant = simulator.get_instant()
        """
    def add_component(self, component: Component) -> None:
        """
                            Add a child component.
        
                            Args:
                                component (Component): The child component to add.
        
                            Example:
                                >>> component.add_component(subsensor)
        """
    def add_geometry(self, geometry: typing.Any) -> None:
        """
                            Add a geometry to the component.
        
                            Args:
                                geometry (Geometry): The geometry to add.
        
                            Example:
                                >>> component.add_geometry(panel_geometry)
        """
    def get_geometries(self) -> list[...]:
        """
                            Get all geometries attached to the component.
        
                            Returns:
                                list: Array of geometry objects.
        
                            Example:
                                >>> geometries = component.get_geometries()
                                >>> len(geometries)
                                2
        """
    def get_tags(self) -> list[ostk.core.type.String]:
        """
                            Get the component tags.
        
                            Returns:
                                list: Array of tag strings.
        
                            Example:
                                >>> tags = component.get_tags()
                                >>> "attitude" in tags
                                True
        """
    def get_type(self) -> ...:
        """
                            Get the component type.
        
                            Returns:
                                Component.Type: The component type.
        
                            Example:
                                >>> comp_type = component.get_type()
                                >>> comp_type == Component.Type.Sensor
                                True
        """
    def is_defined(self) -> bool:
        """
                            Check if the component is defined.
        
                            Returns:
                                bool: True if the component is defined, False otherwise.
        
                            Example:
                                >>> component.is_defined()
                                True
        """
    def set_parent(self, component: Component) -> None:
        """
                            Set the parent component.
        
                            Args:
                                component (Component): The parent component.
        
                            Example:
                                >>> component.set_parent(satellite)
        """
class ComponentConfiguration:
    """
    
                Configuration structure for creating components.
    
                ComponentConfiguration defines all parameters needed to construct a Component,
                including type, tags, orientation, geometries, and child components.
            
    """
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, type: Component.Type = ..., tags: list[ostk.core.type.String] = [], orientation: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion = [0.0, 0.0, 0.0, 1.0], geometries: list[...] = [], components: list[ComponentConfiguration] = []) -> None:
        """
                        Create a ComponentConfiguration instance.
        
                        Args:
                            id (str): The unique component identifier.
                            name (str): The component name.
                            type (Component.Type): The component type (optional).
                            tags (list[str]): Array of classification tags (optional).
                            orientation (Quaternion): Orientation relative to parent (optional).
                            geometries (list[GeometryConfiguration]): Array of geometry configurations (optional).
                            components (list[ComponentConfiguration]): Array of child component configurations (optional).
        
                        Returns:
                            ComponentConfiguration: The configuration instance.
        
                        Example:
                            >>> config = ComponentConfiguration(
                            ...     id="sensor-1",
                            ...     name="Star Tracker",
                            ...     type=Component.Type.Sensor,
                            ...     tags=["attitude", "primary"]
                            ... )
        """
class ComponentHolder:
    """
    
                Mixin class providing component management functionality for hierarchical component structures.
    
                ComponentHolder enables storage and retrieval of child components, supporting both flat
                and hierarchical component organization with path-based access.
            
    """
    def access_component_at(self, arg0: ostk.core.type.String) -> ...:
        """
                        Access a component at a given path.
        
                        Args:
                            path (str): The component path (e.g., "parent/child").
        
                        Returns:
                            Component: The component at the specified path.
        
                        Example:
                            >>> component = holder.access_component_at("payload/sensor-1")
        """
    def access_component_with_id(self, arg0: ostk.core.type.String) -> ...:
        """
                        Access a component by its ID.
        
                        Args:
                            id (str): The component ID.
        
                        Returns:
                            Component: The component with the specified ID.
        
                        Example:
                            >>> component = holder.access_component_with_id("sensor-1")
        """
    def access_component_with_name(self, arg0: ostk.core.type.String) -> ...:
        """
                        Access a component by its name.
        
                        Args:
                            name (str): The component name.
        
                        Returns:
                            Component: The component with the specified name.
        
                        Example:
                            >>> component = holder.access_component_with_name("Main Sensor")
        """
    def access_components(self) -> list[...]:
        """
                        Access all child components.
        
                        Returns:
                            list: Array of all child components.
        
                        Example:
                            >>> components = holder.access_components()
                            >>> len(components)
                            3
        """
    def access_components_with_tag(self, arg0: ostk.core.type.String) -> list[...]:
        """
                        Access all components with a specific tag.
        
                        Args:
                            tag (str): The tag to filter by.
        
                        Returns:
                            list: Array of components with the specified tag.
        
                        Example:
                            >>> sensors = holder.access_components_with_tag("sensor")
                            >>> len(sensors)
                            2
        """
    def add_component(self, arg0: typing.Any) -> None:
        """
                        Add a child component.
        
                        Args:
                            component (Component): The component to add.
        
                        Example:
                            >>> holder.add_component(sensor)
        """
    def has_component_at(self, arg0: ostk.core.type.String) -> bool:
        """
                        Check if a component exists at the given path.
        
                        Args:
                            path (str): The component path (e.g., "parent/child").
        
                        Returns:
                            bool: True if a component exists at the path, False otherwise.
        
                        Example:
                            >>> holder.has_component_at("payload/sensor-1")
                            True
        """
    def has_component_with_id(self, arg0: ostk.core.type.String) -> bool:
        """
                        Check if a component with the given ID exists.
        
                        Args:
                            id (str): The component ID to search for.
        
                        Returns:
                            bool: True if a component with the ID exists, False otherwise.
        
                        Example:
                            >>> holder.has_component_with_id("sensor-1")
                            True
        """
    def has_component_with_name(self, arg0: ostk.core.type.String) -> bool:
        """
                        Check if a component with the given name exists.
        
                        Args:
                            name (str): The component name to search for.
        
                        Returns:
                            bool: True if a component with the name exists, False otherwise.
        
                        Example:
                            >>> holder.has_component_with_name("Main Sensor")
                            True
        """
class Entity:
    """
    
                    Base class representing a simulation entity with ID and name properties.
    
                    An Entity is the fundamental building block in the simulation, providing identification
                    and naming capabilities.
                
    """
    @staticmethod
    def undefined() -> Entity:
        """
                            Create an undefined entity.
        
                            Returns:
                                Entity: An undefined entity.
        
                            Example:
                                >>> entity = Entity.undefined()
                                >>> entity.is_defined()
                                False
        """
    def get_id(self) -> ostk.core.type.String:
        """
                            Get the unique identifier of the entity.
        
                            Returns:
                                str: The unique identifier.
        
                            Example:
                                >>> entity.get_id()
                                'my-entity'
        """
    def get_name(self) -> ostk.core.type.String:
        """
                            Get the name of the entity.
        
                            Returns:
                                str: The entity name.
        
                            Example:
                                >>> entity.get_name()
                                'My Entity'
        """
    def is_defined(self) -> bool:
        """
                            Check if the entity is defined.
        
                            Returns:
                                bool: True if the entity is defined, False otherwise.
        
                            Example:
                                >>> entity.is_defined()
                                True
        """
class Satellite(Component):
    """
    
                Satellite component representing a spacecraft entity.
    
                A Satellite extends Component with an astrodynamics Profile that defines its
                trajectory and state information over time.
            
    """
    @staticmethod
    def configure(configuration: typing.Any, simulator: Simulator = None) -> Satellite:
        """
                        Create a satellite from configuration.
        
                        Args:
                            configuration (SatelliteConfiguration): The satellite configuration.
                            simulator (Simulator): Optional reference to the parent simulator.
        
                        Returns:
                            Satellite: The configured satellite.
        
                        Example:
                            >>> config = SatelliteConfiguration(
                            ...     id="sat-1",
                            ...     name="My Satellite",
                            ...     profile=profile
                            ... )
                            >>> satellite = Satellite.configure(config, simulator)
        """
    @staticmethod
    def undefined() -> Satellite:
        """
                        Create an undefined satellite.
        
                        Returns:
                            Satellite: An undefined satellite.
        
                        Example:
                            >>> satellite = Satellite.undefined()
                            >>> satellite.is_defined()
                            False
        """
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, tags: list[ostk.core.type.String], geometries: list[component.Geometry], components: list[Component], frame: ostk.physics.coordinate.Frame, profile: ostk.astrodynamics.flight.Profile, simulator: Simulator) -> None:
        """
                        Create a Satellite instance.
        
                        Args:
                            id (str): The unique satellite identifier.
                            name (str): The satellite name.
                            tags (list[str]): Array of classification tags.
                            geometries (list[Geometry]): Array of geometry objects.
                            components (list[Component]): Array of child components.
                            frame (Frame): The satellite reference frame.
                            profile (Profile): The astrodynamics profile (trajectory).
                            simulator (Simulator): Reference to the parent simulator.
        
                        Returns:
                            Satellite: The satellite instance.
        
                        Example:
                            >>> satellite = Satellite(
                            ...     id="sat-1",
                            ...     name="My Satellite",
                            ...     tags=["LEO"],
                            ...     geometries=[],
                            ...     components=[],
                            ...     frame=frame,
                            ...     profile=profile,
                            ...     simulator=sim
                            ... )
        """
    def access_profile(self) -> ostk.astrodynamics.flight.Profile:
        """
                        Access the satellite's astrodynamics profile.
        
                        Returns:
                            Profile: The satellite trajectory profile.
        
                        Example:
                            >>> profile = satellite.access_profile()
                            >>> state = profile.get_state_at(instant)
        """
    def is_defined(self) -> bool:
        """
                        Check if the satellite is defined.
        
                        Returns:
                            bool: True if the satellite is defined, False otherwise.
        
                        Example:
                            >>> satellite.is_defined()
                            True
        """
class SatelliteConfiguration:
    """
    
                Configuration structure for creating satellites.
    
                SatelliteConfiguration defines all parameters needed to construct a Satellite,
                including its profile, components, tags, and geometries.
            
    """
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, profile: ostk.astrodynamics.flight.Profile, components: list[ComponentConfiguration] = [], tags: list[ostk.core.type.String] = [], geometries: list[component.GeometryConfiguration] = []) -> None:
        """
                        Create a SatelliteConfiguration instance.
        
                        Args:
                            id (str): The unique satellite identifier.
                            name (str): The satellite name.
                            profile (Profile): The astrodynamics profile (trajectory).
                            components (list[ComponentConfiguration]): Array of component configurations (optional).
                            tags (list[str]): Array of classification tags (optional).
                            geometries (list[GeometryConfiguration]): Array of geometry configurations (optional).
        
                        Returns:
                            SatelliteConfiguration: The configuration instance.
        
                        Example:
                            >>> config = SatelliteConfiguration(
                            ...     id="sat-1",
                            ...     name="My Satellite",
                            ...     profile=profile,
                            ...     tags=["LEO", "science"]
                            ... )
        """
class Simulator:
    """
    
                Main simulation orchestrator managing satellites and environment.
    
                The Simulator coordinates the overall simulation, managing a collection of satellites,
                the physics environment, and the simulation time. It provides methods to step forward
                in time and manage satellite lifecycles.
            
    """
    @staticmethod
    def configure(configuration: typing.Any) -> Simulator:
        """
                        Create a simulator from configuration.
        
                        Args:
                            configuration (SimulatorConfiguration): The simulator configuration.
        
                        Returns:
                            Simulator: The configured simulator.
        
                        Example:
                            >>> config = SimulatorConfiguration(
                            ...     environment=environment,
                            ...     satellites=[sat_config1, sat_config2]
                            ... )
                            >>> simulator = Simulator.configure(config)
        """
    @staticmethod
    def undefined() -> Simulator:
        """
                        Create an undefined simulator.
        
                        Returns:
                            Simulator: An undefined simulator.
        
                        Example:
                            >>> simulator = Simulator.undefined()
                            >>> simulator.is_defined()
                            False
        """
    def __init__(self, environment: ostk.physics.Environment, satellites: list[...]) -> None:
        """
                        Create a Simulator instance.
        
                        Args:
                            environment (Environment): The physics environment (celestial bodies, gravity, etc.).
                            satellites (list[Satellite]): Array of satellite objects to simulate.
        
                        Returns:
                            Simulator: The simulator instance.
        
                        Example:
                            >>> simulator = Simulator(
                            ...     environment=environment,
                            ...     satellites=[satellite1, satellite2]
                            ... )
        """
    def access_environment(self) -> ostk.physics.Environment:
        """
                        Access the physics environment.
        
                        Returns:
                            Environment: The simulation environment.
        
                        Example:
                            >>> environment = simulator.access_environment()
                            >>> earth = environment.access_celestial_object_with_name("Earth")
        """
    def access_satellite_map(self) -> dict[ostk.core.type.String, ...]:
        """
                        Access the satellite map (name to satellite mapping).
        
                        Returns:
                            dict: Map of satellite names to satellite objects.
        
                        Example:
                            >>> satellite_map = simulator.access_satellite_map()
                            >>> len(satellite_map)
                            2
        """
    def access_satellite_with_name(self, name: ostk.core.type.String) -> ...:
        """
                        Access a satellite by name.
        
                        Args:
                            name (str): The satellite name.
        
                        Returns:
                            Satellite: The satellite with the specified name.
        
                        Example:
                            >>> satellite = simulator.access_satellite_with_name("sat-1")
        """
    def add_satellite(self, satellite: typing.Any) -> None:
        """
                        Add a satellite to the simulation.
        
                        Args:
                            satellite (Satellite): The satellite to add.
        
                        Example:
                            >>> simulator.add_satellite(new_satellite)
        """
    def clear_satellites(self) -> None:
        """
                        Remove all satellites from the simulation.
        
                        Example:
                            >>> simulator.clear_satellites()
                            >>> len(simulator.access_satellite_map())
                            0
        """
    def get_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the current simulation time.
        
                        Returns:
                            Instant: The current simulation instant.
        
                        Example:
                            >>> instant = simulator.get_instant()
                            >>> print(instant)
        """
    def has_satellite_with_name(self, name: ostk.core.type.String) -> bool:
        """
                        Check if a satellite with the given name exists.
        
                        Args:
                            name (str): The satellite name to search for.
        
                        Returns:
                            bool: True if a satellite with the name exists, False otherwise.
        
                        Example:
                            >>> simulator.has_satellite_with_name("sat-1")
                            True
        """
    def is_defined(self) -> bool:
        """
                        Check if the simulator is defined.
        
                        Returns:
                            bool: True if the simulator is defined, False otherwise.
        
                        Example:
                            >>> simulator.is_defined()
                            True
        """
    def remove_satellite_with_name(self, name: ostk.core.type.String) -> None:
        """
                        Remove a satellite from the simulation by name.
        
                        Args:
                            name (str): The satellite name.
        
                        Example:
                            >>> simulator.remove_satellite_with_name("sat-1")
        """
    def set_instant(self, instant: ostk.physics.time.Instant) -> None:
        """
                        Set the current simulation time.
        
                        Args:
                            instant (Instant): The new simulation instant.
        
                        Example:
                            >>> simulator.set_instant(start_instant)
        """
    def step_forward(self, duration: ostk.physics.time.Duration) -> None:
        """
                        Step the simulation forward by a duration.
        
                        Args:
                            duration (Duration): The time step duration.
        
                        Example:
                            >>> from ostk.physics.time import Duration
                            >>> simulator.step_forward(Duration.seconds(60.0))
        """
class SimulatorConfiguration:
    """
    
                Configuration structure for creating simulators.
    
                SimulatorConfiguration defines the environment and satellite configurations
                needed to construct a Simulator.
            
    """
    def __init__(self, environment: ostk.physics.Environment, satellites: list[...] = []) -> None:
        """
                        Create a SimulatorConfiguration instance.
        
                        Args:
                            environment (Environment): The physics environment.
                            satellites (list[SatelliteConfiguration]): Array of satellite configurations (optional).
        
                        Returns:
                            SimulatorConfiguration: The configuration instance.
        
                        Example:
                            >>> config = SimulatorConfiguration(
                            ...     environment=environment,
                            ...     satellites=[sat_config1, sat_config2]
                            ... )
        """
