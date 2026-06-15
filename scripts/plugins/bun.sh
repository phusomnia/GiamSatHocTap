bun_info() {
  echo "Bun: $(bun --version 2>/dev/null || echo 'not installed')"
}