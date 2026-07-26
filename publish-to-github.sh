#!/bin/sh
# Create or update the public GitHub repository using GitHub CLI.
set -eu
REPO=we6jbo/hol-family-source-diagnostic
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

command -v git >/dev/null 2>&1 || { echo 'git is required.' >&2; exit 1; }
command -v gh >/dev/null 2>&1 || { echo 'GitHub CLI (gh) is required.' >&2; exit 1; }
gh auth status >/dev/null

cd "$SOURCE_DIR"
[ -d .git ] || git init -b main
git config --get user.name >/dev/null 2>&1 || git config user.name "Jeremiah O'Neal"
git config --get user.email >/dev/null 2>&1 || git config user.email joneal97@users.noreply.github.com
git add --all
git diff --cached --quiet || git commit -m 'Publish HOL family source diagnostic'

if gh repo view "$REPO" >/dev/null 2>&1; then
    git remote get-url origin >/dev/null 2>&1 \
      && git remote set-url origin "https://github.com/$REPO.git" \
      || git remote add origin "https://github.com/$REPO.git"
    git push -u origin main
else
    gh repo create "$REPO" --public \
      --description "Genealogy source diagnostic and evidence-review toolkit for Holderman, Loveland, Smith, and Prickett family research." \
      --source . --remote origin --push
fi

gh repo edit "$REPO" \
  --description "Genealogy source diagnostic and evidence-review toolkit for Holderman, Loveland, Smith, and Prickett family research." \
  --add-topic genealogy --add-topic family-history --add-topic source-criticism \
  --add-topic provenance --add-topic historical-research --add-topic python \
  --add-topic digital-humanities --add-topic gplv3
printf 'Published: https://github.com/%s\n' "$REPO"
