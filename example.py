# -*- coding: utf-8 -*-

# License: GPL 3.0

import sys

import matplotlib.pyplot as plt
import numpy as np
from graphviz import Digraph
from scipy.cluster.hierarchy import dendrogram, linkage
import pandas as pd

from bhc import (BayesianHierarchicalClustering,
                 BayesianRoseTrees,
                 NormalInverseWishart)


def main():
    # dt = np.dtype([('col1', 'float64'), ('col2', 'float64'), ('col3', 'U50')])
    # data = np.genfromtxt('data/data.csv', dtype=dt, delimiter=',')
    data = np.genfromtxt('data/data.csv', delimiter=',')
    # cities = np.genfromtxt('data/cities.csv', delimiter=',')
    cities = pd.read_csv('data/cities.csv')
    cities = [string for sublist in cities.values for string in sublist]

    # print(cities)
    # print(data.shape)
    # plot_data(data)

    # run_linkage(data, 'single')
    # run_linkage(data, 'complete')
    # run_linkage(data, 'average', cities)

    run_bhc(data, cities)
    # run_brt(data)


def plot_data(data):
    colors = ["#AB274F", "#7C0902", "#FE6F5E", "#BF4F51", "#FF00FF", "#00FFFF", "#800000", "#008000", "#000080",
              "#FF8080", "#80FF80", "#8080FF", "#FFFF80", "#FF80FF", "#80FFFF", "#FF6666", "#66FF66", "#6666FF",
              "#FFFF66", "#FF66FF", "#66FFFF", "#FF3333", "#33FF33", "#3333FF", "#FFFF33", "#FF33FF", "#33FFFF",
              "#FF9999", "#99FF99", "#9999FF", "#FFFF99", "#FF99FF", "#99FFFF", "#FFCC00", "#CCFF00", "#00CCFF",
              "#FF9966", "#66FF99", "#9966FF", "#FFFF66", "#FF66FF", "#66FFFF", "#FFCC99", "#99FFCC", "#CC99FF",
              "#FFFFCC", "#CCFF66", "#66CCFF", "#FF99CC", "#CCFF99", "#99CCFF", "#FFCCCC", "#CCFFCC", "#CCCCFF",
              "#FFFFFF", "#CCCCCC", "#999999", "#666666", "#333333", "#000000", "#F0F8FF", "#FAEBD7", "#00FFFF",
              "#7FFFD4", "#F0FFFF", "#F5F5DC", "#FFE4C4", "#FFEBCD", "#000080", "#8A2BE2", "#A52A2A", "#DEB887",
              "#5F9EA0", "#7FFF00", "#D2691E", "#FF7F50", "#6495ED", "#FFF8DC", "#DC143C", "#00FFFF", "#00008B",
              "#008B8B", "#B8860B", "#A9A9A9", "#006400", "#BDB76B", "#8B008B", "#556B2F", "#FF8C00", "#9932CC",
              "#8B0000", "#E9967A", "#8FBC8F", "#483D8B", "#2F4F4F", "#00CED1", "#9400D3", "#FF1493", "#00BFFF",
              "#696969", "#1E90FF", "#B22222", "#FFFAF0", "#228B22", "#FF00FF", "#DCDCDC", "#F8F8FF", "#FFD700",
              "#DAA520", "#808080", "#008000", "#ADFF2F", "#F0FFF0", "#FF69B4", "#CD5C5C", "#8B4513"]

    fig, ax = plt.subplots(figsize=(8, 6))

    for i in range(data.shape[0]):
        x = data[i][0]
        y = data[i][1]
        label = data[i][2]
        color = colors[i % len(colors)]
        ax.scatter(x, y, c=color, label=label, s=100, alpha=0.7)

    ax.set_xlabel('PC 1', fontsize=14)
    ax.set_ylabel('PC 2', fontsize=14)
    ax.set_title('Scatter Plot', fontsize=16)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

    plt.savefig('results/scatter_plot.png', bbox_inches='tight')
    plt.close()

    fig2, ax2 = plt.subplots(figsize=(8, 2))
    handles, labels = ax.get_legend_handles_labels()
    ax2.legend(handles, labels, loc='upper left', ncol=10, fontsize=8)
    ax2.axis('off')

    # plt.savefig('results/legend.png', bbox_inches='tight')
    # plt.close()


def run_linkage(data, method, cities):
    frame = pd.DataFrame(data=data, columns=["PC 1", "PC 2"], index=cities)
    plt.clf()
    plt.figure(figsize=(15, 18))
    Z = linkage(data, method)
    dendrogram(Z, labels=frame.index, orientation='right')

    # plt.draw()
    ax = plt.gca()
    ax.tick_params(axis='x', which='major', labelsize=15)
    ax.tick_params(axis='y', which='major', labelsize=8)
    plt.savefig(
        'results/linkage_{0}_plot.png'.format(method), format='png', dpi=100)


def run_bhc(data, cities):
    # Hyper-parameters (these values must be optimized!)
    g = 20
    scale_factor = 0.001
    alpha = 1

    model = NormalInverseWishart.create(data, g, scale_factor)

    bhc_result = BayesianHierarchicalClustering(data,
                                                model,
                                                alpha,
                                                cut_allowed=True).build()

    build_graph(bhc_result.node_ids,
                bhc_result.arc_list,
                'results/bhc_plot', cities)


def run_brt(data):
    # Hyper-parameters (these values must be optimized!)
    g = 10
    scale_factor = 0.001
    alpha = 0.5

    model = NormalInverseWishart.create(data, g, scale_factor)

    brt_result = BayesianRoseTrees(data,
                                   model,
                                   alpha,
                                   cut_allowed=True).build()

    build_graph(brt_result.node_ids,
                brt_result.arc_list,
                'results/brt_plot')


def build_graph(node_ids, arc_list, filename, cities):
    dag = Digraph()

    # for index, node_id in enumerate(node_ids, start=0):
    #     if index < 90:
    #         dag.node(cities[index])
    #     else:
    #         dag.node(str(node_id))

    # for node_id in node_ids:
    #     dag.node(str(node_id))

    for node_id in node_ids:
        if node_id < 90:
            dag.node(str(node_id), label=f"{cities[node_id]}")
        else:
            dag.node(str(node_id))

    for arc in arc_list:
        dag.edge(str(arc.source), str(arc.target))

    dag.render(filename=filename, format='png', cleanup=True)


if __name__ == "__main__":
    main()
    sys.exit()
