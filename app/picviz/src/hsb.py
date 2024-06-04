import json
import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go
import math
import time
import plotly.express as px
from typing import List 
import logging

class Config:
    """
    Config class holds the configuration settings for the visualization.
    """
    paper_bgcolor: str = '#F1EFEF'
    colors: List[str] = ["#BCA37F", "#113946", '#053B50',"#FE0000"]
    title: str = "Human Cost of Palestine-Israel Conflict (2000 To April-2024)"
    title_size = float = 20
    plot_bgcolor: str = 'white'
    xgridcolor: str = "#F1EFEF"
    ygridcolor: str = "#F1EFEF"
    axiseslabel_size : float = 14
    axisestick_size : float = 9
    width: int = 800
    height: int = 450
    signature: str = "ainarabic.ai<br>Data Source : OCHA"
    signature_color = '#279EFF'
    @classmethod
    def from_dict(cls, config_dict):
        """
        Create an instance of Config from a dictionary.
        
        Args:
            config_dict (dict): Dictionary containing the configuration settings.
        
        Returns:
            Config: An instance of Config with the provided configuration settings.
        """
        config = cls()
        config.paper_bgcolor = config_dict.get('paper_bgcolor', '#F1EFEF')
        config.colors = config_dict.get('colors', ["#BCA37F", "#113946", '#053B50'])
        config.title = config_dict.get('title', "Human Cost of Palestine-Israel Conflict From 2000 To April-2024")
        config.title = config_dict.get('title_size', 20)
        config.plot_bgcolor = config_dict.get('plot_bgcolor', 'white')
        config.xgridcolor = config_dict.get('xgridcolor', "#F1EFEF")
        config.ygridcolor = config_dict.get('ygridcolor', "#F1EFEF")
        config.axiseslabel_size = config_dict.get('axiseslabel_size', 16)
        config.axisestick_size = config_dict.get('axisestick_size', 12)
        config.width = config_dict.get('width', 1000)
        config.height = config_dict.get('height', 500)
        config.signature = config_dict.get('signature', "ainarabic.ai<br>Data Source : OCHA")
        config.signature_color = config_dict.get('signature_color', "#279EFF")
        return config
        
    @classmethod
    def from_json(cls, json_file):
        """
        Create an instance of Config from a JSON file.
        
        Args:
            json_file (str): Path to the JSON file containing the configuration settings.
        
        Returns:
            Config: An instance of Config with the configuration settings from the JSON file.
        """
        with open(json_file, 'r') as file:
            config_dict = json.load(file)
        return cls.from_dict(config_dict)
class Histogram:
    def __init__(self, data: pd.DataFrame, variable: str):
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
        self.config = Config()
        
    

    

    def create_histogram(self):
        """
        Create a histogram plot using Plotly Express.

        Raises:
        - IndexError: If self.colors has less than 2 elements.
        """
        columns = [self.data.columns[0], self.variable, self.data.columns[4]]
        if len(self.config.colors) >= 2:
            color_discrete_sequence = self.config.colors[:2]
        else:
            color_discrete_sequence = self.config.colors
        fig = px.histogram(data_frame=self.data[columns], x="Year", y=self.variable, color="Group",
                           hover_data=columns, color_discrete_sequence=color_discrete_sequence)
        self.create_annotations(fig)
        fig.update_layout(
            
            title={
                'text': self.config.title,
                'font': {
                    'size': self.config.title_size,
                    'color': self.config.colors[2],
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
                        'size': self.config.axiseslabel_size,
                        'color': self.config.colors[2],
                        'family': 'bold'
                    }
                },
                tickfont=dict(size=self.config.axisestick_size,
                              color = "#3F1D38"),
                gridcolor=self.config.xgridcolor,
                gridwidth=3,
                tickangle=-45,
                automargin=True
            ),
            yaxis=dict(
                title={
                    'font': {
                        'size': self.config.axiseslabel_size,
                        'color': self.config.colors[2],
                        'family': 'bold'
                    }
                },
                tickfont=dict(size=self.config.axisestick_size,
                              color = "#3F1D38"),
                gridcolor=self.config.ygridcolor,
                gridwidth=3,
                tickangle=-45,
                automargin=True
                
            ),
            paper_bgcolor=self.config.paper_bgcolor,
            plot_bgcolor=self.config.plot_bgcolor,
            width=self.config.width,
            height=self.config.height
        )
        #fig.update_yaxes(tickvals=[1000, 3000, 5000, 7000, 9000, 11000, 13000, 15000])

        return fig

    def create_annotations(self, fig): 
        """
        Create annotations for the given figure.
   
        Args:
            fig (go.Figure): The figure to add annotations to.
        """
        variable_text = f"{self.variable}".upper()
        annotations = [
            {
                'text': variable_text,
                'color': '#3F1D38',
                'font_size': 14,
                'x': 0.5,
                'y': 1.06,
                'bg_color': 'white'
            },
            {
                'text':self.config.signature,
                'color': self.config.signature_color,
                'font_size': 10,
                'x': 1.1,
                'y': 0.0,
                'bg_color': '#F1EFEF'
            }
        ]
        for annotation in annotations:
            text_annotation = go.layout.Annotation(
                x=annotation['x'],
                y=annotation['y'],
                xref='paper',
                yref='paper',
                xanchor='center',
                yanchor='top',
                showarrow=False,
                text=annotation['text'],
                align='left',
                font_size=annotation['font_size'],
                font_color=annotation['color'],
                bgcolor=annotation['bg_color']
            )
            fig.add_annotation(text_annotation)

                
    def show(self, save_filename: str = None):
        """
        Show the histogram plot.

        Parameters:
        - save_filename (str): The filename to save the plot as HTML.

        Returns:
        - str: A success message if the plot is successfully saved as HTML.
        """
        fig = self.create_histogram()
        if save_filename is not None and isinstance(save_filename, str) and save_filename.endswith(".html"):
            try:
                fig.write_html(save_filename)
                
            except Exception as e:
                return f"Error saving plot as HTML: {str(e)}"
        fig.show()
        



class Scatter:
    def __init__(self, df : pd.DataFrame, var : str):
        self.df = df
        self.var = self.validate_var(var, self.df)
        self.config = Config()

    @staticmethod
    def validate_var(var, df):
        if not isinstance(var, str):
            raise TypeError('The input variable must be a string.')
        if var not in df.columns:
            raise KeyError('The input variable must be a column in the dataframe.')
        return var

    
    # def log_execution_time(func):
    #     def wrapper(*args, **kwargs):
    #         logging.info(f'Starting to execute {func.__name__}')
    #         start_time = time.time()
    #         result = func(*args, **kwargs)
    #         end_time = time.time()
    #         execution_time = end_time - start_time
    #         logging.info(f'Finished executing {func.__name__} in {execution_time} seconds')
    #         return result
    #     return wrapper

    #@log_execution_time
    def show(self, save_filename: str = None):
        """_summary_

        Args:
            save_filename (str, optional): 
            _description_
            To set path to html-file-name that used to save figure, Defaults to None.
        """
        yearstxt = "2000 2005 2010 2015 2020 2024"
        try:
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
                hovertext='Sum of ' + label + ' in ('+self.df["Year"].astype(str)+ ", "+self.df["Month"].astype(str)+") : "+ self.df[self.var].astype(str)
            )
             
            # Create a layout
            layout = go.Layout(
                title=dict(
                    text=label.upper(),
                    font=dict(size=14, color='#0039A6'),
                    x=0.5,
                    y=0.81
                    
                ),
                xaxis=dict(
                    
                    showticklabels=False, showgrid=False,
                    
                ),
                yaxis=dict(
                    showticklabels=False, showgrid=False
                ),
                width=self.config.width,  # Set the width of the figure
                height=self.config.height,
                
                annotations =[dict(text = self.config.signature,
                            x = 1.15, y=-0.25,
                            xref="paper",yref="paper",
                            showarrow=False,
                            font=dict(
                                size=10,
                                color=self.config.signature_color

                            ),align="left"),
                             
                              dict(text = self.config.title,
                            x = 0.5, y=1.25,
                            xref="paper",yref="paper",
                            showarrow=False,
                            font=dict(
                                size=self.config.title_size,
                                color="#872341",
                               
                                family = "bold",

                            ),align="center"),
                              dict(
                                  text = " " * 25 + yearstxt.replace(" ", " " * 35),
                            x = 0.45, y=0,
                            xref="paper",yref="paper",
                            showarrow=False,
                            font=dict(
                                size=10,
                                color="#6C0345",
                               
                                family = "bold",

                            ),align="center")
                              ]
            )
            

            # Create a figure
            fig = go.Figure(data=[trace], layout=layout)
            if  save_filename is not None :
                fig.write_html(save_filename)
            fig.show()
            
        except Exception as e:
            raise e


class Bubbles:
    def __init__(self, data : pd.DataFrame):
        """
        Initialize the class with data, colors, and optional required columns.

        Args:
            data (pd.DataFrame): The input data as a pandas DataFrame.
          
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
        if data.empty:
            raise ValueError("Data cannot be empty")
        if data.isnull().values.any():
            raise ValueError("Data contains NaN values")

        self.data = data
        self.config = Config()
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
            marker_color=self.config.colors[2] if group_name == 'Israel' else self.config.colors[3]
        ) for group_name, group in groups_data.items()])

        # Tune marker appearance and layout
        fig.update_traces(mode='markers', marker=dict(sizemode='area',
                                                      sizeref=sizeref, line_width=0.7))
        fig.update_xaxes(showline=False, overwrite=False)

        fig.update_layout(
    
            xaxis=dict(
                title={
                    'text': self.data.columns[3].upper(),
                    'font': {
                        'size': 12,
                        'color': self.config.colors[2],
                        'family': 'bold'
                    }
                },
                tickfont=dict(size=self.config.axisestick_size),
                gridcolor='#F1EFEF',
                type='log',
                gridwidth=3,
                tickangle=-45  # Rotate tick labels by -45 degrees
            ),
            yaxis=dict(
                title={
                    'text': self.data.columns[2].upper(),
                    'font': {
                        'size': 12,
                        'color': self.config.colors[2],
                        'family': 'bold'
                    }
                },
                tickfont=dict(size=self.config.axisestick_size),
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45
                
            ),
             annotations =[dict(text = self.config.signature,
                            x = 1.2, y=-0.25,
                            xref="paper",yref="paper",
                            showarrow=False,
                            font=dict(
                                size=10,
                                color=self.config.signature_color

                            ),align="left"),
                           
                            dict(text = self.config.title,
                            x = 0.5, y=1.3,
                            xref="paper",yref="paper",
                            showarrow=False,
                            font=dict(
                                size=self.config.title_size,
                                color=self.config.colors[2],
                               
                                family = "bold",

                            ),
                            align="center")],

            paper_bgcolor=self.config.paper_bgcolor,
            plot_bgcolor=self.config.plot_bgcolor,

            width=self.config.width,
            height=self.config.height  #

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
        
            fig.write_html(save_filename)
        fig.show()

