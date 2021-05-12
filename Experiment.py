import math
import numpy as np
import scipy as sc
import seaborn as sns
import matplotlib.pyplot as plt
import gc

from Graph import *


class Experiment:

    def __init__(self, model_type, title, baseline, 
                 stub_distribution_type=None,
                 stub_distribution_param=None,
                 w_distribution_type=None,
                 w_distribution_param=None,
                 w_gamma = 1,
                 n_runs=5,
                 n_range=[100, 1000, 10000],
                 verbose=False):

        self.results = {}
        self.models = {}
        self.baseline = baseline

        self.title  = title
        self.model_type = model_type

        self.n_runs  = n_runs
        self.n_range = n_range


        for num_nodes in self.n_range:

            model = None
            self.results[num_nodes] = []
            self.models[num_nodes] = []

            for run_idx in range(self.n_runs):
                if self.model_type == 'repeated':
                    stub_distribution = lambda: stub_distribution_type(stub_distribution_param, 1)[0]
                    model = Repeated_Configuration_Model(num_nodes=int(num_nodes),
                                                         stub_distribution=stub_distribution,
                                                         verbose=verbose)
                elif self.model_type == 'erased':
                    stub_distribution = lambda: stub_distribution_type(stub_distribution_param, 1)[0]
                    model = Erased_Configuration_Model(num_nodes=int(num_nodes),
                                                       stub_distribution=stub_distribution,
                                                       verbose=verbose)
                elif self.model_type == 'general':
                    w_distribution = lambda: w_distribution_type(w_distribution_param, 1)[0]
                    model = Generalized_Random_Graph_Model(num_nodes=int(num_nodes),
                                                           gamma=w_gamma,
                                                           w_distribution=w_distribution,
                                                           verbose=verbose)
                
                elif self.model_type == 'DAG':
                    stub_distribution = lambda: stub_distribution_type(stub_distribution_param, 1)[0]
                    model = DAG_Model(num_nodes=int(num_nodes),
                                      neigh_distribution=stub_distribution,
                                      verbose=verbose)

                self.results[num_nodes].append((model.graph.degree_distribution(), model.graph.cluster_sizes()))

                del model
                gc.collect()

        self.plot_cluster_dist_results()
        self.plot_degree_dist_results()

    def plot_degree_dist_results(self):
        plot_size = 8
        fig, axs = plt.subplots(1, len(self.n_range), figsize=(plot_size * len(self.n_range), plot_size))
        fig_idx = 0

        sns.set(rc={'figure.figsize': (plot_size * len(self.n_range), plot_size)})
        max_degrees = 0

        for n_nodes, results in self.results.items():
            degree_dists, _ = zip(*results)
            degree_dists = pd.DataFrame(degree_dists)
            max_degrees = max([len(degree_dists.columns), max_degrees])

        max_degrees = min([max_degrees,10])

        for n_nodes, results in self.results.items():
            degree_dists, _ = zip(*results)
            degree_dists = pd.DataFrame(degree_dists)

            
            if self.baseline is not None:
                baseline_range = [int(col) for col in degree_dists.columns]
   
                baseline_df = pd.DataFrame( [self.baseline(i) for i in baseline_range],
                                            columns = ['Predicted Degree Distribution'])
           
                sns.lineplot(data=baseline_df, palette=sns.color_palette("RdPu", 1), ax=axs[fig_idx])
            
            sns.pointplot(data=degree_dists, ci='sd',
                          errwidth=5, join=False, markers=['_'],
                          ax=axs[fig_idx], label='test')

            fontsize = 18

            axs[fig_idx].set_ylim([0, 1])
            axs[fig_idx].set_xlim([0, max_degrees])
            axs[fig_idx].set_title('n = ' + str(n_nodes), fontsize=fontsize)
            axs[fig_idx].set_xlabel('Degree', fontsize=fontsize)
            axs[fig_idx].set_ylabel('Empircal Degree Distribution', fontsize=fontsize)
            axs[fig_idx].legend(['Predicted Degree Distribution'], fontsize=fontsize)

            fig_idx += 1

        plt.savefig(self.title + '_degree.png')

    def plot_cluster_dist_results(self):

        plot_size = 8
        fig, axs = plt.subplots(1, len(self.n_range), figsize=(plot_size * len(self.n_range), plot_size))
        fig_idx = 0

        sns.set(rc={'figure.figsize': (plot_size * len(self.n_range), plot_size)})

        for n_nodes, results in self.results.items():
            _, cluster_dists = zip(*results)

            for run_idx,cluster_dist in enumerate(cluster_dists):

                data = cluster_dist[0].rename("Run "+str(run_idx))
                sns.scatterplot(data=data,ax=axs[fig_idx],label="Run "+str(run_idx))

            fontsize = 18
            axs[fig_idx].set_ylim([0, 1])
            axs[fig_idx].set_title('n = ' + str(n_nodes), fontsize=fontsize)
            axs[fig_idx].set_xlabel('Cluster Size', fontsize=fontsize)
            axs[fig_idx].set_ylabel('Portion of Nodes in Cluster', fontsize=fontsize)

            fig_idx += 1

        plt.savefig(self.title + '_cluster.png')

