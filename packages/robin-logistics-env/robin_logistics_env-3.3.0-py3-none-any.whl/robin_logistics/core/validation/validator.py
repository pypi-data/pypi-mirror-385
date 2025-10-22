"""
Solution validation module for comprehensive route and operation validation.
"""

from typing import Dict, List, Tuple, Optional, Any


class SolutionValidator:
    """
    Comprehensive solution validation for all constraints and business logic.
    Separated from environment for better modularity and testing.
    """
    
    def __init__(self, warehouses: Dict, vehicles: Dict, orders: Dict, skus: Dict, network_manager):
        """Initialize validator with system components."""
        self.warehouses = warehouses
        self.vehicles = vehicles
        self.orders = orders
        self.skus = skus
        self.network_manager = network_manager
    
    def validate_solution_business_logic(self, solution: Dict) -> Tuple[bool, str]:
        """Validate solution business logic."""
        if not solution or 'routes' not in solution:
            return False, "Solution must contain routes"

        routes = solution['routes']
        if not isinstance(routes, list):
            return False, "Routes must be a list"

        assigned_vehicles = set()

        for route in routes:
            vehicle_id = route.get('vehicle_id')
            if not vehicle_id:
                return False, "Each route must have a vehicle_id"

            if vehicle_id in assigned_vehicles:
                return False, f"Vehicle {vehicle_id} assigned to multiple routes"

            assigned_vehicles.add(vehicle_id)

            if vehicle_id not in self.vehicles:
                return False, f"Unknown vehicle {vehicle_id}"

        return True, "Solution business logic is valid"

    def validate_route_steps(self, vehicle_id: str, steps: List[Dict]) -> Tuple[bool, str]:
        """
        Validate a route provided as ordered steps with node-bound operations.

        Enforces sequential feasibility with capacity, inventory, and connectivity.
        """
        if vehicle_id not in self.vehicles:
            return False, f"Unknown vehicle {vehicle_id}"

        if not steps or len(steps) < 2:
            return False, "Sequential route must have at least 2 steps"

        vehicle = self.vehicles[vehicle_id]

        route_nodes: List[int] = []
        for step in steps:
            node_id = step.get('node_id')
            if node_id is None:
                return False, "Each step must include node_id"
            route_nodes.append(node_id)

        warehouse_node_id = None
        for wh in self.warehouses.values():
            if wh.id == vehicle.home_warehouse_id:
                warehouse_node_id = wh.location.id
                break
        if warehouse_node_id is None:
            return False, f"Warehouse {vehicle.home_warehouse_id} not found for vehicle {vehicle_id}"

        if route_nodes[0] != warehouse_node_id or route_nodes[-1] != warehouse_node_id:
            return False, f"Sequential route must start and end at home warehouse node {warehouse_node_id}"

        cumulative_distance = 0.0
        for i in range(len(route_nodes) - 1):
            u = route_nodes[i]
            v = route_nodes[i + 1]
            if u == v:
                continue
            if not self.network_manager.has_edge(u, v):
                return False, f"No road connection from node {u} to {v}"
            leg_distance = self.network_manager.get_distance(u, v) or 0.0
            cumulative_distance += leg_distance
            if cumulative_distance > vehicle.max_distance:
                return False, (
                    f"Cumulative distance exceeded at step {i+2}: "
                    f"{cumulative_distance:.2f} km > max {vehicle.max_distance:.2f} km"
                )

        current_weight = 0.0
        current_volume = 0.0
        vehicle_inventory: Dict[str, int] = {}
        staged_wh_inventory: Dict[str, Dict[str, int]] = {
            wh_id: inv.inventory.copy() if hasattr(inv, 'inventory') else {}
            for wh_id, inv in self.warehouses.items()
        }

        for idx, step in enumerate(steps):
            node_id = step.get('node_id')

            # 1) Unloads first (free capacity / return inventory)
            for unload in (step.get('unloads') or []):
                warehouse_id = unload.get('warehouse_id')
                sku_id = unload.get('sku_id')
                quantity = int(unload.get('quantity', 0))
                if quantity < 0:
                    return False, f"Negative quantity in unload at step {idx+1}"
                if warehouse_id not in self.warehouses:
                    return False, f"Unknown warehouse {warehouse_id} at step {idx+1}"
                wh = self.warehouses[warehouse_id]
                if wh.location.id != node_id:
                    return False, f"Unload at step {idx+1} not at correct warehouse node"
                have_qty = vehicle_inventory.get(sku_id, 0)
                if have_qty < quantity:
                    return False, f"Insufficient {sku_id} on vehicle for unload at step {idx+1}: need {quantity}, have {have_qty}"
                sku = self.skus[sku_id]
                sub_w = sku.weight * quantity
                sub_v = sku.volume * quantity
                current_weight -= sub_w
                current_volume -= sub_v
                vehicle_inventory[sku_id] = have_qty - quantity
                if vehicle_inventory[sku_id] <= 0:
                    del vehicle_inventory[sku_id]
                prev = staged_wh_inventory.get(warehouse_id, {}).get(sku_id, 0)
                if warehouse_id not in staged_wh_inventory:
                    staged_wh_inventory[warehouse_id] = {}
                staged_wh_inventory[warehouse_id][sku_id] = prev + quantity

            # 2) Pickups next (after potential unloads)
            for pickup in (step.get('pickups') or []):
                warehouse_id = pickup.get('warehouse_id')
                sku_id = pickup.get('sku_id')
                quantity = int(pickup.get('quantity', 0))
                if quantity < 0:
                    return False, f"Negative quantity in pickup at step {idx+1}"
                if warehouse_id not in self.warehouses:
                    return False, f"Unknown warehouse {warehouse_id} at step {idx+1}"
                wh = self.warehouses[warehouse_id]
                if wh.location.id != node_id:
                    return False, f"Pickup at step {idx+1} not at correct warehouse node"
                if sku_id not in self.skus:
                    return False, f"Unknown SKU {sku_id} at step {idx+1}"
                available = staged_wh_inventory.get(warehouse_id, {}).get(sku_id, 0)
                if available < quantity:
                    return False, f"Insufficient inventory for {sku_id} at step {idx+1}"
                sku = self.skus[sku_id]
                add_w = sku.weight * quantity
                add_v = sku.volume * quantity
                if current_weight + add_w > vehicle.capacity_weight:
                    return False, f"Weight capacity exceeded at step {idx+1}"
                if current_volume + add_v > vehicle.capacity_volume:
                    return False, f"Volume capacity exceeded at step {idx+1}"
                current_weight += add_w
                current_volume += add_v
                vehicle_inventory[sku_id] = vehicle_inventory.get(sku_id, 0) + quantity
                if warehouse_id not in staged_wh_inventory:
                    staged_wh_inventory[warehouse_id] = {}
                staged_wh_inventory[warehouse_id][sku_id] = available - quantity

            # 3) Deliveries last
            for delivery in (step.get('deliveries') or []):
                order_id = delivery.get('order_id')
                sku_id = delivery.get('sku_id')
                quantity = int(delivery.get('quantity', 0))
                if quantity < 0:
                    return False, f"Negative quantity in delivery at step {idx+1}"
                if order_id not in self.orders:
                    return False, f"Unknown order {order_id} at step {idx+1}"
                order = self.orders[order_id]
                if order.destination.id != node_id:
                    return False, f"Delivery at step {idx+1} not at order destination node"
                if sku_id not in self.skus:
                    return False, f"Unknown SKU {sku_id} at step {idx+1}"
                have_qty = vehicle_inventory.get(sku_id, 0)
                if have_qty < quantity:
                    return False, f"Insufficient {sku_id} on vehicle for delivery at step {idx+1}: need {quantity}, have {have_qty}"
                sku = self.skus[sku_id]
                sub_w = sku.weight * quantity
                sub_v = sku.volume * quantity
                current_weight -= sub_w
                current_volume -= sub_v
                vehicle_inventory[sku_id] = have_qty - quantity
                if vehicle_inventory[sku_id] <= 0:
                    del vehicle_inventory[sku_id]

        total_distance = self.network_manager.get_route_distance(route_nodes)
        if total_distance > vehicle.max_distance:
            return False, f"Route distance {total_distance:.2f} km exceeds vehicle max distance {vehicle.max_distance:.2f} km"

        return True, "Sequential route is valid"
    
    def validate_solution_complete(self, solution: Dict) -> Tuple[bool, str, Dict]:
        """Comprehensive solution validation with detailed failure information."""
        is_business_valid, business_msg = self.validate_solution_business_logic(solution)
        if not is_business_valid:
            return False, f"Business logic validation failed: {business_msg}", {}

        routes = solution.get('routes', [])
        if not routes:
            # Empty solution is considered invalid - no routes to execute
            validation_details = {
                'valid_routes': [],
                'invalid_routes': [],
                'total_routes': 0,
                'valid_count': 0,
                'invalid_count': 0
            }
            return False, "Solution is empty - no routes provided", validation_details

        valid_routes = []
        invalid_routes = []
        
        for i, route in enumerate(routes):
            vehicle_id = route.get('vehicle_id')
            steps = route.get('steps', [])

            if not vehicle_id or not steps:
                invalid_routes.append({
                    'route_index': i,
                    'route_data': route,
                    'error': f"Route {i + 1} missing vehicle_id or steps",
                    'vehicle_id': vehicle_id,
                    'steps_count': len(steps) if steps else 0
                })
                continue

            is_valid, error_msg = self.validate_route_steps(vehicle_id, steps)
            if not is_valid:
                invalid_routes.append({
                    'route_index': i,
                    'route_data': route,
                    'error': f"Route {i + 1} validation failed: {error_msg}",
                    'vehicle_id': vehicle_id,
                    'steps_count': len(steps)
                })
            else:
                valid_routes.append(route)

        validation_details = {
            'valid_routes': valid_routes,
            'invalid_routes': invalid_routes,
            'total_routes': len(routes),
            'valid_count': len(valid_routes),
            'invalid_count': len(invalid_routes)
        }

        if invalid_routes:
            route_word = "route" if len(invalid_routes) == 1 else "routes"
            return False, f"Solution has {len(invalid_routes)} invalid {route_word}", validation_details
        
        return True, "Solution is completely valid", validation_details
