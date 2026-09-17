#!/usr/bin/env python3
"""
Build olm.package and olm.channel FBC entries from a community-operators package directory.

Given a package directory where each subdirectory is a bundle version:
  <pkg>/
    1.0.0/
      manifests/   (contains CSV and CRDs)
      metadata/    (contains annotations.yaml)
    1.1.0/
      ...

Reads annotations.yaml (channels, default channel) and the CSV (csv name, spec.replaces)
from each version, then writes olm.package + olm.channel YAML to stdout for appending
to a catalog file before running opm validate.
"""

import os
import sys
import yaml


def find_csv(manifests_dir):
    """Return the parsed CSV document from a bundle's manifests directory, or None."""
    if not os.path.isdir(manifests_dir):
        return None
    for fname in os.listdir(manifests_dir):
        if not (fname.endswith(".yaml") or fname.endswith(".yml")):
            continue
        path = os.path.join(manifests_dir, fname)
        try:
            with open(path) as fh:
                doc = yaml.safe_load(fh)
            if doc and doc.get("kind") == "ClusterServiceVersion":
                return doc
        except Exception:
            continue
    return None


def parse_bundle(bundle_dir):
    """
    Parse a single bundle version directory.
    Returns a dict with version metadata, or None if the directory is not a valid bundle.
    """
    annotations_path = os.path.join(bundle_dir, "metadata", "annotations.yaml")
    if not os.path.exists(annotations_path):
        return None

    try:
        with open(annotations_path) as fh:
            annotations_doc = yaml.safe_load(fh)
    except Exception as exc:
        print(f"Warning: could not parse {annotations_path}: {exc}", file=sys.stderr)
        return None

    annotations = (annotations_doc or {}).get("annotations", {})
    channels_raw = annotations.get("operators.operatorframework.io.bundle.channels.v1", "")
    default_channel = annotations.get(
        "operators.operatorframework.io.bundle.channel.default.v1", ""
    ).strip()
    channels = [c.strip() for c in channels_raw.split(",") if c.strip()]

    csv = find_csv(os.path.join(bundle_dir, "manifests"))
    if not csv:
        print(f"Warning: no CSV found in {bundle_dir}/manifests", file=sys.stderr)
        return None

    csv_name = (csv.get("metadata") or {}).get("name", "").strip()
    replaces = (csv.get("spec") or {}).get("replaces", "").strip()

    if not csv_name:
        print(f"Warning: CSV in {bundle_dir} has no metadata.name", file=sys.stderr)
        return None

    return {
        "dir": bundle_dir,
        "version": os.path.basename(bundle_dir),
        "csv_name": csv_name,
        "channels": channels,
        "default_channel": default_channel,
        "replaces": replaces,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: build_catalog_metadata.py <operator_package_dir>", file=sys.stderr)
        sys.exit(1)

    pkg_dir = sys.argv[1].rstrip("/")
    if not os.path.isdir(pkg_dir):
        print(f"Error: {pkg_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    pkg_name = os.path.basename(pkg_dir)

    # Collect all valid bundle version directories (sorted by version string)
    version_dirs = sorted(
        entry.path
        for entry in os.scandir(pkg_dir)
        if entry.is_dir()
    )

    bundles = []
    for vdir in version_dirs:
        info = parse_bundle(vdir)
        if info:
            bundles.append(info)

    if not bundles:
        print(f"Error: no valid bundle directories found in {pkg_dir}", file=sys.stderr)
        sys.exit(1)

    # Determine the default channel from the highest-sorted bundle that declares one
    default_channel = ""
    for bundle in reversed(bundles):
        if bundle["default_channel"]:
            default_channel = bundle["default_channel"]
            break
    if not default_channel:
        # Fall back to the first channel of the highest bundle
        for bundle in reversed(bundles):
            if bundle["channels"]:
                default_channel = bundle["channels"][0]
                break

    # Build channel -> ordered list of entries
    channels: dict = {}
    for bundle in bundles:
        for ch in bundle["channels"]:
            if ch not in channels:
                channels[ch] = []
            entry: dict = {"name": bundle["csv_name"]}
            if bundle["replaces"]:
                entry["replaces"] = bundle["replaces"]
            channels[ch].append(entry)

    # Emit olm.package
    pkg_doc = {
        "schema": "olm.package",
        "name": pkg_name,
        "defaultChannel": default_channel,
    }
    print("---")
    print(yaml.dump(pkg_doc, default_flow_style=False).rstrip())

    # Emit olm.channel for each channel
    for ch_name, entries in channels.items():
        ch_doc = {
            "schema": "olm.channel",
            "package": pkg_name,
            "name": ch_name,
            "entries": entries,
        }
        print("---")
        print(yaml.dump(ch_doc, default_flow_style=False).rstrip())


if __name__ == "__main__":
    main()
