import pandas as pd
import os
from IPython.core.display import display, HTML
import matplotlib.pyplot as plt


class Loader:
    """
    A class used to load data from CSV files.

    Methods
    -------
    load_csv(path): Loads and prints the data from the CSV file path if it is not None.
    printout(data, title): Prints the data with a title.
    get_dataset_name(path): Returns the name of the file from the file path.
    get_title(t, size): Displays a title using matplotlib.
    """
 
    def __init__(self):
        pass

    def read_csv(self, path):
        """
        Load a CSV file and print its top 5 observations.

        Parameters:
        path (str): The path of the CSV file.

        Returns:
        DataFrame: The loaded DataFrame.
        """
        if not path:
            raise ValueError("Please provide a data path.")

        df = pd.read_csv(path)

        return df
    def read_xsls(self, path):
        """
        Load an Excel file and print its top 5 observations.

        Parameters:
        path (str): The path of the excel file.

        Returns:
        DataFrame: The loaded DataFrame.
        """
        if not path:
            raise ValueError("Please provide a data path.")

        df = pd.read_excel(path)

        return df

    

    def printout(self, data, show_index=False, title=None):
        """
        Display a pandas DataFrame with custom formatting.
        Removes trailing zeros and formats float numbers to 2 decimal places.

        Parameters:
        data (DataFrame): The DataFrame to display.
        show_index (bool): Whether or not to show the DataFrame index.
        title (str): The title of the DataFrame.
        """
        with open('CSS\styles.css', 'r') as f:
            css = f.read()
        # Define CSS styling

        data = data.style.format("{:.2f}").set_table_styles([{"selector": "th", "props": [("background-color", "#113946"), ("color", "white"), ("font-size", "10pt")]}, {"selector": "td", "props": [("background-color", "#F9F3CC"), ("color", "black"), ("font-size", "8pt"), ("font-weight", "bold")]}])
        styled_df = HTML(css + data.render(index=show_index))
        if title:
            self.plot_title(title)
        display(styled_df)

    @staticmethod
    def get_dataset_name(path):
        """
        Return the name of the file from the file path.

        Parameters:
        path (str): The file path.

        Returns:
        str: The name of the file.
        """
        filename = os.path.basename(path)
        name, _ = os.path.splitext(filename)
        return name
    
    @staticmethod
    def plot_title(t, size=(12.6,0.5), fc= "#113946", pfc ="none"):  #fc= "#113946", pfc ="#F9F3CC"
        """
        Display a title using matplotlib.

        Parameters:
        t (str): The title to display.
        size (tuple): The size of the figure. Default is (11,0.5).
        """
        fig, ax = plt.subplots(figsize=size)
        ax.text(0.5, 0.5, t, fontsize=12, color=fc, ha='center', va='center',fontweight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_facecolor(pfc)
        fig.patch.set_facecolor(pfc)
        plt.show()
        
class DataFrameCopier:
    def __init__(self):
        self.df = None
    def copy_dataframe(self, df):
        self.df = df.copy()
    def recall_dataframe(self):
        return self.df