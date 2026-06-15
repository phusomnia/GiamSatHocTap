git_status() {
  git status
}

git_rename_main() {
  if git branch --show-current | grep -q master; then
    git branch -M main
    echo "Renamed master → main"
  else
    echo "Current branch is not master"
  fi
}

git_add() {
  git add .
  echo "Staged all changes"
}

git_commit() {
  read -p "Commit message: " msg
  git commit -m "$msg"
}

git_push() {
  git push -u origin main
}

