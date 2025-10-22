"""
Mock solvers that generate different types of solutions for testing environment validation.
These solvers test various edge cases and validation scenarios.
"""

def valid_mock_solver(env):
    """
    Generates a valid solution for testing environment validation.
    Uses simple but correct logic.
    """
    solution = {'routes': []}
    
    order_ids = env.get_all_order_ids()
    vehicle_ids = env.get_available_vehicles()
    road_network = env.get_road_network_data()
    adjacency_list = road_network['adjacency_list']
    
    # Simple assignment: one order per vehicle
    for i, order_id in enumerate(order_ids[:len(vehicle_ids)]):
        vehicle_id = vehicle_ids[i]
        order_location = env.get_order_location(order_id)
        home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
        
        # Create simple round trip
        route = create_simple_path(home_warehouse, order_location, adjacency_list)
        if route:
            steps = [{'node_id': int(n), 'pickups': [], 'deliveries': [], 'unloads': []} for n in route]
            solution['routes'].append({
                'vehicle_id': vehicle_id,
                'steps': steps
            })
    
    return solution


def invalid_route_solver(env):
    """
    Generates solution with invalid routes for testing validation.
    """
    vehicle_ids = env.get_available_vehicles()
    
    return {
        'routes': [
            {
                'vehicle_id': vehicle_ids[0] if vehicle_ids else 'fake_vehicle',
                'steps': [
                    {'node_id': 1, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 999, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 1, 'pickups': [], 'deliveries': [], 'unloads': []}
                ]
            }
        ]
    }


def capacity_violation_solver(env):
    """
    Generates solution that violates vehicle capacity constraints.
    """
    vehicle_ids = env.get_available_vehicles()
    order_ids = env.get_all_order_ids()
    
    if not vehicle_ids or not order_ids:
        return {'routes': []}
    
    home_warehouse = env.get_vehicle_home_warehouse(vehicle_ids[0])
    
    # Create route that's too long for vehicle capacity
    long_nodes = ([home_warehouse, order_ids[0] if order_ids else home_warehouse] * 600)[:1200] + [home_warehouse]
    steps = [{'node_id': int(n) if isinstance(n, int) else home_warehouse, 'pickups': [], 'deliveries': [], 'unloads': []} for n in long_nodes]
    return {
        'routes': [
            {
                'vehicle_id': vehicle_ids[0],
                'steps': steps
            }
        ]
    }


def wrong_warehouse_solver(env):
    """
    Generates solution where vehicles don't start/end at home warehouse.
    """
    vehicle_ids = env.get_available_vehicles()
    
    if not vehicle_ids:
        return {'routes': []}
    
    return {
        'routes': [
            {
                'vehicle_id': vehicle_ids[0],
                'steps': [
                    {'node_id': 2, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 3, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 4, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 2, 'pickups': [], 'deliveries': [], 'unloads': []}
                ]
            }
        ]
    }


def empty_solution_solver(env):
    """
    Generates empty solution for testing edge cases.
    """
    return {'routes': []}


def malformed_solution_solver(env):
    """
    Generates malformed solution for testing error handling.
    """
    return {
        'routes': [
            {
                # Missing vehicle_id
                'steps': [
                    {'node_id': 1, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 2, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 3, 'pickups': [], 'deliveries': [], 'unloads': []},
                    {'node_id': 1, 'pickups': [], 'deliveries': [], 'unloads': []}
                ]
            },
            {
                'vehicle_id': 'valid_vehicle'
                # Missing steps
            }
        ]
    }


def partial_fulfillment_solver(env):
    """
    Generates solution with detailed pickup/delivery operations for testing fulfillment tracking.
    """
    solution = {'routes': []}
    
    order_ids = env.get_all_order_ids()
    vehicle_ids = env.get_available_vehicles()
    road_network = env.get_road_network_data()
    adjacency_list = road_network['adjacency_list']
    
    if not order_ids or not vehicle_ids:
        return solution
    
    # Create route with detailed operations
    vehicle_id = vehicle_ids[0]
    order_id = order_ids[0]
    order_location = env.get_order_location(order_id)
    home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
    
    route = create_simple_path(home_warehouse, order_location, adjacency_list)
    
    if route:
        requirements = env.get_order_requirements(order_id)
        steps = []
        # First node: pickups at a warehouse that has required SKUs (use home WH as default)
        pickup_ops = []
        for sku_id, quantity in requirements.items():
            warehouses_with_sku = env.get_warehouses_with_sku(sku_id, quantity)
            wh_id = warehouses_with_sku[0] if warehouses_with_sku else None
            if wh_id:
                pickup_ops.append({'warehouse_id': wh_id, 'sku_id': sku_id, 'quantity': quantity})
        steps.append({'node_id': route[0], 'pickups': pickup_ops, 'deliveries': [], 'unloads': []})
        
        # Intermediate nodes (no ops) until destination
        for node_id in route[1:-1]:
            if node_id == order_location:
                # Deliver half at destination
                delivery_ops = []
                for sku_id, quantity in requirements.items():
                    delivery_ops.append({'order_id': order_id, 'sku_id': sku_id, 'quantity': max(1, quantity // 2)})
                steps.append({'node_id': node_id, 'pickups': [], 'deliveries': delivery_ops, 'unloads': []})
            else:
                steps.append({'node_id': node_id, 'pickups': [], 'deliveries': [], 'unloads': []})
        
        # Return to home
        steps.append({'node_id': route[-1], 'pickups': [], 'deliveries': [], 'unloads': []})
        
        solution['routes'].append({
            'vehicle_id': vehicle_id,
            'steps': steps
        })
    
    return solution


def create_simple_path(start, end, adjacency_list):
    """
    Simple BFS pathfinding for mock solvers.
    """
    if start == end:
        return [start, start]  # Simple round trip
    
    from collections import deque
    
    # Find path to destination
    queue = deque([(start, [start])])
    visited = {start}
    path_to_end = None
    
    while queue and len(queue) < 1000:  # Prevent infinite loops
        current, path = queue.popleft()
        
        if len(path) > 20:  # Reasonable path limit
            continue
        
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                new_path = path + [neighbor_int]
                
                if neighbor_int == end:
                    path_to_end = new_path
                    break
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, new_path))
        
        if path_to_end:
            break
    
    if not path_to_end:
        return None  # No path found
    
    # Find path back to start
    queue = deque([(end, [end])])
    visited = {end}
    path_to_start = None
    
    while queue and len(queue) < 1000:
        current, path = queue.popleft()
        
        if len(path) > 20:
            continue
        
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                new_path = path + [neighbor_int]
                
                if neighbor_int == start:
                    path_to_start = new_path
                    break
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, new_path))
        
        if path_to_start:
            break
    
    if not path_to_start:
        return None  # No path back
    
    # Combine paths
    return path_to_end + path_to_start[1:]  # Avoid duplicate end node


# Dictionary of all mock solvers for easy testing
MOCK_SOLVERS = {
    'valid': valid_mock_solver,
    'invalid_route': invalid_route_solver,
    'capacity_violation': capacity_violation_solver,
    'wrong_warehouse': wrong_warehouse_solver,
    'empty_solution': empty_solution_solver,
    'malformed_solution': malformed_solution_solver,
    'partial_fulfillment': partial_fulfillment_solver
}
