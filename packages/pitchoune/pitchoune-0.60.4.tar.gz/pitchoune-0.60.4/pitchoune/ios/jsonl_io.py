from pathlib import Path
from typing import Any

import polars as pl

from pitchoune.io import IO


class JSONL_IO(IO):
    """ JSONL IO class that can read and write JSON Lines files using Polars
    """
    def __init__(
        self
    ):
        super().__init__(suffix="jsonl")

    def deserialize(
        self,
        filepath: Path|str,
        schema=None
    ) -> pl.DataFrame:
        """ Reads a JSON Lines file and return a Polars DataFrame
        """
        return pl.read_ndjson(str(filepath), schema_overrides=schema)

    def serialize(
        self,
        df: pl.DataFrame | list[Any],
        filepath: Path|str
    ) -> None:
        """ Writes a Polars DataFrame to a JSON Lines file
        """
        if isinstance(df, pl.DataFrame):
            df.write_ndjson(str(filepath))
        elif isinstance(df, list):
            import json
            with open(filepath, "w", encoding="utf-8") as f:
                for item in df:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
