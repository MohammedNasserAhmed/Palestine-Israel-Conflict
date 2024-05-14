import pandas as pd


def make_autopct(values):
    """
    Generate the autopct function for a pie chart.

    Parameters:
    - values: The values for the pie chart.

    Returns:
    The autopct function.
    """
    total = sum(values)
    def my_autopct(pct):
        val = int(round(pct * total / 100.0))
        return f'{val} ({pct:.0f}%)'
    return my_autopct


def reset_months(data):
    """
    Rename the index of the given DataFrame 'data' with month abbreviations.

    Args:
        data (pd.DataFrame): The DataFrame to be renamed.

    Returns:
        pd.DataFrame: The DataFrame with renamed index.
    """
    try:
        if isinstance(data, pd.DataFrame):
            months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
            data = data.reindex(index=months)
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            rename_dict = {data.index[i]: month_names[i] for i in range(len(data.index))}
            data = data.rename(index=rename_dict)
    except Exception as e:
        print(f'Error occurred during renaming process: {e}')

    return data