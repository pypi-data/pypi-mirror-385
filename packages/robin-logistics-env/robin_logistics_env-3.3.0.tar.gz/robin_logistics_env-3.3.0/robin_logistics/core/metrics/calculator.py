"""
Metrics calculation module for comprehensive solution analysis.
"""

from typing import Dict, List, Any


class MetricsCalculator:
    """
    Centralized metrics and statistics calculation for solutions.
    Handles all performance metrics, costs, and fulfillment analysis.
    """
    
    def __init__(self, warehouses: Dict, vehicles: Dict, orders: Dict, skus: Dict, network_manager):
        """Initialize calculator with system components."""
        self.warehouses = warehouses
        self.vehicles = vehicles
        self.orders = orders
        self.skus = skus
        self.network_manager = network_manager
    
    def calculate_solution_cost(self, solution: Dict) -> float:
        """Calculate the total operational cost of a solution."""
        if not solution or not isinstance(solution, dict):
            return 0.0
            
        total_cost = 0.0
        routes = solution.get("routes", [])
        
        if not routes:
            return 0.0

        for route_info in routes:
            vehicle_id = route_info.get('vehicle_id')
            steps = route_info.get('steps', [])

            if vehicle_id and steps and vehicle_id in self.vehicles:
                vehicle = self.vehicles[vehicle_id]
                total_cost += vehicle.fixed_cost
                route_nodes = [step.get('node_id') for step in steps if step.get('node_id')]
                route_distance = self.network_manager.get_route_distance(route_nodes)
                total_cost += route_distance * vehicle.cost_per_km

        return total_cost

    def calculate_cost_breakdown(self, solution: Dict) -> Dict[str, float]:
        """Return fixed, variable and total costs for the solution."""
        if not solution or not isinstance(solution, dict):
            return {
                'fixed_cost_total': 0.0,
                'variable_cost_total': 0.0,
                'total_cost': 0.0
            }
            
        fixed_total = 0.0
        variable_total = 0.0
        routes = solution.get("routes", [])
        
        if not routes:
            return {
                'fixed_cost_total': 0.0,
                'variable_cost_total': 0.0,
                'total_cost': 0.0
            }

        for route_info in routes:
            vehicle_id = route_info.get('vehicle_id')
            steps = route_info.get('steps', [])

            if vehicle_id and steps and vehicle_id in self.vehicles:
                vehicle = self.vehicles[vehicle_id]
                fixed_total += vehicle.fixed_cost
                route_nodes = [step.get('node_id') for step in steps if step.get('node_id')]
                route_distance = self.network_manager.get_route_distance(route_nodes)
                variable_total += route_distance * vehicle.cost_per_km

        return {
            'fixed_cost_total': fixed_total,
            'variable_cost_total': variable_total,
            'total_cost': fixed_total + variable_total
        }
    
    def get_solution_statistics(self, solution: Dict, validation_details: Dict = None) -> Dict:
        """Get comprehensive solution statistics for valid routes only."""
        if not solution or not isinstance(solution, dict):
            return self._get_empty_statistics()
            
        routes = solution.get('routes', [])
        if not routes:
            return self._get_empty_statistics()

        # Filter to only valid routes if validation details provided
        valid_routes = routes
        if validation_details and 'valid_routes' in validation_details:
            valid_routes = validation_details['valid_routes']
        
        vehicles_used = set()
        total_distance = 0.0

        for route in valid_routes:
            vehicle_id = route.get('vehicle_id')
            steps = route.get('steps', [])

            if vehicle_id and steps:
                vehicles_used.add(vehicle_id)
                route_nodes = [step.get('node_id') for step in steps if step.get('node_id')]
                route_distance = self.network_manager.get_route_distance(route_nodes)
                total_distance += route_distance

        cost_breakdown = self.calculate_cost_breakdown({'routes': valid_routes})
        total_cost = cost_breakdown['total_cost']
        fulfillment_summary = self.get_solution_fulfillment_summary({'routes': valid_routes})

        total_vehicles = len(self.vehicles)
        total_orders = len(self.orders)

        vehicle_utilization_ratio = len(vehicles_used) / total_vehicles if total_vehicles > 0 else 0
        unique_orders_served = fulfillment_summary.get('orders_served', 0)

        return {
            'total_routes': len(valid_routes),
            'unique_vehicles_used': len(vehicles_used),
            'total_vehicles': total_vehicles,
            'unique_orders_served': unique_orders_served,
            'total_orders': total_orders,
            'total_distance': total_distance,
            'total_cost': total_cost,
            'fixed_cost_total': cost_breakdown['fixed_cost_total'],
            'variable_cost_total': cost_breakdown['variable_cost_total'],
            'vehicle_utilization_ratio': vehicle_utilization_ratio,
            'orders_fulfillment_ratio': fulfillment_summary['average_fulfillment_rate'] / 100.0,
            'average_fulfillment_rate': fulfillment_summary['average_fulfillment_rate'],
            'fully_fulfilled_orders': fulfillment_summary['fully_fulfilled_orders']
        }
    
    def _get_empty_statistics(self) -> Dict:
        """Return empty statistics when no solution is provided."""
        return {
            'total_routes': 0,
            'unique_vehicles_used': 0,
            'total_vehicles': len(self.vehicles),
            'unique_orders_served': 0,
            'total_orders': len(self.orders),
            'total_distance': 0.0,
            'total_cost': 0.0,
            'fixed_cost_total': 0.0,
            'variable_cost_total': 0.0,
            'vehicle_utilization_ratio': 0.0,
            'orders_fulfillment_ratio': 0.0,
            'average_fulfillment_rate': 0.0,
            'fully_fulfilled_orders': 0
        }
    
    def get_solution_fulfillment_summary(self, solution: Dict, validation_details: Dict = None) -> Dict:
        """Get comprehensive fulfillment summary for entire solution."""
        if not solution or not isinstance(solution, dict):
            return self._get_empty_fulfillment_summary()
            
        routes = solution.get('routes', [])
        if not routes:
            return self._get_empty_fulfillment_summary()

        # Filter to only valid routes if validation details provided
        valid_routes = routes
        if validation_details and 'valid_routes' in validation_details:
            valid_routes = validation_details['valid_routes']

        order_fulfillment = {}
        vehicles_used = set()
        total_distance = 0.0

        for order_id, order in self.orders.items():
            order_fulfillment[order_id] = {
                'requested': dict(order.requested_items),
                'delivered': {},
                'remaining': {}
            }

        for route in valid_routes:
            vehicle_id = route.get('vehicle_id')
            steps = route.get('steps', [])

            if vehicle_id and steps:
                vehicles_used.add(vehicle_id)
                route_nodes = [step.get('node_id') for step in steps if step.get('node_id')]
                route_distance = self.network_manager.get_route_distance(route_nodes)
                total_distance += route_distance

        for order_id, order in self.orders.items():
            delivered_from_state = getattr(order, '_delivered_items', {}) or {}
            if delivered_from_state:
                for sku_id, qty in delivered_from_state.items():
                    if sku_id in order_fulfillment[order_id]['requested']:
                        order_fulfillment[order_id]['delivered'][sku_id] = order_fulfillment[order_id]['delivered'].get(sku_id, 0) + qty
            else:
                for route in valid_routes:
                    for step in route.get('steps', []) or []:
                        for d in step.get('deliveries', []) or []:
                            if d.get('order_id') == order_id:
                                sku_id = d.get('sku_id')
                                qty = d.get('quantity', 0)
                                if sku_id in order_fulfillment[order_id]['requested']:
                                    order_fulfillment[order_id]['delivered'][sku_id] = order_fulfillment[order_id]['delivered'].get(sku_id, 0) + qty


        total_fulfillment_rate = 0.0
        fully_fulfilled_orders = 0

        for order_id, fulfillment in order_fulfillment.items():
            total_requested = sum(fulfillment['requested'].values())
            capped_delivered_per_sku = {
                sku_id: min(fulfillment['delivered'].get(sku_id, 0), requested_qty)
                for sku_id, requested_qty in fulfillment['requested'].items()
            }
            total_capped_delivered = sum(capped_delivered_per_sku.values())

            for sku_id in fulfillment['requested']:
                requested = fulfillment['requested'][sku_id]
                delivered_raw = fulfillment['delivered'].get(sku_id, 0)
                delivered_capped = min(delivered_raw, requested)
                fulfillment['remaining'][sku_id] = max(0, requested - delivered_capped)

            if total_requested > 0:
                fulfillment['fulfillment_rate'] = (total_capped_delivered / total_requested) * 100
                total_fulfillment_rate += fulfillment['fulfillment_rate']

                if total_capped_delivered >= total_requested:
                    fully_fulfilled_orders += 1
            else:
                fulfillment['fulfillment_rate'] = 100.0
                total_fulfillment_rate += 100.0
                fully_fulfilled_orders += 1

        avg_fulfillment_rate = total_fulfillment_rate / len(self.orders) if self.orders else 0

        total_cost = self.calculate_solution_cost(solution)

        return {
            'total_orders': len(self.orders),
            'orders_served': len([
                o for o in order_fulfillment.values()
                if sum(min(o['delivered'].get(sku_id, 0), req)
                       for sku_id, req in o['requested'].items()) > 0
            ]),
            'fully_fulfilled_orders': fully_fulfilled_orders,
            'total_vehicles': len(self.vehicles),
            'vehicles_used': len(vehicles_used),
            'total_distance': total_distance,
            'total_cost': total_cost,
            'average_fulfillment_rate': avg_fulfillment_rate,
            'order_fulfillment_details': order_fulfillment,
            'vehicle_utilization': len(vehicles_used) / len(self.vehicles) if self.vehicles else 0
        }
    
    def _get_empty_fulfillment_summary(self) -> Dict:
        """Return empty fulfillment summary when no solution is provided."""
        return {
            'total_orders': len(self.orders),
            'orders_served': 0,
            'fully_fulfilled_orders': 0,
            'total_vehicles': len(self.vehicles),
            'vehicles_used': 0,
            'total_distance': 0.0,
            'total_cost': 0.0,
            'average_fulfillment_rate': 0.0,
            'order_fulfillment_details': {}
        }
