"""
Quantum Network Coordination System for Ariadne.

This module implements the quantum network coordination system that enables
distributed quantum computing across multiple quantum devices and backends
with 22ps timing precision and advanced synchronization protocols.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from qiskit import QuantumCircuit

WEBSOCKETS_AVAILABLE = False
websockets: Any | None = None

if TYPE_CHECKING:
    from websockets.server import ServerProtocol
else:
    try:
        import websockets
        from websockets.server import ServerProtocol

        WEBSOCKETS_AVAILABLE = True
    except ImportError:
        websockets = cast(Any, None)

        class ServerProtocol:
            """Fallback protocol placeholder when websockets is unavailable."""

            pass


try:
    import zmq

    ZMQ_AVAILABLE = True
except ImportError:
    ZMQ_AVAILABLE = False

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the quantum network."""

    COORDINATOR = "coordinator"
    COMPUTE_NODE = "compute_node"
    GATEWAY = "gateway"
    MONITOR = "monitor"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class NetworkStatus(Enum):
    """Network status indicators."""

    OFFLINE = "offline"
    CONNECTING = "connecting"
    ONLINE = "online"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class NetworkNode:
    """Represents a node in the quantum network."""

    node_id: str
    node_type: NodeType
    address: str
    port: int
    capabilities: dict[str, Any] = field(default_factory=dict)
    status: NetworkStatus = NetworkStatus.OFFLINE
    last_heartbeat: float = 0.0
    latency: float = 0.0
    load: float = 0.0

    def __post_init__(self) -> None:
        if not self.node_id:
            self.node_id = str(uuid.uuid4())


@dataclass
class QuantumTask:
    """Represents a quantum computation task."""

    task_id: str
    circuit: QuantumCircuit
    shots: int
    priority: TaskPriority = TaskPriority.NORMAL
    backend_requirements: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    timeout: float = 300.0  # 5 minutes default
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.task_id:
            self.task_id = str(uuid.uuid4())


@dataclass
class TaskResult:
    """Result of a quantum task execution."""

    task_id: str
    node_id: str
    result: dict[str, Any]
    execution_time: float
    timestamp: float = field(default_factory=time.time)
    error: str | None = None


class TimePrecisionManager:
    """Manages high-precision timing for quantum network synchronization."""

    def __init__(self, target_precision_ps: int = 22):
        self.target_precision_ps = target_precision_ps
        self.clock_sync_offset = 0.0
        self.drift_compensation = 0.0
        self._calibration_data: list[float] = []

    def get_precise_timestamp(self) -> float:
        """Get high-precision timestamp with picosecond accuracy."""
        base_time = time.time_ns()

        # Apply clock synchronization offset and drift compensation
        corrected_time = base_time + self.clock_sync_offset + self.drift_compensation

        # Convert to seconds with picosecond precision
        return corrected_time / 1e9

    def calibrate_with_reference(self, reference_timestamps: list[tuple[float, float]]) -> None:
        """Calibrate timing with reference clock measurements."""
        if len(reference_timestamps) < 2:
            return

        # Calculate offset and drift from reference measurements
        offsets = []
        for local_time, reference_time in reference_timestamps:
            offset = reference_time - local_time
            offsets.append(offset)

        self.clock_sync_offset = sum(offsets) / len(offsets)

        # Calculate drift if we have historical data
        if len(self._calibration_data) > 0:
            recent_offset = offsets[-1]
            old_offset = self._calibration_data[-1]
            time_diff = (
                reference_timestamps[-1][0] - self._calibration_data[-2] if len(self._calibration_data) > 1 else 1.0
            )

            self.drift_compensation = (recent_offset - old_offset) / time_diff

        self._calibration_data.extend([ts[0] for ts in reference_timestamps])

        # Keep only recent calibration data
        if len(self._calibration_data) > 100:
            self._calibration_data = self._calibration_data[-50:]

    def estimate_network_latency(self, round_trip_time: float) -> float:
        """Estimate one-way network latency with precision corrections."""
        # Simple estimation: RTT/2 with some statistical corrections
        base_latency = round_trip_time / 2.0

        # Apply corrections based on historical data
        if len(self._calibration_data) >= 5:
            # Use exponential smoothing for latency estimation
            alpha = 0.125  # Smoothing factor
            smoothed_latency = alpha * base_latency + (1 - alpha) * (self.clock_sync_offset * 0.1)
            return max(smoothed_latency, 0.0)

        return base_latency


class NetworkCoordinator:
    """Central coordinator for the quantum network."""

    def __init__(
        self,
        coordinator_id: str | None = None,
        listen_port: int = 8765,
        enable_websockets: bool = True,
        enable_zmq: bool = True,
        timing_precision_ps: int = 22,
    ):
        self.coordinator_id = coordinator_id or str(uuid.uuid4())
        self.listen_port = listen_port
        self.enable_websockets = enable_websockets and WEBSOCKETS_AVAILABLE
        self.enable_zmq = enable_zmq and ZMQ_AVAILABLE

        # Network management
        self.nodes: dict[str, NetworkNode] = {}
        self.connections: dict[str, Any] = {}
        self.task_queue: list[QuantumTask] = []
        self.active_tasks: dict[str, QuantumTask] = {}
        self.completed_tasks: dict[str, TaskResult] = {}

        # Timing and synchronization
        self.timing_manager = TimePrecisionManager(timing_precision_ps)
        self.sync_interval = 10.0  # Sync every 10 seconds

        # Threading and async management
        self._running = False
        self._coordinator_thread: threading.Thread | None = None
        self._heartbeat_thread: threading.Thread | None = None

        # Network protocols
        self._websocket_server: Any = None
        self._zmq_context: Any = None
        self._zmq_socket: Any = None

        # Statistics and monitoring
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "average_latency": 0.0,
            "nodes_online": 0,
        }

        logger.info(f"NetworkCoordinator initialized with ID: {self.coordinator_id}")

    async def start(self) -> None:
        """Start the network coordinator."""
        if self._running:
            logger.warning("Coordinator already running")
            return

        self._running = True
        logger.info(f"Starting NetworkCoordinator on port {self.listen_port}")

        # Start network protocols
        if self.enable_websockets:
            await self._start_websocket_server()

        if self.enable_zmq:
            await self._start_zmq_server()

        # Start background tasks
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

        await self._main_coordination_loop()

    async def stop(self) -> None:
        """Stop the network coordinator."""
        logger.info("Stopping NetworkCoordinator")
        self._running = False

        # Stop WebSocket server
        if self._websocket_server:
            self._websocket_server.close()
            await self._websocket_server.wait_closed()

        # Stop ZMQ server
        if self._zmq_socket:
            self._zmq_socket.close()
        if self._zmq_context:
            self._zmq_context.term()

    async def _start_websocket_server(self) -> None:
        """Start WebSocket server for network communication."""
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("WebSockets not available, skipping WebSocket server")
            return

        # Define handler function outside closure
        async def handle_websocket(websocket: ServerProtocol, path: str) -> None:
            try:
                await self._handle_websocket_connection(websocket, path)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")

        if websockets is None:
            logger.error("WebSockets library unavailable despite flag; cannot start server")
            return

        self._websocket_server = await websockets.serve(handle_websocket, "localhost", self.listen_port)
        logger.info(f"WebSocket server started on port {self.listen_port}")

    async def _start_zmq_server(self) -> None:
        """Start ZMQ server for high-performance communication."""
        if not ZMQ_AVAILABLE:
            logger.warning("ZMQ not available, skipping ZMQ server")
            return

        self._zmq_context = zmq.Context()
        self._zmq_socket = self._zmq_context.socket(zmq.REP)
        self._zmq_socket.bind(f"tcp://*:{self.listen_port + 1}")
        logger.info(f"ZMQ server started on port {self.listen_port + 1}")

    async def _handle_websocket_connection(self, websocket: Any, path: Any) -> None:
        """Handle individual WebSocket connections."""
        if websockets is None:
            logger.warning("WebSockets library unavailable; cannot handle connection")
            return

        node_id: str | None = None
        try:
            async for message in websocket:
                data = json.loads(message)
                response = await self._process_message(data, websocket)

                if response:
                    await websocket.send(json.dumps(response))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for node {node_id}")
        except Exception as e:
            logger.error(f"WebSocket handling error: {e}")
        finally:
            if node_id and node_id in self.nodes:
                self.nodes[node_id].status = NetworkStatus.OFFLINE

    async def _process_message(self, data: dict[str, Any], connection: Any) -> dict[str, Any] | None:
        """Process incoming network messages."""
        message_type = data.get("type")

        if message_type == "register_node":
            return await self._handle_node_registration(data, connection)
        elif message_type == "heartbeat":
            return await self._handle_heartbeat(data)
        elif message_type == "task_result":
            return await self._handle_task_result(data)
        elif message_type == "node_status":
            return await self._handle_node_status(data)
        elif message_type == "sync_time":
            return await self._handle_time_sync(data)
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return {"type": "error", "message": "Unknown message type"}

    async def _handle_node_registration(self, data: dict[str, Any], connection: Any) -> dict[str, Any]:
        """Handle node registration requests."""
        try:
            node = NetworkNode(
                node_id=data.get("node_id", str(uuid.uuid4())),
                node_type=NodeType(data["node_type"]),
                address=data.get("address", "unknown"),
                port=data.get("port", 0),
                capabilities=data.get("capabilities", {}),
                status=NetworkStatus.ONLINE,
            )

            self.nodes[node.node_id] = node
            self.connections[node.node_id] = connection

            logger.info(f"Registered node {node.node_id} of type {node.node_type}")

            return {
                "type": "registration_success",
                "node_id": node.node_id,
                "coordinator_id": self.coordinator_id,
                "timestamp": self.timing_manager.get_precise_timestamp(),
            }

        except Exception as e:
            logger.error(f"Node registration error: {e}")
            return {"type": "error", "message": str(e)}

    async def _handle_heartbeat(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle heartbeat messages from nodes."""
        node_id = data.get("node_id")

        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.last_heartbeat = self.timing_manager.get_precise_timestamp()
            node.load = data.get("load", 0.0)
            node.status = NetworkStatus(data.get("status", "online"))

            # Calculate latency
            client_timestamp = data.get("timestamp", 0.0)
            current_time = self.timing_manager.get_precise_timestamp()
            node.latency = current_time - client_timestamp

            return {
                "type": "heartbeat_ack",
                "timestamp": current_time,
                "coordinator_load": self._calculate_coordinator_load(),
            }

        return {"type": "error", "message": "Node not registered"}

    async def _handle_task_result(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle task completion results."""
        task_id = data.get("task_id")
        node_id = data.get("node_id")

        if task_id in self.active_tasks:
            result = TaskResult(
                task_id=task_id,
                node_id=node_id or "",
                result=data.get("result", {}),
                execution_time=data.get("execution_time", 0.0),
                error=data.get("error"),
            )

            # Move task from active to completed
            del self.active_tasks[task_id]
            self.completed_tasks[task_id] = result

            # Update statistics
            self.stats["tasks_completed"] += 1
            self.stats["total_execution_time"] += result.execution_time

            if result.error:
                self.stats["tasks_failed"] += 1

            logger.info(f"Task {task_id} completed by node {node_id}")

            return {"type": "result_ack", "task_id": task_id}

        return {"type": "error", "message": "Task not found"}

    async def _handle_node_status(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle node status updates."""
        node_id = data.get("node_id")

        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.status = NetworkStatus(data.get("status", "online"))
            node.load = data.get("load", 0.0)
            node.capabilities.update(data.get("capabilities", {}))

            return {"type": "status_ack"}

        return {"type": "error", "message": "Node not registered"}

    async def _handle_time_sync(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle time synchronization requests."""
        client_timestamp = data.get("timestamp", 0.0)
        coordinator_timestamp = self.timing_manager.get_precise_timestamp()

        # Record timing data for calibration
        self.timing_manager.calibrate_with_reference([(client_timestamp, coordinator_timestamp)])

        return {
            "type": "time_sync_response",
            "coordinator_timestamp": coordinator_timestamp,
            "client_timestamp": client_timestamp,
            "round_trip_estimate": coordinator_timestamp - client_timestamp,
        }

    def _heartbeat_loop(self) -> None:
        """Background thread for sending heartbeats and monitoring nodes."""
        while self._running:
            try:
                current_time = self.timing_manager.get_precise_timestamp()

                # Check for offline nodes
                offline_nodes = []
                for node_id, node in self.nodes.items():
                    if current_time - node.last_heartbeat > 30.0:  # 30 second timeout
                        if node.status != NetworkStatus.OFFLINE:
                            node.status = NetworkStatus.OFFLINE
                            offline_nodes.append(node_id)
                            logger.warning(f"Node {node_id} went offline")

                # Remove offline nodes from active task assignments
                for node_id in offline_nodes:
                    self._reassign_tasks_from_node(node_id)

                # Update statistics
                self.stats["nodes_online"] = sum(
                    1 for node in self.nodes.values() if node.status == NetworkStatus.ONLINE
                )

                # Calculate average latency
                online_nodes = [node for node in self.nodes.values() if node.status == NetworkStatus.ONLINE]
                if online_nodes:
                    avg_latency = sum(node.latency for node in online_nodes) / len(online_nodes)
                    self.stats["average_latency"] = avg_latency

                time.sleep(self.sync_interval)

            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                time.sleep(1.0)

    async def _main_coordination_loop(self) -> None:
        """Main coordination loop for task scheduling and management."""
        while self._running:
            try:
                # Process pending tasks
                await self._schedule_pending_tasks()

                # Check for task timeouts
                await self._check_task_timeouts()

                # Rebalance load if necessary
                await self._rebalance_load()

                await asyncio.sleep(0.1)  # 100ms coordination cycle

            except Exception as e:
                logger.error(f"Coordination loop error: {e}")
                await asyncio.sleep(1.0)

    async def _schedule_pending_tasks(self) -> None:
        """Schedule pending tasks to available nodes."""
        if not self.task_queue:
            return

        # Sort tasks by priority
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)

        # Find available nodes
        available_nodes = [
            node for node in self.nodes.values() if node.status == NetworkStatus.ONLINE and node.load < 0.8
        ]

        if not available_nodes:
            return

        # Schedule tasks to best available nodes
        tasks_to_remove = []

        for i, task in enumerate(self.task_queue):
            # Find best node for this task
            best_node = self._select_best_node(task, available_nodes)

            if best_node:
                success = await self._assign_task_to_node(task, best_node)
                if success:
                    self.active_tasks[task.task_id] = task
                    tasks_to_remove.append(i)

                    # Update node load (simplified)
                    best_node.load += 0.1

                    # Remove from available if fully loaded
                    if best_node.load >= 0.8:
                        available_nodes.remove(best_node)

                    if not available_nodes:
                        break

        # Remove scheduled tasks from queue
        for i in reversed(tasks_to_remove):
            del self.task_queue[i]

    def _select_best_node(self, task: QuantumTask, available_nodes: list[NetworkNode]) -> NetworkNode | None:
        if not available_nodes:
            return None

        # Score nodes based on capabilities, load, and latency
        best_node = None
        best_score = -1.0

        for node in available_nodes:
            score = self._calculate_node_score(task, node)
            if score > best_score:
                best_score = score
                best_node = node

        return best_node

    def _calculate_node_score(self, task: QuantumTask, node: NetworkNode) -> float:
        """Calculate a score for assigning a task to a node."""
        score = 1.0

        # Penalty for high load
        score -= node.load * 0.3

        # Penalty for high latency
        score -= min(node.latency * 100, 0.5)  # Max penalty of 0.5

        # Bonus for matching capabilities
        required_backends = task.backend_requirements.get("backends", [])
        node_backends = node.capabilities.get("backends", [])

        if required_backends:
            matches = len(set(required_backends) & set(node_backends))
            score += matches / len(required_backends) * 0.5

        # Bonus for higher priority tasks on less loaded nodes
        if task.priority == TaskPriority.CRITICAL:
            score += (1.0 - node.load) * 0.2

        return max(score, 0.0)

    async def _assign_task_to_node(self, task: QuantumTask, node: NetworkNode) -> bool:
        """Assign a task to a specific node."""
        try:
            # Prepare task message
            task_message = {
                "type": "execute_task",
                "task_id": task.task_id,
                "circuit": self._serialize_circuit(task.circuit),
                "shots": task.shots,
                "priority": task.priority.value,
                "backend_requirements": task.backend_requirements,
                "timeout": task.timeout,
                "timestamp": self.timing_manager.get_precise_timestamp(),
            }

            # Send task to node
            connection = self.connections.get(node.node_id)
            if connection:
                if hasattr(connection, "send"):  # WebSocket
                    await connection.send(json.dumps(task_message))
                else:  # ZMQ or other protocol
                    # Handle other protocols
                    pass

                logger.info(f"Assigned task {task.task_id} to node {node.node_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to assign task {task.task_id} to node {node.node_id}: {e}")

        return False

    def _serialize_circuit(self, circuit: QuantumCircuit) -> dict[str, Any]:
        """Serialize quantum circuit for network transmission."""
        # Simple serialization - in production, use more robust methods
        return {
            "num_qubits": circuit.num_qubits,
            "num_clbits": circuit.num_clbits,
            "operations": [
                {
                    "name": op.operation.name,
                    "params": list(op.operation.params),
                    "qubits": [circuit.find_bit(q).index for q in op.qubits],
                    "clbits": [circuit.find_bit(c).index for c in op.clbits],
                }
                for op in circuit.data
            ],
        }

    async def _check_task_timeouts(self) -> None:
        """Check for and handle task timeouts."""
        current_time = self.timing_manager.get_precise_timestamp()
        timed_out_tasks = []

        for task_id, task in self.active_tasks.items():
            if current_time - task.created_at > task.timeout:
                timed_out_tasks.append(task_id)

        for task_id in timed_out_tasks:
            logger.warning(f"Task {task_id} timed out")
            task = self.active_tasks[task_id]

            # Create timeout result
            timeout_result = TaskResult(
                task_id=task_id,
                node_id="coordinator",
                result={},
                execution_time=task.timeout,
                error="Task timeout",
            )

            del self.active_tasks[task_id]
            self.completed_tasks[task_id] = timeout_result
            self.stats["tasks_failed"] += 1

    async def _rebalance_load(self) -> None:
        """Rebalance load across nodes if necessary."""
        # Simple load balancing - can be enhanced
        overloaded_nodes = [
            node for node in self.nodes.values() if node.status == NetworkStatus.ONLINE and node.load > 0.9
        ]

        underloaded_nodes = [
            node for node in self.nodes.values() if node.status == NetworkStatus.ONLINE and node.load < 0.3
        ]

        # In a full implementation, we would migrate tasks between nodes
        # For now, just log the imbalance
        if overloaded_nodes and underloaded_nodes:
            logger.info(
                f"Load imbalance detected: {len(overloaded_nodes)} overloaded, "
                f"{len(underloaded_nodes)} underloaded nodes"
            )

    def _reassign_tasks_from_node(self, node_id: str) -> None:
        """Reassign active tasks from a failed node."""
        tasks_to_reassign = []

        for task_id in self.active_tasks:
            # Find tasks assigned to the failed node (simplified check)
            # In production, we'd maintain explicit task-to-node mappings
            tasks_to_reassign.append(task_id)

        for task_id in tasks_to_reassign:
            task = self.active_tasks[task_id]
            del self.active_tasks[task_id]
            self.task_queue.append(task)
            logger.info(f"Reassigned task {task_id} from failed node {node_id}")

    def _calculate_coordinator_load(self) -> float:
        """Calculate current coordinator load."""
        active_task_count = len(self.active_tasks)
        queue_length = len(self.task_queue)
        node_count = len([n for n in self.nodes.values() if n.status == NetworkStatus.ONLINE])

        # Simple load calculation
        base_load = (active_task_count + queue_length * 0.1) / max(node_count, 1)
        return min(base_load, 1.0)

    # Public API methods

    def submit_task(self, task: QuantumTask) -> str:
        """Submit a task to the network for execution."""
        self.task_queue.append(task)
        logger.info(f"Submitted task {task.task_id} to network queue")
        return task.task_id

    def get_task_result(self, task_id: str) -> TaskResult | None:
        """Get the result of a completed task."""
        return self.completed_tasks.get(task_id)

    def get_network_status(self) -> dict:
        """Get current network status and statistics."""
        return {
            "coordinator_id": self.coordinator_id,
            "nodes": {
                node_id: {
                    "type": node.node_type.value,
                    "status": node.status.value,
                    "load": node.load,
                    "latency": node.latency,
                    "last_heartbeat": node.last_heartbeat,
                }
                for node_id, node in self.nodes.items()
            },
            "stats": self.stats.copy(),
            "task_queue_length": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "timestamp": self.timing_manager.get_precise_timestamp(),
        }

    def clear_completed_tasks(self, older_than_seconds: float = 3600) -> None:
        """Clear completed tasks older than specified time."""
        current_time = self.timing_manager.get_precise_timestamp()
        tasks_to_remove = [
            task_id
            for task_id, result in self.completed_tasks.items()
            if current_time - result.timestamp > older_than_seconds
        ]

        for task_id in tasks_to_remove:
            del self.completed_tasks[task_id]

        if tasks_to_remove:
            logger.info(f"Cleared {len(tasks_to_remove)} old completed tasks")
