#!/usr/bin/env python3
import os
import subprocess
import sys

def log(message):
    """辅助函数用于日志记录"""
    print(f"[LOG] {message}")

def error(message):
    """辅助函数用于错误报告"""
    print(f"[ERROR] {message}", file=sys.stderr)

def is_c_or_h_file(filename):
    """
    检查文件是否是 .c 或 .h 文件。
    
    :param filename: 文件路径
    :return: 如果文件是 .c 或 .h 文件，则返回 True；否则返回 False
    """
    return filename.lower().endswith(('.c', '.h'))

def create_patch_for_file(repo_path, commit_id_src, commit_id_dst, filename, output_dir):
    """
    使用 git diff 为指定文件生成从原始提交到目标提交的补丁文件。
    
    :param repo_path: Git 仓库的根路径
    :param commit_id_src: 原始提交的哈希或分支名
    :param commit_id_dst: 目标提交的哈希或分支名
    :param filename: 文件名（相对于仓库根目录）
    :param output_dir: 补丁文件输出目录
    """
    relative_path = os.path.relpath(filename, repo_path)
    patch_filename = f"{os.path.splitext(relative_path)[0]}.patch"
    patch_filepath = os.path.join(output_dir, relative_path + '.patch')

    # 确保输出目录存在
    os.makedirs(os.path.dirname(patch_filepath), exist_ok=True)

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
        
        # 检查补丁文件是否为空
        if os.path.getsize(patch_filepath) == 0:
            os.remove(patch_filepath)
            log(f"Patch for {filename} is empty, skipped.")
        else:
            log(f"Patch created successfully: {patch_filename}")
    
    except subprocess.CalledProcessError as e:
        error(f"Failed to create patch for {filename}: {e.stderr}")
        if os.path.exists(patch_filepath):
            os.remove(patch_filepath)  # 清理可能创建的空文件

def scan_and_create_patches(repo_path, target_dir, commit_id_src, commit_id_dst, output_base_dir):
    """
    扫描指定文件夹下的所有 .c 和 .h 文件，并为每个文件生成补丁。
    
    :param repo_path: Git 仓库的根路径
    :param target_dir: 需要扫描的文件夹路径（相对于仓库根目录）
    :param commit_id_src: 原始提交的哈希或分支名
    :param commit_id_dst: 目标提交的哈希或分支名
    :param output_base_dir: 补丁文件输出的基础目录
    """
    full_target_dir = os.path.join(repo_path, target_dir)

    if not os.path.isdir(full_target_dir):
        error(f"The target directory does not exist or is not a directory: {full_target_dir}")
        return

    log(f"Scanning .c and .h files in {target_dir}")
    for root, _, files in os.walk(full_target_dir):
        for file in files:
            if is_c_or_h_file(file):
                filename = os.path.join(root, file)
                relative_path = os.path.relpath(filename, repo_path)
                output_dir = os.path.join(output_base_dir, os.path.dirname(relative_path))
                create_patch_for_file(repo_path, commit_id_src, commit_id_dst, filename, output_dir)

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

    scan_and_create_patches(repo_path, target_dir, commit_id_src, commit_id_dst, output_base_dir)
