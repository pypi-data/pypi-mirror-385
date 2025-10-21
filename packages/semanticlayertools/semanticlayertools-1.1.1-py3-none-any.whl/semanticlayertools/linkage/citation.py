"""Calculate different bibliometric measures."""

import math
import multiprocessing
import os
import time
from collections import Counter
from itertools import combinations, islice
from pathlib import Path
from typing import TypeVar

import igraph as ig
import numpy as np
import pandas as pd
from tqdm import tqdm

num_processes = multiprocessing.cpu_count()

limitRefLength = TypeVar("limitRefLength", bool, int)
inPath = TypeVar("inPath", str, pd.DataFrame)


class Couplings:
    """Calculate different coupling networks based on citation data.

    Expected input format in the INPATH are JSONL files with names
    containing the year data. The files itself should contain
    ids for each publication (PUBIDCOLUMN) and information on its references
    (REFERENCESCOLUMN). For the years in the TIMERANGE (default 1945-2005)
    files within TIMEWINDOW (default 3 years) are joined together.

    :param inpath: Path to input JSONL files
    :type inpath: str
    :param inputType: Type of input data, files or dataframe (default: files)
    :type inputType: str
    :param outpath: Path to write output to
    :type outpath: str
    :param pubIDColumn: Column for unique publication IDs (default: nodeID)
    :type pubIDColumn: str
    :param referencesColumn: Column for references data (default: reference)
    :type referencesColumn: str
    :param timerange: Time range for analysis, tuple of integers (default (1945, 2005))
    :param dateColumn: Column for year data in case of inputType = dataframes (default: year)
    :type dateColumn: str
    :type timerange: tuple
    :param timeWindow: Rolling window in years (default: 3)
    :type timeWindow: int
    :param numberProc: Number of CPU processes for parallelization (default: all)
    :type numberProc: int
    :param limitRefLength: Limit the maximal length of reference list (default: False)
    :type limitRefLength: bool
    :param debug: Switch on additional debug messages (default: False)
    :type debug: bool

    .. seealso::
       Rajmund Kleminski, Przemysiaw Kazienko, and Tomasz Kajdanowicz (2020)
       Analysis of direct citation, co-citation and bibliographic coupling in scientific topic identification
       J of Information Science, 48, 3. 10.1177/0165551520962775
    """

    def __init__(
        self,
        inpath: inPath,
        outpath: str,
        inputType: str = "files",
        pubIDColumn: str = "nodeID",
        referenceColumn: str = "reference",
        dateColumn: str = "year",
        timerange: [int, int] = (1945, 2005),
        timeWindow: int = 3,
        numberProc: int = num_processes,
        *,
        limitRefLength: limitRefLength = False,
        debug: bool = False,
    ) -> None:
        """Init class."""
        self.inpath = inpath
        self.outpath = outpath
        self.inputType = inputType
        self.pubIdCol = pubIDColumn
        self.refCol = referenceColumn
        self.yearCol = dateColumn
        self.timerange = timerange
        self.numberProc = numberProc
        self.limitRefLength = limitRefLength
        self.window = timeWindow
        self.debug = debug

    def _window(self, seq: list, n: int) -> list:
        """Return a sliding window (of width n) over data from the iterable.

        s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
        """
        it = iter(seq)
        result = tuple(islice(it, n))
        if len(result) == n:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result

    def _checkFileExists(self, basefilename: str) -> Path:
        """Check if file exists."""
        outfilepathGC = Path(self.outpath, f"{basefilename}_GC.net")
        outfilepathNCOL = Path(self.outpath, f"{basefilename}.ncol")
        if outfilepathGC.is_file() or outfilepathNCOL.is_file():
            text = f"Output file for GC or Net at {outfilepathGC} exists. Please move or delete."
            raise OSError(text)
        return outfilepathNCOL

    def _generateSliceData(self, sl: list) -> tuple:
        """Generate dataframe for given timeslice.

        Dataframe entries without references are ignored.
        """
        if self.inputType == "files":
            yearFiles = [
                file
                for file in os.listdir(self.inpath)
                if any([yearname in file for yearname in [str(year) for year in sl]])
            ]
            if self.debug is True:
                print(f"\tCreating data for yearfiles: {yearFiles}.")

            dflist = []
            for elem in yearFiles:
                dfTemp = pd.read_json(Path(self.inpath, elem), lines=True)
                dflist.append(dfTemp)

            dfSlice = pd.concat(dflist, ignore_index=True)
        elif self.inputType == "dataframe":
            dfSlice = self.inpath[self.inpath[self.yearCol].isin(sl)]
        dfDataRef = dfSlice[~dfSlice[self.refCol].isna()]
        targetSet = [
            (row[self.pubIdCol], set(row[self.refCol]))
            for idx, row in dfDataRef.iterrows()
        ]
        return dfSlice, dfDataRef, targetSet

    def _writeGraphMetadata(
        self, citetype: str, yearname: int, graph: ig.Graph, *, writeGC: bool = True
    ) -> None:
        """Write metadata and giant component of given graph.

        This can give hints on the coverage of the giant component in
        relation to the full graph accros time slices.
        """
        # Disconnected components are identified, i.e. subgraphs without edges to other subgraphs
        components = graph.components()
        # Sorting the result in reverse order yields the first element as the giant component of the network.
        sortedComponents = sorted(
            [(x, len(x), len(x) * 100 / len(graph.vs)) for x in components],
            key=lambda x: x[1],
            reverse=True,
        )
        giantComponent = sortedComponents[0]
        giantComponentGraph = graph.vs.select(giantComponent[0]).subgraph()
        if writeGC is True:
            outfilepathGC = Path(self.outpath, f"{citetype}_{yearname}_GC.net")
            with outfilepathGC.open("w") as outfile:
                giantComponentGraph.write_pajek(outfile)
        # To judge the quality of the giant component in relation to the full graph, reports are created.
        outfilepathMeta = Path(self.outpath, f"{citetype}_{yearname}_metadata.txt")
        with outfilepathMeta.open("w") as outfile:
            if self.inputType == "files":
                outfile.write(f"Graph derived from {self.inpath}\nSummary:\n")
            elif self.inputType == "dataframe":
                outfile.write(
                    f"Graph derived from dataframe with shape {self.inpath.shape}\nSummary:\n"
                )
            outfile.write(graph.summary() + "\n\nComponents (ordered by size):\n\n")
            for idx, elem in enumerate(sortedComponents):
                gcompTemp = graph.vs.select(elem[0]).subgraph()
                outfile.write(
                    f"{idx}:\n\t{elem[1]} nodes ({elem[2]:.3f}% of full graph)\n\t{len(gcompTemp.es)} edges ({len(gcompTemp.es)*100/len(graph.es):.3f}% of full graph)\n\n",
                )

    def getBibliometricCoupling(self) -> None:
        """Calculate bibliometric coupling.

        For all publication in each time slice, combinations
        of two publications are created. For each combination
        the overlap between the references is determined. If
        the overlap is larger then 1, an edge between the two
        publications is generated.
        All edges are saved in NCOL format.
        The list of all edges is read-in as a graph, and the
        giant component is saved in Pajek format.

        Due to the nature of the combinatorics, this routine
        can be time-intensive. Switch on debugging messages to
        get a rough estimate of the runtime in hours.
        """
        slices = self._window(
            range(self.timerange[0], self.timerange[1] + 1, 1),
            self.window,
        )
        overallStarttime = time.time()
        for sl in list(slices):
            yearname = sl[-1]
            outfilepathNCOL = self._checkFileExists(f"bibcoup_{yearname}")
            if self.debug is True:
                print(f"Working on year slice {yearname}.")

            dfSlice, dfDataRef, targetSet = self._generateSliceData(sl)

            comLen = math.factorial(len(targetSet)) / (
                math.factorial(2) * (math.factorial(len(targetSet) - 2))
            )
            if self.debug is True:
                print(
                    f"\tWill have to calculate {comLen} combinations for {dfDataRef.shape[0]} entries with references ({dfSlice.shape[0]} entries in total).\n\tEstimated runtime {((comLen)/1838000)/3600:.2f} hours."
                )

            starttime = time.time()
            with outfilepathNCOL.open("w") as outfile:
                for tup in tqdm(combinations(targetSet, 2), leave=False):
                    overlap = tup[0][1].intersection(tup[1][1])
                    if overlap and len(overlap) > 1:
                        outfile.write(
                            f"{tup[0][0]} {tup[1][0]} {len(overlap)}\n",
                        )
            tempG = ig.Graph.Read_Ncol(
                f"{self.outpath}bibcoup_{yearname}.ncol",
                names=True,
                weights=True,
                directed=False,
            )
            tempG.vs["id"] = tempG.vs["name"]
            self._writeGraphMetadata("bibcoup", yearname, tempG)
            print(f"Done in {(time.time()-starttime)/3600:.2f} hours.")
        print(
            f"Finished all slices in {(time.time()-overallStarttime)/3600:.2f} hours."
        )

    def _getCombinations(self, chunk: pd.DataFrame) -> list:
        """Calculate combinations of references in publications chunk.

        :param chunk: A chunk of the corpus dataframe
        :type chunk: `pd.Dataframe`
        :returns: A list of all reference combinations for each corpus entry
        :rtype: list
        """
        res = []
        if self.limitRefLength is not False:
            reflen = chunk[self.refCol].apply(
                lambda x: isinstance(x, list) and len(x) <= self.limitRefLength,
            )
            data = chunk[reflen].copy()
        else:
            data = chunk.copy()
        for _, row in data.iterrows():
            comb = combinations(row[self.refCol], 2)
            res.extend(list(comb))
        return res

    def getCocitationCoupling(self) -> None:
        """Calculate cocitation coupling.

        Creates three files: Metadata-File with all components information,
        Giant component network data in pajek format and full graph data in
        edgelist format.

        The input dataframe is split in chunks depending on the available cpu processes.
        All possible combinations for all elements of the reference column are calculated.
        The resulting values are counted to define the weight of two
        papers being cocited in the source dataframe.

        :returns: A tuple of GC information: Number of nodes and percentage of total, Number of edges and percentage of total
        :rtype: tuple
        """
        slices = self._window(
            range(self.timerange[0], self.timerange[1] + 1, 1),
            self.window,
        )
        overallStarttime = time.time()
        for sl in list(slices):
            yearname = sl[-1]
            outfilepathNCOL = self._checkFileExists(f"cocite_{yearname}")
            if self.debug is True:
                print(f"Working on year slice {yearname}.")

            dfSlice, dfDataRef, targetSet = self._generateSliceData(sl)
            data = dfSlice.dropna(subset=[self.refCol]).reset_index(drop=True)
            chunks = np.array_split(data, self.numberProc)
            pool = multiprocessing.Pool(processes=self.numberProc)
            cocitations = pool.map(self._getCombinations, chunks)
            # This defines the weight of the cocitation edge.
            cocitCounts = Counter([x for y in cocitations for x in y])
            sortCoCitCounts = [
                (x[0][0], x[0][1], x[1]) for x in cocitCounts.most_common()
            ]
            # Igraph is used to generate the basic graph from the weighted tuples.
            tempG = ig.Graph.TupleList(
                sortCoCitCounts,
                weights=True,
                vertex_name_attr="id",
            )
            # Two different network formats are written.
            # The giant component as a Pajek file, and the full graph in NCOL format.
            self._writeGraphMetadata("cocite", yearname, tempG)
            with outfilepathNCOL.open("w") as outfile:
                for edge in sortCoCitCounts:
                    outfile.write(f"{edge[0]} {edge[1]} {edge[2]}\n")
        if self.debug is True:
            print(f"\tDone in {time.time() - overallStarttime} seconds.")

    def getCitationCoupling(self) -> None:
        """Calculate direct citation coupling.

        For each time slice, direct citation links are created
        if a publication of a specific time slice is cited in
        the same time slice by another publication. The edge has
        a weight of one. Giant component behaviour is highly
        unlikely, therefore only information about the components
        is written to the output path. The full network is saved
        in NCOL format.
        """
        slices = self._window(
            range(self.timerange[0], self.timerange[1] + 1, 1),
            self.window,
        )
        overallStarttime = time.time()
        for sl in list(slices):
            yearname = sl[-1]
            outfilepathNcol = self._checkFileExists(f"citecoup_{yearname}")
            if self.debug is True:
                print(f"Working on year slice {yearname}.")

            dfSlice, dfDataRef, targetSet = self._generateSliceData(sl)

            sourceSet = set(dfSlice[self.pubIdCol].unique())
            directedCitationEdges = []
            for target in tqdm(targetSet):
                overlap = sourceSet.intersection(target[1])
                if overlap:
                    overlapList = list(overlap)
                    for elem in overlapList:
                        directedCitationEdges.append(
                            (target[0], elem, 1),
                        )
            tempG = ig.Graph.TupleList(
                directedCitationEdges,
                directed=True,
                weights=True,
                vertex_name_attr="id",
            )
            self._writeGraphMetadata("citecoup", yearname, tempG, writeGC=False)
            with outfilepathNcol.open("w") as outfile:
                for edge in directedCitationEdges:
                    outfile.write(f"{edge[0]} {edge[1]} {edge[2]}\n")
        if self.debug is True:
            print(f"\tDone in {time.time() - overallStarttime} seconds.")
