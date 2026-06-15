nim_info() {
  echo "Nim: $(nim --version 2>/dev/null || echo 'not installed')"
}