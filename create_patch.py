#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def log(message):
    """Helper function for logging messages"""
    print(f"[LOG] {message}")

def error(message):
    """Helper function for error reporting"""
    print(f"[ERROR] {message}", file=sys.stderr)

def create_patch_for_file(repo_path, commit_id_src, commit_id_dst, filename, output_base_dir):
    """
    Generate a patch file for a specific file from the original commit to the target commit using git diff.
    
    :param repo_path: Root path of the Git repository
    :param commit_id_src: Hash or branch name of the original commit
    :param commit_id_dst: Hash or branch name of the target commit
    :param filename: Filename (relative to the repository root)
    :param output_base_dir: Base directory for output patch files
    """
    relative_path = os.path.relpath(filename, repo_path)
    # Ensure the output directory structure matches the source file's path
    output_subdir = os.path.join(output_base_dir, os.path.dirname(relative_path))
    patch_filename = f"{os.path.basename(filename)}.patch"
    patch_filepath = os.path.join(output_subdir, patch_filename)

    # Ensure the output directory exists
    os.makedirs(output_subdir, exist_ok=True)

    try:
        log(f"Creating patch for {filename} -> {patch_filename}")
        with open(patch_filepath, 'w') as patch_file:
            result = subprocess.run(
                ['git', '-C', repo_path, 'diff', commit_id_src, commit_id_dst, '--', filename],
                stdout=patch_file,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
        
        # Check if the patch file is empty
        if os.path.getsize(patch_filepath) == 0:
            os.remove(patch_filepath)
            log(f"Patch for {filename} is empty, skipped.")
        else:
            log(f"Patch created successfully: {patch_filename}")
    
    except subprocess.CalledProcessError as e:
        error(f"Failed to create patch for {filename}: {e.stderr}")
        if os.path.exists(patch_filepath):
            os.remove(patch_filepath)  # Clean up any potentially created empty file

def scan_and_create_patches(repo_path, target_dir, commit_id_src, commit_id_dst, output_base_dir):
    """
    Scan all files in the specified directory and generate patches for each file.
    
    :param repo_path: Root path of the Git repository
    :param target_dir: Directory to scan (relative to the repository root)
    :param commit_id_src: Hash or branch name of the original commit
    :param commit_id_dst: Hash or branch name of the target commit
    :param output_base_dir: Base directory for output patch files
    """
    full_target_dir = os.path.join(repo_path, target_dir)

    if not os.path.isdir(full_target_dir):
        error(f"The target directory does not exist or is not a directory: {full_target_dir}")
        return

    log(f"Scanning all files in {target_dir}")
    for root, _, files in os.walk(full_target_dir):
        for file in files:
            filename = os.path.join(root, file)
            create_patch_for_file(repo_path, commit_id_src, commit_id_dst, filename, output_base_dir)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        error("Usage: python3 script.py <repo_path> <target_dir> <commit_id_src> <commit_id_dst> <output_base_dir>")
        sys.exit(1)

    repo_path = sys.argv[1]
    target_dir = sys.argv[2]
    commit_id_src = sys.argv[3]
    commit_id_dst = sys.argv[4]
    output_base_dir = sys.argv[5]

    log(f"Starting patch creation with parameters: {sys.argv[1:]}")
    
    if not os.path.isdir(repo_path):
        error(f"The repository path does not exist or is not a directory: {repo_path}")
        sys.exit(1)

    if not os.path.isdir(output_base_dir):
        os.makedirs(output_base_dir, exist_ok=True)

    scan_and_create_patches(repo_path, target_dir, commit_id_src, commit_id_dst, output_base_dir)
