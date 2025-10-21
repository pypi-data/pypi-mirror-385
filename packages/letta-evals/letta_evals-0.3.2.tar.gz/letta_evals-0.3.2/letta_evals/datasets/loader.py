import json
from pathlib import Path
from typing import Iterator, List, Optional

from letta_evals.models import Sample


def load_jsonl(
    file_path: Path, max_samples: Optional[int] = None, sample_tags: Optional[List[str]] = None
) -> Iterator[Sample]:
    """Load samples from a JSONL file."""
    with open(file_path, "r") as f:
        line_index = 0
        yielded_count = 0
        for line in f:
            if max_samples and yielded_count >= max_samples:
                break

            data = json.loads(line.strip())

            # skip filtering by tags since metadata is removed
            if sample_tags:
                # tags filtering no longer supported without metadata
                pass

            sample = Sample(
                id=line_index,
                input=data["input"],
                ground_truth=data.get("ground_truth"),
                agent_args=data.get("agent_args"),
            )

            line_index += 1
            yielded_count += 1
            yield sample
