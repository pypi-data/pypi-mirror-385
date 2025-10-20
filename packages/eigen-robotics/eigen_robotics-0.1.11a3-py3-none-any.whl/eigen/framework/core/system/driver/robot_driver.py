"""! Robot driver base classes.

This module defines abstract interfaces for robot drivers used by the EIGEN
framework. Drivers act as the glue between high level robot components and the
underlying backend (simulation or real hardware).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from eigen.core.system.driver.component_driver import ComponentDriver


class ControlType(Enum):
    """! Supported control modes for robot joints."""

    POSITION = "position"
    VELOCITY = "velocity"
    TORQUE = "torque"
    FIXED = "fixed"


class RobotDriver(ComponentDriver):
    """! Abstract driver interface for robots.

    This class defines the common API that concrete robot drivers must
    implement in order to communicate joint states and control commands to a
    backend system.
    """

    def __init__(
        self,
        component_name: str,
        component_config: dict[str, Any] = None,
        sim: bool = True,
    ) -> None:
        """! Construct the driver.

        @param component_name Name of the robot component.
        @param component_config Configuration dictionary or path.
        @param sim True if the driver interfaces with a simulator.
        """

        super().__init__(
            component_name=component_name,
            component_config=component_config,
            sim=sim,
        )

    #####################
    ##    get infos    ##
    #####################

    @abstractmethod
    def check_torque_status(self) -> bool:
        """! Check whether torque control is enabled on the robot.

        @return ``True`` if torque control is active, ``False`` otherwise.
        """

        pass

    @abstractmethod
    def pass_joint_positions(self, joints: list[str]) -> dict[str, float]:
        """! Retrieve the current joint positions.

        @param joints Names of the queried joints.
        @return dictionary mapping each joint name to its position in radians.
        """

        pass

    @abstractmethod
    def pass_joint_velocities(self, joints: list[str]) -> dict[str, float]:
        """! Retrieve the current joint velocities.

        @param joints Names of the queried joints.
        @return dictionary mapping each joint name to its velocity.
        """

        pass

    @abstractmethod
    def pass_joint_efforts(self, joints: list[str]) -> dict[str, float]:
        """! Retrieve the current joint efforts (torques or forces).

        @param joints Names of the queried joints.
        @return dictionary mapping each joint name to its effort value.
        """

        pass

    #####################
    ##     control     ##
    #####################

    @abstractmethod
    def pass_joint_group_control_cmd(
        self, control_mode: str, cmd: dict[str, float], **kwargs
    ) -> None:
        """! Send a control command to a group of joints.

        @param control_mode One of :class:`ControlType` specifying the command type.
        @param cmd dictionary of joint names to command values.
        @param kwargs Additional backend-specific parameters.
        """

        pass


class SimRobotDriver(RobotDriver, ABC):
    """! Base class for drivers controlling simulated robots."""

    def __init__(
        self,
        component_name: str,
        component_config: dict[str, Any] = None,
        sim: bool = True,
    ) -> None:
        """! Initialize the simulation driver.

        @param component_name Name of the robot component.
        @param component_config Configuration dictionary or path.
        @param sim Unused for simulated robots (always ``True``).
        """

        super().__init__(component_name, component_config, True)

    @abstractmethod
    def sim_reset(
        self,
        base_pos: list[float],
        base_orn: list[float],
        init_pos: list[float],
    ) -> None:
        """! Reset the robot's state in the simulator."""

        ...

    def shutdown_driver(self) -> None:
        """! Shut down the simulation driver."""

        # Nothing to handle here
        pass
