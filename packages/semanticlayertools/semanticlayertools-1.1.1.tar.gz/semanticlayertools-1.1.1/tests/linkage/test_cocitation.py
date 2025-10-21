import tempfile
import unittest
from pathlib import Path

import pandas as pd
from semanticlayertools.linkage.citation import Couplings

basePath = Path().parent.resolve().parent
testfiles = list(Path(basePath, "testdata", "cocite").glob("*.json"))
# testchunk = pd.read_json(testfiles[0], lines=True)


class TestCocitationCreation(unittest.TestCase):

    def setUp(self):
        self.outdir = tempfile.TemporaryDirectory()
        self.cociteinit = Couplings(
            Path(basePath, "testdata", "cocite"),
            self.outdir,
            "reference",
            numberProc=2,
        )
