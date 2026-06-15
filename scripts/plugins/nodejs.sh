nodejs_info() {
  echo "Node: $(node --version 2>/dev/null || echo 'not installed')"
  echo "NPM: $(npm --version 2>/dev/null || echo 'not installed')"
}