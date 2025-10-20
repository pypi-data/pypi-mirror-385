import click
import pandas as pd
from rich import get_console
from rich.table import Table
from rich.traceback import install

console = get_console()

SUPPRESS_TRACEBACKS = [click]

install(console=console, show_locals=False, suppress=SUPPRESS_TRACEBACKS)


def print_pandas_dataframe(df: pd.DataFrame, title: str | None = None):
    table = Table(title=title)

    for col in df.index.names:
        table.add_column(col, header_style="italic")

    for col in df.columns:
        table.add_column(col)

    old_index = [None] * df.index.nlevels
    for row in df.itertuples():
        new_index = (
            [str(e) for e in row[0]] if isinstance(row[0], tuple) else [str(row[0])]
        )

        index = [
            (new if old != new else "")
            for old, new in zip(old_index, new_index, strict=False)
        ]
        old_index = new_index

        data = (str(e) for e in row[1:])
        table.add_row(*index, *data)

    console.print(table)
