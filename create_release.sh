#!/bin/bash
set -e

VERSION=${1:-"1.0.0"}
RELEASE_NAME="callblocker-${VERSION}"
BUILD_DIR="build/${RELEASE_NAME}"

echo "Creazione release Call Blocker v${VERSION}..."

rm -rf build
mkdir -p "$BUILD_DIR"

cp -r *.py "$BUILD_DIR/"
cp *.sh "$BUILD_DIR/"
cp *.service "$BUILD_DIR/"
cp requirements.txt "$BUILD_DIR/"
cp Makefile "$BUILD_DIR/"
cp *.md "$BUILD_DIR/"
cp LICENSE "$BUILD_DIR/" 2>/dev/null || true
cp daemon.conf.example "$BUILD_DIR/"

chmod +x "$BUILD_DIR"/*.sh
chmod +x "$BUILD_DIR"/*.py

cd build
sha256sum "$RELEASE_NAME"/* > "$RELEASE_NAME/SHA256SUMS"
tar czf "${RELEASE_NAME}.tar.gz" "$RELEASE_NAME"
sha256sum "${RELEASE_NAME}.tar.gz" > "${RELEASE_NAME}.tar.gz.sha256"
cd ..

echo ""
echo "✓ Release creata: build/${RELEASE_NAME}.tar.gz"
