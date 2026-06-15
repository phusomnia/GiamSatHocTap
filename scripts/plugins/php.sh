php_info() {
    echo "Php: $(php --version)"
}

php_init() 
{
    local dir="${1:-demo/php}"

    log_info "Stage 1/4: init — $dir"

    command -v php >/dev/null || die "PHP not found"
}

php_install_deps() 
{
    local dir="${1:-demo/php}"

    log_info "Stage 2/4: install — $dir"

    if [ -f "$dir/composer.json" ]; then
        command -v composer >/dev/null || die "Composer not found"

        (cd "$dir" && composer install)
    fi
}

php_build() 
{
    local dir="${1:-demo/php}"

    log_info "Stage 3/4: build — $dir"

    find "$dir" \
        -type f \
        -name "*.php" \
        -not -path "$dir/vendor/*" \
        -exec php -l {} \; \
        || die "PHP syntax check failed"
}

php_run() 
{
    local dir="${1:-demo/php}"

    log_info "Stage 4/4: run — $dir"

    php -S localhost:8080 -t "$dir/public"
}

php_demo_pipeline() {
    php_init
    php_install_deps
    php_build
    php_run
}