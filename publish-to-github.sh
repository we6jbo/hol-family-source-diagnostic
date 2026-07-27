#!/bin/sh
# Safely create or update the public GitHub repository using an explicit allowlist.
set -eu
REPO=we6jbo/hol-family-source-diagnostic
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

FILES='hol-family-source-diagnostic.py
hol-family-source-investigator.py
hol-reddit-ollama-bridge.py
QVIX.py
hol_reddit_adapter.py
communication.py
ada.py
install-communication-service.sh
run-hol-family-source-investigator.sh
run-reddit-ollama-bridge.sh
chrome-extension/background.js
chrome-extension/content.js
chrome-extension/manifest.json
chrome-extension/popup.html
chrome-extension/popup.js
README.md
LICENSE
.gitignore
install.sh
publish-to-github.sh
reinstall-source-tree.sh
install-extension-to-home.sh
NEXT-VERSION.md
PF2F5QTT.md
setup-pf2f5qtt-private-recovery.sh
token439873.touch'

command -v git >/dev/null 2>&1 || { echo 'git is required.' >&2; exit 1; }
command -v gh >/dev/null 2>&1 || { echo 'GitHub CLI (gh) is required.' >&2; exit 1; }
gh auth status >/dev/null

cd "$SOURCE_DIR"
[ -d .git ] || git init -b main
git config --get user.name >/dev/null 2>&1 || git config user.name "Jeremiah O'Neal"
git config --get user.email >/dev/null 2>&1 || git config user.email joneal97@users.noreply.github.com

# Never stage unknown files. Remove tracked files that are no longer allowlisted.
git ls-files -z | while IFS= read -r -d '' tracked; do
    case "
$FILES
" in
        *"
$tracked
"*) ;;
        *) git rm --cached --ignore-unmatch -- "$tracked" >/dev/null ;;
    esac
done
printf '%s\n' "$FILES" | while IFS= read -r file; do
    [ -e "$file" ] && git add -- "$file"
done

git diff --cached --quiet || git commit -m 'Harden and clean HOL family source diagnostic'

if gh repo view "$REPO" >/dev/null 2>&1; then
    git remote get-url origin >/dev/null 2>&1 \
      && git remote set-url origin "https://github.com/$REPO.git" \
      || git remote add origin "https://github.com/$REPO.git"
    git fetch origin main
    if ! git merge-base --is-ancestor origin/main HEAD; then
        echo 'Remote main contains changes not present locally. No push or force-push was attempted.' >&2
        exit 1
    fi
    git push -u origin main
else
    gh repo create "$REPO" --public \
      --description "Date-source and provenance diagnostic with genealogy evidence-review applications for Holderman, Loveland, Smith, and Prickett research." \
      --source . --remote origin --push
fi

gh repo edit "$REPO" \
  --description "Date-source and provenance diagnostic with genealogy evidence-review applications for Holderman, Loveland, Smith, and Prickett research." \
  --add-topic genealogy --add-topic family-history --add-topic source-criticism \
  --add-topic provenance --add-topic historical-research --add-topic python \
  --add-topic digital-humanities --add-topic gplv3
printf 'Published: https://github.com/%s\n' "$REPO"
