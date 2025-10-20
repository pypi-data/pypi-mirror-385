import sys
import traceback

from eigen.core.client.comm_infrastructure.comm_endpoint import CommEndpoint
from eigen.core.tools.log import log


class BaseNode(CommEndpoint):
    """!
    Base class for nodes that interact with the LCM system. Handles the subscription,
    publishing, and communication processes for the node.

    The `BaseNode` class manages the LCM instance and communication handlers, and provides
    methods for creating publishers, subscribers, listeners, and steppers. It also provides
    functionality for handling command-line arguments and the graceful shutdown of the node.

    @param lcm: The LCM instance used for communication.
    @param channel_name: The name of the channel to subscribe to.
    @param channel_type: The type of the message expected for the channel.
    """

    def __init__(self, name: str, global_config=None) -> None:
        """!
        Initializes a BaseNode object with the specified node name and registry host and port.

        @param node_name: The name of the node.
        @param global_config: Contains IP Address and Port
        """
        super().__init__(name, global_config)
        self.config = self._load_config_section(
            global_config=global_config, name=name, type="other"
        )
        self._done = False

    def spin(self) -> None:
        """!
        Runs the node’s main loop, handling LCM messages continuously until the node is finished.

        The loop calls `self._lcm.handle()` to process incoming messages. If an OSError is encountered,
        the loop will stop and the node will shut down.
        """
        while not self._done:
            try:
                self._lcm.handle_timeout(0)
            except OSError as e:
                log.warning(f"LCM threw OSError {e}")
                self._done = True


def main(node_cls: type[BaseNode], *args) -> None:
    """!
    Initializes and runs a node.

    This function creates an instance of the specified `node_cls`, spins the node to handle messages,
    and handles exceptions that occur during the node's execution.

    @param node_cls: The class of the node to run.
    @type node_cls: Type[BaseNode]
    """

    if "--help" in sys.argv or "-h" in sys.argv:
        print(node_cls.get_cli_doc())
        sys.exit(0)

    node = None
    log.ok(f"Initializing {node_cls.__name__} type node")
    try:
        node = node_cls(*args)
        # if node.registered == False:
        #     node.kill_node()
        #     log.ok(f"Register first")
        # else:
        log.ok(f"Initialized {node.name}")
        node.spin()
    except KeyboardInterrupt:
        log.warning(f"User killed node {node_cls.__name__}")
    except Exception:
        tb = traceback.format_exc()
        div = "=" * 30
        log.error(
            f"Exception thrown during node execution:\n{div}\n{tb}\n{div}"
        )
    finally:
        if node is not None:
            node.kill_node()
            log.ok(f"Finished running node {node_cls.__name__}")
        else:
            log.warning(
                f"Node {node_cls.__name__} failed during initialization"
            )
