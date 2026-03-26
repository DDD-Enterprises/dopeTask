#!/usr/bin/env bash
set -euo pipefail

# dopeTask Release Guard
# This script intentionally does not mutate versions, create commits, or push tags.
# Use the PR-first release flow documented in docs/90_RELEASE.md.

if [ $# -gt 1 ]; then
    echo "❌ Usage: $0 [version]"
    exit 1
fi

VERSION="${1:-}"
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | head -n 1 | sed 's/version = "\(.*\)"/\1/')

if [[ -n "$VERSION" ]] && [[ "$VERSION" != "$CURRENT_VERSION" ]]; then
    echo "❌ Version mismatch: requested $VERSION, repo is $CURRENT_VERSION"
    echo "Update version files in a PR before using the guarded release helpers."
    exit 1
fi

echo "dopeTask release is PR-first and tag-gated."
echo ""
echo "Current version: $CURRENT_VERSION"
echo ""
echo "1. Land the release changes in a PR against main."
echo "2. Merge the PR."
echo "3. Verify from a clean checkout:"
echo "   bash scripts/dopetask_release_local.sh"
echo "4. Tag merged main:"
echo "   git tag v$CURRENT_VERSION"
echo "5. Push the tag:"
echo "   git push origin v$CURRENT_VERSION"
echo ""
echo "See docs/90_RELEASE.md for the authoritative flow."
