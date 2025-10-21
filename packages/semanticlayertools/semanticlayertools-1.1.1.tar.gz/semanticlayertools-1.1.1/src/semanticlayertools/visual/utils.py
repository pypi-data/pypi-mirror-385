import os

import numpy as np
import pandas as pd

try:
    import hdbscan
    import torch
    import umap
    from sentence_transformers import SentenceTransformer
except ModuleNotFoundError as e:
    print(
        "Please install the dependencies for the visualization routines, using `pip install semanticlayertools[ml]`.",
    )
    raise e


def embeddedTextPlotting(
    infolderpath: str,
    columnName: str,
    outpath: str,
    umapNeighors: int = 200,
):
    """Create embedding for corpus text."""
    print("Initializing embedder model.")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    clusterfiles = os.listdir(infolderpath)
    clusterdf = []
    for x in clusterfiles:
        try:
            clusterdf.append(
                pd.read_json(os.path.join(infolderpath, x), lines=True),
            )
        except ValueError:
            raise
    dataframe = pd.concat(clusterdf, ignore_index=True)
    dataframe = dataframe.dropna(subset=[columnName], axis=0).reset_index(drop=True)
    corpus = [x[0] for x in dataframe[columnName].values]
    print("Start embedding.")
    corpus_embeddings = model.encode(
        corpus,
        convert_to_tensor=True,
    )
    torch.save(
        corpus_embeddings,
        f'{os.path.join(outpath, "embeddedCorpus.pt")}',
    )
    print("\tDone\nStarting mapping to 2D.")
    corpus_embeddings_2D = umap.UMAP(
        n_neighbors=umapNeighors,
        n_components=2,
        metric="cosine",
    ).fit_transform(corpus_embeddings)
    np.savetxt(
        os.path.join(outpath, "embeddedCorpus_2d.csv"),
        corpus_embeddings_2D,
        delimiter=",",
        newline="\n",
    )
    print("\tDone.")
    dataframe.insert(0, "x", corpus_embeddings_2D[:, 0])
    dataframe.insert(0, "y", corpus_embeddings_2D[:, 1])
    return dataframe


def embeddedTextClustering(
    infolderpath: str,
    columnName: str,
    emdeddingspath: str,
    outpath: str,
    umapNeighors: int = 200,
    umapComponents: int = 50,
    hdbscanMinCluster: int = 500,
):
    """Create clustering based on embedding for corpus texts."""
    print("Initializing embedder model.")
    clusterfiles = os.listdir(infolderpath)
    clusterdf = []
    for x in clusterfiles:
        try:
            clusterdf.append(
                pd.read_json(os.path.join(infolderpath, x), lines=True),
            )
        except ValueError:
            raise
    dataframe = pd.concat(clusterdf, ignore_index=True)
    dataframe = dataframe.dropna(subset=[columnName], axis=0).reset_index(drop=True)
    print("Loading embedding.")
    corpus_embeddings = torch.load(emdeddingspath)
    print("\tDone\nStarting mapping to lower dimensions.")
    corpus_embeddings_50D = umap.UMAP(
        n_neighbors=umapNeighors,
        n_components=umapComponents,
        min_dist=0.0,
        metric="cosine",
    ).fit_transform(corpus_embeddings)
    np.savetxt(
        os.path.join(outpath, "embeddedCorpus_50d.csv"),
        corpus_embeddings_50D,
        delimiter=",",
        newline="\n",
    )
    print("\tDone.\nStarting clustering.")
    cluster = hdbscan.HDBSCAN(
        min_cluster_size=hdbscanMinCluster,
        metric="euclidean",
        cluster_selection_method="eom",
    ).fit(corpus_embeddings_50D)
    dataframe.insert(0, "label", cluster.labels_)
    return dataframe
