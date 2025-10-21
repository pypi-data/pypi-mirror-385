"""Calculate various corpus linguistic measures."""

import math
import time
from collections import Counter
from itertools import groupby, islice
from operator import itemgetter

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, ttest_ind
from tqdm import tqdm


class CalculateKDL:
    """Calculates KDL scores for time slices.

    .. seealso::

        Stefania Degaetano-Ortlieb and Elke Teich. 2017.
        Modeling intra-textual variation with entropy and surprisal: topical vs. stylistic patterns.
        In Proceedings of the Joint SIGHUM Workshop on Computational Linguistics for Cultural Heritage, Social Sciences,
        Humanities and Literature, pages 68-77,
        Vancouver, Canada. Association for Computational Linguistics.

    """

    def __init__(
        self,
        targetData: pd.DataFrame,
        compareData: pd.DataFrame,
        yearColumnTarget: str = "year",
        yearColumnCompare: str = "year",
        tokenColumnTarget: str = "tokens",
        tokenColumnCompare: str = "tokens",
        *,
        debug: bool = False,
    ) -> None:
        """Init class."""
        self.baseDF = compareData
        self.targetDF = targetData
        self.yearColTarget = yearColumnTarget
        self.yearColCompare = yearColumnCompare
        self.tokenColumnTarget = tokenColumnTarget
        self.tokenColumnCompare = tokenColumnCompare
        self.ngramData = []
        self.minNgramNr = 1
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

    def _createSlices(self, windowSize: int) -> list:
        """Create slices of dataframe."""
        slices = []
        years = sorted(self.targetDF[self.yearColTarget].unique())
        for x in self._window(years, windowSize):
            slices.append(x)
        return slices

    def _calculateDistributions(
        self,
        source: str,
        dataframe: pd.DataFrame,
        timesliceNr: int,
        timeslice: list,
        specialChar: str,
    ) -> list:
        unigram = []
        fourgram = []
        if source == "target":
            yearCol = self.yearColTarget
            tokenCol = self.tokenColumnTarget
        elif source == "compare":
            yearCol = self.yearColCompare
            tokenCol = self.tokenColumnCompare
        dfTemp = dataframe[dataframe[yearCol].isin(timeslice)]
        for _, row in dfTemp.iterrows():
            for elem in row[tokenCol]:
                elemLen = len(elem.split(specialChar))
                if elemLen == 1:
                    unigram.append(elem)
                elif elemLen == 4:
                    fourgram.append(elem.split(specialChar))
        unigramCounts = dict(Counter(unigram).most_common())
        fourgram.sort(key=lambda x: x[3])
        sorted4grams = [
            [specialChar.join(x) for x in list(group)]
            for key, group in groupby(fourgram, itemgetter(3))
        ]
        return (timesliceNr, source, timeslice[-1], unigramCounts, sorted4grams)

    def getNgramPatterns(self, windowSize: int = 3, specialChar: str = "#") -> None:
        """Create dictionaries of occuring ngrams.

        :param specialChar: Special character used to delimit tokens in ngrams (default=#)
        :type specialChar: str
        """
        starttime = time.time()
        self.ngramData = []
        if self.debug is True:
            start = self.baseDF[self.yearColCompare].min()
            end = self.baseDF[self.yearColCompare].max()
            print(f"Got data for {start} to {end}, starting calculations.")
        for idx, timeslice in tqdm(
            enumerate(self._createSlices(windowSize)), leave=False
        ):
            sliceName = timeslice[-1]
            if self.debug is True:
                print(f"\tStart slice {sliceName}.")
            self.ngramData.append(
                self._calculateDistributions(
                    "target", self.targetDF, idx, timeslice, specialChar
                ),
            )
            self.ngramData.append(
                self._calculateDistributions(
                    "compare", self.baseDF, idx, timeslice, specialChar
                ),
            )
        if self.debug is True:
            print(f"Done in  {time.time() - starttime} seconds.")

    def getKDLRelations(
        self, windowSize: int = 3, minNgramNr: int = 5, specialChar: str = "#"
    ) -> list:
        """Calculate KDL relations.

        :param specialChar: Special character used to delimit tokens in ngrams (default=#)
        :type specialChar: str
        """
        self.kdlRelations = []
        distributions = pd.DataFrame(
            self.ngramData,
            columns=["sliceNr", "dataType", "sliceName", "unigrams", "fourgrams"],
        )
        for idx in distributions["sliceNr"].unique():
            targetData = distributions.query('dataType == "target" and sliceNr == @idx')
            sorted4gram = targetData["fourgrams"].iloc[0]
            sorted4gramDict = {
                elem[0].split(specialChar)[3]: elem for elem in sorted4gram
            }
            unigramCounts = targetData["unigrams"].iloc[0]
            year1 = targetData["sliceName"].iloc[0]
            compareDataPost = distributions.query(
                f'dataType == "compare" and (sliceNr >= {idx + windowSize} or sliceNr <={idx - windowSize})',
            )
            for _, row in compareDataPost.iterrows():
                kdlVals = []
                idx2 = row["sliceNr"]
                year2 = row["sliceName"]
                sorted4gram2 = row["fourgrams"]
                sorted4gramDict2 = {
                    elem[0].split(specialChar)[3]: elem for elem in sorted4gram2
                }
                for key, elem1 in sorted4gramDict.items():
                    if unigramCounts[key] < minNgramNr:
                        continue
                    if key not in sorted4gramDict2:
                        continue

                    elem2 = sorted4gramDict2[key]
                    basisLen1 = len(set(elem1))
                    basisLen2 = len(set(elem2))

                    counts1 = dict(Counter(elem1).most_common())
                    counts2 = dict(Counter(elem2).most_common())

                    probList = []
                    for key, val in counts1.items():
                        if key in counts2:
                            probList.append(
                                val
                                / basisLen1
                                * math.log2(
                                    (val * basisLen2) / (basisLen1 * counts2[key])
                                ),
                            )
                    kdl = sum(probList)
                    kdlVals.append(kdl)

                self.kdlRelations.append(
                    (idx, idx2, year1, year2, sum(kdlVals)),
                )
        return self.kdlRelations


class UnigramKLD:
    """Calculate unigram KLD."""

    def __init__(
        self,
        data: pd.DataFrame,
        targetName: str,
        lambdaParam: float = 0.995,
        yearCol: str = "Year",
        authorCol: str = "Author",
        tokenCol: str = "tokens",
        docIDCol: str = "bibcode",
        windowSize: int = 1,
        epsilon: float = 1e-10,
    ) -> None:
        """Init class."""
        self.fullcorpus = data
        self.targetcorpus = data.query(
            f"{authorCol}.fillna('').str.contains('{targetName}')",
        )
        self.lambdaParam = lambdaParam
        self.yearCol = yearCol
        self.tokenCol = tokenCol
        self.docIDCol = docIDCol
        self.winSize = windowSize
        self.epsilon = epsilon

        self.fullModel = {}
        self.fullDocModel = {}
        self.targetModel = {}
        self.targetDocModel = {}

    def _createUnigramModel(self, sl: list, data: pd.DataFrame) -> tuple:
        """Create simple unigram language model."""
        unigrams = []
        unigramsPerDoc = []
        for _, row in data.iterrows():
            text = row[self.tokenCol]
            docid = row[self.docIDCol]
            unigramtext = [x for x in text if "#" not in x]
            docLen = len(unigramtext)
            docCounts = Counter(unigramtext)
            for key, val in docCounts.items():
                unigramsPerDoc.append(
                    (sl, docid, key, val / docLen),
                )
            unigrams.extend(unigramtext)
        termlength = len(unigrams)
        counts = Counter(unigrams)
        unigramModel = {x: y / termlength for x, y in counts.items()}
        return unigramModel, unigramsPerDoc

    def _window(self, seq: list, n: int) -> tuple:
        """Return sliding windows of size n from seq."""
        if n == 1:
            for s in seq:
                yield (s,)
        else:
            for i in range(len(seq) - n + 1):
                yield tuple(seq[i : i + n])

    def _createSlices(self, windowSize: int) -> list:
        """Create non-overlapping slices of dataframe."""
        years = sorted(self.fullcorpus[self.yearCol].unique())
        slices = []

        for i in range(0, len(years), windowSize):
            slice_years = years[i : i + windowSize]
            # Check if there's at least one year with data in this slice
            if any(
                year in self.targetcorpus[self.yearCol].unique() for year in slice_years
            ):
                slices.append(slice_years)

        return slices

    def _createCorpora(self, languageModelType: str = "unigram") -> None:
        yearslices = self._createSlices(self.winSize)
        if languageModelType == "unigram":
            for sl in yearslices:
                slStart = sl[0]
                slEnd = sl[-1]
                slicefull = self.fullcorpus.query(
                    f"{slStart} <= {self.yearCol} <= {slEnd}"
                )
                slicetarget = self.targetcorpus.query(
                    f"{slStart} <= {self.yearCol} <= {slEnd}"
                )

                # Check if slicetarget is not empty and only then create models
                if not slicetarget.empty:
                    # Entferne Einträge von slicetarget aus slicefull damit fullModel nicht targetModel enthält
                    target_ids = slicetarget[self.docIDCol].tolist()
                    slicefull = slicefull[~slicefull[self.docIDCol].isin(target_ids)]

                    self.fullModel[slEnd], self.fullDocModel[slEnd] = (
                        self._createUnigramModel(slEnd, slicefull)
                    )
                    self.targetModel[slEnd], self.targetDocModel[slEnd] = (
                        self._createUnigramModel(slEnd, slicetarget)
                    )

            self.fullModel["complete"], self.fullDocModel["complete"] = (
                self._createUnigramModel("complete", self.fullcorpus)
            )
        elif languageModelType == "trigram":
            text = "This language model is not implemented yet."
            raise NotImplementedError(text)

    def calculateJMS(self, term: str, targetUM: dict, fullUM: dict) -> float:
        """Jelinek-Mercer smoothening with a lower bound."""
        probF = max(fullUM.get(term, 0), self.epsilon)
        probT = max(targetUM.get(term, 0), self.epsilon)
        return self.lambdaParam * probT + (1 - self.lambdaParam) * probF

    def calculateKLD(
        self, languageModelType: str = "unigram", timeOrder: str = "synchron"
    ) -> tuple:
        """Calculate synchronous or asynchronous comparision with a lower bound."""
        yearslices = self._createSlices(self.winSize)
        self._createCorpora(languageModelType=languageModelType)
        resultPointwise = []
        resultSummed = []
        if timeOrder == "synchron":
            for sl in yearslices:
                # slStart = sl[0]
                slEnd = sl[-1]
                sliceResults = []
                # s1 = set(self.fullModel[slEnd].keys())
                s2 = set(self.targetModel[slEnd].keys())
                # allkeys = list(s1.union(s2))
                for term in list(s2):
                    jelinekTarget = self.calculateJMS(
                        term, self.targetModel[slEnd], self.fullModel["complete"]
                    )
                    jelinekFull = self.calculateJMS(
                        term, self.fullModel[slEnd], self.fullModel["complete"]
                    )
                    try:
                        termProb = jelinekTarget * math.log2(
                            (jelinekTarget) / (jelinekFull)
                        )
                    except ZeroDivisionError:
                        termProb = np.inf
                    resultPointwise.append(
                        (slEnd, term, termProb),
                    )
                    sliceResults.append(termProb)
                resultSummed.append(
                    (slEnd, sum(sliceResults) / len(sliceResults)),
                )
        elif timeOrder == "asynchron":
            for sl in yearslices:
                # slStart = sl[0]
                slEnd = sl[-1]
                s2 = set(self.targetModel[slEnd].keys())
                for key in self.fullModel:
                    if not isinstance(key, str):
                        sliceResults = []
                        # s1 = set(self.fullModel[key].keys())
                        # allkeys = list(s1.union(s2))
                        for term in list(s2):
                            jelinekTarget = self.calculateJMS(
                                term,
                                self.targetModel[slEnd],
                                self.fullModel["complete"],
                            )
                            jelinekFull = self.calculateJMS(
                                term, self.fullModel[key], self.fullModel["complete"]
                            )
                            try:
                                termProb = jelinekTarget * math.log2(
                                    (jelinekTarget) / (jelinekFull)
                                )
                            except ZeroDivisionError:
                                termProb = np.inf
                            resultPointwise.append(
                                (slEnd, key - slEnd, term, termProb),
                            )
                            sliceResults.append(termProb)
                        resultSummed.append(
                            (slEnd, key - slEnd, sum(sliceResults) / len(sliceResults)),
                        )
        return resultPointwise, resultSummed

    def perform_stat_test(
        self,
        test_type: str = "welch",
        languageModelType: str = "unigram",
        timeOrder: str = "synchron",
    ) -> tuple:
        """Calculate significance using specified statistical test."""
        resultPointwise, _ = self.calculateKLD(
            languageModelType=languageModelType, timeOrder=timeOrder
        )
        if timeOrder == "synchron":
            resultdf = pd.DataFrame(resultPointwise, columns=["slice", "term", "KLD"])
            tempvalues = []
            errors = []
            for sl in self.targetDocModel:
                dataT = pd.DataFrame(
                    self.targetDocModel[sl], columns=["sl", "docid", "term", "prob"]
                )
                dataF = pd.DataFrame(
                    self.fullDocModel[sl], columns=["sl", "docid", "term", "prob"]
                )
                for term in dataT.term.unique():
                    try:
                        probT = self.calculateJMS(
                            term, self.targetModel[sl], self.fullModel["complete"]
                        )
                        probF = self.calculateJMS(
                            term, self.fullModel[sl], self.fullModel["complete"]
                        )

                        dataseriesT = (
                            dataT.query(f'term == "{term}"')
                            .apply(lambda x: probT, axis=1)
                            .to_numpy()
                        )
                        dataseriesF = (
                            dataF.query(f'term == "{term}"')
                            .apply(lambda x: probF, axis=1)
                            .to_numpy()
                        )

                        if test_type == "welch":
                            test = ttest_ind(dataseriesT, dataseriesF, equal_var=False)
                        elif test_type == "mannwhitney":
                            test = mannwhitneyu(
                                dataseriesT, dataseriesF, alternative="two-sided"
                            )

                        tempvalues.append(
                            (sl, term, test.pvalue, test.statistic),
                        )
                    except Exception as e:
                        errors.append((sl, term, str(e)))
            tempdf = pd.DataFrame(
                tempvalues, columns=["slice", "term", "pvalue", "statistic"]
            )
            result = resultdf.merge(
                tempdf,
                left_on=["slice", "term"],
                right_on=["slice", "term"],
                how="outer",
            )
        elif timeOrder == "asynchron":
            resultdf = pd.DataFrame(
                resultPointwise, columns=["slice", "timedifference", "term", "KLD"]
            )
            tempvalues = []
            errors = []
            for sl in self.targetDocModel:
                dataT = pd.DataFrame(
                    self.targetDocModel[sl], columns=["sl", "docid", "term", "prob"]
                )
                for key in self.fullDocModel:
                    if not isinstance(key, str):
                        dataF = pd.DataFrame(
                            self.fullDocModel[key],
                            columns=["sl", "docid", "term", "prob"],
                        )
                        for term in dataT.term.unique():
                            try:
                                probT = self.calculateJMS(
                                    term,
                                    self.targetModel[sl],
                                    self.fullModel["complete"],
                                )
                                probF = self.calculateJMS(
                                    term,
                                    self.fullModel[key],
                                    self.fullModel["complete"],
                                )

                                dataseriesT = (
                                    dataT.query(f'term == "{term}"')
                                    .apply(lambda x: probT, axis=1)
                                    .to_numpy()
                                )
                                dataseriesF = (
                                    dataF.query(f'term == "{term}"')
                                    .apply(lambda x: probF, axis=1)
                                    .to_numpy()
                                )

                                if test_type == "welch":
                                    test = ttest_ind(
                                        dataseriesT, dataseriesF, equal_var=False
                                    )
                                elif test_type == "mannwhitney":
                                    test = mannwhitneyu(
                                        dataseriesT,
                                        dataseriesF,
                                        alternative="two-sided",
                                    )

                                tempvalues.append(
                                    (sl, key - sl, term, test.pvalue, test.statistic),
                                )
                            except Exception as e:
                                errors.append((sl, key - sl, term, str(e)))
            tempdf = pd.DataFrame(
                tempvalues,
                columns=["slice", "timedifference", "term", "pvalue", "statistic"],
            )
            result = resultdf.merge(
                tempdf,
                left_on=["slice", "timedifference", "term"],
                right_on=["slice", "timedifference", "term"],
                how="outer",
            )
        return result, errors
