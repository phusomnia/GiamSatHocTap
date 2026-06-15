java_info() {
    echo "Java: $(java --version 2>/dev/null || die "Java not installed")"
}

java_init() {
    local path_project="${1:-demo/java}"
    
    if [ ! -d "$path_project" ]; then
        log_error "Directory does not exist: $path_project"
        return 1
    fi 
    
    if [ -f "$path_project/pom.xml" ] || [ -f "$path_project/build.gradle" ]; then
        log_warn "Java build doesn't exist" 
        return 1
    fi 

    # 
    
    mvn archetype:structure \ 
        -DgroupId="$group_id" \
        -DartifactId="$artifact_id" \
        -DarchetypeArtifactId=maven-archetype-quickstart \
        -DarchetypeVersion=1.4 \
        -DinteractiveMode=false
}

