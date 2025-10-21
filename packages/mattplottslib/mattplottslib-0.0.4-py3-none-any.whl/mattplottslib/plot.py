import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

_SIGNATURE = 'Matthew Potts\ncrossbordercode.com'

def line_plot(
        df: pd.DataFrame, 
        title: str = None, 
        unit : str = 'USD (millions)', 
        key: str = 'Title',
        sig_loc: str = None,
        include_gfc: bool = False) -> None:
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['Date'], df['Value'], color='red', label=key)

    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    if include_gfc:
        include_gfc(ax)        
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')

    ax.set_ylabel(unit, fontsize=12)

    if sig_loc is not None:
        add_signature(sig_loc, ax)

    ax.legend()
    plt.show()

def multiline_plot(
        df: list[pd.DataFrame], 
        key: list[str], 
        title: str = None, 
        unit: str = 'USD (millions)',
        sig_loc: str = None,
        include_gfc: bool = False) -> None:
    
    fig, ax = plt.subplots(figsize=(10, 6))

    for df, key in zip(df, key):
        ax.plot(df['Date'], df['Trailing_4Q_Sum'], label=key)

    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if include_gfc:
        include_gfc(ax)

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')

    ax.set_ylabel(unit, fontsize=12)

    if sig_loc is not None:
        add_signature(sig_loc, ax)

    ax.legend()

    plt.show()


def scatter_plot(col1: pd.Series,
                col2: pd.Series,
                title: str = None,
                sig_loc: str = None) -> None:
    fig, ax = plt.subplots(figsize=(8, 8))

    col1 = pd.to_numeric(col1, errors='coerce')
    col2 = pd.to_numeric(col2, errors='coerce')

    ax.scatter(col1, col2, color='blue', alpha=0.5)

    x = pd.to_numeric(col1, errors='coerce')
    y = pd.to_numeric(col2, errors='coerce')
    mask = x.notna() & y.notna()
    if mask.sum() > 1:
        coef = np.polyfit(col1[mask], col2[mask], 1)
        slope, intercept = coef[0], coef[1]
        x_vals = np.linspace(col1[mask].min(), col1[mask].max(), 200)
        y_vals = slope * x_vals + intercept
        ax.plot(x_vals, y_vals, color='red', linewidth=2)
        ax.legend()

    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_xlabel(col1.name, fontsize=12)
    ax.set_ylabel(col2.name, fontsize=12)

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')

    if sig_loc is not None:
        add_signature(sig_loc, ax)

    plt.show()
    


def add_signature(loc: str, ax: plt.Axes) -> None:
    
    if loc == 'bottom right':
        ax.text(0.95, 0.05, _SIGNATURE,
            fontsize=10, color='black',
            ha='right', va='bottom', transform=ax.transAxes)
    elif loc == 'top left':
        ax.text(0.05, 0.95, _SIGNATURE,
            fontsize=10, color='black',
            ha='left', va='top', transform=ax.transAxes)
    elif loc == 'top right':
        ax.text(0.95, 0.95, _SIGNATURE,
            fontsize=10, color='black',
            ha='left', va='top', transform=ax.transAxes)
    elif loc == 'bottom left':
        ax.text(0.05, 0.05, _SIGNATURE,
            fontsize=10, color='black',
            ha='left', va='top', transform=ax.transAxes)
    else:
        raise ValueError("Invalid signature location specified.\nOptions are:\n 'bottom right'\n 'top left'")
    return 


def add_gfc(ax: plt.Axes):
    start_period = pd.Timestamp('2007-01-01')
    end_period = pd.Timestamp('2008-06-30')
    ax.add_patch(Rectangle((start_period, ax.get_ylim()[0]),
                            end_period - start_period,
                            ax.get_ylim()[1] - ax.get_ylim()[0],
                            color='grey', alpha=0.3))