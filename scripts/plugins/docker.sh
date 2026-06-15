docker_info() {
  echo "Docker: $(docker --version 2>/dev/null || echo 'not installed')"
  echo "Compose: $(docker compose version 2>/dev/null || echo 'not installed')"
}