import random, time
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


class Stub:

    def __init__(self, parent_node, neighbor_stub=None):

        self.parent_node = parent_node
        self.neighbor_stub = neighbor_stub

    def attach(self, stub, allow_self_loops=False):

        if not allow_self_loops:
            assert (stub.parent_node is not self)
        elif stub.parent_node is self:
            return

        self.neighbor_stub = stub
        stub.neighbor_stub = self


class Node:

    def __init__(self, index, stub_generator=None):

        self.index = index
        self.num_stubs = 0 if stub_generator is None else stub_generator()

        while self.num_stubs >= 10e7:
            print('Too Many Stubs')
            self.num_stubs = stub_generator()

        self.stubs = [Stub(self) for i in range(self.num_stubs)]
        self.visited = False

    def attach(self, node):
        
        new_stub = Stub(self)
        neigh_stub = Stub(node)

        new_stub.attach(neigh_stub)

        self.stubs.append(new_stub)
        node.stubs.append(neigh_stub)
        
        self.num_stubs += 1
        node.num_stubs += 1

    def get_neighbors(self):

        return [stub.neighbor_stub.parent_node for stub in self.stubs \
                                    if stub.neighbor_stub is not None]

    def check_neighbors(self, clean=False):

        checked = []
        idx_to_delete = []

        for idx, neighbor in enumerate(self.get_neighbors()):
            assert (clean is True or neighbor not in checked)
            if neighbor not in checked:
                checked.append(neighbor)
            else:
                idx_to_delete.append(idx)

        for idx in idx_to_delete[::-1]:
            del self.stubs[idx]

        self.num_stubs = len(self.stubs)


class Graph:

    def __init__(self, num_nodes, stub_generator=None):
        self.stub_generator = stub_generator
        self.num_nodes = num_nodes
        self.nodes = {i: Node(i, stub_generator=self.stub_generator) for i in range(num_nodes)}

    def degree_distribution(self, title=None, plot=False):
        degree_distribution = [len(node.stubs) for node in self.nodes.values()]
        degree_distribution = pd.Series(degree_distribution).value_counts()/self.num_nodes
        if plot:
            sns.scatterplot(data=degree_distribution)
            ax = plt.gca()
            ax.set_title("Degree Distribution" if title is None else title)

        return degree_distribution

    def cluster_sizes(self, title=None, verbose=False, plot=False):

        start_time = time.time()

        def recursive_helper(clusters, current_cluster_idx, current_node):
            current_node.visited = True
            clusters[current_cluster_idx].append(current_node)
            for node in current_node.get_neighbors():
                if node.visited is False:
                    recursive_helper(clusters, current_cluster_idx, node)

        clusters = {}
        current_cluster_idx = 0

        for node in self.nodes.values():
            if node.visited is False:
                clusters[current_cluster_idx] = []
                recursive_helper(clusters, current_cluster_idx, node)
                current_cluster_idx += 1

        for node in self.nodes.values():
            node.visited = False

        value_counts = pd.Series([len(node_list) for idx, node_list in clusters.items()]).value_counts()
        cluster_size, num_nodes = zip(*[(cluster_size, num_clusters * cluster_size / self.num_nodes) \
                                        for cluster_size, num_clusters in value_counts.items()])

        data = pd.DataFrame(index=cluster_size, data=num_nodes)

        if plot:
            sns.scatterplot(data=data)
            ax = plt.gca()
            ax.set_title("Degree Distribution" if title is None else title)

        if verbose:
            print("Clusters Computed in " + str(time.time() - start_time) + " seconds")

        return data

    
class DAG_Model: 
    
    def __init__(self, num_nodes, neigh_distribution, verbose=False):

        start_time = time.time()
        self.graph = Graph(num_nodes)
        num_neighs = [neigh_distribution() for i in range(self.graph.num_nodes)]

        for i in range(num_nodes):
         
            neighs = []
            while(len(neighs) is 0 or (i in neighs)): 
                if len(neighs) is 0:
                    neighs = [np.random.randint(0,num_nodes-1) for _ in range(num_neighs[i])]
                else:
                    neighs = [np.random.randint(0,num_nodes-1) if x is i else x for x in neighs]
                    
            neighs = list( dict.fromkeys(neighs) )
            for j in neighs:
                self.graph.nodes[i].attach(self.graph.nodes[j])
                    
            for node in self.graph.nodes.values():
                node.check_neighbors(clean=True)
                
        if verbose:
            print("Graph Generated in " + str(time.time() - start_time) + " seconds")

class Generalized_Random_Graph_Model:

    def __init__(self, num_nodes, w_distribution, gamma, verbose=False):

        start_time = time.time()
        self.graph = Graph(num_nodes)
        W = [w_distribution() for i in range(self.graph.num_nodes)]

        for i in range(num_nodes):
            for j in range(num_nodes):

                alpha = W[i] * W[j] / (self.graph.num_nodes**(1.0/gamma))
                edge_p = alpha / (1 + alpha)
                if i > j and random.random() <= edge_p:
                    self.graph.nodes[i].attach(self.graph.nodes[j])

        if verbose:
            print("Graph Generated in " + str(time.time() - start_time) + " seconds")


class Configuration_Model:

    def __init__(self, num_nodes, stub_distribution, erased, verbose=False):
        start_time = time.time()
        self.graph = Graph(num_nodes, stub_generator=stub_distribution)
        self.num_nodes = num_nodes

        all_stubs = []
        for node in self.graph.nodes.values():
            all_stubs += node.stubs

        random.seed()
        random.shuffle(all_stubs)

        for i in range(0, len(all_stubs)-1, 2):
            all_stubs[i].attach(all_stubs[i + 1], allow_self_loops=erased)


        for node in self.graph.nodes.values():
            node.check_neighbors(clean=erased)

        if verbose:
            print("Graph Generated in " + str(time.time() - start_time) + " seconds")


class Erased_Configuration_Model(Configuration_Model):

    def __init__(self, num_nodes, stub_distribution, verbose=False):
        success = False
        while not success:
            try:
                super().__init__(num_nodes, stub_distribution, erased=True, verbose=verbose)
                success = True
            except:
                if verbose:
                    print('Too many stubs')
                pass

class Repeated_Configuration_Model(Configuration_Model):

    def __init__(self, num_nodes, stub_distribution, verbose=False):
        success = False
        try_count = 1
        start_time = time.time()

        while not success:
            if verbose:
                print("Attempt #" + str(try_count))
            try:
                super().__init__(num_nodes, stub_distribution, erased=False)
                success = True
            except:
                try_count += 1
                pass

        if verbose:
            print("Graph Generated in " + str(time.time() - start_time) + " seconds")

