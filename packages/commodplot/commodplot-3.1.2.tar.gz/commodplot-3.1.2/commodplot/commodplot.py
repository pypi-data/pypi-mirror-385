import itertools

import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
from commodutil import dates
from commodutil import transforms
from plotly.subplots import make_subplots
import numpy as np

from scipy.stats import zscore

from commodplot import commodplottrace as cptr
from commodplot import commodplotutil as cpu

preset_margins = {"l": 0, "r": 0, "t": 40, "b": 0}


def seas_line_plot(df, fwd=None, **kwargs):
    """
    Given a DataFrame produce a seasonal line plot (x-axis - Jan-Dec, y-axis Yearly lines)
    Can overlay a forward curve on top of this
    """
    df = df.sort_index()

    fig = go.Figure()
    traces = cptr.seas_plot_traces(df, fwd, **kwargs)
    if "shaded_range" in traces and traces["shaded_range"]:
        for trace in traces["shaded_range"]:
            fig.add_trace(trace)

    if "average_line" in traces:
        fig.add_trace(traces["average_line"])

    if "hist" in traces:
        for trace in traces["hist"]:
            fig.add_trace(trace)

    if "fwd" in traces:
        for trace in traces["fwd"]:
            fig.add_trace(trace)

    fig.layout.xaxis.tickvals = pd.date_range(
        start=str(dates.curyear), periods=12, freq="MS"
    )

    title = cpu.gen_title(df, **kwargs)
    legend = go.layout.Legend(font=dict(size=10), traceorder="reversed")
    yaxis_title = kwargs.get("yaxis_title", None)
    hovermode = kwargs.get("hovermode", "x")
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b",
        yaxis_title=yaxis_title,
        legend=legend,
        hovermode=hovermode,
        margin=preset_margins,
    )

    return fig


def seas_line_subplot(rows, cols, df, fwd=None, **kwargs):
    """
    Generate a plot with multiple seasonal subplots.
    :param rows:
    :param cols:
    :param dfs:
    :param fwds:
    :param kwargs:
    :return:
    """
    fig = make_subplots(
        cols=cols,
        rows=rows,
        specs=[[{"type": "scatter"} for x in range(0, cols)] for y in range(0, rows)],
        subplot_titles=kwargs.get("subplot_titles", None),
    )

    chartcount = 0
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            # print(row, col)
            if chartcount > len(df):
                chartcount += 1
                continue

            dfx = df[df.columns[chartcount]]
            fwdx = None
            if fwd is not None and len(fwd) > chartcount:
                fwdx = fwd[fwd.columns[chartcount]]

            showlegend = True if chartcount == 0 else False

            traces = cptr.seas_plot_traces(
                dfx, fwd=fwdx, showlegend=showlegend, **kwargs
            )

            for trace_set in ["shaded_range", "hist", "fwd"]:
                if trace_set in traces:
                    for trace in traces[trace_set]:
                        fig.add_trace(trace, row=row, col=col)

            chartcount += 1

    legend = go.layout.Legend(font=dict(size=10))
    fig.update_xaxes(
        tickvals=pd.date_range(start=str(dates.curyear), periods=12, freq="MS"),
        tickformat="%b",
    )
    title = kwargs.get("title", "")
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b",
        legend=legend,
        margin=preset_margins,
    )
    return fig


def seas_box_plot(hist, fwd=None, **kwargs):
    hist = transforms.monthly_mean(hist)
    hist = hist.T

    data = []
    monthstr = {
        x.month: x.strftime("%b")
        for x in pd.date_range(start="2018", freq="M", periods=12)
    }
    for x in hist.columns:
        trace = go.Box(name=monthstr[x], y=hist[x])
        data.append(trace)

    fwdl = transforms.seasonailse(fwd)
    fwdl.index = fwdl.index.strftime("%b")
    for col in fwdl.columns:
        ser = fwdl[col].copy()
        trace = go.Scatter(
            name=col,
            x=ser.index,
            y=ser,
            line=dict(color=cptr.get_year_line_col(col), dash="dot"),
        )
        data.append(trace)

    fig = go.Figure(data=data)
    title = kwargs.get("title", "")
    fig.update_layout(title=title, title_x=0.01, margin=preset_margins)

    return fig


def seas_table_plot(hist, fwd=None):
    hist = hist.sort_index()
    df = cpu.seas_table(hist, fwd)

    colsh = list(df.columns)
    colsh.insert(0, "Period")

    cols = [df[x] for x in df]
    cols.insert(0, list(df.index))
    fillcolor = ["lavender"] * 12
    fillcolor.extend(["aquamarine"] * 4)
    fillcolor.extend(["darkturquoise"] * 2)
    fillcolor.append("dodgerblue")

    figm = go.Figure(
        data=[
            go.Table(
                header=dict(values=colsh, fill_color="paleturquoise", align="left"),
                cells=dict(values=cols, fill_color=[fillcolor], align="left"),
            )
        ]
    )
    return figm


def table_plot(df, **kwargs):
    row_even_colour = kwargs.get("row_even_colour", "lightgrey")
    row_odd_color = kwargs.get("row_odd_colour", "white")

    # include index col as part of plot
    indexname = "" if df.index.name is None else df.index.name
    colheaders = [indexname] + list(df.columns)
    headerfill = ["white" if x == "" else "grey" for x in colheaders]

    cols = [df[x] for x in df.columns]
    # apply red/green to formatted_cols
    fcols = kwargs.get("formatted_cols", [])
    font_color = [
        ["red" if str(y).startswith("-") else "green" for y in df[x]]
        if x in fcols
        else "black"
        for x in colheaders
    ]

    if isinstance(df.index, pd.DatetimeIndex):  # if index is datetime, format dates
        df.index = df.index.map(lambda x: x.strftime("%d-%m-%Y"), )
    cols.insert(0, df.index)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=colheaders,
                    fill_color=headerfill,
                    align="center",
                    font=dict(color="white", size=12),
                ),
                cells=dict(
                    values=cols,
                    line=dict(color="#506784"),
                    fill_color=[[row_odd_color, row_even_colour] * len(df)],
                    align="right",
                    font_color=font_color,
                ),
            )
        ]
    )
    return fig


def forward_history_plot(df, title=None, **kwargs):
    """
    Given a dataframe of a curve's pricing history, plot a line chart showing how it has evolved over time
    """
    df = df.rename(columns={x: pd.to_datetime(x) for x in df.columns})
    df = df[sorted(list(df.columns), reverse=True)]  # have latest column first
    df = df.rename(
        columns={x: cpu.format_date_col(x, "%d-%b-%y") for x in df.columns}
    )  # make nice labels for legend eg 05-Dec

    colseq = py.colors.sequential.Aggrnyl
    text = df.index.strftime("%b-%y")

    fig = go.Figure()
    colcount = 0
    for col in df.columns:
        color = colseq[colcount] if colcount < len(colseq) else colseq[-1]
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[col],
                hoverinfo="y",
                name=str(col),
                line=dict(color=color),
                hovertemplate=cptr.hovertemplate_default,
                text=text,
            )
        )

        colcount = colcount + 1

    fig["data"][0]["line"]["width"] = 2.2  # make latest line thicker
    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get("yaxis_title", None)
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b-%y",
        yaxis_title=yaxis_title,
        legend=legend,
        margin=preset_margins,
    )
    return fig


def bar_line_plot(df, linecol="Total", **kwargs):
    """
    Give a dataframe, make a stacked bar chart along with overlaying line chart.
    """
    if linecol not in df:
        df[linecol] = df.sum(1, skipna=False)

    fig = go.Figure()
    # create the bar trace
    for col in df.columns:
        if col != linecol:
            bar_trace = go.Bar(
                x=df.index,
                y=df[col],
                name=col,
            )
            fig.add_trace(bar_trace)

    # create the line trace
    line_trace = go.Scatter(
        x=df.index,
        y=df[linecol],
        name=linecol,
        mode="lines",
        line=dict(color="black"),
    )

    fig.add_trace(line_trace)

    # update the figure layout if needed
    yaxis_title = kwargs.get("yaxis_title", None)
    yaxis_range = kwargs.get("yaxis_range", None)
    title = kwargs.get("title", None)
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        barmode="relative",
        margin=dict(l=40, r=20, t=40, b=20),
    )
    if yaxis_range is not None:
        fig.update_layout(yaxis=dict(range=yaxis_range))

    return fig


def horizontal_bar_plot(df, **kwargs):
    bar = go.Bar(x=df.iloc[:, 0], y=df.index, orientation="h")  # horizontal bars

    fig = go.Figure(data=[bar])

    fig.update_layout(
        title=kwargs.get("title", None),
        xaxis_title=df.columns[0],
        yaxis_title=df.index.name,
        bargap=kwargs.get("bargap", 0.25),  # space between bars
        width=kwargs.get("width", None),
        height=kwargs.get("height", None),
    )

    return fig


def diff_plot(df, **kwargs):
    """
    Given a dataframe, plot each column as line plot with a subplot below
    showing differences between each column.
    :param df:
    :param kwargs:
    :return:
    """
    # calculate difference between each column
    for comb in itertools.combinations(df.columns, 2):
        df["%s-%s" % (comb[0], comb[1])] = df[comb[0]] - df[comb[1]]

    barcols = [x for x in df.columns if "-" in x]
    linecols = [x for x in df.columns if "-" not in x]

    fig = make_subplots(
        rows=2, cols=1, row_heights=[0.8, 0.2], shared_xaxes=True, vertical_spacing=0.02
    )
    for col in linecols:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col))

    for col in barcols:
        fig.add_trace(go.Bar(x=df.index, y=df[col], name=col), row=2, col=1)

    today = pd.Timestamp.today()
    vline = go.layout.Shape(
        type="line",
        x0=today,
        x1=today,
        y0=df.min().min(),  # Set y0 to the minimum value of y_data
        y1=df.max().max(),  # Set y1 to the maximum value of y_data
        line=dict(color="grey", width=1, dash="dash"),
    )
    fig.update_layout(shapes=[vline])

    title = kwargs.get("title", "")
    fig.update_layout(title_text=title, title_x=0.01, margin=preset_margins)
    return fig


def reindex_year_line_plot(df, **kwargs):
    """
    Given a dataframe of timeseries, reindex years and produce line plot
    :param df:
    :return:
    """
    fig = go.Figure()
    dft = transforms.reindex_year(df)
    max_results = kwargs.get("max_results", None)
    if max_results:
        dft = dft.tail(max_results)
    colsel = cpu.reindex_year_df_rel_col(dft)

    traces = cptr.reindex_plot_traces(dft, current_select_year=colsel, **kwargs)

    if "shaded_range" in traces and traces["shaded_range"]:
        for trace in traces["shaded_range"]:
            fig.add_trace(trace)

    if "hist" in traces:
        for trace in traces["hist"]:
            fig.add_trace(trace)

    kwargs["title_postfix"] = colsel
    title = cpu.gen_title(df[colsel], title_prefix=colsel, **kwargs)

    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get("yaxis_title", None)
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b-%y",
        yaxis_title=yaxis_title,
        legend=legend,
        margin=preset_margins,
    )
    # zoom into last 3 years
    fig.update_xaxes(
        type="date",
        range=[
            dft.tail(365 * 3).index[0].strftime("%Y-%m-%d"),
            dft.index[-1].strftime("%Y-%m-%d"),
        ],
    )

    return fig


def candle_chart(df, **kwargs):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
            )
        ]
    )

    title = cpu.gen_title(df["Close"], **kwargs)
    fig.update_layout(
        title=title,
        margin=preset_margins,
    )
    return fig


def stacked_area_chart(df, **kwargs):
    fig = go.Figure()
    group = kwargs.get("stackgroup", "stackgroup")
    showlegend = kwargs.get("showlegend", None)

    for col in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df[col], name=col, stackgroup=group, showlegend=showlegend
            )
        )

    fig.update_layout(
        title=kwargs.get("title", ""), showlegend=showlegend, margin=preset_margins
    )
    return fig


def stacked_area_chart_negative_cols(df, **kwargs):
    """
    Similar to stacked_area_chart except showing negative columns as a separate stackgroup
    below the 0 line
    """
    fig = go.Figure()
    showlegend = kwargs.get("showlegend", None)

    for col in df.columns:
        if df[col].sum() < 0:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=col,
                    stackgroup="neg",
                    showlegend=showlegend,
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=col,
                    stackgroup="pos",
                    showlegend=showlegend,
                )
            )
    fig.update_layout(
        title=kwargs.get("title", ""),
        showlegend=showlegend,
        margin=preset_margins,
    )
    return fig


def bar_chart(df, **kwargs):
    fig = go.Figure()

    for col in df.columns:
        fig.add_trace(go.Bar(x=df.index, y=df[col], name=col))

    hovermode = kwargs.get("hovermode", "x")
    fig.update_layout(
        title=kwargs.get("title", ""),
        hovermode=hovermode,
        margin=preset_margins,
    )
    barmode = kwargs.get("barmode", None)
    if barmode:
        fig.update_layout(barmode=barmode)

    return fig


def stacked_grouped_bar_chart(df, **kwargs):
    """Given a dataframe with multi-indexed columns, generate a stacked group barchart.
    Column level 0 will be used for grouping of the bars.
    Column level 1 will be used for the stacked bars.
    based on : https://stackoverflow.com/questions/65289591/python-plotly-stacked-grouped-bar-chart
    """

    fig = go.Figure()

    color = dict(
        zip(
            df.columns.levels[1],
            px.colors.qualitative.Plotly[: len(df.columns.levels[1])],
        )
    )

    seen_commod = set()
    showlegend = []
    for src, prod in df.columns:
        if prod not in seen_commod:
            showlegend.append(True)
            seen_commod.add(prod)
        else:
            showlegend.append(False)

    # xaxis_tickformat doesn't appear to work so have to format the dataframe index
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        freq = pd.infer_freq(df.index)
        if freq is not None:
            if freq in ("M", "MS", "ME"):
                df.index = df.index.map(lambda x: x.strftime("%m-%Y"))
            if freq in ("Y", "YS", "YE"):
                df.index = df.index.map(lambda x: x.year )
            if freq in ("D", "B"):
                df.index = df.index.map(lambda x: x.date())

    i = 0
    for col in df.columns:
        f = df[col[0]][col[1]]
        fig.add_trace(
            go.Bar(
                x=[f.index, [col[0]] * len(f.index)],
                y=f,
                name=col[1],
                marker_color=color[col[1]],
                legendgroup=col[1],
                showlegend=showlegend[i],
            )
        )
        i += 1

    # Adding dots for the sum of each level 1 within each level 0 category
    for level0 in df.columns.levels[0]:
        group_sum = df[level0].sum(axis=1)
        x_coords = [df.index, [level0] * len(df.index)]
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=group_sum,
                mode="markers",
                marker=dict(
                    size=10,
                    color="black",  # set color equal to a variable
                ),
                name=f"Sum of {level0}",
                legendgroup=level0,
                showlegend=False,
            )
        )

    fig.update_layout(
        title=kwargs.get("title", ""),
        xaxis=dict(title_text=kwargs.get("xaxis_title", None)),
        yaxis=dict(title_text=kwargs.get("yaxis_title", None)),
        barmode="relative",
        margin=preset_margins,
    )

    return fig


def reindex_year_line_subplot(rows, cols, dfs, **kwargs):
    fig = make_subplots(
        cols=cols,
        rows=rows,
        specs=[[{"type": "scatter"} for x in range(0, cols)] for y in range(0, rows)],
        subplot_titles=kwargs.get("subplot_titles", None),
        shared_xaxes=False,
    )

    chartcount = 0
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            # print(row, col)
            if chartcount > len(dfs):
                chartcount += 1
                continue
            showlegend = True if chartcount == 0 else False

            dfx = dfs[chartcount]
            dft = transforms.reindex_year(dfx)
            colsel = cpu.reindex_year_df_rel_col(dft)
            traces = cptr.reindex_plot_traces(
                dft, current_select_year=colsel, showlegend=showlegend, **kwargs
            )
            for trace_set in ["shaded_range", "hist"]:
                if trace_set in traces:
                    for trace in traces[trace_set]:
                        fig.add_trace(trace, row=row, col=col)

            chartcount += 1

    legend = go.layout.Legend(font=dict(size=10))
    yaxis_title = kwargs.get("yaxis_title", None)
    hovermode = kwargs.get("hovermode", "closest")
    title = kwargs.get("title", "")
    fig.update_layout(
        title=title,
        title_x=0.01,
        xaxis_tickformat="%b-%y",
        yaxis_title=yaxis_title,
        legend=legend,
        hovermode=hovermode,
        margin=preset_margins,
    )

    fig.update_xaxes(type="date")

    return fig


def line_plot(df, fwd=None, **kwargs):
    fig = go.Figure()
    kwargs['colyearmap_enabled'] = False # dont enable colyearmap for line plot as it doesn't apply in this context
    res = cptr.line_plot_traces(df, fwd, **kwargs)
    for trace in res:
        fig.add_trace(trace)

    title = cpu.gen_title(df, inc_change_sum=False, **kwargs)
    legend = go.layout.Legend(font=dict(size=10))
    showlegend = kwargs.get("showlegend", True)
    yaxis_title = kwargs.get("yaxis_title", None)
    hovermode = kwargs.get("hovermode", "closest")
    fig.update_layout(
        title=title,
        title_x=0.01,
        yaxis_title=yaxis_title,
        legend=legend,
        showlegend=showlegend,
        hovermode=hovermode,
        margin=preset_margins,
    )
    return fig


def timeseries_scatter_plot(df, **kwargs):
    """
    Generate a scatter plot for a time series dataframe.

    Parameters:
    - df: A dataframe with a DateTimeIndex and at least two columns.
          The x-axis will be based on df.iloc[:, 0] and the y-axis on df.iloc[:, 1].
    """

    # Convert the date index to numbers for color gradient
    color_values = df.index.astype(int)

    # Create scatter plot using Plotly
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.iloc[:, 0],
            y=df.iloc[:, 1],
            mode="markers",
            marker=dict(
                color=color_values,
                colorscale="Plasma",
                colorbar=dict(title="Date"),
                showscale=True,
            ),
            text=df.index.strftime("%Y-%m-%d"),
            hovertemplate="<b>Date:</b> %{text}<br><b>X:</b> %{x}<br><b>Y:</b> %{y}",
        )
    )

    title = kwargs.get("title", f"{df.columns[0]} vs {df.columns[1]}")

    fig.update_layout(
        title=title,
        xaxis_title=df.columns[0],
        yaxis_title=df.columns[1],
        hovermode="closest",
    )

    # Adjust the colorbar to display actual dates
    colorbar_tickvals = color_values[
        [0, len(df) // 4, len(df) // 2, 3 * len(df) // 4, -1]
    ]
    colorbar_ticktext = (
        df.index[[0, len(df) // 4, len(df) // 2, 3 * len(df) // 4, -1]]
        .strftime("%Y-%m-%d")
        .to_list()
    )
    fig.update_traces(
        marker_colorbar_tickvals=colorbar_tickvals,
        marker_colorbar_ticktext=colorbar_ticktext,
    )

    return fig


def timeseries_scatter_plot(df, line_last_n=None, fit_line=False, **kwargs):
    """
    Generate a scatter plot for a time series dataframe.

    Parameters:
    - df: A dataframe with a DateTimeIndex and at least two columns.
          The x-axis will be based on df.iloc[:, 0] and the y-axis on df.iloc[:, 1].
    - line_last_n: Optional, an integer to indicate how many of the last points to connect with a line.
    - fit_line: Optional, boolean to add a line of best fit excluding outliers.
    """

    # Convert the date index to numbers for color gradient
    color_values = df.index.astype(int)

    # Create scatter plot using Plotly
    fig = go.Figure()

    # If fit_line is True, calculate the line of best fit
    if fit_line:
        # Using z-score to identify and exclude outliers
        z_scores = zscore(df.iloc[:, 1])
        abs_z_scores = np.abs(z_scores)
        filtered_entries = abs_z_scores < 2  # Adjust the z-score threshold as needed
        new_df = df[filtered_entries]

        # Perform linear regression on the data without outliers
        m, b = np.polyfit(new_df.iloc[:, 0], new_df.iloc[:, 1], 1)
        # Add the line of best fit to the plot
        fig.add_trace(
            go.Scatter(
                x=new_df.iloc[:, 0],
                y=m * new_df.iloc[:, 0] + b,
                mode="lines",
                line=dict(color="grey", dash="dash"),
                name="Line of Best Fit",
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df.iloc[:, 0],
            y=df.iloc[:, 1],
            mode="markers",
            marker=dict(
                color=color_values,
                colorscale="Viridis",
                colorbar=dict(title="Date"),
                showscale=True,
            ),
            text=df.index.strftime("%Y-%m-%d"),
            hovertemplate="<b>Date:</b> %{text}<br><b>X:</b> %{x}<br><b>Y:</b> %{y}",
        )
    )

    # Add a line connecting the last N data points if specified
    if line_last_n is not None and line_last_n > 0:
        # Ensuring the number of points does not exceed the dataframe's length
        line_last_n = min(len(df), line_last_n)
        last_points = df.iloc[-line_last_n:, :]
        last_color_values = last_points.index.astype(int)
        fig.add_trace(
            go.Scatter(
                x=last_points.iloc[:, 0],
                y=last_points.iloc[:, 1],
                mode="lines+markers",
                line=dict(color="rgba(0,0,0,0.5)", width=1),
                marker=dict(color=last_color_values, colorscale="Viridis", size=8),
                showlegend=False,
                hovertemplate="<b>Date:</b> %{text}<br><b>X:</b> %{x}<br><b>Y:</b> %{y}",
                text=last_points.index.strftime("%Y-%m-%d"),
            )
        )

    title = kwargs.get("title", f"Scatter plot of {df.columns[0]} vs {df.columns[1]}")
    xaxis_title = kwargs.get("xaxis_title", df.columns[0])
    yaxis_title = kwargs.get("yaxis_title", df.columns[1])

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        hovermode="closest",
    )

    # Adjust the colorbar to display actual dates
    colorbar_tickvals = color_values[
        [0, len(df) // 4, len(df) // 2, 3 * len(df) // 4, -1]
    ]
    colorbar_ticktext = (
        df.index[[0, len(df) // 4, len(df) // 2, 3 * len(df) // 4, -1]]
        .strftime("%Y-%m-%d")
        .to_list()
    )
    fig.update_traces(
        marker_colorbar_tickvals=colorbar_tickvals,
        marker_colorbar_ticktext=colorbar_ticktext,
    )

    return fig
