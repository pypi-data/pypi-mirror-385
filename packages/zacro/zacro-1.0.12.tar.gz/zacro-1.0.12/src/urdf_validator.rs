use crate::xml_element::{Element, XMLNode};
use petgraph::algo::{connected_components, is_cyclic_directed};
use petgraph::graph::UnGraph;
use petgraph::visit::Dfs;
use std::collections::{HashMap, HashSet};
use std::env;

#[derive(Debug, Clone, Copy)]
pub enum Language {
    English,
    Japanese,
}

impl Language {
    pub fn from_locale() -> Self {
        // Check LANG environment variable
        if let Ok(lang) = env::var("LANG") {
            if lang.starts_with("ja") {
                return Language::Japanese;
            }
        }

        // Check LC_ALL environment variable
        if let Ok(lang) = env::var("LC_ALL") {
            if lang.starts_with("ja") {
                return Language::Japanese;
            }
        }

        // Default to English
        Language::English
    }
}

pub struct Messages;

impl Messages {
    pub fn duplicate_name(lang: Language, name: &str) -> String {
        match lang {
            Language::English => format!("Name '{name}' is used for both a link and a joint"),
            Language::Japanese => {
                format!("名前 '{name}' がリンクとジョイントの両方で使用されています")
            }
        }
    }

    pub fn invalid_link_naming_conventions(lang: Language) -> &'static str {
        match lang {
            Language::English => "Invalid link naming conventions:",
            Language::Japanese => "無効なリンク命名規則:",
        }
    }

    pub fn invalid_joint_naming_conventions(lang: Language) -> &'static str {
        match lang {
            Language::English => "Invalid joint naming conventions:",
            Language::Japanese => "無効なジョイント命名規則:",
        }
    }

    pub fn affected_links(lang: Language) -> &'static str {
        match lang {
            Language::English => "Affected links:",
            Language::Japanese => "影響を受けるリンク:",
        }
    }

    pub fn affected_joints(lang: Language) -> &'static str {
        match lang {
            Language::English => "Affected joints:",
            Language::Japanese => "影響を受けるジョイント:",
        }
    }

    pub fn joints_with_zero_velocity(lang: Language) -> &'static str {
        match lang {
            Language::English => "Joints with zero velocity limits (may prevent motion):",
            Language::Japanese => "速度制限が0に設定されているジョイント:",
        }
    }

    pub fn joints_with_velocity_zero(lang: Language, joint_type: &str) -> String {
        match lang {
            Language::English => format!("{joint_type} joints with velocity=0.0:"),
            Language::Japanese => {
                let joint_type_ja = match joint_type {
                    "revolute" => "回転",
                    "continuous" => "連続回転",
                    "prismatic" => "直動",
                    _ => joint_type,
                };
                format!("{joint_type_ja}ジョイント({joint_type})の速度制限が0に設定されています")
            }
        }
    }

    pub fn velocity_suggestion(lang: Language) -> &'static str {
        match lang {
            Language::English => "Set velocity to typical value (e.g., velocity=\"3.14\" for ~180°/s or velocity=\"1.57\" for ~90°/s)",
            Language::Japanese => "速度を標準的な値に設定してください（例：velocity=\"3.14\"で約180°/s、velocity=\"1.57\"で約90°/s）",
        }
    }

    pub fn fixed_joint_note(lang: Language) -> &'static str {
        match lang {
            Language::English => {
                "Note: If you intend to keep the joint static, consider using type='fixed' instead"
            }
            Language::Japanese => {
                "※ ジョイントを静的に保つ場合は、type='fixed'の使用を検討してください"
            }
        }
    }

    pub fn warnings_header(lang: Language) -> &'static str {
        match lang {
            Language::English => "Warnings:",
            Language::Japanese => "警告:",
        }
    }

    pub fn validation_errors_header(lang: Language) -> &'static str {
        match lang {
            Language::English => "Validation Errors:",
            Language::Japanese => "検証エラー:",
        }
    }

    pub fn naming_issue_empty_name(lang: Language) -> &'static str {
        match lang {
            Language::English => "empty name",
            Language::Japanese => "空の名前",
        }
    }

    pub fn naming_issue_starts_with_number(lang: Language, first_char: char) -> String {
        match lang {
            Language::English => {
                format!("starts with number '{first_char}' (must start with letter)")
            }
            Language::Japanese => {
                format!("数字 '{first_char}' で始まっています（文字で始まる必要があります）")
            }
        }
    }

    pub fn naming_issue_starts_with_invalid_char(lang: Language, first_char: char) -> String {
        match lang {
            Language::English => {
                format!("starts with invalid character '{first_char}' (must start with letter)")
            }
            Language::Japanese => {
                format!("無効な文字 '{first_char}' で始まっています（文字で始まる必要があります）")
            }
        }
    }

    pub fn naming_issue_invalid_characters(lang: Language, chars_str: &str) -> String {
        match lang {
            Language::English => format!("contains invalid characters: {chars_str} (only letters, numbers, and underscores allowed)"),
            Language::Japanese => format!("無効な文字({chars_str})が含まれています（文字、数字、アンダースコアのみ使用可能）"),
        }
    }

    pub fn naming_issue_valid(lang: Language) -> &'static str {
        match lang {
            Language::English => "valid name",
            Language::Japanese => "有効な名前",
        }
    }

    pub fn velocity_suggestion_revolute(lang: Language) -> &'static str {
        match lang {
            Language::English => "Set velocity to typical value (e.g., velocity=\"3.14\" for ~180°/s or velocity=\"1.57\" for ~90°/s)",
            Language::Japanese => "推奨値: velocity=\"3.14\"（約180°/s）またはvelocity=\"1.57\"（約90°/s）",
        }
    }

    pub fn velocity_suggestion_continuous(lang: Language) -> &'static str {
        match lang {
            Language::English => "Set velocity for continuous rotation (e.g., velocity=\"6.28\" for 1 rev/s or velocity=\"3.14\" for 0.5 rev/s)",
            Language::Japanese => "推奨値: velocity=\"6.28\"（1回転/s）またはvelocity=\"3.14\"（0.5回転/s）",
        }
    }

    pub fn velocity_suggestion_prismatic(lang: Language) -> &'static str {
        match lang {
            Language::English => "Set velocity for linear motion (e.g., velocity=\"0.5\" for 0.5 m/s or velocity=\"0.1\" for slow motion)",
            Language::Japanese => "推奨値: velocity=\"0.5\"（0.5m/s）またはvelocity=\"0.1\"（低速運動）",
        }
    }

    pub fn velocity_suggestion_generic(lang: Language) -> &'static str {
        match lang {
            Language::English => {
                "Set velocity to a non-zero value appropriate for your application"
            }
            Language::Japanese => "推奨: アプリケーションに適した非ゼロの速度値を設定してください",
        }
    }
}

#[derive(Debug, Clone)]
pub struct Link {
    pub name: String,
    pub element: Element,
}

#[derive(Debug, Clone)]
pub struct Joint {
    pub name: String,
    pub parent: String,
    pub child: String,
    pub joint_type: String,
    pub element: Element,
}

#[derive(Debug)]
pub struct ValidationError {
    pub message: String,
}

impl std::fmt::Display for ValidationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for ValidationError {}

#[derive(Debug)]
pub struct ValidationResult {
    pub is_valid: bool,
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
    pub summary: ValidationSummary,
}

#[derive(Debug)]
pub struct ValidationSummary {
    pub links_count: usize,
    pub joints_count: usize,
    pub base_links: Vec<String>,
    pub end_links: Vec<String>,
    pub connected_components: usize,
}

pub struct URDFValidator {
    links: HashMap<String, Link>,
    joints: HashMap<String, Joint>,
    parent_child_map: HashMap<String, String>, // child -> parent
    child_parent_map: HashMap<String, Vec<String>>, // parent -> [children]
}

impl Default for URDFValidator {
    fn default() -> Self {
        Self::new()
    }
}

impl URDFValidator {
    pub fn new() -> Self {
        Self {
            links: HashMap::new(),
            joints: HashMap::new(),
            parent_child_map: HashMap::new(),
            child_parent_map: HashMap::new(),
        }
    }

    pub fn parse_urdf(&mut self, urdf_content: &str) -> Result<(), ValidationError> {
        let root = Element::parse(urdf_content.as_bytes()).map_err(|e| ValidationError {
            message: format!("Failed to parse URDF XML: {e}"),
        })?;

        if root.name != "robot" {
            return Err(ValidationError {
                message: format!("Expected 'robot' root element, got '{}'", root.name),
            });
        }

        // Clear previous data
        self.links.clear();
        self.joints.clear();
        self.parent_child_map.clear();
        self.child_parent_map.clear();

        // Extract links
        for child in &root.children {
            if let XMLNode::Element(element) = child {
                if element.name == "link" {
                    let name = element
                        .attributes
                        .get("name")
                        .ok_or_else(|| ValidationError {
                            message: "Found link without 'name' attribute".to_string(),
                        })?;

                    self.links.insert(
                        name.clone(),
                        Link {
                            name: name.clone(),
                            element: element.clone(),
                        },
                    );
                }
            }
        }

        // Extract joints
        for child in &root.children {
            if let XMLNode::Element(element) = child {
                if element.name == "joint" {
                    let joint_name =
                        element
                            .attributes
                            .get("name")
                            .ok_or_else(|| ValidationError {
                                message: "Found joint without 'name' attribute".to_string(),
                            })?;

                    let parent_elem = element
                        .children
                        .iter()
                        .find_map(|child| {
                            if let XMLNode::Element(elem) = child {
                                if elem.name == "parent" {
                                    Some(elem)
                                } else {
                                    None
                                }
                            } else {
                                None
                            }
                        })
                        .ok_or_else(|| ValidationError {
                            message: format!("Joint '{joint_name}' missing parent element"),
                        })?;

                    let child_elem = element
                        .children
                        .iter()
                        .find_map(|child| {
                            if let XMLNode::Element(elem) = child {
                                if elem.name == "child" {
                                    Some(elem)
                                } else {
                                    None
                                }
                            } else {
                                None
                            }
                        })
                        .ok_or_else(|| ValidationError {
                            message: format!("Joint '{joint_name}' missing child element"),
                        })?;

                    let parent_link =
                        parent_elem
                            .attributes
                            .get("link")
                            .ok_or_else(|| ValidationError {
                                message: format!(
                                    "Joint '{joint_name}' parent missing 'link' attribute"
                                ),
                            })?;

                    let child_link =
                        child_elem
                            .attributes
                            .get("link")
                            .ok_or_else(|| ValidationError {
                                message: format!(
                                    "Joint '{joint_name}' child missing 'link' attribute"
                                ),
                            })?;

                    let joint_type = element
                        .attributes
                        .get("type")
                        .unwrap_or(&"unknown".to_string())
                        .clone();

                    self.joints.insert(
                        joint_name.clone(),
                        Joint {
                            name: joint_name.clone(),
                            parent: parent_link.clone(),
                            child: child_link.clone(),
                            joint_type,
                            element: element.clone(),
                        },
                    );

                    // Build parent-child relationships
                    self.parent_child_map
                        .insert(child_link.clone(), parent_link.clone());
                    self.child_parent_map
                        .entry(parent_link.clone())
                        .or_default()
                        .push(child_link.clone());
                }
            }
        }

        Ok(())
    }

    pub fn find_base_links(&self) -> Vec<String> {
        self.links
            .keys()
            .filter(|link_name| !self.parent_child_map.contains_key(*link_name))
            .cloned()
            .collect()
    }

    pub fn find_end_links(&self) -> Vec<String> {
        self.links
            .keys()
            .filter(|link_name| !self.child_parent_map.contains_key(*link_name))
            .cloned()
            .collect()
    }

    pub fn find_connected_components(&self) -> Vec<Vec<String>> {
        let mut graph = UnGraph::new_undirected();
        let mut node_indices = HashMap::new();

        // Add all links as nodes
        for link_name in self.links.keys() {
            let index = graph.add_node(link_name.clone());
            node_indices.insert(link_name.clone(), index);
        }

        // Add edges for joints (undirected for connectivity check)
        for joint in self.joints.values() {
            if let (Some(&parent_idx), Some(&child_idx)) = (
                node_indices.get(&joint.parent),
                node_indices.get(&joint.child),
            ) {
                graph.add_edge(parent_idx, child_idx, ());
            }
        }

        let component_count = connected_components(&graph);
        let mut components = vec![Vec::new(); component_count];
        let mut visited = HashSet::new();

        for &node_idx in node_indices.values() {
            if visited.contains(&node_idx) {
                continue;
            }

            let mut component = Vec::new();
            let mut dfs = Dfs::new(&graph, node_idx);

            while let Some(nx) = dfs.next(&graph) {
                if !visited.contains(&nx) {
                    visited.insert(nx);
                    if let Some(node_weight) = graph.node_weight(nx) {
                        component.push(node_weight.clone());
                    }
                }
            }

            if !component.is_empty() {
                for comp in components.iter_mut() {
                    if comp.is_empty() {
                        *comp = component;
                        break;
                    }
                }
            }
        }

        components.into_iter().filter(|c| !c.is_empty()).collect()
    }

    pub fn detect_cycles(&self) -> Vec<Vec<String>> {
        use petgraph::Graph as DirectedGraph;

        let mut graph = DirectedGraph::new();
        let mut node_indices = HashMap::new();

        // Add all links as nodes
        for link_name in self.links.keys() {
            let index = graph.add_node(link_name.clone());
            node_indices.insert(link_name.clone(), index);
        }

        // Add directed edges for joints (parent -> child)
        for joint in self.joints.values() {
            if let (Some(&parent_idx), Some(&child_idx)) = (
                node_indices.get(&joint.parent),
                node_indices.get(&joint.child),
            ) {
                graph.add_edge(parent_idx, child_idx, ());
            }
        }

        // Use petgraph's cycle detection
        let mut cycles = Vec::new();
        if is_cyclic_directed(&graph) {
            // Simple cycle detection - for now just report that cycles exist
            // More sophisticated cycle finding would require additional implementation
            cycles.push(vec!["Cycle detected".to_string()]);
        }

        cycles
    }

    pub fn validate_link_references(&self) -> Vec<String> {
        let mut errors = Vec::new();

        for joint in self.joints.values() {
            if !self.links.contains_key(&joint.parent) {
                errors.push(format!(
                    "Joint '{}' references non-existent parent link '{}'",
                    joint.name, joint.parent
                ));
            }

            if !self.links.contains_key(&joint.child) {
                errors.push(format!(
                    "Joint '{}' references non-existent child link '{}'",
                    joint.name, joint.child
                ));
            }
        }

        errors
    }

    pub fn validate_duplicate_names(&self) -> Vec<String> {
        self.validate_duplicate_names_with_lang(Language::from_locale())
    }

    pub fn validate_duplicate_names_with_lang(&self, lang: Language) -> Vec<String> {
        let mut errors = Vec::new();

        // Check for duplicate names between links and joints
        for link_name in self.links.keys() {
            if self.joints.contains_key(link_name) {
                errors.push(Messages::duplicate_name(lang, link_name));
            }
        }

        errors
    }

    pub fn validate_naming_conventions(&self) -> Vec<String> {
        self.validate_naming_conventions_with_lang(Language::from_locale())
    }

    pub fn validate_naming_conventions_with_lang(&self, lang: Language) -> Vec<String> {
        let mut errors = Vec::new();
        let mut invalid_links: HashMap<String, Vec<String>> = HashMap::new();
        let mut invalid_joints: HashMap<String, Vec<String>> = HashMap::new();

        // Check link names and group by issue type
        for link_name in self.links.keys() {
            if !Self::is_valid_ros_name(link_name) {
                let issue = Self::get_naming_issue_with_lang(link_name, lang);
                invalid_links
                    .entry(issue)
                    .or_default()
                    .push(link_name.clone());
            }
        }

        // Check joint names and group by issue type
        for joint_name in self.joints.keys() {
            if !Self::is_valid_ros_name(joint_name) {
                let issue = Self::get_naming_issue_with_lang(joint_name, lang);
                invalid_joints
                    .entry(issue)
                    .or_default()
                    .push(joint_name.clone());
            }
        }

        // Format link errors grouped by issue
        if !invalid_links.is_empty() {
            let mut link_error = Messages::invalid_link_naming_conventions(lang).to_string();
            let mut issues: Vec<_> = invalid_links.keys().cloned().collect();
            issues.sort();

            for issue in issues {
                if let Some(links) = invalid_links.get(&issue) {
                    let mut sorted_links = links.clone();
                    sorted_links.sort();
                    link_error.push_str(&format!("\n  ◆ {issue}"));
                    link_error.push_str(&format!("\n    {}", Messages::affected_links(lang)));
                    for link in &sorted_links {
                        link_error.push_str(&format!("\n      - {link}"));
                    }
                }
            }
            errors.push(link_error);
        }

        // Format joint errors grouped by issue
        if !invalid_joints.is_empty() {
            let mut joint_error = Messages::invalid_joint_naming_conventions(lang).to_string();
            let mut issues: Vec<_> = invalid_joints.keys().cloned().collect();
            issues.sort();

            for issue in issues {
                if let Some(joints) = invalid_joints.get(&issue) {
                    let mut sorted_joints = joints.clone();
                    sorted_joints.sort();
                    joint_error.push_str(&format!("\n  ◆ {issue}"));
                    joint_error.push_str(&format!("\n    {}", Messages::affected_joints(lang)));
                    for joint in &sorted_joints {
                        joint_error.push_str(&format!("\n      - {joint}"));
                    }
                }
            }
            errors.push(joint_error);
        }

        errors
    }

    pub fn validate_joint_velocity_limits(&self) -> Vec<String> {
        self.validate_joint_velocity_limits_with_lang(Language::from_locale())
    }

    pub fn validate_joint_velocity_limits_with_lang(&self, lang: Language) -> Vec<String> {
        let mut warnings = Vec::new();
        let mut zero_velocity_by_type: HashMap<String, Vec<String>> = HashMap::new();

        for joint in self.joints.values() {
            // Skip fixed joints - they should not have velocity limits
            if joint.joint_type == "fixed" {
                continue;
            }

            // Look for limit element with velocity attribute
            for child in &joint.element.children {
                if let XMLNode::Element(elem) = child {
                    if elem.name == "limit" {
                        if let Some(velocity_str) = elem.attributes.get("velocity") {
                            if let Ok(velocity) = velocity_str.parse::<f64>() {
                                if velocity == 0.0 {
                                    zero_velocity_by_type
                                        .entry(joint.joint_type.clone())
                                        .or_default()
                                        .push(joint.name.clone());
                                }
                            }
                        }
                    }
                }
            }
        }

        if !zero_velocity_by_type.is_empty() {
            let mut warning = Messages::joints_with_zero_velocity(lang).to_string();

            // Sort joint types for consistent output
            let mut joint_types: Vec<_> = zero_velocity_by_type.keys().cloned().collect();
            joint_types.sort();

            for joint_type in joint_types {
                if let Some(joints) = zero_velocity_by_type.get(&joint_type) {
                    let mut sorted_joints = joints.clone();
                    sorted_joints.sort();

                    let suggestion = match joint_type.as_str() {
                        "revolute" => Messages::velocity_suggestion_revolute(lang),
                        "continuous" => Messages::velocity_suggestion_continuous(lang),
                        "prismatic" => Messages::velocity_suggestion_prismatic(lang),
                        _ => Messages::velocity_suggestion_generic(lang),
                    };

                    warning.push_str(&format!(
                        "\n  ◆ {}",
                        Messages::joints_with_velocity_zero(lang, &joint_type)
                    ));
                    warning.push_str(&format!("\n    {}", Messages::affected_joints(lang)));
                    for joint in &sorted_joints {
                        warning.push_str(&format!("\n      - {joint}"));
                    }
                    warning.push_str(&format!("\n    → {suggestion}"));
                }
            }
            warning.push_str(&format!("\n  {}", Messages::fixed_joint_note(lang)));
            warnings.push(warning);
        }

        warnings
    }

    fn is_valid_ros_name(name: &str) -> bool {
        if name.is_empty() {
            return false;
        }

        // Must start with a letter
        let first_char = name.chars().next().unwrap();
        if !first_char.is_ascii_alphabetic() {
            return false;
        }

        // Must contain only alphanumeric characters and underscores
        name.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
    }

    fn get_naming_issue_with_lang(name: &str, lang: Language) -> String {
        if name.is_empty() {
            return Messages::naming_issue_empty_name(lang).to_string();
        }

        let first_char = name.chars().next().unwrap();
        if !first_char.is_ascii_alphabetic() {
            if first_char.is_ascii_digit() {
                return Messages::naming_issue_starts_with_number(lang, first_char);
            } else {
                return Messages::naming_issue_starts_with_invalid_char(lang, first_char);
            }
        }

        let mut invalid_chars = Vec::new();
        for c in name.chars() {
            if !c.is_ascii_alphanumeric() && c != '_' && !invalid_chars.contains(&c) {
                invalid_chars.push(c);
            }
        }

        if !invalid_chars.is_empty() {
            let chars_str = invalid_chars
                .iter()
                .map(|c| format!("'{c}'"))
                .collect::<Vec<_>>()
                .join(", ");
            return Messages::naming_issue_invalid_characters(lang, &chars_str);
        }

        Messages::naming_issue_valid(lang).to_string()
    }

    pub fn validate(
        &mut self,
        urdf_content: &str,
        verbose: bool,
    ) -> Result<ValidationResult, ValidationError> {
        self.parse_urdf(urdf_content)?;

        let mut errors = Vec::new();
        let mut warnings = Vec::new();

        // Check 1: Validate link references
        let link_errors = self.validate_link_references();
        errors.extend(link_errors);

        // Check 2: Validate duplicate names
        let duplicate_errors = self.validate_duplicate_names();
        errors.extend(duplicate_errors);

        // Check 3: Validate naming conventions
        let naming_errors = self.validate_naming_conventions();
        errors.extend(naming_errors);

        // Check 4: Validate joint velocity limits (warnings)
        let velocity_warnings = self.validate_joint_velocity_limits();
        warnings.extend(velocity_warnings);

        // Check 5: Find connected components
        let components = self.find_connected_components();
        if components.len() > 1 {
            let mut error_msg = format!(
                "Links are not all connected. Found {} disconnected components:",
                components.len()
            );
            for (i, component) in components.iter().enumerate() {
                let mut sorted_component = component.clone();
                sorted_component.sort();
                error_msg.push_str(&format!(
                    "\n  Component {}: {}",
                    i + 1,
                    sorted_component.join(", ")
                ));
            }
            errors.push(error_msg);
        }

        // Check 6: Detect cycles
        let cycles = self.detect_cycles();
        if !cycles.is_empty() {
            for cycle in cycles {
                if cycle.len() == 1 && cycle[0] == "Cycle detected" {
                    errors.push("Detected cycle in link graph".to_string());
                } else {
                    let cycle_str = cycle.join(" -> ");
                    errors.push(format!("Detected cycle in link graph: {cycle_str}"));
                }
            }
        }

        // Check 7: Base link validation
        let base_links = self.find_base_links();
        if base_links.is_empty() {
            errors.push(
                "No base link found (all links have parents - this creates a cycle)".to_string(),
            );
        } else if base_links.len() > 1 {
            let base_links_str = base_links
                .iter()
                .map(|link| format!("'{link}'"))
                .collect::<Vec<_>>()
                .join(", ");
            errors.push(format!(
                "Multiple base links found: {base_links_str}. A valid URDF should have exactly one base link."
            ));
        }

        // Check 8: End links (warnings only)
        let end_links = self.find_end_links();
        if end_links.is_empty() {
            warnings.push("No end links found (all links have children)".to_string());
        }

        let summary = ValidationSummary {
            links_count: self.links.len(),
            joints_count: self.joints.len(),
            base_links: base_links.clone(),
            end_links: end_links.clone(),
            connected_components: components.len(),
        };

        // Print validation summary if verbose
        if verbose {
            eprintln!("URDF Validation Summary:");
            eprintln!("  Links: {}", summary.links_count);
            eprintln!("  Joints: {}", summary.joints_count);
            eprintln!(
                "  Base links: {} ({})",
                base_links.len(),
                if base_links.is_empty() {
                    "None".to_string()
                } else {
                    base_links.join(", ")
                }
            );
            eprintln!(
                "  End links: {} ({})",
                end_links.len(),
                if end_links.is_empty() {
                    "None".to_string()
                } else {
                    end_links.join(", ")
                }
            );
            eprintln!("  Connected components: {}", components.len());

            let lang = Language::from_locale();

            if !warnings.is_empty() {
                eprintln!("\x1b[33m{}:\x1b[0m", Messages::warnings_header(lang));
                for warning in &warnings {
                    // Print multi-line warnings with proper indentation and orange color
                    if warning.contains('\n') {
                        let lines: Vec<&str> = warning.lines().collect();
                        eprintln!("\x1b[33m  - {}\x1b[0m", lines[0]);
                        for line in &lines[1..] {
                            eprintln!("\x1b[33m    {line}\x1b[0m");
                        }
                    } else {
                        eprintln!("\x1b[33m  - {warning}\x1b[0m");
                    }
                }
            }

            if !errors.is_empty() {
                eprintln!(
                    "\x1b[31m{}:\x1b[0m",
                    Messages::validation_errors_header(lang)
                );
                for error in &errors {
                    // Print multi-line errors with proper indentation and red color
                    if error.contains('\n') {
                        let lines: Vec<&str> = error.lines().collect();
                        eprintln!("\x1b[31m  - {}\x1b[0m", lines[0]);
                        for line in &lines[1..] {
                            eprintln!("\x1b[31m    {line}\x1b[0m");
                        }
                    } else {
                        eprintln!("\x1b[31m  - {error}\x1b[0m");
                    }
                }
            } else {
                let success_msg = match lang {
                    Language::English => "✓ All validation checks passed!",
                    Language::Japanese => "✓ 全ての検証チェックに合格しました！",
                };
                eprintln!("\x1b[32m{success_msg}\x1b[0m");
            }
        }

        Ok(ValidationResult {
            is_valid: errors.is_empty(),
            errors,
            warnings,
            summary,
        })
    }
}

impl URDFValidator {
    pub fn print_link_tree(&self) -> String {
        let base_links = self.find_base_links();

        if base_links.is_empty() {
            return "No base links found - cannot build tree structure".to_string();
        }

        let mut output = String::new();
        output.push_str("URDF Link Tree Structure:\n");

        for (i, base_link) in base_links.iter().enumerate() {
            if i > 0 {
                output.push('\n');
            }
            self.print_subtree(base_link, "", true, &mut output);
        }

        output
    }

    fn print_subtree(&self, link_name: &str, prefix: &str, is_last: bool, output: &mut String) {
        // Print current link
        let branch = if is_last { "└── " } else { "├── " };
        output.push_str(&format!("{prefix}{branch}{link_name}\n"));

        // Find children of this link
        let children = self
            .child_parent_map
            .get(link_name)
            .cloned()
            .unwrap_or_default();

        // Print children
        for (i, child) in children.iter().enumerate() {
            let is_last_child = i == children.len() - 1;
            let new_prefix = if is_last {
                format!("{prefix}    ")
            } else {
                format!("{prefix}│   ")
            };

            self.print_subtree(child, &new_prefix, is_last_child, output);
        }
    }
}

pub fn validate_urdf(
    urdf_content: &str,
    verbose: bool,
) -> Result<ValidationResult, ValidationError> {
    let mut validator = URDFValidator::new();
    validator.validate(urdf_content, verbose)
}

pub fn print_urdf_tree(urdf_content: &str) -> Result<String, ValidationError> {
    let mut validator = URDFValidator::new();
    validator.parse_urdf(urdf_content)?;
    Ok(validator.print_link_tree())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_duplicate_names() {
        let urdf_content = r#"<?xml version="1.0"?>
<robot name="test_robot">
  <link name="base"/>
  <link name="duplicate"/>
  <joint name="duplicate" type="fixed">
    <parent link="base"/>
    <child link="duplicate"/>
  </joint>
</robot>"#;

        let mut validator = URDFValidator::new();
        validator.parse_urdf(urdf_content).unwrap();

        let duplicate_errors = validator.validate_duplicate_names();
        assert_eq!(duplicate_errors.len(), 1);
        assert!(
            duplicate_errors[0].contains("Name 'duplicate' is used for both a link and a joint")
        );
    }

    #[test]
    fn test_validate_naming_conventions() {
        let urdf_content = r#"<?xml version="1.0"?>
<robot name="test_robot">
  <link name="valid_link"/>
  <link name="1_invalid_link"/>
  <link name="link-with-hyphen"/>
  <joint name="valid_joint" type="fixed">
    <parent link="valid_link"/>
    <child link="1_invalid_link"/>
  </joint>
  <joint name="joint with space" type="fixed">
    <parent link="1_invalid_link"/>
    <child link="link-with-hyphen"/>
  </joint>
</robot>"#;

        let mut validator = URDFValidator::new();
        validator.parse_urdf(urdf_content).unwrap();

        let naming_errors = validator.validate_naming_conventions();
        assert_eq!(naming_errors.len(), 2); // One for links, one for joints

        let error_string = naming_errors.join(" ");
        assert!(error_string.contains("1_invalid_link"));
        assert!(error_string.contains("link-with-hyphen"));
        assert!(error_string.contains("joint with space"));
        assert!(error_string.contains("Affected"));
    }

    #[test]
    fn test_no_duplicate_names() {
        let urdf_content = r#"<?xml version="1.0"?>
<robot name="test_robot">
  <link name="base"/>
  <link name="link1"/>
  <joint name="joint1" type="fixed">
    <parent link="base"/>
    <child link="link1"/>
  </joint>
</robot>"#;

        let mut validator = URDFValidator::new();
        validator.parse_urdf(urdf_content).unwrap();

        let duplicate_errors = validator.validate_duplicate_names();
        assert_eq!(duplicate_errors.len(), 0);
    }

    #[test]
    fn test_valid_naming_conventions() {
        let urdf_content = r#"<?xml version="1.0"?>
<robot name="test_robot">
  <link name="base_link"/>
  <link name="Link_123"/>
  <link name="valid_name_with_underscores"/>
  <joint name="joint_1" type="fixed">
    <parent link="base_link"/>
    <child link="Link_123"/>
  </joint>
</robot>"#;

        let mut validator = URDFValidator::new();
        validator.parse_urdf(urdf_content).unwrap();

        let naming_errors = validator.validate_naming_conventions();
        assert_eq!(naming_errors.len(), 0);
    }

    #[test]
    fn test_validate_joint_velocity_limits() {
        let urdf_content = r#"<?xml version="1.0"?>
<robot name="test_robot">
  <link name="base"/>
  <link name="link1"/>
  <link name="link2"/>
  <!-- Fixed joint with zero velocity should NOT trigger warning -->
  <joint name="fixed_joint" type="fixed">
    <parent link="base"/>
    <child link="link1"/>
    <limit velocity="0.0" effort="100.0"/>
  </joint>
  <!-- Revolute joint with zero velocity should trigger warning -->
  <joint name="revolute_zero" type="revolute">
    <parent link="link1"/>
    <child link="link2"/>
    <limit velocity="0.0" effort="100.0"/>
    <axis xyz="0 0 1"/>
  </joint>
</robot>"#;

        let mut validator = URDFValidator::new();
        validator.parse_urdf(urdf_content).unwrap();

        let velocity_warnings = validator.validate_joint_velocity_limits();
        assert_eq!(velocity_warnings.len(), 1);

        let warning_string = velocity_warnings[0].clone();
        assert!(warning_string.contains("revolute_zero"));
        assert!(warning_string.contains("revolute joints with velocity=0.0"));
        assert!(warning_string.contains("Affected joints"));
        assert!(!warning_string.contains("fixed_joint")); // Fixed joints should not be included
    }

    #[test]
    fn test_no_velocity_warnings() {
        let urdf_content = r#"<?xml version="1.0"?>
<robot name="test_robot">
  <link name="base"/>
  <link name="link1"/>
  <!-- Normal joint with non-zero velocity -->
  <joint name="normal_joint" type="revolute">
    <parent link="base"/>
    <child link="link1"/>
    <limit velocity="1.5" effort="100.0"/>
    <axis xyz="0 0 1"/>
  </joint>
</robot>"#;

        let mut validator = URDFValidator::new();
        validator.parse_urdf(urdf_content).unwrap();

        let velocity_warnings = validator.validate_joint_velocity_limits();
        assert_eq!(velocity_warnings.len(), 0);
    }
}
