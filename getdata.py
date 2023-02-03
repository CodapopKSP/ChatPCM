import io
import json
import re
from pathlib import Path

import zstandard as zstd

# Get PCM comments
DCTX = zstd.ZstdDecompressor(max_window_size=2**31)


def read_lines_from_zst_file(zstd_file_path: Path):
    with (
        zstd.open(zstd_file_path, mode="rb", dctx=DCTX) as zfh,
        io.TextIOWrapper(zfh) as iofh,
    ):
        for line in iofh:
            yield line


# Compile PCM comments into a text file
if __name__ == "__main__":
    file = Path("training_data/PoliticalCompassMemes_comments.zst")
    records = map(json.loads, read_lines_from_zst_file(file))
    numrecords = 0
    data = []
    with open("test.txt", "w+", encoding="utf8") as fh:
        for record in records:
            body = re.sub(r'[^\w\s.?!,"\'%$-=+()]', "", record.get("body"))
            data.append("{}:\n{}".format(record.get("author"), body))
            print(f"Comments: {numrecords}\r", end="")
            numrecords += 1
            if numrecords > 10000:
                break
        fh.write("\n\n".join(data))
