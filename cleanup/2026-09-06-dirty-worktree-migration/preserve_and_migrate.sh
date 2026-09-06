#!/usr/bin/env bash
set -euo pipefail

archive_root=/home/stanislav/repository-cleanup-archives/2026-09-06-dirty-worktree-migration
mirror=/home/stanislav/repository-cleanup-archives/2026-09-06-history-rewrite/sanitized-mirror.git
verify_root="$archive_root/verify"
migration_root="$archive_root/migrated-worktrees"

names=(main managed-program-r20-isolated orchestrator-review-loop-reduction)
sources=(
  /home/stanislav/.openclaw/workspace/agents/main
  /home/stanislav/agent-runs/managed-program-r20-isolated
  /home/stanislav/agent-runs/orchestrator-worktrees/orchestrator-review-loop-reduction
)

mkdir -p "$archive_root/preservation" "$verify_root" "$migration_root"

for i in "${!names[@]}"; do
  name=${names[$i]}
  source=${sources[$i]}
  dest="$archive_root/preservation/$name"
  verify="$verify_root/$name"
  migrated="$migration_root/$name"
  mkdir -p "$dest" "$verify"

  git -C "$source" rev-parse HEAD >"$dest/source-head.txt"
  git -C "$source" status --porcelain=v2 --branch -z >"$dest/status-v2.z"
  git -C "$source" diff --binary --full-index >"$dest/tracked-worktree.patch"
  git -C "$source" diff --cached --binary --full-index >"$dest/tracked-index.patch"
  git -C "$source" ls-files --others --exclude-standard -z >"$dest/untracked-paths.z"
  git -C "$source" diff --name-only -z >"$dest/tracked-worktree-paths.z"
  git -C "$source" diff --cached --name-only -z >"$dest/tracked-index-paths.z"

  if [[ -s "$dest/untracked-paths.z" ]]; then
    tar -C "$source" --null --files-from="$dest/untracked-paths.z" -cpf "$dest/untracked.tar"
    tar -C "$verify" -xpf "$dest/untracked.tar"
  else
    tar -C "$source" -cpf "$dest/untracked.tar" --files-from=/dev/null
  fi

  (
    cd "$source"
    while IFS= read -r -d '' path; do
      if [[ -L "$path" ]]; then
        printf 'L\t%s\t%s\n' "$path" "$(readlink "$path")"
      elif [[ -f "$path" ]]; then
        printf 'F\t%s\t%s\n' "$path" "$(sha256sum -- "$path" | cut -d' ' -f1)"
      else
        printf 'O\t%s\n' "$path"
      fi
    done <"$dest/untracked-paths.z"
  ) >"$dest/untracked-manifest.tsv"

  (
    cd "$verify"
    while IFS=$'\t' read -r kind path value; do
      [[ -z "$kind" ]] && continue
      if [[ "$kind" == F ]]; then
        [[ "$(sha256sum -- "$path" | cut -d' ' -f1)" == "$value" ]]
      elif [[ "$kind" == L ]]; then
        [[ -L "$path" && "$(readlink "$path")" == "$value" ]]
      else
        exit 1
      fi
    done <"$dest/untracked-manifest.tsv"
  )

  sha256sum "$dest/tracked-worktree.patch" "$dest/tracked-index.patch" \
    "$dest/untracked.tar" "$dest/untracked-manifest.tsv" >"$dest/preservation-sha256.txt"

  git clone --no-hardlinks "$mirror" "$migrated"
  git -C "$migrated" checkout "$name"
  if [[ -s "$dest/tracked-index.patch" ]]; then
    git -C "$migrated" apply --index --binary "$dest/tracked-index.patch"
  fi
  if [[ -s "$dest/tracked-worktree.patch" ]]; then
    git -C "$migrated" apply --binary "$dest/tracked-worktree.patch"
  fi
  tar -C "$migrated" -xpf "$dest/untracked.tar"
  git -C "$migrated" status --porcelain=v2 --branch -z >"$dest/migrated-status-v2.z"
done
