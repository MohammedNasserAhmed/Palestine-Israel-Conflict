import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from enum import Enum
import warnings
import calendar

# Ignore the FutureWarning message
warnings.filterwarnings("ignore", category=UserWarning)


class Choice(Enum):
    Injuries = "Injuries"
    Fatalities = "Fatalities"

class Reindexer:
    def reindex_monthcols(self, df, months, rename=False):
        """
        Reindexes the columns of a DataFrame based on a list of months.

        Args:
            df: The DataFrame to be reindexed.
            months: The list of months to be used for reindexing.
            rename: Whether to rename the columns using month abbreviations. Defaults to False.

        Returns:
            The reindexed DataFrame. If reindexing or renaming fails, the original DataFrame is returned.
        """
        try:
            df = df.reindex(columns=months)
            if rename:
                month_abbr = calendar.month_abbr[1:]
                df.rename(columns=dict(zip(months, month_abbr)), inplace=True)
        except KeyError as e:
            logging.error("Failed to reindex columns: " + str(e))
        except ValueError as e:
            logging.error("Failed to rename columns: " + str(e))
        except Exception as e:
            logging.error("Failed to reindex or rename columns: " + str(e))

        return df

# remove rows with all zeros
class Processor:
    def remove_zero_rows(self, data):
        """
        Remove rows from the DataFrame where all values are zero.

        Args:
            data (pandas.DataFrame): The input DataFrame.

        Returns:
            pandas.DataFrame: The DataFrame with zero rows removed.
        """
        data = data.loc[(data!=0).any(axis=1)]
        return data
         
class Plotter:
    def __init__(self, df, choice:Choice, cmap : str):
        self._df = None
        self._choice = None
        self.df = df
        self.choice = choice
        self.cmap=cmap
        self.months = self.df['Month'].unique().tolist()
        self.DataFrameProcessor = Processor()
        self.reindexer = Reindexer()
        
        
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
    
    def get_data(self):
        """
        This method groups the data by Year and Month and performs some transformations.
        """
        column_mapping = {
            Choice.Injuries: ["Palestinians Injuries", "Israelis Injuries"],
            Choice.Fatalities: ["Palestinians Killed", "Israelis Killed"]
        }
        column_names = column_mapping[self.choice]
    
        grouped_data = {}
        for var in column_names:
            grouped = self.df.groupby(["Year", "Month"])[var].sum().sort_index(ascending=True)
            grouped = grouped.unstack(level=1).astype(int)
            grouped = self.reindexer.reindex_monthcols(grouped, self.months, rename=True)
            grouped.index.name = None
            grouped.columns.name = None
            grouped_data[var] = grouped

        data = [grouped_data[var] for var in column_names]

        processed_data = self.DataFrameProcessor.remove_zero_rows(grouped)
        data.append(processed_data)

        return data, column_names

    def create_heatmap(self, data, vars):
        """
        This method plots the heatmap for the given data.
        """
        vmax = max(data[0].max().max(), data[1].max().max())
        fig, axn = plt.subplots(2, 1, sharex=True, sharey=True, figsize=(8,8))
        cbar_ax = fig.add_axes([.90, .3, .03, .4])
        #cbar_kws=dict(pad=2,shrink=0.5, drawedges=False)  

        for (i,ax), data_item, var in zip(enumerate(axn.flat), data, vars):
            heatmap_array = data_item.values.T
            heatmap = sns.heatmap(heatmap_array, ax=ax, cmap=self.cmap,
                                  cbar= i ==0,
                                  vmin=0, vmax=vmax,
                                  cbar_ax=None if i else cbar_ax,
                                  xticklabels=data_item.index, yticklabels=data_item.columns)
            ax.set_title(var, fontsize=10, color="#2E4F4F")
            for axis in ['x', 'y']:
                ax.tick_params(axis=axis, colors='#2E4F4F', length=3, rotation=90 if axis == 'x' else 360, width=1, labelsize=8)

        self._customize_colorbar(heatmap, cbar_ax)
        fig.text(-0.07, 0.5, 'MONTH', fontsize=10, color='#2E4F4F', rotation=0, va='center')
        fig.text(0.45, -0.02, 'YEAR', fontsize=10, color='#2E4F4F', rotation=0, va='center')
        fig.tight_layout(rect=[0, 0, .9, 1])
        plt.subplots_adjust(hspace=0.1)
        return fig
    
    
    def _customize_colorbar(self, heatmap, cbar_ax):
        """
        This method customizes the colorbar of the heatmap.
        """
        cbar = heatmap.figure.colorbar(heatmap.collections[0], cax=cbar_ax)
        cbar.set_label(self.choice, fontsize=10, color='#2E4F4F', rotation=360, labelpad=40)
        cmap = cbar.cmap
        norm = cbar.norm
        cbar.outline.set_edgecolor('none')  # Code Improvement Suggestion 1

        for t in cbar.ax.yaxis.get_ticklabels():  # Code Improvement Suggestion 2
            y_pos = t.get_position()[1]
            normalized_y_pos = norm(y_pos)
            color = cmap(normalized_y_pos)
            t.set_color(color)
            t.set_fontsize(8)
    
    def show(self, savefilename):
        """
        This method displays the heatmap and saves it to the specified filename.
        """
        try:
            data, vars = self.get_data()
            fig = self.create_heatmap(data, vars)
            fig.savefig(savefilename + ".pdf", transparent=True, bbox_inches='tight', pad_inches=0)
            plt.show()
        except Exception as e:
            logging.error("An error occurred during the execution of the 'show' method: " + str(e))

               

# Usage
# twilight, rocket_r, magma_r
df = pd.read_csv('E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\data\ps_il.csv')  # replace with your actual dataframe
choice = Choice.Injuries
heatmap = Plotter(df, choice=choice, cmap = "rocket_r")
heatmap.show("heatmap")
