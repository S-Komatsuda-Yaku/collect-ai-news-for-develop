#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
news_path="${1:-}"

if [[ -z "$news_path" ]]; then
  echo "Usage: $0 aI_knowledge/YYYY/MMDD.md" >&2
  exit 2
fi

if [[ "$news_path" = /* ]]; then
  case "$news_path" in
    "$repo_root"/*) news_path="${news_path#"$repo_root"/}" ;;
    *)
      echo "News file must be inside $repo_root/aI_knowledge" >&2
      exit 2
      ;;
  esac
fi

if [[ ! "$news_path" =~ ^aI_knowledge/[0-9]{4}/[0-9]{4}\.md$ ]]; then
  echo "News path must match aI_knowledge/YYYY/MMDD.md" >&2
  exit 2
fi

if [[ ! -f "$repo_root/$news_path" ]]; then
  echo "News file does not exist: $repo_root/$news_path" >&2
  exit 2
fi

if [[ "$(git -C "$repo_root" branch --show-current)" != "main" ]]; then
  echo "Refusing to publish from a branch other than main" >&2
  exit 1
fi

# Incorporate remote updates before creating the daily commit.
git -C "$repo_root" pull --rebase --autostash origin main
git -C "$repo_root" add -- "$news_path"

if git -C "$repo_root" diff --cached --quiet -- "$news_path"; then
  echo "No changes to publish: $news_path"
  exit 0
fi

news_date="$(basename "$news_path" .md)"
news_year="$(basename "$(dirname "$news_path")")"
git -C "$repo_root" commit -m "Add AI news for ${news_year}-${news_date:0:2}-${news_date:2:2}" -- "$news_path"
git -C "$repo_root" push origin main

echo "Published $news_path to origin/main"
