import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go
import math


class Bubbles:
    def __init__(self, data, colors, required_columns=['Year', 'Month', 'Deaths', 'Injuries', 'Group']):
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

        self.colors = colors or  ['#088395','#E55604','#053B50']

        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Data is missing the following required columns: {', '.join(missing_columns)}")
    
        self.create_text_and_sizes()
    def create_text_and_sizes(self):
        """
        Create text and size columns
        """
        self.data['text'] = self.data.apply(lambda row: ('Year: {year}<br>'+
                                                         'Month: {month}<br>'+
                                                         'Deaths: {deaths}<br>'+
                                                         'Injuries: {injuries}<br>').format(year=row['Year'],
                                                                                            month=row['Month'],
                                                                                            deaths=row['Deaths'],
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
            x=group['Deaths'], y=group['Injuries'],
            name=group_name, text=group['text'],
            marker_size=group['size'],
            marker_color=self.colors[2] if group_name == 'Israel' else self.colors[1]
        ) for group_name, group in groups_data.items()])

        # Tune marker appearance and layout
        fig.update_traces(mode='markers', marker=dict(sizemode='area',
                                                      sizeref=sizeref, line_width=0.5))
        fig.update_xaxes(showline=False, overwrite=False)

        fig.update_layout(
            title={
                'text': 'Deaths v. Injuries',
                'font': {
                    'size': 24,
                    'color': self.colors[2],
                    'family': 'bold'
                },
                'x': 0.5,
                'y': 0.9,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title={
                    'text': 'Deaths',
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                        # 'Courier New, monospace'
                    }
                },
                gridcolor='#F1EFEF',
                type='log',
                gridwidth=3,
                tickangle=-45  # Rotate tick labels by -45 degrees
            ),
            yaxis=dict(
                title={
                    'text': 'Injuries',
                    'font': {
                        'size': 18,
                        'color': self.colors[2],
                        'family': 'bold'
                    }
                },
                gridcolor='#F1EFEF',
                gridwidth=3,
                tickangle=-45
            ),

            paper_bgcolor='#F1EFEF',
            plot_bgcolor='white',

            width=1000,
            height=500  #

        )

        return fig

    def show(self, filename='bubblechart.html', save=True):
        """
        Display the plot
        Args:
            filename (str, optional): The filename for the plot. Defaults to 'bubblechart.html'.
        """

        fig = self.create_figure()
        if fig is None:
            raise ValueError("Failed to create the plot")
        if not isinstance(filename, str) or not filename.endswith('.html'):
            raise ValueError("Invalid filename. Filename must be a string and end with '.html'")
        if save:
            pio.write_html(fig, file=filename)
        fig.show()
