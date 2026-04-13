#!/usr/bin/env python
"""Deploy updated files directly to HF Space using huggingface_hub."""

from huggingface_hub import upload_folder
import os

space_repo_id = "Sushruth21/energy-optimization-space"
local_dir = "."

print(f"🚀 Deploying to HF Space: {space_repo_id}")
print(f"📁 Local directory: {local_dir}")

try:
    info = upload_folder(
        repo_id=space_repo_id,
        folder_path=local_dir,
        repo_type="space",
        commit_message="Fix PYTHONPATH in Dockerfile for grader discovery and add critical files",
        multi_commits=False,
        multi_commits_verbose=False,
    )
    print(f"✅ Upload successful!")
    print(f"📝 Commit URL: {info.commit_url}")
except Exception as e:
    print(f"❌ Upload failed: {type(e).__name__}: {e}")
