#!/usr/bin/env python3
import os
import sys
import argparse
import configparser
import re
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(description="Simple palette-based manifest image replacer")
    parser.add_argument("--config", "-c", default="palette.conf", help="Path to config file (default: palette.conf)")
    parser.add_argument("--palletes_version", action="store_true", help="Print version (from [git] section) and exit")
    return parser.parse_args()

def load_config(path):
    if not os.path.isfile(path):
        print(f"Error: config file '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    cfg = configparser.ConfigParser()
    cfg.optionxform = lambda optionstr: optionstr
    try:
        cfg.read(path)
    except configparser.Error as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)
    return cfg

def checkout_and_print_version(cfg, root_folder):
    git_section = cfg.get("git", {})
    hash_sum = git_section.get("hash_sum", "").strip().strip('"').strip("'")
    version = git_section.get("version", "").strip().strip('"').strip("'")
    if hash_sum:
        result = subprocess.run(
            ["git", "checkout", hash_sum],
            cwd=root_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"Error: git checkout failed: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
    if version:
        print(version)

def replace_images(root_folder, images_map):
    summary = []
    for manifest_name, new_image in images_map.items():
        new_image = new_image.strip().strip('"').strip("'")
        manifest_path = os.path.join(root_folder, manifest_name)
        if not os.path.isfile(manifest_path):
            summary.append(f"[WARN] File not found: {manifest_path}")
            continue
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
        except IOError as e:
            summary.append(f"[ERROR] Cannot read '{manifest_path}': {e}")
            continue
        pattern = re.compile(r'^(\s*image:\s*)(["\']?)[^"\']+(["\']?)', flags=re.MULTILINE)
        def _repl(match):
            prefix = match.group(1)
            open_q = match.group(2) or ""
            close_q = match.group(3) or ""
            return f"{prefix}{open_q}{new_image}{close_q}"
        new_content, count = pattern.subn(_repl, content)
        if count == 0:
            summary.append(f"[INFO] No 'image:' lines replaced in {manifest_path}")
        else:
            try:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                summary.append(f"[OK] Replaced {count} occurrence(s) in {manifest_path}")
            except IOError as e:
                summary.append(f"[ERROR] Cannot write '{manifest_path}': {e}")
    return summary

def main():
    args = parse_args()
    cfg = load_config(args.config)
    if args.palletes_version:
        if "git" in cfg and "version" in cfg["git"]:
            version = cfg["git"]["version"].strip().strip('"').strip("'")
            print(version)
            sys.exit(0)
        else:
            print("Version info not found in config under [git].", file=sys.stderr)
            sys.exit(1)
    if "conf" not in cfg or "root_folder" not in cfg["conf"]:
        print("Error: [conf] section with 'root_folder' is required in config.", file=sys.stderr)
        sys.exit(1)
    root_folder = cfg["conf"]["root_folder"].strip().strip('"').strip("'")
    if not root_folder:
        root_folder = "."
    if "git" in cfg:
        checkout_and_print_version(cfg, root_folder)
    if "images" not in cfg:
        print("Error: [images] section is required in config.", file=sys.stderr)
        sys.exit(1)
    images_map = {}
    for key, val in cfg["images"].items():
        manifest_name = key.strip()
        image_ref = val.strip()
        if manifest_name and image_ref:
            images_map[manifest_name] = image_ref
    summary = replace_images(root_folder, images_map)
    for line in summary:
        print(line)

if __name__ == "__main__":
    main()
