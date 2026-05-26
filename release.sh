#!/bin/bash
# Usage: bash release.sh 1.2.0
set -euo pipefail

VERSION="${1:-}"
if [ -z "$VERSION" ]; then
  echo "Usage: bash release.sh <version>  (e.g. 1.2.0)"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Releasing v$VERSION..."

# Bump version in manifest.json
jq --arg v "$VERSION" '.version = $v' \
  custom_components/aionflux/manifest.json > /tmp/manifest_tmp.json
mv /tmp/manifest_tmp.json custom_components/aionflux/manifest.json

# Commit all changes + manifest
git add custom_components/
git diff --cached --quiet || git commit -m "chore: release v$VERSION"
git tag "v$VERSION"

# Push to GitLab (triggers CI pipeline which mirrors to GitHub)
git push origin main
git push origin "v$VERSION"

echo "Tag v$VERSION pushed — GitLab CI will publish to GitHub automatically."
