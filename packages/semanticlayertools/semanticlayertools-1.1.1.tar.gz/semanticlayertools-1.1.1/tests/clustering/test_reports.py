import tempfile
import unittest
from pathlib import Path

from semanticlayertools.clustering.leiden import TimeCluster
from semanticlayertools.clustering.reports import ClusterReports
from semanticlayertools.linkage.citation import Couplings

basePath = Path().parent.resolve().parent
filePath = Path(basePath, "testdata", "cocite")


class TestReportsCreation(unittest.TestCase):

    def setUp(self):
        self.outpath = tempfile.TemporaryDirectory()

        self.citeinit = Couplings(
            inpath=filePath,
            outpath=self.outpath.name,
            referenceColumn="reference",
            numberProc=2,
            timerange=(1950, 1959),
        )
        _ = self.citeinit.getCocitationCoupling()

        self.cluinit = TimeCluster(
            inpath=self.outpath.name,
            outpath=self.outpath.name,
            timerange=(1950, 1959),
        )
        self.res1 = self.cluinit.optimize(clusterSizeCompare=10)

        self.reportsinit = ClusterReports(
            infile=self.res1.outfile,
            metadatapath=filePath,
            outpath=self.outpath.name,
            textcolumn="title",
            numberProc=2,
            minClusterSize=1,
            timerange=(1950, 1959),
        )
