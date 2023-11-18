import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go
import math
import time
import plotly.express as px
from typing import List 
from pydantic import BaseModel, validator, Field
import logging
import matplotlib.patches as patches


class Histogram:
    def __init__(self, data: pd.DataFrame, variable: str, 
                 colors: List[str] = ["#BCA37F", "#113946", '#053B50'],
                 title:str=None):
        """
        Initialize the Histogram class.

        Parameters:
        - data (pd.DataFrame): The input data for creating the histogram.
        - variable (str): The variable to be plotted on the y-axis of the histogram.
        - colors (List[str]): The list of colors to be used for the histogram bars.

        Raises:
        - TypeError: If data is not a pandas DataFrame.
        - ValueError: If data is empty or contains NaN values.
        - TypeError: If colors is not a list.
        - ValueError: If colors has less than 2 elements.
        - ValueError: If any element in colors is not a string.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Data cannot be empty")
        if data.isnull().values.any():
            raise ValueError("Data contains NaN values")

        self.data = data
        if not isinstance(variable, str):
            raise TypeError("Variable Input should be a string")
        self.variable = variable
        if not isinstance(colors, list):
            raise TypeError("Colors must be a list")
        if len(colors) < 2:
            raise ValueError("Colors must have at least 2 elements")
        if not all(isinstance(color, str) for color in colors):
            raise ValueError("All elements in colors must be strings")

        self.colors = colors
        self.title = title

    def create_histogram(self, width, height):
        """
        Create a histogram plot using Plotly Express.

        Raises:
        - IndexError: If self.colors has less than 2 elements.
        """
        columns = ["Year", self.variable, "Group"]
        if len(self.colors) >= 2:
            color_discrete_sequence = self.colors[:2]
        else:
            color_discrete_sequence = self.colors
        fig = px.histogram(data_frame=self.data[columns], x="Year", y=self.variable, color="Group",
                           hover_data=columns, color_discrete_sequence=color_discrete_sequence)
        self._create_annotations(fig)
        fig.update_layout(
            
            title={
                'text': self.title,
                'font': {
                    'size': 24,
                    'color': self.colors[2],
                    'family': 'bold'
                   
                },
                'x': 0.5,
                'y': 0.98,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            
            xaxis=dict(
                title={
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45,
                automargin=True
            ),
            yaxis=dict(
                title={
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45,
                automargin=True
                
            ),
            paper_bgcolor='#F1EFEF',
            plot_bgcolor='white',
            width=width,
            height=height
        )
        
        return fig
    def _create_annotations(self, fig): 
        """
        Create annotations for the given figure.

        Args:
            fig (go.Figure): The figure to add annotations to.
        """
        texts = ["aiNarabic", f"{self.variable}"]
        colors = ['lightgray', '#3F1D38']  
        font_sizes = [14,19]  
        xs =[0.045,0.5]
        ys=[1.07,1.06]
        bc =["#F1EFEF",'white']
        for text, color, font_size, x, y, bg_color in zip(texts, colors, font_sizes, xs, ys, bc):
            text_annotation = go.layout.Annotation(
                x=x,
                y=y,
                xref='paper',
                yref='paper',
                xanchor='center',
                yanchor='top',
                showarrow=False,
                text=text,
                align='center',
                font_size=font_size,
                font_color=color,
                bgcolor=bg_color
            )
            fig.add_annotation(text_annotation)

                
    def show(self, width: int = 1000, 
             height: int = 500, 
             save_filename:str = None):
        """
        Show the histogram plot.

        Parameters:
        - width (int): The width of the histogram plot.
        - height (int): The height of the histogram plot.
        """
        fig = self.create_histogram(width, height)
        if save_filename is not None:
            pio.write_html(fig, file=save_filename)
        fig.show()



class PXScatter(BaseModel):
    df: List[dict] = Field(..., description="Input data should be a dictionary")
    var: str =  Field(..., description="Input variable should be a string and a column in data")
    title : str =Field(..., fdescription = "Tile of total project")
    @validator('df')
    def validate_df(cls, df):
        if not isinstance(df, list):
            raise ValueError('df must be a dictionary')
        for item in df:
            if not isinstance(item, dict):
                raise ValueError('Each item in df must be a dictionary')
        df = pd.DataFrame(df)
        return df

    @classmethod
    @validator('var')
    def validate_var(cls, var: str, df: pd.DataFrame)-> str:
        """
        Validates the input variable.

        Args:
            var (str): The input variable to be validated.

        Returns:
            str: The validated input variable.

        Raises:
            TypeError: If the input variable is not a string.
            KeyError: If the input variable is not a column in the dataframe.
        """
        if not isinstance(var, str):
            raise TypeError('The input variable must be a string.')
        if var not in df.columns:
            raise KeyError('The input variable must be a column in the dataframe.')
        return var

    def log_execution_time(func):
        def wrapper(*args, **kwargs):
            logging.info(f'Starting to execute {func.__name__}')
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logging.info(f'Finished executing {func.__name__} in {execution_time} seconds')
            return result
        return wrapper

    @log_execution_time
    def show(self, save_filename: str = None):

        try:
            logging.info('Starting to plot scatter')
            if self.var.split()[1] == "Killed":
                label = f"{self.var.split()[0]} Fatalities"
            else :
                label = self.var
            # Create a scatter trace
            trace = go.Scatter(
                x=self.df.index,
                y=self.df[self.var],
                mode='markers',
                marker=dict(
                    size=self.df[self.var],
                    sizeref=(2.0 * self.df[self.var].max()) / (70**2),
                    sizemode='area',
                    color=self.df[self.var],
                    colorscale="temps",
                    colorbar=dict(
                        title=dict(
                            text="",
                            font=dict(size=12, color='#414A4C')
                        ),
                        tickfont=dict(size=8, color='#777'),
                        
                        
                    ),
                    showscale=True
                ),
                hoverinfo='text',
                hovertext='Sum of: ' + label + ": "+ self.df[self.var].astype(str)
            )
            
            # Create a layout
            layout = go.Layout(
                title=dict(
                    text=label.upper(),
                    font=dict(size=16, color='#0039A6'),
                    x=0.5,
                    y=0.85
                ),
                xaxis=dict(
                    
                    showticklabels=False, showgrid=False
                ),
                yaxis=dict(
                    showticklabels=False, showgrid=False
                ),
                width=800,  # Set the width of the figure
                height=500,
                annotations =[dict(text = "aiNarabic.ai<br>DATA SOURCE : https://www.ochaopt.org/data/casualties",
                            y = 0.0, x=1.0,
                            xref="paper",yref="paper",
                            showarrow=False,
                            font=dict(
                                size=14,
                                color="gray"

                            ),align="left"),
                             
                              dict(text = self.title,
                            x = 0.5, y=1.25,
                            xref="paper",yref="paper",
                            showarrow=False,
                            #bgcolor = "",
                            font=dict(
                                size=24,
                                color="#872341",
                               
                                family = "bold",

                            ),align="center")
                              ]
            )
            # Define the rectangle data points
            

            # Create a figure
            fig = go.Figure(data=[trace], layout=layout)
            # Show the figure
            if  save_filename is not None :
                fig.write_html(save_filename)
            fig.show()

            logging.info('Finished plotting scatter')
        except Exception as e:
            logging.error(f'Error plotting scatter: {str(e)}')
            raise


class Bubbles:
    def __init__(self, data, title = None,
                 colors : List[str] = ['#088395','#E55604','#04364A']):
        """
        Initialize the class with data, colors, and optional required columns.

        Args:
            data (pd.DataFrame): The input data as a pandas DataFrame.
            colors (list): The list of colors.
            required_columns (list, optional): The list of required columns. Defaults to ['Year', 'Month', 'Deaths', 'Injuries', 'Group'].
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Data cannot be empty")
        if data.isnull().values.any():
            raise ValueError("Data contains NaN values")

        self.data = data

        if not isinstance(colors, list):
            raise TypeError("Colors must be a list")
        if len(colors) < 2:
            raise ValueError("Colors must have at least 2 elements")
        if not all(isinstance(color, str) for color in colors):
            raise ValueError("All elements in colors must be strings")

        self.colors = colors 

        
        self.title = title 
        self.create_text_and_sizes()
        
    def create_text_and_sizes(self):
        """
        Create text and size columns
        """
        self.data['text'] = self.data.apply(lambda row: ('Year: {year}<br>'+
                                                         'Month: {month}<br>'+
                                                         'Fatalities: {fatalities}<br>'+
                                                         'Injuries: {injuries}<br>').format(year=row['Year'],
                                                                                            month=row['Month'],
                                                                                            fatalities=row['Fatalities'],
                                                                                            injuries=row['Injuries']), axis=1)
        self.data['size'] = self.data['Injuries'].apply(math.sqrt)

    def create_figure(self):
        """
        Create a scatter plot from the DataFrame
        """
        max_size = max(self.data['size'])
        sizeref = 2. * max_size / (100 * 50)

        # Dictionary with dataframes for each group
        groups = self.data['Group'].value_counts().index.tolist()
        groups_data = {group: self.data[self.data['Group'] == group] for group in groups}

        fig = go.Figure()
        
        fig.add_traces([go.Scatter(
            x=group['Fatalities'], y=group['Injuries'],
            name=group_name, text=group['text'],
            marker_size=group['size'],
            marker_color=self.colors[2] if group_name == 'Israel' else self.colors[1]
        ) for group_name, group in groups_data.items()])

        # Tune marker appearance and layout
        fig.update_traces(mode='markers', marker=dict(sizemode='area',
                                                      sizeref=sizeref, line_width=0.5))
        fig.update_xaxes(showline=False, overwrite=False)

        fig.update_layout(
    
            xaxis=dict(
                title={
                    'text': self.data.columns[3].upper(),
                    'font': {
                        'size': 14,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                type='log',
                gridwidth=3,
                tickangle=-45  # Rotate tick labels by -45 degrees
            ),
            yaxis=dict(
                title={
                    'text': self.data.columns[2].upper(),
                    'font': {
                        'size': 14,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45
                
            ),
             annotations =[dict(text = "aiNarabic.ai",
                            x = 0.0, y=1.08,
                            xref="paper",yref="paper",
                            showarrow=False,
                            font=dict(
                                size=14,
                                color="lightgray"

                            ),align="left"),
                            dict(text = self.title,
                            x = 0.5, y=1.3,
                            xref="paper",yref="paper",
                            showarrow=False,
                            #bgcolor = "",
                            font=dict(
                                size=24,
                                color=self.colors[2],
                               
                                family = "bold",

                            ),align="center")],

            paper_bgcolor='#F1EFEF',
            plot_bgcolor='white',

            width=800,
            height=450  #

        )
        
        return fig

    def show(self, save_filename : str = None):
        """
        Display the plot
        Args:
            filename (str, optional): The filename for the plot. Defaults to 'bubblechart.html'.
        """

        fig = self.create_figure()
        if fig is None:
            raise ValueError("Failed to create the plot")
        if save_filename is not None:
            if not save_filename.endswith('.html'):
                raise ValueError("Invalid filename. Filename must be end with '.html'")
        
            pio.write_html(fig, file=save_filename)
        fig.show()

if __name__ == "__main__":
    data = pd.read_excel("E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\data\ps_il.xlsx")
    save_filename = "E:\MyOnlineCourses\ML_Projects\palestine_israel_conflict\outputs\Bubbles.html"
    #data=data.to_dict(orient="records")
    title = "Human Cost of Palestine-Israel Conflict <br> 2000 To Oct-2023"
    scatter_plot = Bubbles(data=data, title=title)
    scatter_plot.show(save_filename)