Utility functions for visualizations
====================================

The usage of some of these methods requires installing the package with
the extra requirements for text embedding and clustering

.. code-block:: bash
   :linenos:

   pip install semanticlayertools[ml]
   pip install semanticlayertools[ml]

Plotting routines for 3D and stream- graphs
*******************************************

A 3d routine generates multiplex or multilayer network plots from sets of dataframes.
Uses edge bundling for more clear visuals and allows manual setting of 
cluster colors.

Another routine creates 3D graphs for clustered centralities measures.

To compare found time cluster a third routine plots streamgraphs of the 
clustersizes across time. 

.. automodule:: semanticlayertools.visual.plotting
  :members:
  :private-members:
  :undoc-members:

Embedding routines for text
***************************

A BerTopic based routine to first generate embeddings, then topics, find descriptions 
of these topics using large-language models and then create an interactive visualization
to assist researchers to find structures in large corpora of mixed content.  

.. automodule:: semanticlayertools.visual.embedding
  :members:
  :private-members:
  :undoc-members:


Embedding a text corpus in 2 dimensions
***************************************

Meant to be used to visualize a corpus on 2D by embedding a text column using
the SentenceTransformer approach of SBERT and UMAP. Time consuming method!

.. code-block:: python
   :linenos:

   embeddedTextPlotting(infolderpath, columnName, outpath, umapNeighors)

.. seealso ::
    `SBERT docs <https://www.sbert.net/index.html>`_

    `UMAP docs <https://umap-learn.readthedocs.io/en/latest/index.html>`_


Clustering texts using SentenceEmbedding
****************************************

Similar to the above method but extended to help finding large scale structures
of a given text corpus. Similar to topic modelling, in addition makes use of
HDBSCAN clustering. Reuses previously generated embedding of corpus.

.. code-block:: python
   :linenos:

   embeddedTextClustering(
       infolderpath, columnName, embeddingspath, outpath,
       umapNeighors, umapComponents, hdbscanMinCluster
   )

.. seealso ::
    `HDBSCAN docs <https://hdbscan.readthedocs.io>`_
