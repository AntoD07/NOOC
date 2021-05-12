Based on the paper from Tom Britton, Maria Deijfen, Anders Martin-Löf "Generating simple random graphs with prescribed degree distribution", the project presents 
three different algorithms to simulate simple random graphs with the emphasize put on their limitations when treating particular degree distributions. 

1 - Erased configuration model : from a given distribution, sample a number of stubs at each vertex , link them and remove any self loop or multiple edges to ensure the simpleness. Fails if the chosen distribution has infinite mean.

2 - Repeated configuration model : generate a random graph as in the erased configuration model, not removing any self loop or multiple edge. Reiterate until the graph is simple. Fails if the chosen distribution has infinite second moment. 

3 - Generalized random graph : Erdos-Renyi graph where edge probabilities are deeply connected to the limiting degree distirbution.

Zeta distributions are particulary suitable for exploring the limitations of each algorithm. It can also be used to investigate on the existence of "infinite" size cluster in the graph using the Molloy-Reed condition. 

See the report for more details.
