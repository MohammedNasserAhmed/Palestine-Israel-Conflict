from pathlib import Path
import pandas as pd
import os
from enum import Enum


class Choice(Enum):
    Injuries = "Injuries"
    Fatalities = "Fatalities"

class Loader:
    """
    A class used to load data from CSV files.

    Methods
    -------
    read_csv(path): Loads and prints the data from the CSV file path if it is not None.
    read_xsls(path): Loads and prints the data from the Excel file path if it is not None.
    printout(data, show_index=False, title=None): Prints the data with a title.
    get_dataset_name(path): Returns the name of the file from the file path.
    plot_title(t, size=(12.6,0.5), fc= "#113946", pfc ="none"): Returns the title string.
    """

    def __init__(self):
        #with open('path/to/your/.css file', 'r') as f:
        #    self.css = f.read()
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

        if not Path(path).is_file():
            raise FileNotFoundError("File does not exist at the given path.")

        try:
            df = pd.read_csv(path, encoding='utf-8')
        except pd.errors.ParserError as e:
            raise ValueError("Error occurred while parsing the CSV file.") from e

        return df

    def read_xsls(self, path, header=None, index_col=None, usecols=None):
        """
        Load an Excel file and print its top 5 observations.

        Parameters:
        path (str): The path of the excel file.
        header (int, list of int, default None): Row(s) to use as the column names.
        index_col (int, str, sequence[int/str], or False, default None): Column(s) to set as index(MultiIndex).
        usecols (int, str, list-like, or callable, default None): Return a subset of the columns.

        Returns:
        DataFrame: The loaded DataFrame.
        """
        if not path:
            raise ValueError("Please provide a data path.")

        if not os.path.exists(path):
            raise FileNotFoundError("File does not exist at the given path.")

        if not path.endswith(('.xls', '.xlsx')):
            raise ValueError("Invalid file extension. Only '.xls' and '.xlsx' files are supported.")

        try:
            df = pd.read_excel(path, header=header, index_col=index_col, usecols=usecols)
        except pd.errors.ParserError as e:
            raise ValueError("Error occurred while parsing the Excel file.") from e

        return df

   
    def dataframe_as_table(self, data, show_index=False, save_html=False, html_path=None, html_filename=None):
        """
        Display a pandas DataFrame with custom formatting.
        Removes trailing zeros and formats float numbers to 2 decimal places.

        Parameters:
        data (DataFrame): The DataFrame to display.
        show_index (bool): Whether or not to show the DataFrame index.
        title (str): The title of the DataFrame.
        save_html (bool): Whether or not to save the output to an HTML file.
        html_path (str): The path to save the HTML file.
        html_filename (str): The filename of the HTML file.

        Returns:
        str: The HTML string of the formatted DataFrame.
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("The 'data' parameter must be a pandas DataFrame.")

        if data.empty:
            return None

        table_styles = [{"selector": "th", "props": [("background-color", "#113946"), ("color", "white"), ("font-size", "10pt")]},
                        {"selector": "td", "props": [("background-color", "#F9F3CC"), ("color", "black"), ("font-size", "8pt"), ("font-weight", "bold")]}]

        data = data.applymap(lambda x: "{:.2f}".format(x).rstrip('0').rstrip('.') if isinstance(x, float) else x)
        styled_df = data.style.set_table_styles(table_styles)

        if save_html and Path(html_path).is_dir():
            filename = 'styled_df.html' if html_filename is None else html_filename
            try:
                with open(os.path.join(html_path, filename), 'w') as f:
                    f.write(styled_df.to_html(index=show_index))
            except (IOError, PermissionError) as e:
                print("Error occurred while writing to the file:", str(e))

        return styled_df

    @staticmethod
    def get_dataset_name(path):
        """
        Return the name of the file from the file path.

        Parameters:
        path (str): The file path.

        Returns:
        str: The name of the file.
        """
        filename = Path(path).name
        name, _ = os.path.splitext(filename)
        return name

        
class DataFrameCopier:
    def __init__(self, df=None):
        """
        Initialize the DataFrameCopier object.

        Parameters:
        - df (pandas.DataFrame, optional): The dataframe to be copied. Defaults to None.
        """
        self.df = df.copy() if df is not None else None

    def get_dataframe(self):
        """
        Get the copied dataframe.

        Returns:
        - pandas.DataFrame: The copied dataframe.
        """
        return self.df

    def __str__(self):
        """
        Get a string representation of the DataFrameCopier object.

        Returns:
        - str: The string representation of the DataFrameCopier object.
        """
        return str(self.df)

    def __repr__(self):
        """
        Get a detailed representation of the DataFrameCopier object.

        Returns:
        - str: The detailed representation of the DataFrameCopier object.
        """
        return f"DataFrameCopier(df={self.df})"
    
loader = Loader()
loader.get_dataset_name("E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\data\ps_il.csv")