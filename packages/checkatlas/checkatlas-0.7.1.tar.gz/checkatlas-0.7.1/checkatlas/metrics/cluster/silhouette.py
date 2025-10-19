from sklearn.metrics import silhouette_score


def run(count_repr, annotations):
    """
    `Davies-Bouldin readthedocs
    <https://checkatlas.readthedocs.io/en/latest/metrics/clustering/silhouette/>`__

    :param count_repr:
    :param annotations:
    :return:
    """
    return silhouette_score(count_repr, annotations)
