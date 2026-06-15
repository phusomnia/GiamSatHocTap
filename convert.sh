convert_dbml_to_sql() {
    echo "Convert DBML to SQL..."

    echo -n "DBML file: "
    read -e DBML_FILE

    if [ -z "$DBML_FILE" ]; then
        print_error "File name can't be empty"
        return -1
    fi

    print_info "Convert $DBML_FILE to SQL..."
    dbml2sql "$DBML_FILE" -o "${DBML_FILE}.sql"

    echo "OK"
}

convert_sql_to_orm() {
    TARGET_FILE="src/Domain/base_entities.py"
    CONFIG="src/config/app-config.yaml"

    PROVIDER=$(yq -r '.databases.provider' "$CONFIG")
    DB_URL=$(yq -r ".databases.${PROVIDER}.url" "$CONFIG")

    if [ -z "$DB_URL" ] || [ "$DB_URL" = "null" ]; then
        print_error "Failed to read database URL from config"
        return -1
    fi

    DB_URL=$(echo "$DB_URL" | sed 's/+asyncpg//')

    if [ "$PROVIDER" = "postgresql" ]; then
        SEARCH_PATH=$(echo "$DB_URL" | sed -n 's/.*options=-csearch_path%3D\([^&]*\).*/\1/p')

        if [ -n "$SEARCH_PATH" ] && [ "$SEARCH_PATH" != "$DB_URL" ]; then
            print_info "Using schema: $SEARCH_PATH"
            python -m sqlacodegen "$DB_URL" --generator sqlmodels --outfile $TARGET_FILE --schema "$SEARCH_PATH"
        else
            print_info "Using default schema (no --schema parameter)"
            python -m sqlacodegen "$DB_URL" --generator sqlmodels --outfile $TARGET_FILE
        fi
    else
        python -m sqlacodegen "$DB_URL" --generator sqlmodels --outfile $TARGET_FILE
    fi

    if [ $? -eq 0 ]; then
        print_success "ORM models generated at $TARGET_FILE"
    else
        print_error "Failed to generate ORM models"
        return -1
    fi
}

check_size() {
    echo -n "Enter folder path: "
    read -e FOLDER_PATH

    if [ -z "$FOLDER_PATH" ]; then
        print_error "Folder path can't be empty"
        return -1
    fi

    if [ ! -d "$FOLDER_PATH" ]; then
        print_error "Folder '$FOLDER_PATH' does not exist"
        return -1
    fi

    print_info "Calculating size of '$FOLDER_PATH'..."

    HUMAN_SIZE=$(du -sh "$FOLDER_PATH" | cut -f1)
    BYTE_SIZE=$(du -sb "$FOLDER_PATH" | cut -f1)
    FILE_COUNT=$(find "$FOLDER_PATH" -type f | wc -l)
    DIR_COUNT=$(find "$FOLDER_PATH" -type d | wc -l)

    print_success "Folder: $FOLDER_PATH"
    print_success "Size: $HUMAN_SIZE ($BYTE_SIZE bytes)"
    print_success "Files: $FILE_COUNT"
    print_success "Directories: $DIR_COUNT"
}

clean_pycache() {
    print_info "Cleaning Python cache files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete 2>/dev/null
    find . -type f -name "*.pyo" -delete 2>/dev/null
    print_success "Python cache cleaned"
}

clean_uploads() {
    print_info "Đang xóa UUID folders..."
    find src/static/uploads -type d -name "*-*-*-*-*" -exec rm -rf {} + 2>/dev/null
    print_success "Done"
}
