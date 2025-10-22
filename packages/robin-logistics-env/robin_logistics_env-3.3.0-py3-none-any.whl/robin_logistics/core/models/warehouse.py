
class Warehouse:
    """Represents a depot with dynamic inventory and a vehicle fleet."""

    def __init__(self, warehouse_id, location_node):
        """
        Initialize a Warehouse.

        Args:
            warehouse_id: Unique identifier for the warehouse
            location_node: Node object representing the warehouse location
        """
        self.id = warehouse_id
        self.location = location_node
        self.inventory = {}
        self.vehicles = []


    def __repr__(self):
        return f"Warehouse({self.id} at {self.location})"