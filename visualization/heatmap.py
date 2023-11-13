from typing import List
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from enum import Enum
import warnings
import calendar
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Ignore the FutureWarning message
warnings.filterwarnings("ignore", category=UserWarning)


class Choice(Enum):
    Injuries = "Injuries"
    Fatalities = "Fatalities"


class Preprocessor:
    
    def reindex_monthcols(self, data: pd.DataFrame, months: List[str], rename: bool=False) -> pd.DataFrame:
        """
        Reindex the columns of the given DataFrame using the provided list of months.
    
        Args:
            data (pd.DataFrame): The DataFrame to reindex.
            months (List[str]): The list of months to use for reindexing.
            rename (bool, optional): Whether to rename the columns using month abbreviations. Defaults to False.
    
        Returns:
            pd.DataFrame: The reindexed DataFrame.
        """
        data = data.reindex(columns=months)
        if rename:
            month_abbr = calendar.month_abbr[1:]
            data.rename(columns=dict(zip(months, month_abbr)), inplace=True)
        return data

    def get_data(self, data, choice, months):
        column_mapping = {
            Choice.Injuries: ["Palestinians Injuries", "Israelis Injuries"],
            Choice.Fatalities: ["Palestinians Killed", "Israelis Killed"]
        }
        column_names = column_mapping[choice]

        grouped_data = [self.reindex_monthcols(data.groupby(["Year", "Month"])[var].sum().sort_index(ascending=True).unstack(level=1).astype(int), months, 
                                               rename=True).rename_axis(index=None, columns=None) for var in column_names]

        return grouped_data, column_names


class HeatmapPlot:
    def __init__(self, df, choice: Choice, cmap: str, library: str = 'sns'):
        self._df = None
        self._choice = None
        self.df = df
        self.choice = choice
        self.cmap = cmap
        self.library = library
        self.months = self.df['Month'].unique().tolist()
        self.preprocessor = Preprocessor()

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        self._df = value

    @property
    def choice(self):
        return self._choice

    @choice.setter
    def choice(self, value):
        if not isinstance(value, Choice):
            raise TypeError("Invalid choice value. Allowed values are 'Injuries' and 'Fatalities'.")
        self._choice = value

    def create_heatmap(self, data, vars):
        if self.library == 'sns':
            fig = self._create_heatmap_sns(data, vars)
        elif self.library == 'go':
            fig = self._create_heatmap_go(data)
        else:
            raise ValueError("Invalid library. Allowed values are 'sns' and 'go'.")
        return fig
    def _create_heatmap_sns(self, data, vars):
        vmax = max(data[0].max().max(), data[1].max().max())
        fig, axn = plt.subplots(2, 1, sharex=True, sharey=True, figsize=(8, 8))
        cbar_ax = fig.add_axes([.90, .3, .03, .4])

        for (i, ax), data_item, var in zip(enumerate(axn.flat), data, vars):
            heatmap_array = data_item.values.T
            heatmap = sns.heatmap(heatmap_array, ax=ax, cmap=self.cmap,
                                  cbar=i == 0,
                                  vmin=0, vmax=vmax,
                                  cbar_ax=None if i else cbar_ax,
                                  xticklabels=data_item.index, yticklabels=data_item.columns)
            ax.set_title(var, fontsize=10, color="#2E4F4F")
            for axis in ['x', 'y']:
                ax.tick_params(axis=axis, colors='#2E4F4F', length=3, rotation=90 if axis == 'x' else 360, width=1,
                               labelsize=8)

        self._customize_colorbar(heatmap, cbar_ax)
        fig.text(-0.07, 0.5, 'MONTH', fontsize=10, color='#2E4F4F', rotation=0, va='center')
        fig.text(0.45, -0.02, 'YEAR', fontsize=10, color='#2E4F4F', rotation=0, va='center')
        fig.tight_layout(rect=[0, 0, .9, 1])
        plt.subplots_adjust(hspace=0.1)
        return fig

    def _customize_colorbar(self, heatmap, cbar_ax):
        cbar = heatmap.figure.colorbar(heatmap.collections[0], cax=cbar_ax)
        cbar.set_label(self.choice, fontsize=10, color='#2E4F4F', rotation=360, labelpad=40)
        cmap = cbar.cmap
        norm = cbar.norm
        cbar.outline.set_edgecolor('none')

        for t in cbar.ax.yaxis.get_ticklabels():
            y_pos = t.get_position()[1]
            normalized_y_pos = norm(y_pos)
            color = cmap(normalized_y_pos)
            t.set_color(color)
            t.set_fontsize(8)
            
    def _create_heatmap_go(self, data):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.07)
        max_value = max(data[0].max().max(), data[1].max().max())

        row = 1
        for data_item in data:
            data_item = data_item.T
            xticks = ["%s" % i for i in data_item.columns]
            yticks = ["%s" % i for i in data_item.index]
            heatmap = go.Heatmap(
                z=data_item.values,
                x=xticks,
                y=yticks,
                coloraxis="coloraxis",
                hoverongaps=False,
                hovertemplate='Year: %{x}<br>Month: %{y}<br>Count: %{z}<extra></extra>'
            )
            fig.add_trace(heatmap, row=row, col=1)
            row = row + 1
        self.add_subtitles(fig)
        self.update_layout(fig, max_value)
        return fig
    def add_subtitles(self, fig):
        subtitle_font = dict(size=14, color="#04364A")

        fig.add_annotation(dict(
            xref='paper', yref='paper', x=0.5, y=1.05,
            text='Palestinians', showarrow=False, font=subtitle_font))
        fig.add_annotation(dict(
            xref='paper', yref='paper', x=0.5, y=0.5,
            text='Israelis', showarrow=False, font=subtitle_font))
        
    def _set_colorbar(self):
        colorbar = dict(
            title=self.choice.value,
            titleside="top",
            tickmode="auto",
            ticktext=["Low", "Medium", "High"],
            ticks="outside",
            len=0.75, y=0.5)
        return colorbar

    def update_layout(self, fig, max_value):
        title_font = dict(family="Courier New, monospace", size=18, color="#04364A")
        fig.update_layout(
            title={
                'text': f'Palestine-Israeli Conflict {self.choice.value} 2000 - 2023',
                'x': 0.6,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': title_font,
                'pad': {'b': 10}
            },
            width=1000, height=800,
            hovermode='closest',
            xaxis1=dict(zeroline=False, scaleanchor="y", constrain="domain"),
            xaxis2=dict(zeroline=False, scaleanchor="y", constrain="domain"),
            yaxis=dict(zeroline=False),
            coloraxis=dict(colorscale=self.cmap, cmin=0, cmax=max_value, colorbar=self._set_colorbar()),
            margin=dict(l=300, t=100, b=100)
        )
        fig.update_yaxes(ticksuffix="  ")
      
    def show(self, savefilename=None):
        data, vars = self.preprocessor.get_data(self.df, self.choice, self.months)
        fig = self.create_heatmap(data, vars)
        if savefilename is not None:
            if self.library == 'sns':
                plt.savefig(f'{savefilename}.pdf', transparent=True, bbox_inches='tight', pad_inches=0)
            elif self.library == 'go':
                pio.write_html(fig, f'{savefilename}')
        fig.show()

if __name__ == "__main__":
    df = pd.read_csv("E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\data\ps_il.csv")
    choice = Choice.Injuries
    heatmap = HeatmapPlot(df = df, choice= choice, library = "go", cmap = "ice_r")
    heatmap.show(savefilename="goheatmap")