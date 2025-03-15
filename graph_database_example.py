import networkx as nx
import json

class GraphDatabase:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node_id, attributes=None):
        if attributes is None:
            attributes = {}
        self.graph.add_node(node_id, **attributes)

    def add_edge(self, node1, node2, attributes=None):
        if attributes is None:
            attributes = {}
        self.graph.add_edge(node1, node2, **attributes)

    def get_node(self, node_id):
        if node_id in self.graph:
            return self.graph.nodes[node_id]
        else:
            return None

    def get_edge(self, node1, node2):
        if self.graph.has_edge(node1, node2):
            return self.graph[node1][node2]
        else:
            return None

    def remove_node(self, node_id):
        if node_id in self.graph:
            self.graph.remove_node(node_id)

    def remove_edge(self, node1, node2):
        if self.graph.has_edge(node1, node2):
            self.graph.remove_edge(node1, node2)

    def save_to_file(self, filename):
        data = nx.readwrite.json_graph.node_link_data(self.graph)
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.graph = nx.readwrite.json_graph.node_link_graph(data)

    def get_neighbors(self, node_id):
        if node_id in self.graph:
            return list(self.graph.neighbors(node_id))
        else:
            return []

    def get_all_nodes(self):
        return list(self.graph.nodes(data=True))

    def get_all_edges(self):
        return list(self.graph.edges(data=True))

    def bfs(self, start_node):
        visited = set()
        queue = [start_node]
        result = []

        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.add(node)
                result.append(node)
                queue.extend(set(self.graph.neighbors(node)) - visited)
        return result

    def dfs(self, start_node):
        visited = set()
        result = []

        def dfs_helper(node):
            visited.add(node)
            result.append(node)
            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    dfs_helper(neighbor)

        dfs_helper(start_node)
        return result

    def shortest_path(self, source, target):
        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return None

    def connected_components(self):
        return [list(component) for component in nx.connected_components(self.graph)]

    def node_degree(self, node_id):
        if node_id in self.graph:
            return self.graph.degree(node_id)
        else:
            return None

    def display_graph(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=nx.get_edge_attributes(self.graph, 'weight'))
        

if __name__ == "__main__":
    db = GraphDatabase()
    db.add_node("A", {"name": "Node A"})
    db.add_node("B", {"name": "Node B"})
    db.add_node("C", {"name": "Node C"})
    db.add_edge("A", "B", {"weight": 5})
    db.add_edge("B", "C", {"weight": 3})
    db.add_edge("A", "C", {"weight": 2})

    print("All Nodes:", db.get_all_nodes())
    print("All Edges:", db.get_all_edges())
    print("Neighbors of A:", db.get_neighbors("A"))
    print("BFS from A:", db.bfs("A"))
    print("DFS from A:", db.dfs("A"))
    print("Shortest path from A to C:", db.shortest_path("A", "C"))
    print("Node Degree of B:", db.node_degree("B"))
    print("Connected Components:", db.connected_components())
    
    db.save_to_file("graph_data.json")
    db.load_from_file("graph_data.json")

    db.display_graph()