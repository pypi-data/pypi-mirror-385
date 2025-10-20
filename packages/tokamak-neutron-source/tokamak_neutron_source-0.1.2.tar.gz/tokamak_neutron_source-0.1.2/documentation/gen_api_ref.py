# SPDX-FileCopyrightText: 2024-present Tokamak Neutron Source Maintainers
#
# SPDX-License-Identifier: LGPL-2.1-or-later

"""Generate the API reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files
from mkdocs_gen_files.nav import Nav

nav = Nav()

root = Path(__file__).parent.parent
package_name = "tokamak_neutron_source"
src = root / package_name
reference = Path("source", "reference")

for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(root).with_suffix("")
    doc_path = path.relative_to(root).with_suffix(".md")
    full_doc_path = Path(reference, doc_path)

    parts = tuple(module_path.parts)

    # if is_init:= (parts[-1] =="__init__"):
    #     parts = parts[:-1]
    #     if len(parts) > 1:
    #         continue
    if parts[-1] in {"__init__", "__main__", "_version"}:
        continue

    p = ".".join(parts)
    # parts = (*parts, p) if is_init else parts
    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        fd.write(f"::: {p}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

with mkdocs_gen_files.open(Path(reference, "overview.md"), "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
