use crate::error::{Result, XacroError};

pub fn get_boolean_value(value: &str) -> Result<bool> {
    match value.trim().to_lowercase().as_str() {
        "true" | "1" | "1.0" => Ok(true),
        "false" | "0" | "0.0" => Ok(false),
        _ => {
            // Try to parse as number
            if let Ok(num) = value.parse::<f64>() {
                Ok(num != 0.0)
            } else {
                Err(XacroError::Type(format!(
                    "Cannot convert '{value}' to boolean"
                )))
            }
        }
    }
}

pub fn is_valid_name(name: &str) -> bool {
    if name.is_empty() {
        return false;
    }

    // Must start with letter or underscore
    let first_char = name.chars().next().unwrap();
    if !first_char.is_alphabetic() && first_char != '_' {
        return false;
    }

    // Rest must be alphanumeric or underscore
    name.chars().all(|c| c.is_alphanumeric() || c == '_')
}

pub fn abs_filename_spec(
    filename: &str,
    current_file: Option<&std::path::Path>,
) -> std::path::PathBuf {
    let path = std::path::Path::new(filename);
    if path.is_absolute() {
        path.to_path_buf()
    } else if let Some(current) = current_file {
        let parent = current
            .parent()
            .unwrap_or_else(|| std::path::Path::new("."));
        parent.join(filename)
    } else {
        std::path::Path::new(".").join(filename)
    }
}

pub fn tokenize(s: &str, sep: &str, skip_empty: bool) -> Vec<String> {
    let mut results = Vec::new();
    let mut current = String::new();

    for ch in s.chars() {
        if sep.contains(ch) {
            if !skip_empty || !current.is_empty() {
                results.push(current);
                current = String::new();
            }
        } else {
            current.push(ch);
        }
    }

    if !skip_empty || !current.is_empty() {
        results.push(current);
    }

    results
}

/// Search for a file by traversing up the directory tree
pub fn search_up(start_dir: &std::path::Path, relative_path: &str) -> Option<std::path::PathBuf> {
    let mut current_dir = start_dir.to_path_buf();

    loop {
        let candidate = current_dir.join(relative_path);
        if candidate.exists() {
            return Some(candidate);
        }

        let parent = current_dir.parent()?;
        if parent == current_dir {
            break;
        }
        current_dir = parent.to_path_buf();
    }

    None
}

/// Resolve a ROS2 package path using AMENT_PREFIX_PATH
fn resolve_ros2_package_path(package_name: &str) -> Option<std::path::PathBuf> {
    if let Ok(ament_prefix_path) = std::env::var("AMENT_PREFIX_PATH") {
        let path_separator = if cfg!(windows) { ';' } else { ':' };
        for prefix_str in ament_prefix_path.split(path_separator) {
            let prefix_path = std::path::Path::new(prefix_str);
            let resource_path = prefix_path
                .join("share")
                .join("ament_index")
                .join("resource_index")
                .join("packages")
                .join(package_name);

            if resource_path.exists() {
                // The actual package is located at <prefix>/share/<package_name>
                let package_path = prefix_path.join("share").join(package_name);
                if package_path.is_dir() {
                    return Some(package_path);
                }
            }
        }
    }
    None
}

/// Resolve a ROS package path, searching ROS2 first, then ROS1, then up directories
pub fn resolve_package_path(
    package_name: &str,
    base_path: &std::path::Path,
) -> Option<std::path::PathBuf> {
    // 1. Try ROS2 (ament) method first
    if let Some(path) = resolve_ros2_package_path(package_name) {
        return Some(path);
    }

    // 2. Try ROS1 (rospack) method if ROS2 fails
    if let Ok(ros_package_path) = std::env::var("ROS_PACKAGE_PATH") {
        // Use the correct path separator for the current OS
        let path_separator = if cfg!(windows) { ';' } else { ':' };
        for path_str in ros_package_path.split(path_separator) {
            let path = std::path::Path::new(path_str);

            // Check if this path IS the package directory
            if path.file_name().is_some_and(|name| name == package_name) && path.exists() {
                // Prefer package.xml if available, but accept directory existence
                if path.join("package.xml").exists() || path.is_dir() {
                    return Some(path.to_path_buf());
                }
            }

            // Check if package exists directly in this path
            let direct_package_path = path.join(package_name);
            if direct_package_path.exists() {
                // Prefer package.xml if available, but accept directory existence
                if direct_package_path.join("package.xml").exists() || direct_package_path.is_dir()
                {
                    return Some(direct_package_path);
                }
            }

            // Also check if this path contains the package as a subdirectory
            if let Ok(entries) = std::fs::read_dir(path) {
                for entry in entries.flatten() {
                    if entry.file_type().is_ok_and(|t| t.is_dir()) {
                        let subdir_package_path = entry.path().join(package_name);
                        if subdir_package_path.exists() {
                            // Prefer package.xml if available, but accept directory existence
                            if subdir_package_path.join("package.xml").exists()
                                || subdir_package_path.is_dir()
                            {
                                return Some(subdir_package_path);
                            }
                        }
                    }
                }
            }
        }
    }

    // 3. Fallback to searching up the directory tree
    // If neither ROS2 nor ROS1 methods work, search up from base_path
    // First, check if we're already inside the package directory
    let mut current_path = base_path.to_path_buf();

    loop {
        // Check if current directory name matches the package we're looking for
        if let Some(dir_name) = current_path.file_name() {
            if dir_name == package_name {
                // Prefer directories with package.xml, but fall back to any matching directory
                if current_path.join("package.xml").exists() {
                    return Some(current_path);
                } else if current_path.is_dir() {
                    // For non-ROS packages, just check if it's a directory
                    return Some(current_path);
                }
            }
        }

        // Check if package exists as subdirectory
        let package_path = current_path.join(package_name);
        if package_path.exists() {
            // Prefer directories with package.xml, but fall back to any matching directory
            if package_path.join("package.xml").exists() {
                return Some(package_path);
            } else if package_path.is_dir() {
                // For non-ROS packages, just check if it's a directory
                return Some(package_path);
            }
        }

        // Move up one directory
        if let Some(parent) = current_path.parent() {
            if parent == current_path {
                break;
            }
            current_path = parent.to_path_buf();
        } else {
            break;
        }
    }

    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_boolean_value() {
        assert!(get_boolean_value("true").unwrap());
        assert!(get_boolean_value("True").unwrap());
        assert!(get_boolean_value("1").unwrap());
        assert!(get_boolean_value("1.0").unwrap());

        assert!(!get_boolean_value("false").unwrap());
        assert!(!get_boolean_value("False").unwrap());
        assert!(!get_boolean_value("0").unwrap());
        assert!(!get_boolean_value("0.0").unwrap());

        assert!(get_boolean_value("invalid").is_err());
    }

    #[test]
    fn test_is_valid_name() {
        assert!(is_valid_name("foo"));
        assert!(is_valid_name("foo_bar"));
        assert!(is_valid_name("_foo"));
        assert!(is_valid_name("foo123"));

        assert!(!is_valid_name(""));
        assert!(!is_valid_name("123foo"));
        assert!(!is_valid_name("foo-bar"));
        assert!(!is_valid_name("foo.bar"));
    }

    #[test]
    fn test_tokenize() {
        let result = tokenize("a,b;c d", ",; ", true);
        assert_eq!(result, vec!["a", "b", "c", "d"]);

        let result = tokenize("a,,b", ",", false);
        assert_eq!(result, vec!["a", "", "b"]);

        let result = tokenize("a,,b", ",", true);
        assert_eq!(result, vec!["a", "b"]);
    }
}
