import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def heatmap(x, y, size):
    fig, ax = plt.subplots()

    # Mapping from column names to integer coordinates
    x_labels = [v for v in sorted(x.unique())]
    y_labels = [v for v in sorted(y.unique())]
    x_to_num = {p[1]: p[0] for p in enumerate(x_labels)}
    y_to_num = {p[1]: p[0] for p in enumerate(y_labels)}

    size_scale = 300
    ax.scatter(
        x=x.map(x_to_num),  # Use mapping for x
        y=y.map(y_to_num),  # Use mapping for y
        s=size * size_scale,  # Vector of square sizes, proportional to size
        marker='s'  # Use square as scatterplot marker
    )

    # Show column labels on the axes
    ax.set_xticks([x_to_num[v] for v in x_labels])
    ax.set_xticklabels(x_labels, rotation=90, horizontalalignment='right')
    ax.set_yticks([y_to_num[v] for v in y_labels])
    ax.set_yticklabels(y_labels)
    return plt


def main():
    # parser = init_argparser()
    # args = parser.parse_args()
    data = pd.read_csv("myreport/csv/journaltopic.csv", sep="\t")
    # data = data.transpose()
    print(data)
    corr = pd.melt(data, id_vars='Journal')
    print(corr)
    corr['value'] = np.log10(corr['value'])
    corr.columns = ['x', 'y', 'value']
    plt = heatmap(
        x=corr['x'],
        y=corr['y'],
        size=corr['value'].abs()
    )
    plt.show()


if __name__ == '__main__':
    main()
