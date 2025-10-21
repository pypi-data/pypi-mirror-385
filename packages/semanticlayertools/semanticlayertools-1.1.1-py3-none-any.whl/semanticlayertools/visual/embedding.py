"""Create and use text embeddings."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import datamapplot
import matplotlib.pyplot as plt
import pandas as pd
import transformers
from bertopic import BERTopic
from bertopic.representation import (
    KeyBERTInspired,
    MaximalMarginalRelevance,
    TextGeneration,
)
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from umap import UMAP


class TextEmbedder:
    """A text embedder creating visualizations.

    Creates a base embedding, then highlights documents
    and clusters for each concept.

    Returns output path and reduced 2D embedding.
    """

    def __init__(
        self,
        inputDataframe: pd.DataFrame,
        outputBasepath: Path,
        *,
        textColumnName: str,
        titleColumnName: str,
        corpusLanguage: str = "German",
        topicsLanguage: str = "German",
        subsample: bool = False,
        prompt: str = "",
        modelName: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        modelDir: str = "~/.cache/huggingface/hub/",
        device: str = "cuda",
        embeddingName: str = "BAAI/bge-m3",
        umapNeighbors: int = 15,
        umapComponents: int = 5,
        hdbMinClusterSize: int = 50,
        bertopicNrDocs: int = 10,
        bertopicNrWords: int = 10,
    ) -> None:
        """Initialize embedder."""
        self.inputData = inputDataframe
        self.textColumnName = textColumnName
        self.titleColumnName = titleColumnName
        self.umapNeighbors = umapNeighbors
        self.bertopicNrWords = bertopicNrWords
        self.device = device
        now = datetime.now(tz=timezone(timedelta(hours=+2), "CEST"))
        date_time_str = now.strftime("%d_%m_%Y-%H_%M_%S")
        self.outpath = Path(outputBasepath, date_time_str)

        #################################
        ## Create path with date and time
        #################################
        self.outpath.mkdir(
            parents=True,
            exist_ok=True,
        )

        if subsample is True:
            self.inputData = self.inputData.sample(frac=0.1).reset_index(drop=True)

        self.text = self.inputData[self.textColumnName]
        self.titlestring = self.inputData[self.titleColumnName]

        ##################
        ## Embedding parts
        ##################
        self.embedding_model = SentenceTransformer(embeddingName, device=device)

        self.umap_model = UMAP(
            n_neighbors=self.umapNeighbors,
            n_components=umapComponents,
            min_dist=0.0,
            metric="cosine",
        )

        self.hdbscan_model = HDBSCAN(
            min_cluster_size=hdbMinClusterSize,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=True,
        )

        ################
        # Default prompt
        ################
        system_prompt = """
        <s>[INST] <<SYS>>
        You are a helpful, respectful and honest assistant for labeling topics.
        <</SYS>>
        """

        example_prompt = """
        I have a topic that contains the following English documents:
        - Traditional diets in most cultures were primarily plant-based with a little meat on top, but with the rise of industrial style meat production and factory farming, meat has become a staple food.
        - Meat, but especially beef, is the word food in terms of emissions.
        - Eating meat doesn't make you a bad person, not eating meat doesn't make you a good one.

        The topic is described by the following English keywords: 'meat, beef, eat, eating, emissions, steak, food, health, processed, chicken'.

        Based on the information about the topic above, please create a short English label of this topic. Make sure you to only return the label and nothing more.

        [/INST] Environmental impacts of eating meat
        """

        main_prompt = f"""
        [INST]
        I have a topic that contains the following documents in {corpusLanguage}:
        [DOCUMENTS]

        The topic is described by the following {corpusLanguage} keywords: '[KEYWORDS]'.

        Based on the information about the topic above, please create a short label of this topic in {topicsLanguage}. Make sure you to only return the label and nothing more.
        [/INST]
        """

        if not prompt:
            prompt = system_prompt + example_prompt + main_prompt

        tokenizer = transformers.AutoTokenizer.from_pretrained(
            modelName,
            cache_dir=modelDir,
        )
        tokenizer.pad_token_id = tokenizer.eos_token_id

        model = transformers.AutoModelForCausalLM.from_pretrained(
            modelName,
            cache_dir=modelDir,
            trust_remote_code=True,
            device_map=device,
        )
        model.eval()

        generator = transformers.pipeline(
            model=model,
            tokenizer=tokenizer,
            task="text-generation",
            temperature=0.1,
            max_new_tokens=500,
            do_sample=True,
            repetition_penalty=1.1,
        )
        keybert = KeyBERTInspired()
        mmr = MaximalMarginalRelevance(diversity=0.3)
        llm = TextGeneration(
            generator,
            prompt=prompt,
            nr_docs=bertopicNrDocs,
        )
        self.representation_model = {
            "KeyBERT": keybert,
            "Llm": llm,
            "MMR": mmr,
        }

    def _contains_keyword(self, row: int, keyword: str) -> bool:
        """Return True if Keyword in text column or title."""
        return (
            keyword in row[self.textColumnName].lower()
            or keyword in row["title"].lower()
        )

    def run(
        self,
        concepts: tuple = (),
        dateColumnName: str = "None",
    ) -> str:
        """Run embedding, clustering and visualization."""
        base_embeddings = self.embedding_model.encode(
            self.text,
            show_progress_bar=True,
            device=self.device,
        )

        umap_embeddings = self.umap_model.fit_transform(base_embeddings)

        cluster = self.hdbscan_model.fit(umap_embeddings)

        ##################
        # Reduce embedding
        ##################
        reduced_embeddings = UMAP(
            n_neighbors=self.umapNeighbors,
            n_components=2,
            min_dist=0.0,
            metric="cosine",
        ).fit_transform(
            base_embeddings,
        )

        #####################
        # Plot full output
        #####################
        result = pd.DataFrame(reduced_embeddings, columns=["x", "y"])
        result["labels"] = cluster.labels_
        result.to_csv(
            Path(self.outpath, "clusterCoordinates.csv"),
            index=None,
        )

        fig, ax = plt.subplots(figsize=(16, 9))
        outliers = result.loc[result.labels == -1, :]
        clustered = result.loc[result.labels != -1, :]
        plt.scatter(outliers.x, outliers.y, color="#BDBDBD", s=1)
        plt.scatter(clustered.x, clustered.y, c=clustered.labels, s=1, cmap="hsv_r")
        plt.colorbar()
        fig.suptitle("Overview clusters and embedding.")
        plt.savefig(
            Path(self.outpath, "fullplot.png"),
        )
        plt.close(fig)

        #####################
        # If concepts are given, plot for these
        #####################
        if concepts:
            for keyword in self.concepts:

                ##########################
                # Filter text for keywords
                ##########################
                filtered_data = self.inputData.copy()
                filtered_data["seed_documents"] = filtered_data.apply(
                    self._contains_keyword, axis=1, keyword=keyword
                )
                colors = filtered_data["seed_documents"].map(
                    {True: "red", False: "#BDBDBD"}
                )

                fig, ax = plt.subplots(figsize=(16, 9))
                plt.scatter(result.x, result.y, c=colors, s=1)
                plt.colorbar()
                fig.suptitle(f"Parts containing text: {keyword}")
                plt.savefig(
                    Path(self.outpath, f"{keyword}_seedplot.png"),
                )
                plt.close(fig)

                filtered_data["labels"] = result["labels"]

                filtered_data["seeded_documents"] = False

                for label in filtered_data["labels"].unique():
                    if (
                        label != -1
                        and filtered_data.loc[
                            filtered_data["labels"] == label, "seed_documents"
                        ].any()
                    ):
                        filtered_data.loc[
                            filtered_data["labels"] == label, "seeded_documents"
                        ] = True

                filtered_data.loc[filtered_data["labels"] == -1, "seeded_documents"] = (
                    False
                )

                ########################################################
                # Visualize positions of keyword docs in embedding space
                ########################################################
                colors = filtered_data["seeded_documents"].map(
                    {True: "red", False: "#BDBDBD"}
                )

                fig, ax = plt.subplots(figsize=(16, 9))
                plt.scatter(result.x, result.y, c=colors, s=1)
                plt.colorbar()
                fig.suptitle(f"Clusters containing parts with text: {keyword}")
                plt.savefig(
                    Path(self.outpath, f"{keyword}_clusterplot.png"),
                )
                plt.close(fig)

        ##################
        # Generate topic names by LLM
        ##################
        topic_model = BERTopic(
            # Sub-models
            embedding_model=self.embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            representation_model=self.representation_model,
            # Hyperparameters
            top_n_words=self.bertopicNrWords,
            verbose=True,
        )
        topics, probs = topic_model.fit_transform(
            documents=self.text,
            embeddings=base_embeddings,
        )
        topic_model.get_topic_info().to_csv(
            Path(self.outpath, "topics_info.csv"),
            index=None,
        )
        topicsOut = pd.DataFrame(topic_model.get_topics(full=True))
        topicsOut.to_csv(
            Path(self.outpath, "topics.csv"),
            index=None,
        )
        topic_model.save(
            Path(self.outpath, "topicmodel"),
            serialization="safetensors",
        )

        llm_labels = [
            label[0][0].split("\n")[0]
            for label in topic_model.get_topics(full=True)["Llm"].values()
        ]
        topic_model.set_topic_labels(llm_labels)

        topic_model.get_document_info(self.titlestring).to_json(
            Path(self.outpath, "documentInfo.json"),
            lines=True,
            orient="records",
        )

        vis = topic_model.visualize_documents(
            self.titlestring,
            reduced_embeddings=reduced_embeddings,
            hide_annotations=True,
            hide_document_hover=False,
            custom_labels=True,
        )

        vis.write_html(
            Path(self.outpath, "topics_visualization.html"),
        )
        if dateColumnName != "None":

            timestamps = self.inputData[dateColumnName]

            topics_in_time = topic_model.topics_over_time(
                docs=self.text,
                timestamps=timestamps,
                nr_bins=len(
                    range(
                        timestamps.min(),
                        timestamps.max(),
                    ),
                ),
            )
            vis2 = topic_model.visualize_topics_over_time(
                topics_in_time,
                top_n_topics=100,
                custom_labels=True,
            )
            vis2.write_html(
                Path(self.outpath, "topics_in_time_visualization.html"),
            )

        return self.outpath.name


class TopicExplorerMap:
    """Generate explorable map of topics.

    Used after generating data with the TopicEmbedder.
    Uses datamapplot to generate a map of the embedding
    space with LLM-described topic names. Searchable and
    zoomable. Can be connected to Zotero to display
    documents metadata.
    """

    def __init__(
        self,
        inputfolder: Path,
        sourceDocDF: pd.DataFrame,
        outputPath: Path,
        plotTitle: str,
        displayColumn: str,
        searchTextColumn: str,
        *,
        useZotero: bool = False,
        documentIDColumn: str = "None",
        zoteroGroupe: str = "None",
        zoteroGroupeID: str = "None",
    ) -> None:
        """Generate and save html map file."""
        textdata = sourceDocDF
        data = pd.read_json(
            Path(inputfolder, "documentInfo.json"),
            lines=True,
        )
        extraDataColumns = [displayColumn, searchTextColumn]
        if documentIDColumn != "None":
            extraDataColumns.extend(documentIDColumn)
        extraData = textdata[extraDataColumns]

        def createLabels(row: dict) -> str:
            if row["Topic"] < 0:
                return "Unlabelled"
            return row["CustomName"]

        label = data.apply(lambda x: createLabels(x), axis=1)
        coordinates = pd.read_csv(
            Path(inputfolder, "clusterCoordinates.csv"),
        )
        coord = coordinates[["x", "y"]].to_numpy()

        hover_data = textdata[displayColumn]

        settings = {
            "hover_text": hover_data,
            "title": plotTitle,
            "enable_search": True,
            "cluster_boundary_polygons": True,
            "cluster_boundary_line_width": 6,
            "darkmode": True,
            "extra_point_data": extraData,
            "search_field": searchTextColumn,
        }
        if useZotero is True:
            zID = zoteroGroupeID
            zName = zoteroGroupe
            settings.update(
                {
                    "on_click": "window.open(`https://www.zotero.org/groups/{zID}/{zName}/items/{key}/library`)"
                },
            )
        plot = datamapplot.create_interactive_plot(coord, label, **settings)
        plot.save(
            Path(
                outputPath, f"{'_'.join(plotTitle.split())}-Map_{inputfolder.name}.html"
            ),
        )


def explainTopic(
    inputDataframe: pd.DataFrame,
    textColumnName: str,
    *,
    corpusLanguage: str = "English",
    topicsLanguage: str = "English",
    prompt: str = "",
    modelName: str = "meta-llama/Meta-Llama-3-8B-Instruct",
    modelDir: str = "~/.cache/huggingface/hub/",
    device: str = "cuda",
    bertopicNrDocs: int = 10,
    topicsNr: int = 15,
) -> None:
    """Find suitable labels for collections of texts and words.

    Use a LLM to find the labels for a given corpus.
    Returns text explaining each topic.
    """
    ################
    # Default prompt
    ################
    system_prompt = """
    <s>[INST] <<SYS>>
    You are a helpful, respectful and honest assistant for labeling topics.
    <</SYS>>
    """

    example_prompt = """
    I have a topic that contains the following English documents:
    - Traditional diets in most cultures were primarily plant-based with a little meat on top, but with the rise of industrial style meat production and factory farming, meat has become a staple food.
    - Meat, but especially beef, is the word food in terms of emissions.
    - Eating meat doesn't make you a bad person, not eating meat doesn't make you a good one.

    The topic is described by the following English keywords: 'meat, beef, eat, eating, emissions, steak, food, health, processed, chicken'.

    Based on the information about the topic above, please create a short English label of this topic. Make sure you to only return the label and nothing more.

    [/INST] Environmental impacts of eating meat
    """

    main_prompt = f"""
    [INST]
    I have a topic that contains the following documents in {corpusLanguage}:
    [DOCUMENTS]

    The topic is described by the following {corpusLanguage} keywords: '[KEYWORDS]'.

    Based on the information about the topic above, please create a short label of this topic in {topicsLanguage}. Make sure you to only return the label and nothing more.
    [/INST]
    """

    if not prompt:
        prompt = system_prompt + example_prompt + main_prompt

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        modelName,
        cache_dir=modelDir
    )
    tokenizer.pad_token_id = tokenizer.eos_token_id

    model = transformers.AutoModelForCausalLM.from_pretrained(
        modelName,
        cache_dir=modelDir,
        trust_remote_code=True,
        device_map=device,
    )
    model.eval()

    generator = transformers.pipeline(
        model=model,
        tokenizer=tokenizer,
        task="text-generation",
        temperature=0.1,
        max_new_tokens=500,
        do_sample=True,
        repetition_penalty=1.1,
    )
    keybert = KeyBERTInspired()
    mmr = MaximalMarginalRelevance(diversity=0.3)
    llm = TextGeneration(
        generator,
        prompt=prompt,
        nr_docs=bertopicNrDocs,
    )
    representation_model = {
        "KeyBERT": keybert,
        "Llm": llm,
        "MMR": mmr,
    }

    topic_model = BERTopic(
        representation_model=representation_model,
        top_n_words=20,
        verbose=True,
    )

    text = inputDataframe[textColumnName]

    topics, probs = topic_model.fit_transform(
        documents=text,
    )
    topic_model.reduce_topics(text, topicsNr)

    fullTopicInfo = topic_model.get_topics(full=True)
    llmLabels = fullTopicInfo["Llm"].apply(lambda row: row[0][0].split("\n")[0])
    fullTopicInfo.insert(0, "llmLabel", llmLabels)

    outtext = f"\n\n\tTopic labels in cluster for {topicsNr} topics:\n"
    for idx, data in fullTopicInfo.iterrow():
        outtext += f"\t\tTopic {idx - 1}: {data['llmLabel']}\n"
    return outtext
