from collections import defaultdict
from pathlib import Path
from typing import Union

import yaml
from reno.config import Config
from reno.scanner import Scanner


def collect_notes(conf: Union[Config, None] = None) -> dict:
    conf = conf or Config("./")
    with Scanner(conf) as scnr:
        relnotes = scnr.get_notes_by_version()
        # unfortunately the date is a naive timestamp without timezone info
        versions_to_dates = scnr.get_version_dates()
    reporoot = Path(conf.reporoot)

    relnotes_content: dict = defaultdict(lambda: defaultdict(list))
    for version, version_details in relnotes.items():
        relnotes_content[version]["meta"] = {
            "released": version in versions_to_dates,
        }
        relnotes_content[version]["notes"] = defaultdict(list)
        version_files = [x[0] for x in version_details]
        for f in version_files:
            version_file_content = yaml.load(
                (reporoot / f).read_text(), Loader=yaml.SafeLoader
            )
            for category, notes in version_file_content.items():
                if isinstance(notes, str):
                    relnotes_content[version]["notes"][category].append(notes)
                else:
                    relnotes_content[version]["notes"][category].extend(notes)

    return {"relnotes": relnotes_content}
