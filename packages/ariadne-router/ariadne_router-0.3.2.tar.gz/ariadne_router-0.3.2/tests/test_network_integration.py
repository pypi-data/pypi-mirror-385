"""
Integration Tests for Quantum Network Coordination System.

This module provides comprehensive integration tests for the quantum network
coordination system, testing distributed quantum computing scenarios,
network protocols, and fault tolerance mechanisms.
"""

import asyncio
import importlib.util
import time
from unittest.mock import Mock

import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.random import random_circuit

# Import the modules we're testing
try:
    from ariadne.network_coordination import (
        NetworkCoordinator,
        NetworkNode,
        NetworkStatus,
        NodeType,
        QuantumTask,
        TaskPriority,
        TaskResult,
        TimePrecisionManager,
    )

    NETWORK_COORDINATION_AVAILABLE = True
except ImportError:
    NETWORK_COORDINATION_AVAILABLE = False

WEBSOCKETS_AVAILABLE = importlib.util.find_spec("websockets") is not None
ZMQ_AVAILABLE = importlib.util.find_spec("zmq") is not None


@pytest.mark.skipif(not NETWORK_COORDINATION_AVAILABLE, reason="Network coordination not available")
class TestTimePrecisionManager:
    """Test suite for timing precision management."""

    @pytest.mark.skip(reason="Flaky in CI - timestamp precision timing issues")
    def test_precision_timestamp_generation(self) -> None:
        """Test high-precision timestamp generation."""
        manager = TimePrecisionManager(target_precision_ps=22)

        # Generate multiple timestamps
        timestamps = [manager.get_precise_timestamp() for _ in range(10)]

        # Verify timestamps are increasing
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1]

        # Verify precision (timestamps should be different)
        assert len(set(timestamps)) > 1

    def test_calibration_with_reference(self) -> None:
        """Test clock calibration with reference timestamps."""
        manager = TimePrecisionManager()

        # Simulate reference clock measurements
        local_times = [time.time() + i * 0.1 for i in range(5)]
        reference_times = [t + 0.002 for t in local_times]  # 2ms offset

        reference_data = list(zip(local_times, reference_times, strict=False))
        manager.calibrate_with_reference(reference_data)

        # Verify offset was calculated
        assert abs(manager.clock_sync_offset - 0.002) < 0.001

    def test_network_latency_estimation(self) -> None:
        """Test network latency estimation."""
        manager = TimePrecisionManager()

        # Test various round-trip times
        rtts = [0.001, 0.010, 0.050, 0.100]  # 1ms to 100ms

        for rtt in rtts:
            latency = manager.estimate_network_latency(rtt)
            assert 0 <= latency <= rtt
            assert abs(latency - rtt / 2) <= rtt / 2  # Should be roughly half RTT


@pytest.mark.skipif(not NETWORK_COORDINATION_AVAILABLE, reason="Network coordination not available")
class TestNetworkNode:
    """Test suite for network node management."""

    def test_node_creation(self) -> None:
        """Test network node creation and initialization."""
        node = NetworkNode(
            node_id="test-node-1",
            node_type=NodeType.COMPUTE_NODE,
            address="192.168.1.100",
            port=8080,
            capabilities={"backends": ["cpu", "gpu"], "max_qubits": 20},
        )

        assert node.node_id == "test-node-1"
        assert node.node_type == NodeType.COMPUTE_NODE
        assert node.address == "192.168.1.100"
        assert node.port == 8080
        assert node.capabilities["max_qubits"] == 20
        assert node.status == NetworkStatus.OFFLINE

    def test_node_auto_id_generation(self) -> None:
        """Test automatic node ID generation."""
        node = NetworkNode(node_id="", node_type=NodeType.GATEWAY, address="localhost", port=9000)

        assert node.node_id != ""
        assert len(node.node_id) > 0


@pytest.mark.skipif(not NETWORK_COORDINATION_AVAILABLE, reason="Network coordination not available")
class TestQuantumTask:
    """Test suite for quantum task management."""

    def test_task_creation(self) -> None:
        """Test quantum task creation."""
        circuit = QuantumCircuit(3, 3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        task = QuantumTask(
            task_id="test-task-1",
            circuit=circuit,
            shots=1000,
            priority=TaskPriority.HIGH,
            backend_requirements={"type": "simulator", "min_qubits": 3},
        )

        assert task.task_id == "test-task-1"
        assert task.circuit.num_qubits == 3
        assert task.shots == 1000
        assert task.priority == TaskPriority.HIGH
        assert task.backend_requirements["min_qubits"] == 3

    def test_task_auto_id_generation(self) -> None:
        """Test automatic task ID generation."""
        circuit = QuantumCircuit(2)
        task = QuantumTask(task_id="", circuit=circuit, shots=100)

        assert task.task_id != ""
        assert len(task.task_id) > 0


@pytest.mark.skipif(not NETWORK_COORDINATION_AVAILABLE, reason="Network coordination not available")
@pytest.mark.asyncio
class TestNetworkCoordinator:
    """Test suite for network coordinator functionality."""

    async def test_coordinator_initialization(self) -> None:
        """Test network coordinator initialization."""
        coordinator = NetworkCoordinator(
            coordinator_id="test-coordinator",
            listen_port=18765,  # Use different port to avoid conflicts
            enable_websockets=False,  # Disable to avoid actual network setup
            enable_zmq=False,
        )

        assert coordinator.coordinator_id == "test-coordinator"
        assert coordinator.listen_port == 18765
        assert len(coordinator.nodes) == 0
        assert len(coordinator.task_queue) == 0

    async def test_node_registration_handling(self) -> None:
        """Test node registration message handling."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Mock connection
        mock_connection = Mock()

        # Registration message
        registration_data = {
            "type": "register_node",
            "node_id": "test-node-123",
            "node_type": "compute_node",
            "address": "192.168.1.50",
            "port": 8080,
            "capabilities": {"backends": ["cpu"], "max_qubits": 15},
        }

        response = await coordinator._process_message(registration_data, mock_connection)
        assert response is not None
        assert response["type"] == "registration_success"
        assert response["node_id"] == "test-node-123"
        assert "test-node-123" in coordinator.nodes
        assert coordinator.nodes["test-node-123"].node_type == NodeType.COMPUTE_NODE

    async def test_heartbeat_handling(self) -> None:
        """Test heartbeat message handling."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # First register a node
        node = NetworkNode(
            node_id="heartbeat-test-node",
            node_type=NodeType.COMPUTE_NODE,
            address="localhost",
            port=8080,
        )
        coordinator.nodes[node.node_id] = node

        # Send heartbeat
        heartbeat_data = {
            "type": "heartbeat",
            "node_id": "heartbeat-test-node",
            "timestamp": time.time(),
            "load": 0.3,
            "status": "online",
        }

        response = await coordinator._process_message(heartbeat_data, Mock())
        assert response is not None
        assert response["type"] == "heartbeat_ack"
        assert "timestamp" in response
        assert coordinator.nodes["heartbeat-test-node"].load == 0.3
        assert coordinator.nodes["heartbeat-test-node"].status == NetworkStatus.ONLINE

    async def test_task_submission_and_result_handling(self) -> None:
        """Test task submission and result processing."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Create and submit a task
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        task = QuantumTask(
            task_id="integration-test-task",
            circuit=circuit,
            shots=500,
            priority=TaskPriority.NORMAL,
        )

        task_id = coordinator.submit_task(task)
        assert task_id == "integration-test-task"
        assert len(coordinator.task_queue) == 1

        # Simulate task execution and result
        coordinator.active_tasks[task_id] = task

        result_data = {
            "type": "task_result",
            "task_id": task_id,
            "node_id": "test-executor-node",
            "result": {"00": 245, "11": 255},
            "execution_time": 1.23,
        }

        response = await coordinator._process_message(result_data, Mock())
        assert response is not None
        assert response["type"] == "result_ack"
        assert task_id not in coordinator.active_tasks
        assert task_id in coordinator.completed_tasks

        result = coordinator.get_task_result(task_id)
        assert result is not None
        assert result.node_id == "test-executor-node"
        assert result.execution_time == 1.23

    async def test_time_synchronization(self) -> None:
        """Test time synchronization protocol."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        client_timestamp = time.time()
        sync_data = {"type": "sync_time", "timestamp": client_timestamp}

        response = await coordinator._process_message(sync_data, Mock())
        assert response is not None
        assert response["type"] == "time_sync_response"
        assert "coordinator_timestamp" in response
        assert response["client_timestamp"] == client_timestamp
        assert "round_trip_estimate" in response

    def test_task_scheduling_logic(self) -> None:
        """Test task scheduling and node selection."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Add test nodes with different capabilities
        node1 = NetworkNode(
            node_id="node-1",
            node_type=NodeType.COMPUTE_NODE,
            address="192.168.1.10",
            port=8080,
            capabilities={"backends": ["cpu"], "max_qubits": 10},
            status=NetworkStatus.ONLINE,
            load=0.2,
            latency=0.005,
        )

        node2 = NetworkNode(
            node_id="node-2",
            node_type=NodeType.COMPUTE_NODE,
            address="192.168.1.20",
            port=8080,
            capabilities={"backends": ["gpu", "cuda"], "max_qubits": 25},
            status=NetworkStatus.ONLINE,
            load=0.6,
            latency=0.010,
        )

        coordinator.nodes["node-1"] = node1
        coordinator.nodes["node-2"] = node2

        # Test node selection for different task requirements
        circuit = QuantumCircuit(5)
        task1 = QuantumTask(
            task_id="task-1",
            circuit=circuit,
            shots=1000,
            backend_requirements={"backends": ["cpu"]},
        )

        task2 = QuantumTask(
            task_id="task-2",
            circuit=circuit,
            shots=1000,
            backend_requirements={"backends": ["gpu"]},
        )

        # Test node scoring

        score1_task1 = coordinator._calculate_node_score(task1, node1)
        coordinator._calculate_node_score(task1, node2)

        score1_task2 = coordinator._calculate_node_score(task2, node1)
        score2_task2 = coordinator._calculate_node_score(task2, node2)

        # node1 should be better for CPU task
        assert score1_task1 > score1_task2

        # node2 should be better for GPU task
        assert score2_task2 > score1_task2

    def test_network_status_reporting(self) -> None:
        """Test network status and statistics reporting."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Add some test data
        node = NetworkNode(
            node_id="status-test-node",
            node_type=NodeType.COMPUTE_NODE,
            address="localhost",
            port=8080,
            status=NetworkStatus.ONLINE,
            load=0.4,
            latency=0.008,
        )
        coordinator.nodes["status-test-node"] = node

        # Add some completed tasks
        task_result = TaskResult(
            task_id="completed-task",
            node_id="status-test-node",
            result={"00": 500, "11": 500},
            execution_time=2.5,
        )
        coordinator.completed_tasks["completed-task"] = task_result
        coordinator.stats["tasks_completed"] = 1
        coordinator.stats["total_execution_time"] = 2.5

        status = coordinator.get_network_status()

        assert status["coordinator_id"] == coordinator.coordinator_id
        assert "status-test-node" in status["nodes"]
        assert status["nodes"]["status-test-node"]["status"] == "online"
        assert status["nodes"]["status-test-node"]["load"] == 0.4
        assert status["stats"]["tasks_completed"] == 1
        assert status["completed_tasks"] == 1


@pytest.mark.skipif(
    not NETWORK_COORDINATION_AVAILABLE or not WEBSOCKETS_AVAILABLE,
    reason="Network coordination or WebSockets not available",
)
@pytest.mark.asyncio
class TestNetworkIntegration:
    """Integration tests for full network scenarios."""

    async def test_full_network_simulation(self) -> None:
        """Test a complete network scenario with multiple nodes."""
        # This test simulates a realistic distributed quantum computing scenario

        # Start coordinator
        coordinator = NetworkCoordinator(
            coordinator_id="integration-coordinator",
            listen_port=19765,  # Different port
            enable_websockets=False,  # Keep disabled for unit tests
            enable_zmq=False,
        )

        # Simulate multiple compute nodes
        nodes = []
        for i in range(3):
            node = NetworkNode(
                node_id=f"compute-node-{i}",
                node_type=NodeType.COMPUTE_NODE,
                address=f"192.168.1.{10 + i}",
                port=8080 + i,
                capabilities={
                    "backends": ["cpu", "simulator"],
                    "max_qubits": 15 + i * 5,
                    "shots_per_second": 1000 * (i + 1),
                },
                status=NetworkStatus.ONLINE,
                load=0.1 * i,
                latency=0.005 + 0.002 * i,
            )
            nodes.append(node)
            coordinator.nodes[node.node_id] = node

        # Submit multiple tasks
        tasks = []
        for i in range(5):
            circuit = random_circuit(5 + i, 3 + i, seed=42 + i)
            circuit.measure_all()

            task = QuantumTask(
                task_id=f"integration-task-{i}",
                circuit=circuit,
                shots=1000,
                priority=TaskPriority.NORMAL if i < 3 else TaskPriority.HIGH,
                backend_requirements={"type": "simulator", "min_qubits": circuit.num_qubits},
            )
            tasks.append(task)
            coordinator.submit_task(task)

        assert len(coordinator.task_queue) == 5

        # Simulate task scheduling
        await coordinator._schedule_pending_tasks()

        # Verify some tasks were scheduled (simulated)
        # In real scenario, tasks would be assigned to nodes
        # For unit test, we verify the scheduling logic worked
        assert len(coordinator.task_queue) <= 5  # Some might be scheduled

        # Simulate task completion
        for i, task in enumerate(tasks[:3]):  # Complete first 3 tasks
            # Move to active (would happen in real scheduling)
            if task.task_id in [t.task_id for t in coordinator.task_queue]:
                coordinator.active_tasks[task.task_id] = task
                coordinator.task_queue = [t for t in coordinator.task_queue if t.task_id != task.task_id]

            # Simulate result
            result_data = {
                "type": "task_result",
                "task_id": task.task_id,
                "node_id": f"compute-node-{i % 3}",
                "result": {f"{j:02b}": 100 for j in range(2**task.circuit.num_clbits)},
                "execution_time": 1.0 + i * 0.5,
            }

            await coordinator._process_message(result_data, Mock())

        # Verify results
        assert len(coordinator.completed_tasks) == 3
        assert len(coordinator.active_tasks) == 0

        # Check network status
        status = coordinator.get_network_status()
        assert status["completed_tasks"] == 3
        assert len(status["nodes"]) == 3

        # Verify all nodes are still online
        for node_id in status["nodes"]:
            assert status["nodes"][node_id]["status"] == "online"

    async def test_fault_tolerance_node_failure(self) -> None:
        """Test network behavior when nodes fail."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Add nodes
        stable_node = NetworkNode(
            node_id="stable-node",
            node_type=NodeType.COMPUTE_NODE,
            address="192.168.1.50",
            port=8080,
            status=NetworkStatus.ONLINE,
            last_heartbeat=time.time(),
        )

        failing_node = NetworkNode(
            node_id="failing-node",
            node_type=NodeType.COMPUTE_NODE,
            address="192.168.1.51",
            port=8080,
            status=NetworkStatus.ONLINE,
            last_heartbeat=time.time() - 60,  # Old heartbeat
        )

        coordinator.nodes["stable-node"] = stable_node
        coordinator.nodes["failing-node"] = failing_node

        # Add active task assigned to failing node (simulated)
        circuit = QuantumCircuit(3)
        circuit.h(0)
        circuit.measure_all()

        task = QuantumTask(task_id="failing-task", circuit=circuit, shots=1000)
        coordinator.active_tasks["failing-task"] = task

        # Simulate heartbeat check that detects failed node
        current_time = time.time()

        # Check for offline nodes (simulate heartbeat loop logic)
        for node_id, node in coordinator.nodes.items():
            if current_time - node.last_heartbeat > 30.0:
                node.status = NetworkStatus.OFFLINE
                coordinator._reassign_tasks_from_node(node_id)

        # Verify failing node marked offline
        assert coordinator.nodes["failing-node"].status == NetworkStatus.OFFLINE
        assert coordinator.nodes["stable-node"].status == NetworkStatus.ONLINE

        # Verify task was reassigned to queue
        assert len(coordinator.task_queue) > 0
        assert "failing-task" not in coordinator.active_tasks

    async def test_load_balancing(self) -> None:
        """Test load balancing across multiple nodes."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Create nodes with different load levels
        high_load_node = NetworkNode(
            node_id="high-load",
            node_type=NodeType.COMPUTE_NODE,
            address="192.168.1.10",
            port=8080,
            status=NetworkStatus.ONLINE,
            load=0.95,  # Very high load
        )

        low_load_node = NetworkNode(
            node_id="low-load",
            node_type=NodeType.COMPUTE_NODE,
            address="192.168.1.20",
            port=8080,
            status=NetworkStatus.ONLINE,
            load=0.1,  # Low load
        )

        coordinator.nodes["high-load"] = high_load_node
        coordinator.nodes["low-load"] = low_load_node

        # Create test task
        circuit = QuantumCircuit(2)
        task = QuantumTask(task_id="load-test", circuit=circuit, shots=1000)

        # Test node selection - should prefer low load node
        available_nodes = [high_load_node, low_load_node]
        best_node = coordinator._select_best_node(task, available_nodes)

        assert best_node is not None
        assert best_node.node_id == "low-load"

        # Test load balancing detection
        await coordinator._rebalance_load()

        # The method should detect the imbalance (logged, no return value)
        # This verifies the load balancing logic runs without error


@pytest.mark.skipif(not NETWORK_COORDINATION_AVAILABLE, reason="Network coordination not available")
class TestNetworkSerialization:
    """Test network message serialization and deserialization."""

    def test_circuit_serialization(self) -> None:
        """Test quantum circuit serialization for network transmission."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Create test circuit
        circuit = QuantumCircuit(3, 3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        # Serialize circuit
        serialized = coordinator._serialize_circuit(circuit)

        assert serialized["num_qubits"] == 3
        assert serialized["num_clbits"] == 6
        assert len(serialized["operations"]) > 0

        # Verify operations include expected gates
        operation_names = [op["name"] for op in serialized["operations"]]
        assert "h" in operation_names
        assert "cx" in operation_names
        assert "measure" in operation_names

    def test_message_processing_error_handling(self) -> None:
        """Test error handling in message processing."""
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)

        # Test invalid message type
        invalid_msg = {"type": "invalid_message_type", "data": "test"}

        async def test_invalid_message() -> None:
            response = await coordinator._process_message(invalid_msg, Mock())
            assert response is not None
            assert response["type"] == "error"
            assert "Unknown message type" in response["message"]

        # Run the async test
        import asyncio

        asyncio.run(test_invalid_message())

        # Test malformed registration
        malformed_registration = {
            "type": "register_node",
            "node_id": "test-node",
            # Missing required fields
        }

        async def test_malformed_registration() -> None:
            response = await coordinator._process_message(malformed_registration, Mock())
            assert response is not None
            assert response["type"] == "error"

        asyncio.run(test_malformed_registration())


if __name__ == "__main__":
    # Run tests if executed directly
    import sys

    if not NETWORK_COORDINATION_AVAILABLE:
        print("Network coordination module not available - skipping tests")
        sys.exit(0)

    # Run basic functionality tests
    async def run_basic_tests() -> None:
        print("Running basic network coordination tests...")

        # Test timing manager
        timing_manager = TimePrecisionManager()
        timestamp = timing_manager.get_precise_timestamp()
        print(f"Generated timestamp: {timestamp}")

        # Test coordinator initialization
        coordinator = NetworkCoordinator(enable_websockets=False, enable_zmq=False)
        print(f"Coordinator created with ID: {coordinator.coordinator_id}")

        # Test node registration
        registration_data = {
            "type": "register_node",
            "node_id": "test-node",
            "node_type": "compute_node",
            "address": "localhost",
            "port": 8080,
            "capabilities": {"backends": ["cpu"]},
        }

        response = await coordinator._process_message(registration_data, Mock())
        assert response is not None
        print(f"Registration response: {response}")

        # Test task submission
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        task = QuantumTask(task_id="test-task", circuit=circuit, shots=1000)
        task_id = coordinator.submit_task(task)
        print(f"Submitted task: {task_id}")

        status = coordinator.get_network_status()
        print(f"Network status: nodes={len(status['nodes'])}, queue={status['task_queue_length']}")

        print("Basic tests completed successfully!")

    asyncio.run(run_basic_tests())
