"""
Copyright 2023–2025 Waii, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from waii_sdk_py import WAII
from waii_sdk_py.kg import GetKnowledgeGraphRequest


class TestKnowledgeGraph(unittest.TestCase):
    def setUp(self):
        WAII.initialize(url="http://localhost:9859/api/")
        result = WAII.Database.get_connections()
        self.result = result
        # Activate the first available connection
        if result.connectors:
            WAII.Database.activate_connection(result.connectors[0].key)

    def test_get_knowledge_graph_smoke(self):
        """
        Smoke test to ensure knowledge graph API returns a valid response with nodes and edges
        """
        # Create a simple request
        request = GetKnowledgeGraphRequest(ask="Show me table relationships")
        
        # Call the knowledge graph API
        response = WAII.knowledge_graph.get_knowledge_graph(request)
        
        # Basic assertions - verify we got a response
        self.assertIsNotNone(response, "Response should not be None")
        self.assertIsNotNone(response.graph, "Graph should not be None")
        
        # Verify the graph has nodes and edges
        self.assertIsNotNone(response.graph.nodes, "Graph should have nodes")
        self.assertIsNotNone(response.graph.edges, "Graph should have edges")
        
        # Verify the graph is not empty (has at least some nodes)
        self.assertGreater(len(response.graph.nodes), 0, "Graph should have at least one node")
        
        # Verify basic structure of nodes (if any exist)
        if response.graph.nodes:
            first_node = response.graph.nodes[0]
            self.assertIsNotNone(first_node.id, "Node should have an id")
            self.assertIsNotNone(first_node.display_name, "Node should have a display_name")
            self.assertIsNotNone(first_node.entity_type, "Node should have an entity_type")
            self.assertIsNotNone(first_node.entity, "Node should have an entity")
        
        # Print summary information about the knowledge graph
        print("\n" + "="*60)
        print("KNOWLEDGE GRAPH SUMMARY")
        print("="*60)
        print(f"Total nodes: {len(response.graph.nodes)}")
        print(f"Total edges: {len(response.graph.edges)}")
        
        # Count nodes by type
        node_types = {}
        for node in response.graph.nodes:
            node_type = node.entity_type
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print("\nNode types distribution:")
        for node_type, count in sorted(node_types.items()):
            print(f"  - {node_type}: {count}")
        
        # Print sample nodes (first 5 of each type)
        print("\nSample nodes by type:")
        for node_type in sorted(node_types.keys()):
            print(f"\n  {node_type.upper()}:")
            nodes_of_type = [n for n in response.graph.nodes if n.entity_type == node_type][:5]
            for node in nodes_of_type:
                print(f"    - {node.display_name} (id: {node.id})")
        
        # Count edges by type  
        edge_types = {}
        for edge in response.graph.edges:
            edge_type = edge.edge_type
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        print("\nEdge types distribution:")
        for edge_type, count in sorted(edge_types.items()):
            print(f"  - {edge_type}: {count}")
        
        # Print sample relationships (first 5)
        if response.graph.edges:
            print("\nSample relationships (first 5):")
            for edge in response.graph.edges[:5]:
                source_node = next((n for n in response.graph.nodes if n.id == edge.source_id), None)
                target_node = next((n for n in response.graph.nodes if n.id == edge.target_id), None)
                if source_node and target_node:
                    direction = "->" if edge.directed else "<->"
                    print(f"  - {source_node.display_name} {direction} {target_node.display_name} ({edge.edge_type})")
                    if edge.description:
                        print(f"    Description: {edge.description}")
        
        print("="*60 + "\n")


if __name__ == '__main__':
    unittest.main() 