"""
Network management module for road network and distance calculations.
"""

import networkx as nx
import pandas as pd
from typing import Dict, List, Optional, Tuple
from ..utils.distance import DistanceUtils
import os
import pickle
from importlib import resources


class NetworkManager:
    """
    Manages road network graph and optimized distance calculations.
    Uses pre-calculated distances from edges_df to avoid redundant computation.
    """
    
    def __init__(self, nodes: Dict, edges_df: pd.DataFrame):
        """Initialize network manager with nodes and edges.

        Supports optional on-disk caching via env var ROBIN_NETWORK_CACHE.
        If the cache file exists, loads graph/distances from it and skips CSV processing.
        After building, saves to the cache path if provided and missing.
        """
        self.nodes = nodes
        self._graph = nx.DiGraph()
        self._distance_matrix = {}

        try:
            pkg_resource = resources.files("robin_logistics").joinpath("data/network.pkl")
            with resources.as_file(pkg_resource) as pkg_cache:
                if os.path.exists(pkg_cache):
                    self._load_cache(str(pkg_cache))
                    return
        except Exception:
            pass

        env_val = os.environ.get("ROBIN_NETWORK_CACHE")
        disable_cache = isinstance(env_val, str) and env_val.strip().lower() in {"0", "false", "no", "off", "disable"}
        if env_val and not disable_cache:
            cache_path = env_val
        else:
            cache_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "network.pkl"))

        if not disable_cache and cache_path and os.path.exists(cache_path):
            try:
                self._load_cache(cache_path)
                return
            except Exception:
                pass

        self._build_network(edges_df)

        if not disable_cache and cache_path and not os.path.exists(cache_path):
            try:
                self._save_cache(cache_path)
            except Exception:
                pass
    
    def _build_network(self, edges_df: pd.DataFrame):
        """Build the road network graph from edges data with optimized distance handling."""
        if edges_df.empty:
            return

        if 'u' in edges_df.columns and 'v' in edges_df.columns:
            edges_data = edges_df[['u', 'v']].copy()
        elif 'start_node' in edges_df.columns and 'end_node' in edges_df.columns:
            edges_data = edges_df[['start_node', 'end_node']].copy()
            edges_data.columns = ['u', 'v']
        else:
            raise ValueError("Edges must have either ['u', 'v'] or ['start_node', 'end_node'] columns")

        if 'distance_km' in edges_df.columns:
            edges_data['distance_km'] = edges_df['distance_km']
        elif 'length' in edges_df.columns:
            edges_data['distance_km'] = edges_df['length'] / 1000
        else:
            distances = []
            for _, row in edges_data.iterrows():
                u, v = row['u'], row['v']
                if u in self.nodes and v in self.nodes:
                    nu, nv = self.nodes[u], self.nodes[v]
                    distances.append(DistanceUtils.haversine_km(nu.lat, nu.lon, nv.lat, nv.lon))
                else:
                    distances.append(0.0)
            edges_data['distance_km'] = distances

        for _, row in edges_data.iterrows():
            u, v = int(row['u']), int(row['v'])
            distance = row.get('distance_km', 1.0)

            if u in self.nodes and v in self.nodes:
                self._graph.add_edge(u, v, weight=distance)
                self._distance_matrix[(u, v)] = distance

    def _save_cache(self, cache_path: str):
        """Save graph distances to a binary cache file."""
        edges = [(int(u), int(v), float(data.get('weight', 0.0))) for u, v, data in self._graph.edges(data=True)]
        payload = {
            'edges': edges
        }
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load_cache(self, cache_path: str):
        """Load graph distances from a binary cache file."""
        with open(cache_path, 'rb') as f:
            payload = pickle.load(f)
        edges = payload.get('edges', [])
        for u, v, dist in edges:
            if u in self.nodes and v in self.nodes:
                self._graph.add_edge(u, v, weight=dist)
                self._distance_matrix[(u, v)] = dist
    
    def has_edge(self, node1: int, node2: int) -> bool:
        """Check if there's a direct edge between two nodes."""
        return self._graph.has_edge(node1, node2)
    
    def get_distance(self, node1: int, node2: int) -> Optional[float]:
        """
        Get direct distance between two connected nodes.
        Returns None if no direct connection exists.
        """
        return self._distance_matrix.get((node1, node2))
    
    def get_route_distance(self, route: List[int]) -> float:
        """
        Calculate total distance for a route (list of node IDs).
        Uses pre-calculated distances from distance matrix.
        """
        if not route or len(route) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(route) - 1):
            distance = self.get_distance(route[i], route[i + 1])
            if distance is None:
                return 0.0
            total_distance += distance
        
        return total_distance
    
    def get_road_network_data(self) -> Dict:
        """Get complete road network data for pathfinding."""
        nodes = {}
        for node_id, node in self.nodes.items():
            nodes[node_id] = {'lat': node.lat, 'lon': node.lon}

        edges = []
        adjacency_list = {}

        for u, v, data in self._graph.edges(data=True):
            edges.append({
                'from': u,
                'to': v,
                'distance': data['weight']
            })

            if u not in adjacency_list:
                adjacency_list[u] = []
            adjacency_list[u].append(v)

        return {
            'nodes': nodes,
            'edges': edges,
            'adjacency_list': adjacency_list
        }
    

