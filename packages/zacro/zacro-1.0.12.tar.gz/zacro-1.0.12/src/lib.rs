// Rust implementation of xacro (XML macro language)

pub mod error;
pub mod eval;
pub mod lexer;
pub mod macros;
pub mod parser;
pub mod symbols;
pub mod urdf_validator;
pub mod utils;
pub mod xml_element;

#[cfg(feature = "python")]
pub mod python;

use crate::xml_element::{Element, XMLNode};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

use crate::error::{Result, XacroError};
use crate::symbols::SymbolTable;
use crate::urdf_validator::validate_urdf;

pub struct XacroProcessor {
    filestack: Vec<PathBuf>,
    macrostack: Vec<String>,
    all_includes: Vec<PathBuf>,
    #[allow(dead_code)]
    verbosity: u8,
    symbols: SymbolTable,
    macros: macros::MacroTable,
    format_output: bool,
    remove_root_link: Option<String>,
    validate_urdf: bool,
    validation_verbose: bool,
    // Cache for macro expansion results: (macro_name, params_string) -> expanded nodes
    // params_string is a sorted string representation of parameters for efficient caching
    macro_cache: HashMap<(String, String), Vec<XMLNode>>,
}

impl XacroProcessor {
    pub fn new(verbosity: u8) -> Self {
        Self {
            filestack: Vec::new(),
            macrostack: Vec::new(),
            all_includes: Vec::new(),
            verbosity,
            symbols: SymbolTable::new(),
            macros: macros::MacroTable::new(),
            format_output: true, // Format output by default
            remove_root_link: None,
            validate_urdf: true, // Validation enabled by default
            validation_verbose: true,
            macro_cache: HashMap::new(),
        }
    }

    pub fn set_format_output(&mut self, format: bool) {
        self.format_output = format;
    }

    pub fn set_remove_root_link(&mut self, link_name: Option<String>) {
        self.remove_root_link = link_name;
    }

    pub fn set_validate_urdf(&mut self, validate: bool) {
        self.validate_urdf = validate;
    }

    pub fn set_validation_verbose(&mut self, verbose: bool) {
        self.validation_verbose = verbose;
    }

    pub fn disable_urdf_validation(&mut self) {
        self.validate_urdf = false;
    }

    pub fn init_stacks(&mut self, file: Option<PathBuf>) {
        self.filestack.clear();
        if let Some(f) = file {
            self.filestack.push(f);
        }
        self.macrostack.clear();
    }

    pub fn process_file(
        &mut self,
        input_file: &Path,
        mappings: Option<HashMap<String, String>>,
    ) -> Result<Element> {
        self.init_stacks(Some(input_file.to_path_buf()));

        // Set substitution args
        if let Some(mappings) = mappings {
            self.symbols.set_substitution_args(mappings);
        }

        // Parse the document
        let parse_start = std::time::Instant::now();
        let content = std::fs::read_to_string(input_file).map_err(XacroError::Io)?;
        let mut doc = Element::parse(content.as_bytes())?;
        let parse_elapsed = parse_start.elapsed();

        // Process the document
        let process_start = std::time::Instant::now();
        self.process_doc(&mut doc)?;
        let process_elapsed = process_start.elapsed();

        if self.verbosity > 1 {
            eprintln!("[TIMING] XML parse: {:?}", parse_elapsed);
            eprintln!("[TIMING] Processing: {:?}", process_elapsed);
        }

        // Remove root link if requested (after all processing is complete)
        if self.remove_root_link.is_some() {
            self.remove_root_link_from_doc(&mut doc);
        }

        // Validate URDF if requested
        if self.validate_urdf {
            let urdf_string =
                self.element_to_string_with_source(&doc, Some(&input_file.display().to_string()));
            match validate_urdf(&urdf_string, self.validation_verbose) {
                Ok(validation_result) => {
                    if !validation_result.is_valid {
                        let error_msg = format!(
                            "\x1b[31mURDF validation failed with {} error(s). See details above.\x1b[0m",
                            validation_result.errors.len()
                        );
                        return Err(XacroError::Parse(error_msg));
                    }
                }
                Err(e) => {
                    return Err(XacroError::Parse(format!("URDF validation error: {e}")));
                }
            }
        }

        Ok(doc)
    }

    pub fn process_string(
        &mut self,
        xml_string: &str,
        mappings: Option<HashMap<String, String>>,
    ) -> Result<Element> {
        self.init_stacks(None);

        // Set substitution args
        if let Some(mappings) = mappings {
            self.symbols.set_substitution_args(mappings);
        }

        // Parse the string
        let mut doc = Element::parse(xml_string.as_bytes())?;

        // Process the document
        self.process_doc(&mut doc)?;

        // Remove root link if requested (after all processing is complete)
        if self.remove_root_link.is_some() {
            self.remove_root_link_from_doc(&mut doc);
        }

        // Validate URDF if requested
        if self.validate_urdf {
            let urdf_string = self.element_to_string(&doc);
            match validate_urdf(&urdf_string, self.validation_verbose) {
                Ok(validation_result) => {
                    if !validation_result.is_valid {
                        let error_msg = format!(
                            "\x1b[31mURDF validation failed with {} error(s). See details above.\x1b[0m",
                            validation_result.errors.len()
                        );
                        return Err(XacroError::Parse(error_msg));
                    }
                }
                Err(e) => {
                    return Err(XacroError::Parse(format!("URDF validation error: {e}")));
                }
            }
        }

        Ok(doc)
    }

    fn process_doc(&mut self, doc: &mut Element) -> Result<()> {
        // Apply xacro:targetNamespace as global xmlns (if defined)
        if let Some(target_ns) = doc.attributes.remove("xacro:targetNamespace") {
            doc.attributes.insert("xmlns".to_string(), target_ns);
        }

        // Process all elements
        self.eval_all(doc)?;

        Ok(())
    }

    fn eval_all(&mut self, element: &mut Element) -> Result<()> {
        // Single-pass processing:
        // Process includes, properties, macros, and expand macro calls in one traversal
        let start = std::time::Instant::now();
        self.process_element(element, false)?;
        let elapsed = start.elapsed();

        if self.verbosity > 1 {
            eprintln!("[TIMING] Single-pass processing: {:?}", elapsed);
        }

        Ok(())
    }

    fn process_element(&mut self, element: &mut Element, inside_macro: bool) -> Result<()> {
        // Take ownership of old children and build new Vec
        let old_children = std::mem::take(&mut element.children);
        let mut new_children = Vec::with_capacity(old_children.len());

        for mut node in old_children {
            match &mut node {
                XMLNode::Element(child) => {
                    // Use more flexible matching for XML elements
                    let element_local_name = if child.name.contains('}') {
                        child.name.split('}').next_back().unwrap_or(&child.name)
                    } else if child.name.contains(':') {
                        child.name.split(':').next_back().unwrap_or(&child.name)
                    } else {
                        &child.name
                    };

                    match element_local_name {
                        // Handle include elements - process immediately and add children
                        "include" => {
                            // process_include already calls process_element internally
                            // so the returned children are already fully processed
                            let included_children = self.process_include(child)?;
                            new_children.extend(included_children);
                        }
                        // Handle property definitions - collect and remove
                        "property" => {
                            self.grab_property(child)?;
                            // Don't add to new_children (removed)
                        }
                        // Handle arg definitions - collect and remove
                        "arg" => {
                            self.grab_arg(child)?;
                            // Don't add to new_children (removed)
                        }
                        // Handle macro definitions - collect and remove
                        "macro" => {
                            self.grab_macro(child)?;
                            // Don't add to new_children (removed)
                        }
                        // Handle insert_block
                        "insert_block" => {
                            // insert_block should have been processed - skip it
                        }
                        // Handle if/unless - evaluate conditionals
                        "if" if !inside_macro => {
                            let condition = child.attributes.get("value").ok_or_else(|| {
                                XacroError::Parse("if missing 'value' attribute".into())
                            })?;
                            let evaluated = self.eval_text(condition)?;
                            let keep = utils::get_boolean_value(&evaluated)?;
                            if keep {
                                // Process if's children and add to new_children
                                let mut if_children = std::mem::take(&mut child.children);
                                for if_node in if_children.iter_mut() {
                                    if let XMLNode::Element(elem) = if_node {
                                        self.process_element(elem, inside_macro)?;
                                    }
                                }
                                new_children.extend(if_children);
                            }
                        }
                        "unless" if !inside_macro => {
                            let condition = child.attributes.get("value").ok_or_else(|| {
                                XacroError::Parse("unless missing 'value' attribute".into())
                            })?;
                            let keep = match self.eval_text(condition) {
                                Ok(evaluated) => !utils::get_boolean_value(&evaluated)?,
                                Err(XacroError::UndefinedSymbol(_)) => true,
                                Err(e) => return Err(e),
                            };
                            if keep {
                                // Process unless's children and add to new_children
                                let mut unless_children = std::mem::take(&mut child.children);
                                for unless_node in unless_children.iter_mut() {
                                    if let XMLNode::Element(elem) = unless_node {
                                        self.process_element(elem, inside_macro)?;
                                    }
                                }
                                new_children.extend(unless_children);
                            }
                        }
                        // Skip if/unless inside macro definitions
                        "if" | "unless" if inside_macro => {
                            // Don't evaluate, just process children to handle nested definitions
                            self.process_element(child, true)?;
                            new_children.push(node);
                        }
                        // Check if it's a macro call
                        _ => {
                            let is_builtin_xacro = matches!(
                                element_local_name,
                                "include"
                                    | "property"
                                    | "macro"
                                    | "arg"
                                    | "if"
                                    | "unless"
                                    | "insert_block"
                            );

                            if !is_builtin_xacro
                                && !inside_macro
                                && self.macros.contains(element_local_name)
                            {
                                // Before expanding the macro, process any includes in its children
                                // This ensures all macro definitions are available before expansion
                                let mut i = 0;
                                while i < child.children.len() {
                                    if let XMLNode::Element(child_elem) = &mut child.children[i] {
                                        let child_local_name = if child_elem.name.contains('}') {
                                            child_elem
                                                .name
                                                .split('}')
                                                .next_back()
                                                .unwrap_or(&child_elem.name)
                                        } else if child_elem.name.contains(':') {
                                            child_elem
                                                .name
                                                .split(':')
                                                .next_back()
                                                .unwrap_or(&child_elem.name)
                                        } else {
                                            &child_elem.name
                                        };

                                        if child_local_name == "include" {
                                            let included_children =
                                                self.process_include(child_elem)?;
                                            child.children.splice(i..=i, included_children);
                                            continue;
                                        }
                                    }
                                    i += 1;
                                }

                                // Macro call - expand and add result nodes
                                // handle_macro_call already calls eval_all internally,
                                // so the returned nodes are already fully processed
                                let expanded_nodes = self.handle_macro_call(child)?;
                                new_children.extend(expanded_nodes);
                            } else {
                                // Regular element - process recursively
                                self.process_element(child, inside_macro)?;
                                new_children.push(node);
                            }
                        }
                    }
                }
                XMLNode::Text(text) => {
                    if !inside_macro {
                        *text = self.eval_text(text)?;
                    }
                    new_children.push(node);
                }
                XMLNode::Comment(_) => {
                    // Keep comments as-is
                    new_children.push(node);
                }
            }
        }

        // Replace with new children
        element.children = new_children;

        // Evaluate attributes after processing children (skip if inside macro)
        if !inside_macro {
            let mut attributes_to_remove = Vec::new();
            for (key, value) in element.attributes.iter_mut() {
                let evaluated = self.eval_text(value)?;
                // Handle special cases for different element types
                if element.name == "origin"
                    && key == "rpy"
                    && (evaluated == "None" || evaluated.is_empty())
                {
                    // For origin elements, remove rpy attribute if it evaluates to None or empty
                    // The URDF parser will default to [0, 0, 0] for missing rpy
                    attributes_to_remove.push(key.clone());
                } else if element.name == "material"
                    && key == "name"
                    && (evaluated == "None" || evaluated.is_empty())
                {
                    // For material elements, name is required - provide a default if missing
                    *value = "default_material".to_string();
                } else if evaluated == "None" || evaluated.is_empty() {
                    // For other cases, remove the attribute if it evaluated to None or empty
                    attributes_to_remove.push(key.clone());
                } else {
                    *value = evaluated;
                }
            }

            // Remove attributes that evaluated to None or empty
            for key in attributes_to_remove {
                element.attributes.remove(&key);
            }
        }

        Ok(())
    }

    fn eval_text(&self, text: &str) -> Result<String> {
        let current_file = self.filestack.last().map(|p| p.as_path());
        eval::eval_text(text, &self.symbols, current_file)
    }

    // Helper function to create a cache key string from parameters
    // Converts parameters to a sorted string representation for efficient caching
    fn params_to_cache_key(params: &HashMap<String, String>) -> String {
        if params.is_empty() {
            return String::new();
        }

        // Sort parameters by key for deterministic cache keys
        let mut sorted_params: Vec<_> = params.iter().collect();
        sorted_params.sort_by(|a, b| a.0.cmp(b.0));

        // Build string representation
        sorted_params
            .iter()
            .map(|(k, v)| format!("{}={}", k, v))
            .collect::<Vec<_>>()
            .join(";")
    }

    fn process_include(&mut self, element: &Element) -> Result<Vec<XMLNode>> {
        let filename = element
            .attributes
            .get("filename")
            .ok_or_else(|| XacroError::Parse("include missing 'filename' attribute".into()))?;

        // Evaluate the filename to handle $(find package_name) expressions
        let evaluated_filename = self.eval_text(filename)?;

        // Resolve the file path
        let current_file = self.filestack.last().map(|p| p.as_path());
        let include_path = if std::path::Path::new(&evaluated_filename).is_absolute() {
            std::path::PathBuf::from(evaluated_filename)
        } else if let Some(current) = current_file {
            let parent = current
                .parent()
                .unwrap_or_else(|| std::path::Path::new("."));
            parent.join(evaluated_filename)
        } else {
            std::path::PathBuf::from(evaluated_filename)
        };

        // Check if file exists
        if !include_path.exists() {
            return Err(XacroError::Io(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("Include file not found: {}", include_path.display()),
            )));
        }

        // Parse the included file
        let mut included_doc = parser::parse_file(&include_path)?;

        // Add to filestack for proper context
        self.filestack.push(include_path.clone());

        // Collect definitions (macros, properties, args) from the included file
        // Do NOT expand macro calls - only collect definitions
        self.collect_definitions(&mut included_doc)?;

        // Remove from filestack
        self.filestack.pop();

        // Track included file
        self.all_includes.push(include_path);

        // Return the children of the processed document
        // Note: macro definitions will have been removed, only non-macro content remains
        Ok(included_doc.children)
    }

    // Collect macro definitions, properties, and args without expanding macro calls
    fn collect_definitions(&mut self, element: &mut Element) -> Result<()> {
        let mut i = 0;
        while i < element.children.len() {
            if let XMLNode::Element(child) = &mut element.children[i] {
                let element_local_name = if child.name.contains('}') {
                    child.name.split('}').next_back().unwrap_or(&child.name)
                } else if child.name.contains(':') {
                    child.name.split(':').next_back().unwrap_or(&child.name)
                } else {
                    &child.name
                };

                match element_local_name {
                    // Handle nested includes
                    "include" => {
                        let included_children = self.process_include(child)?;
                        element.children.splice(i..=i, included_children);
                        continue;
                    }
                    // Collect property definitions
                    "property" => {
                        self.grab_property(child)?;
                        element.children.remove(i);
                        continue;
                    }
                    // Collect arg definitions
                    "arg" => {
                        self.grab_arg(child)?;
                        element.children.remove(i);
                        continue;
                    }
                    // Collect macro definitions
                    "macro" => {
                        self.grab_macro(child)?;
                        element.children.remove(i);
                        continue;
                    }
                    _ => {
                        // Recursively collect definitions from child elements
                        // but do NOT expand macro calls
                        self.collect_definitions(child)?;
                    }
                }
            }
            i += 1;
        }
        Ok(())
    }

    fn grab_property(&mut self, element: &Element) -> Result<()> {
        let name = element
            .attributes
            .get("name")
            .ok_or_else(|| XacroError::Parse("property missing 'name' attribute".into()))?;

        let value = element.attributes.get("value");
        let default = element.attributes.get("default");

        if let Some(value) = value {
            // Evaluate the value before storing
            let evaluated_value = self.eval_text(value)?;
            self.symbols.set(name.clone(), evaluated_value);
        } else if let Some(default) = default {
            if !self.symbols.contains(name) {
                // Evaluate the default value before storing
                let evaluated_default = self.eval_text(default)?;
                self.symbols.set(name.clone(), evaluated_default);
            }
        }

        Ok(())
    }

    fn grab_macro(&mut self, element: &Element) -> Result<()> {
        let name = element
            .attributes
            .get("name")
            .ok_or_else(|| XacroError::Parse("macro missing 'name' attribute".into()))?;

        let params = element
            .attributes
            .get("params")
            .map(|s| s.as_str())
            .unwrap_or("");

        // Clone the element once and prepare macro body
        let mut macro_body = element.clone();

        // Remove the name and params attributes from the macro body
        macro_body.attributes.remove("name");
        macro_body.attributes.remove("params");

        // Move macro_body instead of cloning again
        let macro_def = macros::Macro::new(name.clone(), params, macro_body);

        self.macros.insert(name.clone(), macro_def);

        Ok(())
    }

    fn grab_arg(&mut self, element: &Element) -> Result<()> {
        let name = element
            .attributes
            .get("name")
            .ok_or_else(|| XacroError::Parse("arg missing 'name' attribute".into()))?;

        let default = element.attributes.get("default");

        // Check if this argument is overridden by command line mappings
        if let Some(override_value) = self.symbols.get_substitution_arg(name) {
            // Use the command line override value
            self.symbols.set(name.clone(), override_value.clone());
        } else {
            // Set argument to default value if provided and not already set
            if let Some(default_value) = default {
                if !self.symbols.contains(name) {
                    // Evaluate the default value before storing
                    let evaluated_default = self.eval_text(default_value)?;
                    self.symbols.set(name.clone(), evaluated_default);
                }
            }
        }

        Ok(())
    }

    #[allow(dead_code)]
    fn process_conditional(&mut self, element: &mut Element) -> Result<bool> {
        let value = element
            .attributes
            .get("value")
            .ok_or_else(|| XacroError::Parse("conditional missing 'value' attribute".into()))?;

        let evaluated = self.eval_text(value)?;
        let keep = utils::get_boolean_value(&evaluated)?;

        let keep = if element.name == "xacro:unless" {
            !keep
        } else {
            keep
        };

        if keep {
            self.eval_all(element)?;
        }

        Ok(keep)
    }

    fn handle_macro_call(&mut self, call_element: &Element) -> Result<Vec<XMLNode>> {
        // Extract macro name using same logic as in eval_all
        let macro_name = if call_element.name.contains('}') {
            call_element
                .name
                .split('}')
                .next_back()
                .unwrap_or(&call_element.name)
        } else if call_element.name.contains(':') {
            call_element
                .name
                .split(':')
                .next_back()
                .unwrap_or(&call_element.name)
        } else {
            &call_element.name
        };

        if let Some(macro_def) = self.macros.get(macro_name).cloned() {
            // Expand the macro and return the result nodes directly
            self.expand_macro(&macro_def, call_element)
        } else {
            Err(XacroError::Parse(format!(
                "Unknown macro: {}",
                call_element.name
            )))
        }
    }

    fn expand_macro(
        &mut self,
        macro_def: &macros::Macro,
        call_element: &Element,
    ) -> Result<Vec<XMLNode>> {
        // Build parameter mapping from call attributes
        let mut param_values = HashMap::new();

        // Add default values first
        for (param, default) in &macro_def.defaults {
            param_values.insert(param.clone(), default.clone());
        }

        // Override with call attributes
        for (attr_name, attr_value) in &call_element.attributes {
            if macro_def.has_param(attr_name) {
                // Don't evaluate yet - just store the raw value
                // It will be evaluated after substitution in the macro body
                param_values.insert(attr_name.clone(), attr_value.clone());
            }
        }

        // Create cache key from macro name and parameters (using efficient string representation)
        let cache_key = (
            macro_def.name.clone(),
            Self::params_to_cache_key(&param_values),
        );

        // Check cache before expensive cloning and processing
        if let Some(cached_result) = self.macro_cache.get(&cache_key) {
            return Ok(cached_result.clone());
        }

        // Clone macro body and substitute parameters
        let clone_start = std::time::Instant::now();
        let mut expanded_body = macro_def.body.clone();
        let clone_elapsed = clone_start.elapsed();

        // Save current symbol table state to restore after macro expansion
        let saved_symbols = param_values
            .keys()
            .filter_map(|key| {
                self.symbols
                    .get(key)
                    .map(|value| (key.clone(), value.clone()))
            })
            .collect::<HashMap<String, String>>();

        // Evaluate parameter values before setting them in the symbol table
        // This allows nested macro calls to work properly
        let mut evaluated_params = HashMap::new();
        for (param, value) in &param_values {
            // Try to evaluate the parameter value (e.g., "${reflect}" -> "-1", "${(729.0/25.0)*(22.0/16.0)}" -> "40.15")
            let evaluated = match self.eval_text(value) {
                Ok(v) => v,
                Err(_) => {
                    // If evaluation fails, it might be a reference to an undefined parameter
                    // In that case, keep the raw value for later substitution
                    value.clone()
                }
            };
            evaluated_params.insert(param.clone(), evaluated.clone());
        }

        // Set evaluated parameters in symbol table for expression evaluation
        // This must be done BEFORE substitute_params_in_element and eval_all
        for (param, value) in &evaluated_params {
            self.symbols.set(param.clone(), value.clone());
        }

        // Now substitute parameters in the macro body
        let subst_start = std::time::Instant::now();
        self.substitute_params_in_element(&mut expanded_body, &evaluated_params)?;
        let subst_elapsed = subst_start.elapsed();

        // Then evaluate all expressions (properties, conditionals, etc.)
        // Make sure parameters are still available during evaluation
        let eval_start = std::time::Instant::now();
        self.eval_all(&mut expanded_body)?;
        let eval_elapsed = eval_start.elapsed();

        if self.verbosity > 2 {
            eprintln!(
                "[MACRO] clone: {:?}, subst: {:?}, eval_all: {:?}",
                clone_elapsed, subst_elapsed, eval_elapsed
            );
        }

        // Restore symbol table state - remove new parameters and restore old values
        for param in param_values.keys() {
            if let Some(old_value) = saved_symbols.get(param) {
                // Restore old value
                self.symbols.set(param.clone(), old_value.clone());
            } else {
                // Remove parameter that didn't exist before
                self.symbols.remove(param);
            }
        }

        // Handle child elements as block arguments (like <origin> inside macro calls)
        let mut block_args = HashMap::new();
        for child in &call_element.children {
            if let XMLNode::Element(child_elem) = child {
                // Store child elements as block arguments that can be inserted
                let block_name = child_elem.name.clone();
                block_args.insert(block_name, child_elem.clone());
            }
        }

        // Process insert_block elements in the macro body
        self.process_insert_blocks(&mut expanded_body, &block_args)?;

        // Return all children of the macro body (including comments)
        let mut result = Vec::new();

        for child in expanded_body.children {
            match child {
                XMLNode::Element(element) => {
                    // Note: eval_all was already called on expanded_body above,
                    // so we don't need to call it again on individual elements
                    result.push(XMLNode::Element(element));
                }
                XMLNode::Comment(comment) => {
                    // Preserve comments in macro expansions
                    result.push(XMLNode::Comment(comment));
                }
                XMLNode::Text(text) => {
                    // Preserve text nodes
                    result.push(XMLNode::Text(text));
                }
            }
        }

        // No cleanup needed since we're not modifying the global symbol table

        // Note: Joint removal is now handled after all processing

        // Store result in cache for future reuse
        self.macro_cache.insert(cache_key, result.clone());

        Ok(result)
    }

    #[allow(clippy::only_used_in_recursion)]
    fn process_insert_blocks(
        &mut self,
        element: &mut Element,
        block_args: &HashMap<String, Element>,
    ) -> Result<()> {
        let mut i = 0;
        while i < element.children.len() {
            if let XMLNode::Element(child) = &mut element.children[i] {
                let element_local_name = if child.name.contains('}') {
                    child.name.split('}').next_back().unwrap_or(&child.name)
                } else if child.name.contains(':') {
                    child.name.split(':').next_back().unwrap_or(&child.name)
                } else {
                    &child.name
                };

                if element_local_name == "insert_block" {
                    if let Some(block_name) = child.attributes.get("name") {
                        if let Some(block_element) = block_args.get(block_name) {
                            // Replace insert_block with the actual block content
                            element.children[i] = XMLNode::Element(block_element.clone());
                        } else {
                            // If block not found, remove the insert_block element
                            element.children.remove(i);
                            continue;
                        }
                    } else {
                        return Err(XacroError::Parse(
                            "insert_block missing 'name' attribute".into(),
                        ));
                    }
                } else {
                    // Recursively process child elements
                    self.process_insert_blocks(child, block_args)?;
                }
            }
            i += 1;
        }
        Ok(())
    }

    fn remove_root_link_from_doc(&mut self, doc: &mut Element) {
        if let Some(link_name) = self.remove_root_link.clone() {
            self.remove_specified_root_link(doc, &link_name);
        }
    }

    #[allow(clippy::only_used_in_recursion)]
    fn remove_specified_root_link(&mut self, element: &mut Element, link_name: &str) -> bool {
        let mut i = 0;
        while i < element.children.len() {
            if let XMLNode::Element(child_element) = &element.children[i] {
                // Remove the specified link
                if child_element.name == "link" {
                    if let Some(name_attr) = child_element.attributes.get("name") {
                        if name_attr == link_name {
                            element.children.remove(i);
                            // Also remove any joint that references this link as parent
                            self.remove_joints_with_parent(element, link_name);
                            return true;
                        }
                    }
                }
            }
            i += 1;
        }

        // If no link found at this level, search children recursively
        for child in &mut element.children {
            if let XMLNode::Element(child_element) = child {
                if self.remove_specified_root_link(child_element, link_name) {
                    return true;
                }
            }
        }

        false
    }

    #[allow(clippy::only_used_in_recursion)]
    fn remove_joints_with_parent(&mut self, element: &mut Element, parent_link: &str) {
        let mut indices_to_remove = Vec::new();

        // First pass: identify joints to remove
        for (i, child) in element.children.iter().enumerate() {
            if let XMLNode::Element(child_element) = child {
                if child_element.name == "joint" {
                    // Check if this joint has the specified parent link
                    for joint_child in &child_element.children {
                        if let XMLNode::Element(joint_child_elem) = joint_child {
                            if joint_child_elem.name == "parent" {
                                if let Some(link_attr) = joint_child_elem.attributes.get("link") {
                                    if link_attr == parent_link {
                                        indices_to_remove.push(i);
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Second pass: remove joints in reverse order
        for &i in indices_to_remove.iter().rev() {
            element.children.remove(i);
        }

        // Recursively search children
        for child in &mut element.children {
            if let XMLNode::Element(child_element) = child {
                self.remove_joints_with_parent(child_element, parent_link);
            }
        }
    }

    fn substitute_params_in_element(
        &mut self,
        element: &mut Element,
        params: &HashMap<String, String>,
    ) -> Result<()> {
        // Skip parameter substitution for conditional elements' value attributes
        // These will be evaluated later when the symbol table has the necessary parameters
        let is_conditional = element.name == "xacro:if"
            || element.name == "xacro:unless"
            || element.name == "if"
            || element.name == "unless";

        // Substitute in attributes
        for (attr_name, value) in element.attributes.iter_mut() {
            // Skip 'value' attribute for conditional elements
            if is_conditional && attr_name == "value" {
                continue;
            }
            *value = self.substitute_params_in_text(value, params)?;
        }

        // Substitute in text content
        for child in &mut element.children {
            match child {
                XMLNode::Element(child_elem) => {
                    self.substitute_params_in_element(child_elem, params)?;
                }
                XMLNode::Text(text) => {
                    *text = self.substitute_params_in_text(text, params)?;
                }
                XMLNode::Comment(_) => {
                    // Comments are preserved as-is
                }
            }
        }

        Ok(())
    }

    fn substitute_params_in_text(
        &mut self,
        text: &str,
        params: &HashMap<String, String>,
    ) -> Result<String> {
        // Early return if no substitutions needed
        if !text.contains("${") {
            return Ok(text.to_string());
        }

        // Use static regex for efficient pattern matching (same as eval_text_substitution)
        use once_cell::sync::Lazy;
        use regex::Regex;
        static PARAM_REGEX: Lazy<Regex> = Lazy::new(|| Regex::new(r"\$\{([^}]+)\}").unwrap());

        let mut result = String::with_capacity(text.len());
        let mut last_end = 0;
        let mut any_substitution = false;

        for cap in PARAM_REGEX.captures_iter(text) {
            let full_match = cap.get(0).unwrap();
            let var_name = &cap[1];

            // Add text before this match
            result.push_str(&text[last_end..full_match.start()]);

            // Try to substitute with parameter first, then fall back to symbol table
            if let Some(param_value) = params.get(var_name) {
                result.push_str(param_value);
                any_substitution = true;
            } else if let Some(symbol_value) = self.symbols.get(var_name) {
                result.push_str(symbol_value);
                any_substitution = true;
            } else {
                // Keep the original ${...} if not found
                result.push_str(full_match.as_str());
            }

            last_end = full_match.end();
        }

        // Add remaining text
        result.push_str(&text[last_end..]);

        // Only call eval_text if we actually made substitutions
        // (eval_text will handle expressions like ${2*pi}, etc.)
        if any_substitution && (result.contains("${") || result.contains("$")) {
            result = self.eval_text(&result)?;
        }

        Ok(result)
    }

    pub fn element_to_string(&self, element: &Element) -> String {
        self.element_to_string_with_source(element, None)
    }

    pub fn element_to_string_with_source(
        &self,
        element: &Element,
        source_file: Option<&str>,
    ) -> String {
        if self.format_output {
            let mut result = String::new();

            // Add XML declaration
            result.push_str("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");

            // Add xacro banner if source file is provided
            if let Some(file_path) = source_file {
                result.push_str(&format!(
                    "\n<!-- =================================================================================== -->\n<!-- |    This document was autogenerated by xacro from {file_path:<30} | -->\n<!-- |    EDITING THIS FILE BY HAND IS NOT RECOMMENDED                                 | -->\n<!-- =================================================================================== -->"
                ));
            }

            result.push('\n');
            result.push_str(&self.element_to_formatted_string(element, 0));
            result
        } else {
            let mut result = String::new();

            // Add XML declaration
            result.push_str("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");

            // Add xacro banner if source file is provided
            if let Some(file_path) = source_file {
                result.push_str(&format!(
                    "\n<!-- =================================================================================== -->\n<!-- |    This document was autogenerated by xacro from {file_path:<30} | -->\n<!-- |    EDITING THIS FILE BY HAND IS NOT RECOMMENDED                                 | -->\n<!-- =================================================================================== -->"
                ));
            }

            result.push('\n');
            result.push_str(&crate::parser::element_to_string(element));
            result
        }
    }

    #[allow(clippy::only_used_in_recursion)]
    fn element_to_formatted_string(&self, element: &Element, indent_level: usize) -> String {
        let mut result = String::new();
        let indent = "  ".repeat(indent_level);

        // Start tag
        result.push_str(&format!("{}<{}", indent, element.name));

        // Attributes with custom ordering
        let ordered_attributes = self.get_ordered_attributes(element);
        for (key, value) in ordered_attributes {
            result.push_str(&format!(" {key}=\"{value}\""));
        }

        if element.children.is_empty() {
            // Self-closing tag
            result.push_str(" />");
        } else {
            result.push('>');

            // Check if we have only text content
            let only_text = element
                .children
                .iter()
                .all(|child| matches!(child, XMLNode::Text(_)));

            if only_text && element.children.len() == 1 {
                // Single text node - no newlines
                if let Some(XMLNode::Text(text)) = element.children.first() {
                    result.push_str(text);
                }
            } else {
                // Mixed or multiple content - use newlines and indentation
                result.push('\n');

                for child in &element.children {
                    match child {
                        XMLNode::Element(child_elem) => {
                            result.push_str(
                                &self.element_to_formatted_string(child_elem, indent_level + 1),
                            );
                            result.push('\n');
                        }
                        XMLNode::Text(text) => {
                            let trimmed = text.trim();
                            if !trimmed.is_empty() {
                                result.push_str(&format!(
                                    "{}{}\n",
                                    "  ".repeat(indent_level + 1),
                                    trimmed
                                ));
                            }
                        }
                        XMLNode::Comment(comment) => {
                            result.push_str(&format!(
                                "{}<!--{}-->\n",
                                "  ".repeat(indent_level + 1),
                                comment
                            ));
                        }
                    }
                }

                result.push_str(&indent);
            }

            // End tag
            result.push_str(&format!("</{}>", element.name));
        }

        result
    }

    fn get_ordered_attributes(&self, element: &Element) -> Vec<(String, String)> {
        let mut attributes: Vec<(String, String)> = element
            .attributes
            .iter()
            .map(|(k, v)| (k.clone(), v.clone()))
            .collect();

        // Define attribute ordering priority
        let get_priority = |key: &str, element_name: &str| -> u8 {
            match key {
                "name" => 1, // name always first
                "type" => 2, // type second
                // For origin tags, xyz comes before rpy
                "xyz" if element_name == "origin" => 3,
                "rpy" if element_name == "origin" => 4,
                // For other common attributes
                "parent" => 10,
                "child" => 11,
                "link" => 12,
                "joint" => 13,
                "value" => 14,
                "default" => 15,
                "filename" => 16,
                "params" => 17,
                _ => 50, // All other attributes
            }
        };

        // Sort by priority, then alphabetically
        attributes.sort_by(|a, b| {
            let priority_a = get_priority(&a.0, &element.name);
            let priority_b = get_priority(&b.0, &element.name);

            match priority_a.cmp(&priority_b) {
                std::cmp::Ordering::Equal => a.0.cmp(&b.0),
                other => other,
            }
        });

        attributes
    }
}
