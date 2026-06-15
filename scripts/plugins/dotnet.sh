dotnet_info() {
  echo ".NET: $(dotnet --version 2>/dev/null || echo 'not installed')"
}