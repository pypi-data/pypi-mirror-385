# Robin Logistics Environment

A comprehensive logistics optimization environment for hackathons and competitions. This package provides all the infrastructure needed to build and test logistics solvers without implementing the solving logic itself.

## 🚀 Quick Start

### For Developers (Testing)

```bash
# Test with base skeleton solver
python main.py

# Test headless mode
python main.py --headless
```

### For Contestants

```python
from robin_logistics import LogisticsEnvironment
from my_solver import my_solver

# Create environment
env = LogisticsEnvironment()

# Set your solver
env.set_solver(my_solver)

# Launch dashboard (automatically uses your solver)
env.launch_dashboard()  # Default port 8501
env.launch_dashboard(port=8502)  # Custom port

# Or run headless
results = env.run_headless("my_run")
```

**Note**: When you call `env.launch_dashboard()`, your solver is automatically passed to the dashboard process. The solver must be defined in an importable module (not inline in REPL).

## 🏗️ Architecture

The environment is designed with a clear separation of concerns and **centralized step-based execution**:

- **Environment**: Provides data access, validation, and **sequential step-based execution**
- **Solver**: Implements the optimization logic and **generates step-based routes** (provided by contestants)
- **Dashboard**: Visualizes solutions and metrics from **centralized step progression data**
- **Headless Mode**: Runs simulations and saves results using **identical centralized calculations**

## ⚙️ Configuration & Scenario Generation

### Build From Configuration
Generate custom scenarios programmatically with full control over all parameters:

```python
# Custom configuration example
custom_config = {
    'random_seed': 42,                    # For reproducible results
    'num_orders': 25,                     # Number of orders to generate
    'min_items_per_order': 2,             # Minimum items per order
    'max_items_per_order': 8,             # Maximum items per order
    
    # SKU distribution (percentages, must sum to 100)
    'sku_percentages': [40, 35, 25],      # Light, Medium, Heavy items
    
    # Geographic distribution control
    'distance_control': {
        'radius_km': 20,                  # Maximum distance from warehouse centroid
        'density_strategy': 'clustered',   # 'uniform', 'clustered', 'ring'
        'clustering_factor': 0.8,         # 0.0 = uniform, 1.0 = highly clustered
        'ring_count': 4,                  # Number of rings for 'ring' strategy
    },
    
    # Per-warehouse configuration
    'warehouse_configs': [
        {
            # Vehicle fleet per warehouse
            'vehicle_counts': {
                'LightVan': 4,
                'MediumTruck': 2,
                'HeavyTruck': 1
            },
            # Inventory allocation (percentages of total demand)
            'sku_inventory_percentages': [60, 70, 50]  # Light, Medium, Heavy
        },
        {
            'vehicle_counts': {
                'LightVan': 2,
                'MediumTruck': 3,
                'HeavyTruck': 2
            },
            'sku_inventory_percentages': [40, 30, 50]
        }
    ]
}

# Generate scenario from config
env.generate_scenario_from_config(custom_config)

# Or generate new scenario with seed
env.generate_new_scenario(seed=42)
```

### Configuration Options Reference

#### **Core Parameters**
- `random_seed`: Integer for reproducible scenarios
- `num_orders`: Number of orders (1-500)
- `min_items_per_order`: Minimum items per order (default: 1)
- `max_items_per_order`: Maximum items per order (default: 10)
- `sku_percentages`: Distribution of SKU types [Light%, Medium%, Heavy%]

#### **Geographic Distribution (`distance_control`)**
- `radius_km`: Maximum distance from warehouse centroid (5-100 km)
- `density_strategy`: Order distribution pattern
  - `'uniform'`: Even distribution across area
  - `'clustered'`: Orders clustered around warehouses
  - `'ring'`: Orders distributed in concentric rings
- `clustering_factor`: Clustering intensity (0.0-1.0, only for 'clustered')
- `ring_count`: Number of rings (only for 'ring' strategy)

#### **Warehouse Configuration**
- `vehicle_counts`: Fleet composition per warehouse
  - `LightVan`: Capacity 800kg, 3m³, 100km range, $1/km
  - `MediumTruck`: Capacity 1600kg, 6m³, 150km range, $1.25/km  
  - `HeavyTruck`: Capacity 5000kg, 20m³, 200km range, $1.5/km
- `sku_inventory_percentages`: Inventory allocation as % of total demand

### Dashboard Configuration UI
The dashboard provides an interactive configuration interface with:
- **Geographic Control**: Radius, distribution strategy, clustering sliders
- **Supply Configuration**: Inventory distribution across warehouses
- **Fleet Configuration**: Vehicle counts per warehouse type
- **Order Settings**: Number of orders and SKU distribution

All dashboard settings map directly to the configuration schema above.

## 📋 Scenario Export/Import

Export and import scenarios with full configuration preservation:

### Export Scenario
```python
# Export current scenario with all generation parameters
scenario_data = env.export_scenario()

# Save to file
import json
with open('my_scenario.json', 'w') as f:
    json.dump(scenario_data, f, indent=2)
```

### Import Scenario
```python
# Load scenario from file
import json
with open('my_scenario.json', 'r') as f:
    scenario_data = json.load(f)

# Load into environment
env.load_scenario(scenario_data)

# Access stored generation config
config = env.get_stored_generation_config()
print(f"Clustering factor: {config['distance_control']['clustering_factor']}")
```

### Scenario Format
The exported scenario includes:
- **skus**: SKU definitions (weight, volume)
- **warehouses**: Warehouse locations, inventory, and vehicles
- **orders**: Order destinations and requirements
- **generation_config**: Complete configuration used to generate the scenario

This allows you to:
1. Export a scenario with specific settings
2. Manually modify orders, inventory, or vehicles
3. Import the modified scenario while preserving generation parameters
4. Recreate identical scenarios later with same configuration

## 📦 Package Structure

```
robin_logistics/
├── environment.py          # Main interface for contestants
├── solvers.py             # Base skeleton solver for testing
├── dashboard.py           # Streamlit-based visualization
├── headless.py            # Headless execution and result saving
└── core/                  # Core components
    ├── models/            # Data models (Node, SKU, Order, Vehicle, Warehouse)
    ├── state/             # State management and orchestration
    ├── network/           # Road network and distance calculations
    ├── validation/        # Solution validation
    ├── metrics/           # Cost and performance calculations
    └── utils/             # Helper utilities
```

## 🔧 Key Features

- **Step-based route execution**: Routes defined as ordered steps with node-bound operations
- **Centralized validation**: Single `validate_route_steps()` method for all route validation
- **Centralized execution**: Single `execute_route_sequential()` method for all route execution
- **Centralized metrics**: Single source of truth for all calculations (cost, distance, fulfillment)
- **No legacy code**: Pure step-based architecture with no aggregated operation fallbacks
- **Real-time constraint checking**: Capacity, inventory, and distance constraints checked at each step
- **Consistent data flow**: Dashboard and headless mode use identical centralized calculations
 - **Isolated state with baseline resets**: Dashboard and headless restore original inventories and clear deliveries between runs
- **Seamless solver integration**: Your solver automatically works in both modes

## 📊 Dashboard Features

- Problem visualization (nodes, warehouses, orders)
- **Step-based route visualization** with accurate node sequence and operations
- **Centralized metrics display** from step progression data (no redundant calculations)
- **Real-time step progression table** showing cumulative distance, weight, volume, and cost
- **Accurate operation display** showing pickups/deliveries at correct nodes from step data
- Order fulfillment tracking with proper rate capping (never exceeds 100%)
- **No legacy fallbacks** - all data comes from centralized step-based system

## 🚛 Headless Mode

Run simulations without the dashboard and save detailed results:

```python
results = env.run_headless("run_001")
# Results saved to 'results/custom_solver_run_001/'
```

Generated files include:
- Solution summary and validation
- Route details and metrics
- Fulfillment analysis with capped rates
- Raw data for further processing
- **All metrics identical to dashboard** (unified calculation source)

## 🔄 Solver Integration

The environment seamlessly integrates your solver across all modes:

- **Headless Mode**: Direct solver execution with result saving
- **Dashboard Mode**: Automatic solver import and execution with enhanced error reporting
- **CLI Mode**: Command-line solver execution with file paths
- **Unified Metrics**: Both modes use identical calculation logic for perfect consistency

Your solver function is automatically passed to the dashboard process when using `env.launch_dashboard()`, ensuring consistent behavior across all execution modes.

### Required Solution Schema (Step-Based)

Solvers must return routes with ordered steps bound to nodes. Each route requires:

```python
{
  'vehicle_id': 'veh_01',
  'steps': [
    {'node_id': start_node, 'pickups': [...], 'deliveries': [], 'unloads': []},
    {'node_id': some_node, 'pickups': [], 'deliveries': [...], 'unloads': []},
    ...
  ]
}
```

The environment validates connectivity, enforces cumulative distance against vehicle limits, and executes operations sequentially per step.

## 🎯 Recent Improvements (v2.8.0+)

### **Unified Metrics Calculator**
- Dashboard and headless now use identical data sources
- No more calculation discrepancies between modes
- Single source of truth for all metrics

### **Enhanced Error Reporting**
- Dashboard shows detailed solver failure reasons
- Validation errors displayed with specific feedback
- Better debugging and troubleshooting

### **Fixed Fulfillment Logic**
- Fulfillment rates properly capped at 100%
- Correct remaining quantity calculations
- Consistent fulfillment tracking across all sections

### **Simplified Cost Analysis**
 - Cumulative cost shown per step (dispatch fixed cost + variable to date)
- Clean cost breakdown: Total, Fixed, Variable costs
- Total distance display
- No redundant metrics or calculations

### **State Management & Reset**
- **Automatic State Reset**: Dashboard automatically resets inventory and vehicle states between runs
- **Manual Reset Methods**: Use `env.reset_all_state()` or `env.complete_reset()` for manual state management
- **Fresh Environment**: Each simulation starts with original inventory levels and empty vehicles

```python
# Manual state management examples
env.reset_all_state()        # Reset inventory, vehicles, order tracking
env.complete_reset(seed=42)  # Full reset + generate new scenario
env._reset_vehicle_states()  # Reset only vehicle loads/capacities
```

## 🧪 Testing

Test the environment with mock data:

```bash
# Run mock tests
python -m tests.test_environment_mock

# Test with mock solvers
python -m tests.test_environment_with_mock_solvers
```

## 📚 Documentation

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Contributing](CONTRIBUTING.md) - Development guidelines
- [Changelog](CHANGELOG.md) - Version history

## 🚀 Installation

```bash
# Install in development mode from source
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.