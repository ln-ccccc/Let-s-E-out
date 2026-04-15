#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$ROOT_DIR/templates/flutter_mobile"
APPS_DIR="$ROOT_DIR/apps"
APP_DIR="$APPS_DIR/mobile"

if ! command -v flutter >/dev/null 2>&1; then
  echo "flutter 未安装：请先安装 Flutter SDK，然后重新运行该脚本"
  exit 1
fi

mkdir -p "$APPS_DIR"

if [ ! -f "$APP_DIR/pubspec.yaml" ]; then
  rm -rf "$APP_DIR"
  flutter create "$APP_DIR" --org com.example --project-name tandian_fupan --platforms android,ios
fi

rm -rf "$APP_DIR/lib"
mkdir -p "$APP_DIR/lib"
cp -R "$TEMPLATE_DIR/lib/." "$APP_DIR/lib/"
cp "$TEMPLATE_DIR/pubspec.yaml" "$APP_DIR/pubspec.yaml"

if [ -f "$TEMPLATE_DIR/analysis_options.yaml" ]; then
  cp "$TEMPLATE_DIR/analysis_options.yaml" "$APP_DIR/analysis_options.yaml"
fi

(cd "$APP_DIR" && flutter pub get)

echo "Flutter 工程已生成：$APP_DIR"
