"""Run the cocitation time cluster pipeline."""

import multiprocessing
import os
import time
from pathlib import Path

from semanticlayertools.clustering.leiden import TimeCluster
from semanticlayertools.clustering.reports import ClusterReports
from semanticlayertools.linkage.citation import Couplings

num_processes = multiprocessing.cpu_count()


def run(
    inputFilepath: str,
    outputPath: str,
    resolution: float,
    intersliceCoupling: float,
    inputFileType: str = "files",
    minClusterSize: int = 1000,
    timerange: tuple = (1945, 2005),
    timeWindow: int = 3,
    pubIDColumnName: str = "nodeID",
    referenceColumnName: str = "reference",
    yearColumnName: str = "year",
    numberproc: int = num_processes,
    *,
    limitRefLength: bool = False,
    useGC: bool = True,
    skipCocite: bool = False,
    skipClustering: bool = False,
    skipReporting: bool = False,
    timeclusterfile: str = "",
    rerun: bool = False,
    debug: bool = False,
) -> None:
    """Run all steps of the temporal clustering pipepline.

    Creates cocitation networks, finds temporal clusters, writes report files
    for large clusters.

    Default time range is 1945 to 2005. Minimal size for considered clusters is
    1000 nodes. Lists of references are assumed to be contained in column
    "reference".

    By default this routine takes all available cpu cores. Limit this
    to a lower value to allow parallel performance of other tasks.

    :param inputFilepath:  Path to corpora input data
    :type inputFilepath: str
    :param inputFileType:  Type of input data (files or dataframe, default: files)
    :type inputFileType: str
    :param cociteOutpath: Output path for cocitation networks
    :type cociteOutpath: str
    :param timeclusterOutpath: Output path for time clusters
    :type timeclusterOutpath: str
    :param reportsOutpath: Output path for reports
    :type reportsOutpath: str
    :param resolution: Main parameter for the clustering quality function (Constant Pots Model)
    :type resolution: float
    :param intersliceCoupling: Coupling parameter between two year slices, also influences cluster detection
    :type intersliceCoupling: float
    :param minClusterSize: The minimal cluster size, above which clusters are considered (default=1000)
    :type minClusterSize: int
    :param timerange: Time range to evalute clusters for (usefull for limiting computation time, default = (1945, 2005))
    :type timerange: tuple
    :param timeWindow: Time window to join publications into (default: 3)
    :type timeWindow: int
    :param pubIDColumnName: Column name containing the IDs of publications
    :type pubIDColumnName: str
    :param referenceColumnName: Column name containing the references of a publication
    :type referenceColumnName: str
    :param yearColumnName: Column name containing the publiction year in integer format, only used for inputtype dataframe
    :type yearColumnName: str
    :param referenceColumnName: Column name containing the references of a publication
    :type referenceColumnName: str
    :param numberProc: Number of CPUs the package is allowed to use (default=all)
    :type numberProc: int
    :param limitRefLength: Either False or integer giving the maximum number of references a considered publication is allowed to contain
    :type limitRefLength: bool or int
    """
    for subdir in ["cociteGraphs", "timeClusters", "reports"]:
        Path.mkdir(Path(outputPath, subdir), exist_ok=True, parents=True)

    starttime = time.time()
    if skipCocite is False:
        cocites = Couplings(
            inpath=inputFilepath,
            inputType=inputFileType,
            outpath=Path(outputPath, "cociteGraphs"),
            pubIDColumn=pubIDColumnName,
            referenceColumn=referenceColumnName,
            dateColumn=yearColumnName,
            numberProc=numberproc,
            limitRefLength=limitRefLength,
            timerange=timerange,
            timeWindow=timeWindow,
            debug=debug,
        )
        cocites.getCocitationCoupling()
    if skipClustering is False:
        timeclusters = TimeCluster(
            inpath=Path(outputPath, "cociteGraphs"),
            outpath=Path(outputPath, "timeClusters"),
            timerange=timerange,
            useGC=useGC,
        )
        timecl = timeclusters.optimize(
            minClusterSize,
            resolution,
            intersliceCoupling,
        )
        timeclfile = timecl.outfile
    else:
        timeclfile = timeclusterfile
    if skipReporting is False:
        clusterreports = ClusterReports(
            infile=timeclfile,
            metadatapath=inputFilepath,
            outpath=Path(outputPath, "reports"),
            numberProc=numberproc,
            minClusterSize=minClusterSize,
            timerange=(timerange[0], timerange[1] + 3),
            rerun=rerun,
        )
        clusterreports.gatherClusterMetadata()
        clusterreports.writeReports()
    print(f"Done after {(time.time() - starttime)/60:.2f} minutes.")
