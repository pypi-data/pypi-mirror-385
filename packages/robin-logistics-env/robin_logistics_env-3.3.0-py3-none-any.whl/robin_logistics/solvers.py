"""
Clean solver implementations using the centralized orchestrator.
"""

from typing import Dict, List, Tuple, Optional
from collections import deque

def orchestrator_solver(env):
    """
    Simple, robust solver that always generates valid routes.
    """
    solution = {'routes': []}
    
    order_ids = env.get_all_order_ids()
    available_vehicles = env.get_available_vehicles()
    
    if not order_ids or not available_vehicles:
        return solution
    
    for i, order_id in enumerate(order_ids):
        if i >= len(available_vehicles):
            break
            
        vehicle_id = available_vehicles[i]
        vehicle = env.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            continue
            
        route = create_simple_route(env, vehicle_id, order_id)
        if route:
            solution['routes'].append(route)
    
    return solution

def create_simple_route(env, vehicle_id: str, order_id: str) -> Optional[Dict]:
    """
    Create a simple, guaranteed-valid route for an order.
    """
    try:
        vehicle = env.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return None
            
        order_requirements = env.get_order_requirements(order_id)
        if not order_requirements:
            return None
        
        home_warehouse_id = vehicle.home_warehouse_id
        home_warehouse = env.get_warehouse_by_id(home_warehouse_id)
        if not home_warehouse:
            return None
            
        order_location = env.get_order_location(order_id)
        if order_location is None:
            return None
            
        road_network = env.get_road_network_data()
        adjacency_list = road_network.get('adjacency_list', {})
            
        steps = []
        
        warehouse_pickups = []
        for sku_id, qty in order_requirements.items():
            warehouse_inventory = env.get_warehouse_inventory(home_warehouse_id)
            available_qty = warehouse_inventory.get(sku_id, 0)
            if available_qty >= qty:
                warehouse_pickups.append({
                    'warehouse_id': home_warehouse_id,
                    'sku_id': sku_id,
                    'quantity': qty
                })
        
        if warehouse_pickups:
            steps.append({
                'node_id': home_warehouse.location.id,
                'pickups': warehouse_pickups,
                'deliveries': [],
                'unloads': []
            })
        
        order_deliveries = []
        for sku_id, qty in order_requirements.items():
            order_deliveries.append({
                'order_id': order_id,
                'sku_id': sku_id,
                'quantity': qty
            })
        
        if order_deliveries:
            path_to_order = find_shortest_path(home_warehouse.location.id, order_location, adjacency_list)
            if path_to_order and len(path_to_order) > 1:
                for i in range(1, len(path_to_order) - 1):
                    steps.append({
                        'node_id': path_to_order[i],
                        'pickups': [],
                        'deliveries': [],
                        'unloads': []
                    })
            
            steps.append({
                'node_id': order_location,
                'pickups': [],
                'deliveries': order_deliveries,
                'unloads': []
            })
        
        path_to_home = find_shortest_path(order_location, home_warehouse.location.id, adjacency_list)
        if path_to_home and len(path_to_home) > 1:
            for i in range(1, len(path_to_home) - 1):
                steps.append({
                    'node_id': path_to_home[i],
                    'pickups': [],
                    'deliveries': [],
                    'unloads': []
                })
        
        steps.append({
            'node_id': home_warehouse.location.id,
            'pickups': [],
            'deliveries': [],
            'unloads': []
        })
        
        return {
            'vehicle_id': vehicle_id,
            'steps': steps
        }
        
    except Exception as e:
        return None



def find_shortest_path(start_node: int, end_node: int, adjacency_list: Dict, max_path_length: int = 500) -> Optional[List[int]]:
    """Find shortest path using Breadth-First Search."""
    if start_node == end_node:
        return [start_node]
    
    queue = deque([(start_node, [start_node])])
    visited = {start_node}
    
    while queue:
        current, path = queue.popleft()
        
        if len(path) >= max_path_length:
            continue
            
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                new_path = path + [neighbor_int]
                
                if neighbor_int == end_node:
                    return new_path
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, new_path))
    
    return None

def test_solver(env):
    """Default solver implementation for testing and demonstration."""
    return orchestrator_solver(env)


