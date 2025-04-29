import argparse
import typing

import plotly.graph_objects as go  # type: ignore[import-untyped]
from plotly.subplots import make_subplots  # type: ignore[import-untyped]

import pandas as pd  # isort: skip plotly import first for correct numpy import


def main() -> None:
    args = parse_args()
    df = read_phout(args.phout_file)
    rps, status_codes, timings = prepare_data(df)
    create_plots(rps, status_codes, timings)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("phout_file")
    return parser.parse_args()


def read_phout(file_name: str) -> pd.DataFrame:
    columns = [
        "time",
        "tag",
        "interval_real",
        "connect_time",
        "send_time",
        "latency",
        "receive_time",
        "interval_event",
        "size_out",
        "size_in",
        "net_code",
        "proto_code",
    ]

    df = pd.read_csv(file_name, delimiter="\t", names=columns, index_col="time")
    df.index = pd.to_datetime(df.index, unit="s", origin="unix")

    return df


NETWORK_ERROR_CODE = 999


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    status_codes = pd.DataFrame({"proto_code": df["proto_code"]})
    status_codes[df["net_code"] != 0] = NETWORK_ERROR_CODE

    rps = status_codes.resample("1s").count()
    status_codes = status_codes.groupby("proto_code").resample("1s").count()

    timings = df.drop(columns=["tag", "size_out", "size_in", "net_code", "proto_code"])
    timings = timings / 1000

    return rps, status_codes, timings


def create_plots(
    rps: pd.DataFrame, status_codes: pd.DataFrame, timings: pd.DataFrame
) -> None:
    fig = make_subplots(rows=2, shared_xaxes=True)

    position = {"row": 1, "col": 1}
    quantiles = [0.5, 0.9, 0.95, 0.99, 0.995, 1.0]
    timings_quantiles = timings.resample("1s").quantile(quantiles)
    timings_colors = ["red", "orange", "gold", "lightgreen", "darkgreen", "grey"]

    quantiles.reverse()
    timings_colors.reverse()
    for color, quantile in zip(timings_colors, quantiles):
        data = timings_quantiles.loc[(slice(None), quantile), :]
        index = typing.cast(pd.MultiIndex, data.index)
        scatter = go.Scatter(
            x=index.levels[0],
            y=data["interval_real"],
            mode="lines",
            name=f"{quantile * 100} %",
            fillcolor=color,
            line_color=color,
            fill="tozeroy",
            legendgroup="legend1",
            legendgrouptitle={"text": "Timings"},
            x0=0,
        )
        fig.add_trace(scatter, **position)
    fig.update_yaxes(title="Response time, ms", **position)
    fig.update_yaxes(type="log", **position)

    position = {"row": 2, "col": 1}
    status_colors = {
        500: "red",
        200: "green",
        NETWORK_ERROR_CODE: "grey",
    }
    index = typing.cast(pd.MultiIndex, status_codes.index)
    for proto_code in index.levels[0]:
        values = status_codes.loc[proto_code]["proto_code"]
        obj = go.Scatter(
            x=values.index,
            y=values,
            name=f"Status {proto_code}"
            if proto_code != NETWORK_ERROR_CODE
            else "Network error",
            legendgroup="legend2",
            legendgrouptitle={"text": "Response statuses"},
            stackgroup="one",
            fillcolor=status_colors.get(proto_code, None),
            line_color=status_colors.get(proto_code, None),
        )
        fig.add_trace(obj, **position)

    obj = go.Scatter(
        x=rps.index,
        y=rps["proto_code"],
        name="Total RPS",
        legendgroup="legend2",
        legendgrouptitle={"text": "Response statuses"},
    )
    fig.add_trace(obj, **position)
    fig.update_yaxes(title="Count", **position)

    fig.layout.template = "plotly_dark"
    fig.update_layout(legend=dict(groupclick="toggleitem"))
    fig.show()


if __name__ == "__main__":
    main()
