"""
Main interface for hackathon contestants.
Provides clean access to problem data, inventory tracking, and constraint validation.
"""

import pandas as pd
import os
from typing import Dict, List, Tuple, Optional, Any

from .core.models import Node, SKU, Order, Vehicle, Warehouse
from .core.state.orchestrator import LogisticsOrchestrator
from .core.data_generator import generate_problem_instance, generate_scenario_from_config
from .core.validation import SolutionValidator
from .core.metrics import MetricsCalculator
from .core.network import NetworkManager

class LogisticsEnvironment:
    """
    Main interface for hackathon contestants.
    Provides clean access to problem data, inventory tracking, and constraint validation.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize the logistics environment."""
        self._current_seed = None
        self.validator = None
        self.metrics_calculator = None
        self.network_manager = None

        self._load_problem_instance()
        self._reset_vehicle_states()

    def _load_problem_instance(self):
        """Load and initialize the problem instance."""
        nodes_df, edges_df, warehouses, orders, skus, vehicles = generate_problem_instance()
        self._initialize_environment(nodes_df, edges_df, warehouses, orders, skus, vehicles)
        self._current_seed = None

    def _initialize_environment(self, nodes_df, edges_df, warehouses, orders, skus, vehicles):
        """Initialize the environment with problem data."""
        if nodes_df is None or nodes_df.empty:
            raise ValueError("nodes_df cannot be None or empty")
        if edges_df is None:
            raise ValueError("edges_df cannot be None")
        if not warehouses:
            raise ValueError("warehouses cannot be empty")
        if not orders:
            raise ValueError("orders cannot be empty")
        if not skus:
            raise ValueError("skus cannot be empty")
        if not vehicles:
            raise ValueError("vehicles cannot be empty")

        required_node_cols = ['node_id', 'lat', 'lon']
        if not all(col in nodes_df.columns for col in required_node_cols):
            raise ValueError(f"nodes_df must contain columns: {required_node_cols}")

        if not all(-90 <= lat <= 90 for lat in nodes_df['lat']):
            raise ValueError("Latitude values must be between -90 and 90")
        if not all(-180 <= lon <= 180 for lon in nodes_df['lon']):
            raise ValueError("Longitude values must be between -180 and 180")

        self.nodes = {}
        for _, row in nodes_df.iterrows():
            node = Node(
                node_id=row['node_id'],
                lat=row['lat'],
                lon=row['lon']
            )
            self.nodes[node.id] = node

        self.warehouses = {warehouse.id: warehouse for warehouse in warehouses}
        self.orders = {order.id: order for order in orders}
        self.skus = {sku.id: sku for sku in skus}
        
        self._baseline_inventories = {
            wh_id: inv.inventory.copy() if hasattr(inv, 'inventory') else {}
            for wh_id, inv in self.warehouses.items()
        }

        self.network_manager = NetworkManager(self.nodes, edges_df)
        
        self.orchestrator = LogisticsOrchestrator(
            warehouses=self.warehouses,
            vehicles=vehicles,
            orders=self.orders,
            skus=self.skus
        )
        
        vehicles_dict = {v.id: v for v in self.get_all_vehicles()}
        self.validator = SolutionValidator(
            self.warehouses, vehicles_dict, self.orders, self.skus, self.network_manager
        )
        self.metrics_calculator = MetricsCalculator(
            self.warehouses, vehicles_dict, self.orders, self.skus, self.network_manager
        )
        
        self._validate_environment()



    def _validate_environment(self):
        """Validate the environment configuration."""
        if not self.warehouses:
            raise ValueError("No warehouses defined")
        if not self.orders:
            raise ValueError("No orders defined")
        if not self.skus:
            raise ValueError("No SKUs defined")
        all_vehicles = self.get_all_vehicles()
        if not all_vehicles:
            raise ValueError("No vehicles defined")

        for warehouse in self.warehouses.values():
            if warehouse.location.id not in self.nodes:
                raise ValueError(f"Warehouse {warehouse.id} location {warehouse.location.id} not in road network")

        for order in self.orders.values():
            if order.destination.id not in self.nodes:
                raise ValueError(f"Order {order.id} destination {order.destination.id} not in road network")

    def _reset_vehicle_states(self):
        """Reset vehicle load, weight, volume, and location states using central orchestrator."""
        if hasattr(self, 'orchestrator'):
            self.orchestrator.reset_all_vehicles()
    
    def reset_all_state(self):
        """Reset all orchestrator state including inventory, vehicles, and order deliveries.
        
        This performs a TRUE reset by restoring warehouse inventories to the
        original scenario baseline captured at initialization/generation, and
        clearing per-order delivery side effects, then re-initializing the central orchestrator.
        """
        if hasattr(self, 'warehouses') and hasattr(self, '_baseline_inventories'):
            for wh_id, baseline in self._baseline_inventories.items():
                if wh_id in self.warehouses:
                    # Replace with a fresh copy to avoid shared references
                    self.warehouses[wh_id].inventory = dict(baseline)

        if hasattr(self, 'orders'):
            for order in self.orders.values():
                if hasattr(order, '_delivered_items'):
                    delattr(order, '_delivered_items')

        if hasattr(self, 'orchestrator'):
            self.orchestrator.reset_all_state()

    def complete_reset(self, seed: Optional[int] = None):
        """Perform complete environment reset including orchestrator state.
        
        Args:
            seed: Optional random seed for reproducible scenarios
        """
        self.reset_all_state()
        
        if seed is not None:
            self.generate_new_scenario(seed=seed)
        else:
            self.generate_new_scenario()
        
        self.reset_all_state()

    def get_all_vehicles(self):
        """Get all vehicles from all warehouses."""
        all_vehicles = []
        for warehouse in self.warehouses.values():
            all_vehicles.extend(warehouse.vehicles)
        return all_vehicles

    def get_vehicle_by_id(self, vehicle_id):
        """Get vehicle by ID."""
        for warehouse in self.warehouses.values():
            for vehicle in warehouse.vehicles:
                if vehicle.id == vehicle_id:
                    return vehicle
        return None

    def get_warehouse_by_id(self, warehouse_id):
        """Get warehouse by ID."""
        return self.warehouses.get(warehouse_id)

    def get_road_network_data(self) -> Dict:
        """Get complete road network data for pathfinding."""
        return self.network_manager.get_road_network_data()



    def get_distance(self, node1: int, node2: int) -> Optional[float]:
        """
        Get direct distance between two connected nodes.
        Returns None if no direct connection exists.
        """
        return self.network_manager.get_distance(node1, node2)

    def get_route_distance(self, route: List[int]) -> float:
        """
        Calculate total distance for a route (list of node IDs).
        Uses actual road network distances from edges.
        """
        return self.network_manager.get_route_distance(route)

    def get_all_order_ids(self) -> List[str]:
        """Get list of all order IDs."""
        return list(self.orders.keys())

    def get_available_vehicles(self) -> List[str]:
        """Get list of all available vehicle IDs."""
        all_vehicles = self.get_all_vehicles()
        return [v.id for v in all_vehicles]

    def get_order_location(self, order_id: str) -> int:
        """Get the delivery location node ID for an order."""
        if order_id in self.orders:
            return self.orders[order_id].destination.id
        raise ValueError(f"Order {order_id} not found")

    def get_vehicle_home_warehouse(self, vehicle_id: str) -> int:
        """Get the home warehouse node ID for a vehicle."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if vehicle:
            warehouse_id = vehicle.home_warehouse_id

            for warehouse in self.warehouses.values():
                if warehouse.id == warehouse_id:
                    return warehouse.location.id

            raise ValueError(f"Warehouse {warehouse_id} not found for vehicle {vehicle_id}")
        raise ValueError(f"Vehicle {vehicle_id} not found")

    def get_order_requirements(self, order_id: str) -> Dict[str, int]:
        """Get SKU requirements for an order."""
        if order_id in self.orders:
            return self.orders[order_id].requested_items.copy()
        return {}

    def get_warehouse_inventory(self, warehouse_id: str) -> Dict[str, int]:
        """Get current inventory levels for a specific warehouse from central orchestrator."""
        return self.orchestrator.warehouse_inventories.get(warehouse_id, {})

    def get_vehicle_current_load(self, vehicle_id: str) -> Dict[str, int]:
        """Get current SKU quantities loaded on a vehicle from central orchestrator."""
        return self.orchestrator.vehicle_loads.get(vehicle_id, {})

    def get_vehicle_current_capacity(self, vehicle_id: str) -> Tuple[float, float]:
        """Get current weight and volume usage for a vehicle from central orchestrator."""
        return self.orchestrator.get_vehicle_capacity_usage(vehicle_id)

    def get_vehicle_remaining_capacity(self, vehicle_id: str) -> Tuple[float, float]:
        """Get remaining weight and volume capacity for a vehicle from central orchestrator."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return 0.0, 0.0
        
        current_weight, current_volume = self.orchestrator.get_vehicle_capacity_usage(vehicle_id)
        remaining_weight = max(0.0, vehicle.capacity_weight - current_weight)
        remaining_volume = max(0.0, vehicle.capacity_volume - current_volume)
        return remaining_weight, remaining_volume

    def get_order_fulfillment_status(self, order_id: str) -> Dict[str, Dict[str, int]]:
        """Get detailed fulfillment status for an order."""
        if order_id not in self.orders:
            return {}

        order = self.orders[order_id]
        result = {
            'requested': order.requested_items.copy(),
            'delivered': getattr(order, '_delivered_items', {}),
            'remaining': {}
        }

        for sku_id in order.requested_items:
            requested = order.requested_items[sku_id]
            delivered = result['delivered'].get(sku_id, 0)
            result['remaining'][sku_id] = max(0, requested - delivered)

        return result

    def get_warehouses_with_sku(self, sku_id: str, min_quantity: int = 1) -> List[str]:
        """Find all warehouses that have a specific SKU in stock."""
        warehouses_with_sku = []

        for warehouse_id, warehouse in self.warehouses.items():
            if sku_id in warehouse.inventory and warehouse.inventory[sku_id] >= min_quantity:
                warehouses_with_sku.append(warehouse_id)

        return warehouses_with_sku

    def get_sku_details(self, sku_id: str) -> Optional[Dict]:
        """Get SKU specifications (weight, volume)."""
        if sku_id in self.skus:
            sku = self.skus[sku_id]
            return {
                'id': sku.id,
                'weight': sku.weight,
                'volume': sku.volume
            }
        return None

    def pickup_sku_from_warehouse(self, vehicle_id: str, warehouse_id: str, sku_id: str, quantity: int) -> bool:
        """
        Pick up SKU from warehouse and load onto vehicle.
        NOW USES CENTRAL ORCHESTRATOR - Single source of truth.

        Args:
            vehicle_id: ID of the vehicle
            warehouse_id: ID of the warehouse
            sku_id: ID of the SKU to pick up
            quantity: Quantity to pick up

        Returns:
            True if successful, False otherwise
        """
        success, _ = self.orchestrator.execute_pickup(vehicle_id, warehouse_id, sku_id, quantity)
        return success

    def deliver_sku_to_order(self, vehicle_id: str, order_id: str, sku_id: str, quantity: int) -> bool:
        """
        Deliver SKU from vehicle to order.
        NOW USES CENTRAL ORCHESTRATOR - Single source of truth.

        Args:
            vehicle_id: ID of the vehicle
            order_id: ID of the order
            sku_id: ID of the SKU to deliver
            quantity: Quantity to deliver

        Returns:
            True if successful, False otherwise
        """
        success, _ = self.orchestrator.execute_delivery(vehicle_id, order_id, sku_id, quantity)
        return success

    def unload_sku_to_warehouse(self, vehicle_id: str, warehouse_id: str, sku_id: str, quantity: int) -> bool:
        """
        Unload SKU from vehicle to a warehouse.
        NOW USES CENTRAL ORCHESTRATOR - Single source of truth.

        Args:
            vehicle_id: ID of the vehicle
            warehouse_id: ID of the warehouse to unload to
            sku_id: ID of the SKU to unload
            quantity: Quantity to unload

        Returns:
            True if successful, False otherwise
        """
        success, _ = self.orchestrator.execute_unload(vehicle_id, warehouse_id, sku_id, quantity)
        return success

    def execute_route_sequential(self, vehicle_id: str, steps: List[Dict]) -> Tuple[bool, str]:
        """
        Execute a single route defined as ordered steps with operations bound to nodes.
        """
        if not steps or len(steps) < 2:
            return False, "Sequential route must have at least 2 steps"

        is_valid, error_msg = self.validator.validate_route_steps(vehicle_id, steps)
        if not is_valid:
            return False, f"Route validation failed: {error_msg}"

        cumulative_distance = 0.0
        previous_node = None
        for step in steps:
            node_id = step.get('node_id')
            if previous_node is not None:
                leg_distance = self.network_manager.get_distance(previous_node, node_id) or 0.0
                cumulative_distance += leg_distance
                vehicle = self.get_vehicle_by_id(vehicle_id)
                if vehicle and cumulative_distance > vehicle.max_distance:
                    return False, (
                        f"Cumulative distance exceeded en route to node {node_id}: "
                        f"{cumulative_distance:.2f} km > max {vehicle.max_distance:.2f} km"
                    )

            # 1) Unloads first
            for unload in step.get('unloads', []) or []:
                success, msg = self.orchestrator.execute_unload(
                    vehicle_id, unload['warehouse_id'], unload['sku_id'], unload['quantity']
                )
                if not success:
                    return False, f"Unload failed at node {step.get('node_id')}: {msg}"

            # 2) Pickups next
            for pickup in step.get('pickups', []) or []:
                success, msg = self.orchestrator.execute_pickup(
                    vehicle_id, pickup['warehouse_id'], pickup['sku_id'], pickup['quantity']
                )
                if not success:
                    return False, f"Pickup failed at node {step.get('node_id')}: {msg}"

            # 3) Deliveries last
            for delivery in step.get('deliveries', []) or []:
                success, msg = self.orchestrator.execute_delivery(
                    vehicle_id, delivery['order_id'], delivery['sku_id'], delivery['quantity']
                )
                if not success:
                    return False, f"Delivery failed at node {step.get('node_id')}: {msg}"

            previous_node = node_id

        return True, "Sequential route executed successfully"

    def get_route_step_progression(self, route: Dict) -> List[Dict]:
        """
        Compute step-by-step progression metrics for a route with steps.
        """
        steps = route.get('steps') or []
        if not steps:
            return []

        progression: List[Dict] = []
        cumulative_distance = 0.0
        current_weight = 0.0
        current_volume = 0.0
        previous_node = None

        for idx, step in enumerate(steps):
            node_id = step.get('node_id')
            if previous_node is not None:
                leg_distance = self.network_manager.get_distance(previous_node, node_id) or 0.0
                cumulative_distance += leg_distance

            for pickup in (step.get('pickups') or []):
                sku_id = pickup.get('sku_id')
                qty = float(pickup.get('quantity', 0) or 0)
                if sku_id in self.skus:
                    sku = self.skus[sku_id]
                    current_weight += sku.weight * qty
                    current_volume += sku.volume * qty

            for delivery in (step.get('deliveries') or []):
                sku_id = delivery.get('sku_id')
                qty = float(delivery.get('quantity', 0) or 0)
                if sku_id in self.skus:
                    sku = self.skus[sku_id]
                    current_weight -= sku.weight * qty
                    current_volume -= sku.volume * qty
                    if current_weight < 0:
                        current_weight = 0.0
                    if current_volume < 0:
                        current_volume = 0.0

            for unload in (step.get('unloads') or []):
                sku_id = unload.get('sku_id')
                qty = float(unload.get('quantity', 0) or 0)
                if sku_id in self.skus:
                    sku = self.skus[sku_id]
                    current_weight -= sku.weight * qty
                    current_volume -= sku.volume * qty
                    if current_weight < 0:
                        current_weight = 0.0
                    if current_volume < 0:
                        current_volume = 0.0

            progression.append({
                'step_index': idx + 1,
                'node_id': node_id,
                'cumulative_distance_km': cumulative_distance,
                'vehicle_weight_kg': current_weight,
                'vehicle_volume_m3': current_volume,
                'pickups': step.get('pickups') or [],
                'deliveries': step.get('deliveries') or [],
                'unloads': step.get('unloads') or []
            })

            previous_node = node_id

        return progression

    def execute_solution(self, solution: Dict) -> Tuple[bool, str]:
        """
        Execute a complete solution by running all routes.
        
        This method takes a validated solution and actually executes all the
        pickup and delivery operations to update the system state.
        
        Args:
            solution: Dictionary with 'routes' list
            
        Returns:
            Tuple of (success, message)
        """
        if not solution or 'routes' not in solution:
            return False, "Invalid solution: no routes found"
        
        routes = solution['routes']
        if not routes:
            return False, "No routes to execute"
        
        executed_routes = 0
        failed_routes = 0
        
        for route in routes:
            vehicle_id = route.get('vehicle_id')
            steps = route.get('steps')
            
            if not vehicle_id:
                failed_routes += 1
                continue
            
            if steps and isinstance(steps, list):
                success, msg = self.execute_route_sequential(vehicle_id, steps)
            else:
                failed_routes += 1
                msg = "Missing sequential steps for route; aggregated execution disabled"
            
            if success:
                executed_routes += 1
            else:
                failed_routes += 1
        
        if failed_routes == 0:
            return True, f"Successfully executed all {executed_routes} routes"
        elif executed_routes > 0:
            return True, f"Executed {executed_routes} routes, {failed_routes} failed"
        else:
            return False, f"All {failed_routes} routes failed to execute"

    def set_random_seed(self, seed: int):
        """Set random seed for reproducible scenarios."""
        self._current_seed = seed

    def get_current_seed(self) -> Optional[int]:
        """Get current random seed."""
        return self._current_seed

    def generate_new_scenario(self, seed: Optional[int] = None):
        """Generate a new problem scenario."""
        if seed is not None:
            self.set_random_seed(seed)

        from .core import config as core_config

        default_config = {
            'num_orders': core_config.DEFAULT_SETTINGS['num_orders'],
            'num_warehouses': core_config.DEFAULT_SETTINGS['num_warehouses'],
            'min_items_per_order': core_config.DEFAULT_SETTINGS.get('min_items_per_order', 1),
            'max_items_per_order': core_config.DEFAULT_SETTINGS.get('max_items_per_order', 10),
            'sku_percentages': core_config.DEFAULT_SETTINGS['default_sku_distribution'],
            'warehouse_configs': [
                {
                    'vehicle_counts': core_config.DEFAULT_SETTINGS['default_vehicle_counts'],
                    'sku_inventory_percentages': core_config.DEFAULT_WAREHOUSE_SKU_ALLOCATIONS[0]
                },
                {
                    'vehicle_counts': core_config.DEFAULT_SETTINGS['default_vehicle_counts'],
                    'sku_inventory_percentages': core_config.DEFAULT_WAREHOUSE_SKU_ALLOCATIONS[1]
                }
            ],
            'distance_control': core_config.DEFAULT_SETTINGS['distance_control'],
            'random_seed': self._current_seed
        }

        self.generate_scenario_from_config(default_config)

    def generate_scenario_from_config(self, config: Dict):
        """Generate scenario from dashboard configuration."""
        if 'random_seed' in config and config['random_seed'] is not None:
            self._current_seed = config['random_seed']
        else:
            self._current_seed = None

        from .core import config as core_config

        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
        edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))

        problem_data = generate_scenario_from_config(core_config, nodes_df, edges_df, config)

        nodes = problem_data['nodes']
        edges_df_final = problem_data['edges_df']
        warehouses = problem_data['warehouses']
        orders, _ = problem_data['orders']
        skus = problem_data['skus']

        all_vehicles = []
        for warehouse in warehouses:
            all_vehicles.extend(warehouse.vehicles)

        nodes_df_final = pd.DataFrame([
            {'node_id': node.id, 'lat': node.lat, 'lon': node.lon}
            for node in nodes
        ])

        self._initialize_environment(nodes_df_final, edges_df_final, warehouses, orders, skus, all_vehicles)
        self._reset_vehicle_states()

    def export_scenario(self) -> Dict:
        """Export the current scenario (SKUs, warehouses, vehicles, orders) with generation parameters.

        Returns a plain-JSON-serializable dictionary that can be fed back into
        load_scenario() to recreate the exact same setup without regeneration.
        Includes clustering configurations and generation parameters.
        Excludes static nodes/edges (road network) as they're constant.
        
        Returns:
            Dict containing:
            - skus: List of SKU definitions
            - warehouses: List of warehouse configurations with inventory and vehicles
            - orders: List of order requirements
            - generation_config: Parameters used to generate the scenario
        """
        skus_list = [
            {
                'sku_id': sku.id,
                'weight_kg': float(sku.weight),
                'volume_m3': float(sku.volume)
            }
            for sku in self.skus.values()
        ]

        warehouses_list = []
        for wh in self.warehouses.values():
            vehicles_list = []
            for veh in wh.vehicles:
                vehicles_list.append({
                    'id': veh.id,
                    'type': veh.type,
                    'home_warehouse_id': veh.home_warehouse_id,
                    'capacity_weight_kg': float(veh.capacity_weight),
                    'capacity_volume_m3': float(veh.capacity_volume),
                    'max_distance_km': float(veh.max_distance),
                    'cost_per_km': float(veh.cost_per_km),
                    'fixed_cost': float(veh.fixed_cost)
                })

            warehouses_list.append({
                'id': wh.id,
                'location_node_id': int(wh.location.id),
                'inventory': {sku_id: int(qty) for sku_id, qty in wh.inventory.items()},
                'vehicles': vehicles_list
            })

        orders_list = []
        for order in self.orders.values():
            orders_list.append({
                'id': order.id,
                'destination_node_id': int(order.destination.id),
                'requested_items': {sku_id: int(qty) for sku_id, qty in order.requested_items.items()}
            })

        from .core import config as core_config
        generation_config = {
            'num_orders': len(self.orders),
            'num_warehouses': len(self.warehouses),
            'min_items_per_order': core_config.DEFAULT_SETTINGS.get('min_items_per_order', 1),
            'max_items_per_order': core_config.DEFAULT_SETTINGS.get('max_items_per_order', 10),
            'sku_percentages': core_config.DEFAULT_SETTINGS.get('default_sku_distribution', [33, 33, 34]),
            'warehouse_configs': [
                {
                    'vehicle_counts': core_config.DEFAULT_SETTINGS.get('default_vehicle_counts', {}),
                    'sku_inventory_percentages': core_config.DEFAULT_WAREHOUSE_SKU_ALLOCATIONS[i] if i < len(core_config.DEFAULT_WAREHOUSE_SKU_ALLOCATIONS) else [50, 50, 50]
                }
                for i in range(len(self.warehouses))
            ],
            'distance_control': core_config.DEFAULT_SETTINGS.get('distance_control', {
                'radius_km': 15,
                'density_strategy': 'clustered',
                'clustering_factor': 0.7,
                'ring_count': 3,
                'min_node_distance': 0.5,
                'max_orders_per_km2': 0.1
            }),
            'random_seed': self._current_seed
        }

        return {
            'skus': skus_list,
            'warehouses': warehouses_list,
            'orders': orders_list,
            'generation_config': generation_config
        }

    def load_scenario(self, scenario: Dict):
        """Load a dynamic scenario without generation.

        The expected dictionary format is the output of export_scenario():
          - skus: [{sku_id, weight_kg, volume_m3}]
          - warehouses: [{id, location_node_id, inventory: {sku_id: qty}, vehicles: [specs...]}]
          - orders: [{id, destination_node_id, requested_items: {sku_id: qty}}]
          - generation_config: {clustering parameters, random_seed, etc.} (optional)

        If generation_config is provided, it will be stored for future reference.
        Static road network (nodes/edges) is automatically loaded from package data.
        """
        import pandas as pd

        skus_input = scenario.get('skus', [])
        warehouses_input = scenario.get('warehouses', [])
        orders_input = scenario.get('orders', [])
        generation_config = scenario.get('generation_config', {})

        if not skus_input or not warehouses_input or not orders_input:
            raise ValueError("Scenario is missing one or more required sections: skus, warehouses, orders")

        # Store generation config for future reference
        if generation_config:
            self._stored_generation_config = generation_config
            # Set the random seed if provided
            if 'random_seed' in generation_config:
                self._current_seed = generation_config['random_seed']

        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
        edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))
        
        nodes_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
        if 'u' in edges_df.columns and 'v' in edges_df.columns:
            edges_df.rename(columns={'u': 'start_node', 'v': 'end_node'}, inplace=True)
        if 'length' in edges_df.columns:
            edges_df['distance_km'] = edges_df['length'] / 1000

        skus: List[SKU] = []
        for s in skus_input:
            skus.append(SKU(
                sku_id=s['sku_id'],
                weight_kg=float(s['weight_kg']),
                volume_m3=float(s['volume_m3'])
            ))

        node_lookup: Dict[int, Node] = {}
        for _, row in nodes_df.iterrows():
            node_lookup[int(row['node_id'])] = Node(int(row['node_id']), float(row['lat']), float(row['lon']))

        warehouses: List[Warehouse] = []
        all_vehicles: List[Vehicle] = []

        for w in warehouses_input:
            loc_id = int(w['location_node_id'])
            if loc_id not in node_lookup:
                raise ValueError(f"Warehouse {w['id']} references unknown node {loc_id}")
            wh = Warehouse(w['id'], node_lookup[loc_id])

            for sku_id, qty in (w.get('inventory') or {}).items():
                wh.inventory[sku_id] = int(qty)

            for vs in (w.get('vehicles') or []):
                veh = Vehicle(
                    vs['id'],
                    vs['type'],
                    vs.get('home_warehouse_id', w['id']),
                    capacity_weight_kg=float(vs['capacity_weight_kg']),
                    capacity_volume_m3=float(vs['capacity_volume_m3']),
                    max_distance_km=float(vs['max_distance_km']),
                    cost_per_km=float(vs['cost_per_km']),
                    fixed_cost=float(vs['fixed_cost'])
                )
                wh.vehicles.append(veh)
                all_vehicles.append(veh)

            warehouses.append(wh)

        orders: List[Order] = []
        for o in orders_input:
            dest_id = int(o['destination_node_id'])
            if dest_id not in node_lookup:
                raise ValueError(f"Order {o['id']} references unknown node {dest_id}")
            order = Order(o['id'], node_lookup[dest_id])
            for sku_id, qty in (o.get('requested_items') or {}).items():
                order.requested_items[sku_id] = int(qty)
            orders.append(order)

        self._initialize_environment(nodes_df, edges_df, warehouses, orders, skus, all_vehicles)
        self._reset_vehicle_states()

    def get_stored_generation_config(self) -> Optional[Dict]:
        """Get the generation configuration stored from a loaded scenario.
        
        Returns:
            Dict containing clustering parameters and generation settings, or None if not available.
        """
        return getattr(self, '_stored_generation_config', None)

    def validate_solution_business_logic(self, solution: Dict) -> Tuple[bool, str]:
        """Validate solution business logic."""
        return self.validator.validate_solution_business_logic(solution)

    def validate_solution_complete(self, solution: Dict) -> Tuple[bool, str, Dict]:
        """Comprehensive solution validation."""
        return self.validator.validate_solution_complete(solution)

    def calculate_solution_cost(self, solution: Dict) -> float:
        """Calculate the total operational cost of a solution."""
        return self.metrics_calculator.calculate_solution_cost(solution)

    def get_solution_statistics(self, solution: Dict, validation_details: Dict = None) -> Dict:
        """Get comprehensive solution statistics."""
        return self.metrics_calculator.get_solution_statistics(solution, validation_details)

    def get_solution_fulfillment_summary(self, solution: Dict, validation_details: Dict = None) -> Dict:
        """Get comprehensive fulfillment summary for entire solution."""
        return self.metrics_calculator.get_solution_fulfillment_summary(solution, validation_details)

    def set_solver(self, solver_function):
        """Set the solver function for the environment."""
        self._solver_function = solver_function

    def launch_dashboard(self, port: int = 8501):
        """Launch the dashboard with the current solver.
        
        Args:
            port: Port number for the dashboard (default: 8501)
        """
        if not hasattr(self, '_solver_function'):
            raise ValueError("No solver set. Call set_solver() first.")
        
        self.reset_all_state()
        
        import subprocess
        import sys
        import os
        
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.py')
        
        if not os.path.exists(dashboard_path):
            raise FileNotFoundError(f"Dashboard not found at: {dashboard_path}")
        
        print("Launching Robin Logistics Dashboard...")
        print(f"Local URL: http://localhost:{port}")
        print("To stop the dashboard, press Ctrl+C in this terminal")
        
        try:
            solver_func = self._solver_function
            func_name = getattr(solver_func, "__name__", None)

            try:
                module_name = solver_func.__module__
            except Exception:
                module_name = None

            if not module_name:
                raise ValueError("Custom solver must be importable (have a valid __module__). Define it in a module and import it before setting.")

            # Export current scenario to temporary file for dashboard
            import tempfile
            import json
            scenario = self.export_scenario()
            temp_dir = tempfile.gettempdir()
            scenario_path = os.path.join(temp_dir, "robin_dashboard_scenario.json")
            
            with open(scenario_path, 'w') as f:
                json.dump(scenario, f, indent=2)

            env_vars = os.environ.copy()
            env_vars["ROBIN_SOLVER"] = f"{module_name}:{func_name}"
            env_vars["ROBIN_SCENARIO_PATH"] = scenario_path

            cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path, "--server.port", str(port)]
            subprocess.run(cmd, check=True, env=env_vars)
        except subprocess.CalledProcessError as e:
            print(f"Failed to launch dashboard: {e}")
            print("Make sure Streamlit is installed: pip install streamlit")
        except KeyboardInterrupt:
            print("\nDashboard stopped by user")
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Check your Python environment and dependencies")

    def run_headless(self, run_id: str = "run_001"):
        """Run the solver headlessly and save results."""
        if not hasattr(self, '_solver_function'):
            raise ValueError("No solver set. Call set_solver() first.")
        
        self.reset_all_state()
        
        from .headless import HeadlessRunner
        runner = HeadlessRunner()
        runner.env = self
        results = runner.run_solver(self._solver_function, "custom_solver", run_id)
        return results













