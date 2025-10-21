"""Calculate change of publication densities."""
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import polars as pl
from sklearn.neighbors import KernelDensity

logging.basicConfig(
    format="{asctime} - {levelname} - {message} in %(runtime)s seconds.",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

base_path = Path("./")
model_name = "text-embedding-3-large"
filename = base_path / f"df_sampled_full_{model_name}.parquet"

class EmbeddingDensities:
    """Compare embedding densities for filters.

    For a given set of embedded text data, the filter selectes publications
    to compare to the overall density in the embedding space of all other
    publications. This allows to trace the evolution of groups of publications
    in relation to the popularity of the local topic space.

    Assumes the file format Parquet. This allows filtering in very large text
    databases. Filters have the format of a dictionary, where keys are the column titles
    to filter, and values the strings or values that should be contained in the column.
    Embedding_cols denotes the column titles for the 2D embedding space
    in list format, e.g. [x,y].
    """

    def __init__(
        self,
        file_path:Path,
        filters:dict,
        embedding_cols:list,
        *,
        year_col:str = "Year",
        text_col:str = "Title",
    ) -> None:
        """Init class."""
        starttime = time.time()
        self.logger = logging.getLogger(__name__)
        self.file_path = file_path
        self.embedding_cols = embedding_cols
        self.year_col = year_col
        self.text_col = text_col
        selected_columns = embedding_cols.copy()
        selected_columns.extend([year_col, text_col])
        selected_columns.extend(filters.keys())
        selected_columns = list(set(selected_columns))
        filter_list = []
        for column, values in filters.items():
            if isinstance(values[0],str):
                filter_list.append(pl.col(column).str.contains_any(values))
            else:
                filter_list.append(pl.col(column).is_in(values))
        self.filtered_data = pl.scan_parquet(
            file_path,
        ).filter(*filter_list).select(selected_columns).collect()
        self.logger.info("Filtered data", extra={"runtime": f"{time.time() - starttime:.2f}"})

    def shorten_title(self, title:str, max_length:int=30) -> str:
        """Shorten the title to a maximum length with '...' at the end if needed."""
        return (title[:max_length] + "...") if len(title) > max_length else title

    def _get_year_density(self) -> None:
        """Precompute the KDE for all years."""
        starttime = time.time()
        self.kde_data = {}
        year_data = pl.scan_parquet(self.file_path).select(self.year_col).unique().collect()
        years = sorted([x[0] for x in year_data.select(self.year_col).to_numpy()])
        self.max_year = int(max(years))
        for year in years:
            year_data = pl.scan_parquet(
                self.file_path,
            ).filter(pl.col(self.year_col) == year).select(self.embedding_cols).collect()
            if not year_data.is_empty():
                kde = KernelDensity(bandwidth = 1.0, kernel="gaussian").fit(year_data)
                self.kde_data.update(
                    {year: kde},
                )
        self.logger.info("Precalculated densities", extra={"runtime": f"{time.time() - starttime:.2f}"})

    def _create_ref_vectors(self) -> None:
        """Create list of reference vectors."""
        starttime = time.time()
        self.reference_entries = []
        for row in self.filtered_data.iter_rows(named=True):
            self.reference_entries.append(
                (row[self.year_col], row[self.embedding_cols[0]], row[self.embedding_cols[1]], row[self.text_col]),
            )
        self.logger.info("Created reference vector", extra={"runtime": f"{time.time() - starttime:.2f}"})

    def compute_densities(self, plot_title:str, *, show_legend:bool) -> go.Figure:
        """Compute densities and generate traces to plot."""
        starttime = time.time()
        cols = [self.year_col, self.embedding_cols[0], self.embedding_cols[1], self.text_col]
        reference_entries_df = pd.DataFrame(self.reference_entries,columns=cols)
        kde_values = self.kde_data.copy()
        year_range = sorted(kde_values.keys())

        all_results = {
            year: np.maximum(np.exp(kde_values[year].score_samples(reference_entries_df[self.embedding_cols])), 0)
            for year in year_range
        }

        kde_year = pd.DataFrame(all_results)
        time_series = pd.concat([reference_entries_df, kde_year],axis=1)

        median_dict = {year: [] for year in year_range}
        publications = []

        # Process each publication
        for _, row in time_series.iterrows():
            pub_year = row[self.year_col]
            title = row[self.text_col]
            densities = row[year_range]

            # Define years after publication
            x_values = [year for year in year_range if year >= pub_year]
            y_values = [densities[year] if year >= pub_year else np.nan for year in x_values]

            # Calculate median density
            valid_densities = [val for val in y_values if not np.isnan(val)]
            median_density = np.median(valid_densities) if valid_densities else 0

            # Update median dictionary
            for year, val in zip(x_values, y_values):
                if not np.isnan(val):
                    median_dict[year].append(val)

            # Store publication data
            publications.append({
                "pub_year": pub_year,
                "title": title,
                "x_values": x_values,
                "y_values": y_values,
                "median_density": median_density,
            })

        # Sort publications by median density
        publications_sorted = sorted(publications, key=lambda p: p["median_density"], reverse=True)

        # Init figure
        fig = go.Figure()

        # Add publication traces
        for pub in publications_sorted:
            fig.add_trace(
                go.Scatter(
                    x=pub["x_values"],
                    y=pub["y_values"],
                    mode="lines+markers",
                    name=f"{self.shorten_title(pub['title'])} ({int(pub['pub_year'])})",
                ),
            )

        # Calculate and add median density trace
        median_values = []
        valid_years = []
        for year in year_range:
            vals = median_dict[year]
            if vals:
                median_values.append(np.median(vals))
                valid_years.append(year)

        if median_values:
            fig.add_trace(
                go.Scatter(
                    x=valid_years,
                    y=median_values,
                    mode="lines",
                    name="Median density",
                    line={"color": "black", "width": 4},
                ),
            )

        # Update layout settings
        x_axis_start = min(valid_years) if valid_years else self.max_year
        fig.update_layout(
            title=plot_title,
            xaxis_title="Year",
            yaxis_title="Density",
            xaxis={"range": [x_axis_start, self.max_year]},
            legend_title="Publications",
            legend={"x": 1, "y": 0.5, "bgcolor": "rgba(255, 255, 255, 0.5)"},
            showlegend=show_legend,
            height=600,
        )

        self.logger.info("Created plot traces", extra={"runtime": f"{time.time() - starttime:.2f}"})
        return fig

    def create_figure(
        self,
        *,
        save_fig:bool=False,
        plot_title:str = "Density change over time",
        show_legend:bool = True,
    ) -> go.Figure:
        """Run all routines and create the actual plotly figure.

        The plot title can be adjusted as well as whether a legend
        should be shown. If save_fig is set to a path, the figure is
        exported into a HTML file and not ploted.
        """
        self._get_year_density()
        self._create_ref_vectors()
        if save_fig is not False:
            return self.compute_densities(plot_title=plot_title, show_legend=show_legend).write_html(save_fig)
        return self.compute_densities(plot_title=plot_title, show_legend=show_legend).show()
