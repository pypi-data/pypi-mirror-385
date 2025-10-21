from __future__ import annotations
import ostk.core.type
import ostk.mathematics.geometry.d3.object
import ostk.physics.coordinate
import ostk.physics.environment.object
import ostk.simulation
import typing
__all__ = ['Geometry', 'GeometryConfiguration', 'State']
class Geometry:
    """
    
                Physical geometry attached to a component.
    
                Geometry represents the physical shape and structure of a component, enabling
                spatial operations like intersection and containment checks with other geometries
                or celestial objects.
            
    """
    @staticmethod
    def configure(configuration: typing.Any, component: ostk.simulation.Component) -> Geometry:
        """
                        Create a geometry from configuration.
        
                        Args:
                            configuration (GeometryConfiguration): The geometry configuration.
                            component (Component): The parent component.
        
                        Returns:
                            Geometry: The configured geometry.
        
                        Example:
                            >>> config = GeometryConfiguration(
                            ...     name="solar-panel",
                            ...     composite=panel_composite
                            ... )
                            >>> geometry = Geometry.configure(config, component)
        """
    @staticmethod
    def undefined() -> Geometry:
        """
                        Create an undefined geometry.
        
                        Returns:
                            Geometry: An undefined geometry.
        
                        Example:
                            >>> geometry = Geometry.undefined()
                            >>> geometry.is_defined()
                            False
        """
    def __init__(self, name: ostk.core.type.String, composite: ostk.mathematics.geometry.d3.object.Composite, component: ostk.simulation.Component) -> None:
        """
                        Create a Geometry instance.
        
                        Args:
                            name (str): The geometry name.
                            composite (Composite): The 3D composite geometry object.
                            component (Component): The parent component.
        
                        Returns:
                            Geometry: The geometry instance.
        
                        Example:
                            >>> geometry = Geometry(
                            ...     name="solar-panel",
                            ...     composite=panel_composite,
                            ...     component=satellite
                            ... )
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_component(self) -> ostk.simulation.Component:
        """
                        Access the parent component.
        
                        Returns:
                            Component: The parent component.
        
                        Example:
                            >>> component = geometry.access_component()
        """
    def access_composite(self) -> ostk.mathematics.geometry.d3.object.Composite:
        """
                        Access the underlying composite geometry.
        
                        Returns:
                            Composite: The 3D composite geometry object.
        
                        Example:
                            >>> composite = geometry.access_composite()
        """
    def access_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Access the geometry's reference frame.
        
                        Returns:
                            Frame: The geometry frame.
        
                        Example:
                            >>> frame = geometry.access_frame()
        """
    @typing.overload
    def contains(self, geometry: ostk.physics.environment.object.Geometry) -> bool:
        """
                        Check if this geometry contains another geometry.
        
                        Args:
                            geometry (Geometry): The other geometry.
        
                        Returns:
                            bool: True if this geometry contains the other, False otherwise.
        
                        Example:
                            >>> geometry.contains(small_geometry)
                            True
        """
    @typing.overload
    def contains(self, celestial: ostk.physics.environment.object.Celestial) -> bool:
        """
                        Check if this geometry contains a celestial object.
        
                        Args:
                            celestial (Celestial): The celestial object.
        
                        Returns:
                            bool: True if this geometry contains the celestial object, False otherwise.
        
                        Example:
                            >>> geometry.contains(moon)
                            False
        """
    def get_geometry_in(self, frame: ostk.physics.coordinate.Frame) -> ostk.physics.environment.object.Geometry:
        """
                        Get the geometry expressed in a different reference frame.
        
                        Args:
                            frame (Frame): The target reference frame.
        
                        Returns:
                            Geometry: The geometry in the target frame.
        
                        Example:
                            >>> geometry_in_gcrf = geometry.get_geometry_in(gcrf)
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the geometry name.
        
                        Returns:
                            str: The geometry name.
        
                        Example:
                            >>> name = geometry.get_name()
                            >>> name
                            'solar-panel'
        """
    @typing.overload
    def intersection_with(self, geometry: ostk.physics.environment.object.Geometry) -> ostk.physics.environment.object.Geometry:
        """
                        Compute the intersection of this geometry with another geometry.
        
                        Args:
                            geometry (Geometry): The other geometry.
        
                        Returns:
                            Geometry: The intersection geometry.
        
                        Example:
                            >>> intersection = geometry.intersection_with(other_geometry)
        """
    @typing.overload
    def intersection_with(self, celestial_object: ostk.physics.environment.object.Celestial) -> ostk.physics.environment.object.Geometry:
        """
                        Compute the intersection of this geometry with a celestial object.
        
                        Args:
                            celestial_object (Celestial): The celestial object.
        
                        Returns:
                            Geometry: The intersection geometry.
        
                        Example:
                            >>> intersection = geometry.intersection_with(earth)
        """
    @typing.overload
    def intersects(self, geometry: ostk.physics.environment.object.Geometry) -> bool:
        """
                        Check if this geometry intersects another geometry.
        
                        Args:
                            geometry (Geometry): The other geometry.
        
                        Returns:
                            bool: True if geometries intersect, False otherwise.
        
                        Example:
                            >>> geometry.intersects(other_geometry)
                            False
        """
    @typing.overload
    def intersects(self, celestial_object: ostk.physics.environment.object.Celestial) -> bool:
        """
                        Check if this geometry intersects a celestial object.
        
                        Args:
                            celestial_object (Celestial): The celestial object (planet, moon, etc.).
        
                        Returns:
                            bool: True if geometry intersects the celestial object, False otherwise.
        
                        Example:
                            >>> geometry.intersects(earth)
                            False
        """
    def is_defined(self) -> bool:
        """
                        Check if the geometry is defined.
        
                        Returns:
                            bool: True if the geometry is defined, False otherwise.
        
                        Example:
                            >>> geometry.is_defined()
                            True
        """
class GeometryConfiguration:
    """
    
                Configuration structure for creating geometries.
    
                GeometryConfiguration defines the name and composite geometry needed to
                construct a Geometry object.
            
    """
    def __init__(self, name: ostk.core.type.String, composite: ostk.mathematics.geometry.d3.object.Composite) -> None:
        """
                        Create a GeometryConfiguration instance.
        
                        Args:
                            name (str): The geometry name.
                            composite (Composite): The 3D composite geometry object.
        
                        Returns:
                            GeometryConfiguration: The configuration instance.
        
                        Example:
                            >>> config = GeometryConfiguration(
                            ...     name="solar-panel",
                            ...     composite=panel_composite
                            ... )
        """
class State:
    """
    
                Component state representing operational status.
    
                State tracks the operational condition of a component, from undefined to various
                operational states like disabled, idle, busy, or error.
            
    """
    class Status:
        """
        
                    Enumeration of component operational states.
        
                    Defines the possible operational states a component can be in.
                
        
        Members:
        
          Undefined : 
                        Undefined status.
                    
        
          Disabled : 
                        Component is disabled.
                    
        
          Idle : 
                        Component is idle and ready.
                    
        
          Busy : 
                        Component is actively processing.
                    
        
          Error : 
                        Component is in error state.
                    
        """
        Busy: typing.ClassVar[State.Status]  # value = <Status.Busy: 3>
        Disabled: typing.ClassVar[State.Status]  # value = <Status.Disabled: 1>
        Error: typing.ClassVar[State.Status]  # value = <Status.Error: 4>
        Idle: typing.ClassVar[State.Status]  # value = <Status.Idle: 2>
        Undefined: typing.ClassVar[State.Status]  # value = <Status.Undefined: 0>
        __members__: typing.ClassVar[dict[str, State.Status]]  # value = {'Undefined': <Status.Undefined: 0>, 'Disabled': <Status.Disabled: 1>, 'Idle': <Status.Idle: 2>, 'Busy': <Status.Busy: 3>, 'Error': <Status.Error: 4>}
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
    def undefined() -> State:
        """
                        Create an undefined state.
        
                        Returns:
                            State: An undefined state.
        
                        Example:
                            >>> state = State.undefined()
                            >>> state.is_defined()
                            False
        """
    def __init__(self, status: typing.Any) -> None:
        """
                        Create a State instance.
        
                        Args:
                            status (State.Status): The operational status.
        
                        Returns:
                            State: The state instance.
        
                        Example:
                            >>> state = State(State.Status.Idle)
        """
    def get_status(self) -> ...:
        """
                        Get the operational status.
        
                        Returns:
                            State.Status: The current status.
        
                        Example:
                            >>> status = state.get_status()
                            >>> status == State.Status.Idle
                            True
        """
    def is_defined(self) -> bool:
        """
                        Check if the state is defined.
        
                        Returns:
                            bool: True if the state is defined, False otherwise.
        
                        Example:
                            >>> state.is_defined()
                            True
        """
