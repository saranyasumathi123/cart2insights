import pandas as pd
import matplotlib.pyplot as plt


def format_currency(value):
    """Format a number as Indian Rupees."""
    return f"₹{value:,.2f}"


def format_number(value):
    """Format a number with commas."""
    return f"{value:,.0f}"


def create_bar_chart(
    dataframe,
    x_column,
    y_column,
    title,
    x_label,
    y_label,
    rotation=0
):
    """
    Create a reusable bar chart.
    """

    # Check whether data is available
    if dataframe.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        dataframe[x_column],
        dataframe[y_column]
    )

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    plt.xticks(
        rotation=rotation,
        ha="right"
    )

    plt.tight_layout()

    return fig


def create_line_chart(
    dataframe,
    x_column,
    y_column,
    title,
    x_label,
    y_label
):
    """
    Create a reusable line chart.
    """

    # Check whether data is available
    if dataframe.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        dataframe[x_column],
        dataframe[y_column],
        marker="o"
    )

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    plt.xticks(rotation=45)

    plt.tight_layout()

    return fig

