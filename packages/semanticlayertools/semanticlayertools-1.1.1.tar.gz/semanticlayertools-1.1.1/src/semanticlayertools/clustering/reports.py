"""Create reports for found clusters based on metadata and title and abstract texts."""

import multiprocessing
import re
import time
from collections import Counter
from pathlib import Path

import pandas as pd
from bertopic import BERTopic
from tqdm import tqdm

num_processes = multiprocessing.cpu_count() - 2


class ClusterReports:
    """Generate reporting on time-clusters.

    Generate reports to describe the content for all found clusters above a
    minimal size by collecting metadata for all publications in each cluster,
    finding the top 20 authors and affiliations of authors involved in the
    cluster publications, and running basic BERTtopic modelling.
    For each cluster a report file is written to the output path.

    Input CSV filename is used to create the output folder in output path. For
    each cluster above the limit, a subfolder is created to contain all metadata
    for the cluster. The metadata files are assumed to be in JSONL format and
    contain the year in the filename.

    :param infile: Path to input CSV file containing information on nodeid, clusterid, and year
    :type infile: str
    :param metadatapath: Path to JSONL (JSON line) formated metadata files.
    :type metadatapath: str
    :param outpath: Path to create output folder in, foldername reflects input filename
    :type outpath: str

    :param textcolumn: The dataframe column of metadata containing textutal for topic modelling (default=title)
    :type textcolumn: str
    :param numberProc: Number of CPU the routine will use (default = all!)
    :type numberProc: int
    :param minClusterSize: The minimal cluster size, above which clusters are considered (default=1000)
    :type minClusterSize: int
    :param timerange: Time range to evalute clusters for (usefull for limiting computation time, default = (1945, 2005))
    :type timerange: tuple
    """

    def __init__(
        self,
        infile: str,
        metadatapath: Path,
        outpath: Path,
        *,
        textcolumn: str = "title",
        authorColumnName: str = "author",
        affiliationColumnName: str = "aff",
        publicationIDcolumn: str = "nodeID",
        numberProc: int = num_processes,
        minClusterSize: int = 1000,
        timerange: tuple = (1945, 2005),
        rerun: bool = False,
        debug: bool = False,
    ) -> None:
        """Init class."""
        self.numberProc = numberProc
        self.minClusterSize = minClusterSize
        self.metadatapath = metadatapath
        self.textcolumn = textcolumn

        self.authorColumnName = authorColumnName
        self.affiliationColumnName = affiliationColumnName
        self.publicationIDcolumn = publicationIDcolumn
        self.timerange = timerange
        self.debug = debug

        clusterdf = pd.read_csv(infile)
        basedata = (
            clusterdf.groupby(["year", "cluster"])
            .size()
            .to_frame("counts")
            .reset_index()
        )
        basedata = basedata.query(
            f"({self.timerange[0]} <= year <= {self.timerange[1]})"
        )
        self.largeClusterList = list(
            basedata.groupby("cluster")
            .sum()
            .query(f"counts > {self.minClusterSize}")
            .index,
        )
        self.clusternodes = clusterdf.query(
            f"(cluster in @self.largeClusterList) and ({self.timerange[0]} <= year <= {self.timerange[1]})",
        )
        outfolder = infile.name[:-4] + "_minCluSize_" + str(self.minClusterSize)
        self.outpath = Path(outpath, outfolder)
        if Path.is_dir(self.outpath) and rerun is False:
            text = f"Output folder {self.outpath} exists. Aborting."
            raise OSError(text)
        Path.mkdir(self.outpath, exist_ok=True, parents=True)
        for clu in self.largeClusterList:
            Path.mkdir(
                Path(self.outpath, f"Cluster_{clu}"), exist_ok=True, parents=True
            )
        if self.debug is True:
            print(
                f"Found {len(self.largeClusterList)} cluster larger then {self.minClusterSize} nodes."
            )

    def _mergeData(self, filename: str) -> str:
        """Merge metadata for cluster nodes.

        Writes all metadata for nodes in cluster to folders.

        :param filename: Metadata input filename
        :type filename: str
        """
        if self.debug is True:
            print(f"Extracting cluster metadata for file {filename.name}.")
        data = pd.read_json(filename, lines=True)
        selectMerge = data.merge(
            self.clusternodes,
            left_on=self.publicationIDcolumn,
            right_on="node",
            how="inner",
        )
        selectMerge = selectMerge.drop_duplicates(subset=self.publicationIDcolumn)
        if selectMerge.shape[0] > 0:
            for clu, g0 in selectMerge.groupby("cluster"):
                g0.to_json(
                    Path(
                        self.outpath,
                        f"Cluster_{clu}",
                        "merged_" + filename.name,
                    ),
                    orient="records",
                    lines=True,
                )
        return ""

    def gatherClusterMetadata(self) -> None:
        """Gathering metadata for clusters.

        For all files in the metadata path, call `_mergeData` if the found
        year in the filename falls in the bounds.

        This step needs to be run once, then all cluster metadata is generated
        and can be reused.
        """
        filenames = sorted(Path(self.metadatapath).glob("*.json"))
        yearFiles = []
        for x in filenames:
            year = int(re.findall(r"\d{4}", x.name)[0])
            if self.timerange[0] <= year <= self.timerange[1]:
                yearFiles.append(x)
        if self.numberProc > 1:
            with multiprocessing.Pool(self.numberProc) as pool:
                _ = pool.map(self._mergeData, tqdm(yearFiles, leave=False))
        else:
            for elem in tqdm(yearFiles, leave=False):
                self._mergeData(elem)

    def find_topics(
        self,
        topicDF: list,
        n_topics: int,
    ) -> str:
        """Calculate topics in corpus.

        Use Bertopic algorithm to calculate topics in corpus file for `n_topics`
        topics, returning the 20 most representative words for each topic.

        :param topicDF: The result dataframe of Bertopic.
        :type topicDC: `pd.DataFrame`
        :param n_topics: Number of considered topics
        :type n_topics: int
        :returns: List of found topics with top occuring words
        :rtype: str
        """
        outtext = f"\n\n\tTopics in cluster for {n_topics} topics:\n"
        for topnr, data in topicDF[["Topic", "Representation"]].groupby("Topic"):
            if topnr != -1:
                outtext += (
                    f"\t\tTopic {topnr}: {' '.join(data['Representation'].iloc[0])}\n"
                )
        return outtext

    def _metadataStats(
        self, dataframe: pd.DataFrame, column: str, topN: int = 20
    ) -> str:
        """Get top 20 of column."""
        topEntries = Counter(
            [x for y in dataframe[column].fillna("").to_numpy() for x in y],
        ).most_common(topN + 1)
        returntext = ""
        for x in topEntries:
            if x[0] != "" and x[0] != "-":
                returntext += f"\t{x[0]}: {x[1]}\n"
        return returntext

    def fullReport(
        self,
        cluster: int,
        corpusSizeLimit: int = 100,
        sampleLimit: int = 10000,
        *,
        doSample: bool = True,
    ) -> str:
        """Generate full cluster report for one cluster.

        :param cluster: The cluster number to process
        :type cluster: int or str
        :raises ValueError: If input cluster data can not be read.
        :returns: Report text with all gathered informations
        :rtype: str
        """
        starttime = time.time()
        clusterfiles = sorted(Path(self.outpath, f"Cluster_{cluster}").glob("*.json"))
        yearFiles = []
        for x in clusterfiles:
            year = int(re.findall(r"\d{4}", x.name)[0])
            if self.timerange[0] <= year <= self.timerange[1]:
                yearFiles.append(x)
        clusterdflist = [pd.read_json(file, lines=True) for file in yearFiles]
        dfCluster = pd.concat(clusterdflist, ignore_index=True)
        if self.debug is True:
            print(f"Cluster {cluster} has {dfCluster.shape[0]} documents.")
        if dfCluster.shape[0] == 0:
            text = f"No data for Cluster {cluster}."
            raise ValueError(text)
        basedf = self.clusternodes.query(
            f"(cluster == {cluster})",
        )
        inputnodes = set(basedf.node.values)
        notFound = inputnodes.difference(
            set(dfCluster[self.publicationIDcolumn].values)
        )
        authortext = self._metadataStats(dfCluster, self.authorColumnName)
        affiltext = self._metadataStats(dfCluster, self.affiliationColumnName)
        if self.debug is True:
            print(f"\tFinished base report for cluster {cluster}.")
        titlesOnly = dfCluster.drop_duplicates(subset=self.publicationIDcolumn).dropna(
            subset=self.textcolumn
        )
        if titlesOnly.shape[0] > corpusSizeLimit:
            if doSample is True:
                sample = (
                    dfCluster.sample(frac=0.01)
                    if len(dfCluster) > sampleLimit
                    else dfCluster.sample(frac=0.1)
                )
            else:
                sample = dfCluster
            docs = sample.title.apply(lambda row: row[0] if row else "")
            topic_model = BERTopic(
                verbose=False,
                top_n_words=20,
            )
            topic_model.fit_transform(docs)
            topic_model.reduce_topics(docs, 15)
            topicDFAuto = topic_model.get_topic_info()
            topics = self.find_topics(topicDF=topicDFAuto, n_topics="15")
        else:
            topics = f"Number of documents to low ({len(titlesOnly)})."
            if self.debug is True:
                print(f"\tSkiping reports, only {len(titlesOnly)} docs with title.")
        return f"""Report for Cluster {cluster}

    Got {len(inputnodes)} unique co-cited publications.
    Found metadata for {dfCluster.shape[0]} of these in time range: {basedf.year.min()} to {basedf.year.max()}.
    There are {len(notFound)} publications without metadata.

    The top 20 authors of this cluster are:\n{authortext}\n
    The top 20 affiliations of this cluster are:\n{affiltext}\n
    {topics}\n
Finished analysis of cluster {cluster} in {time.time()- starttime:.2f} seconds."""

    def writeReports(
        self, corpusSizeLimit: int = 100, *, doSample: bool = True
    ) -> None:
        """Generate reports and write to output path."""
        for cluster in self.largeClusterList:
            outtext = self.fullReport(
                cluster, corpusSizeLimit=corpusSizeLimit, doSample=doSample
            )
            outpath = Path(
                self.outpath,
                f"Cluster_{cluster}.txt",
            )
            with outpath.open("w") as file:
                file.write(outtext)
