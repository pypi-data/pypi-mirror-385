use crate::xml_element::Element;
use std::collections::HashMap;
// use crate::error::{Result, XacroError};

#[derive(Debug, Clone)]
pub struct Macro {
    pub name: String,
    pub params: Vec<String>,
    pub defaults: HashMap<String, String>,
    pub body: Element,
}

impl Macro {
    pub fn new(name: String, params_str: &str, body: Element) -> Self {
        let (params, defaults) = Self::parse_params(params_str);

        Self {
            name,
            params,
            defaults,
            body,
        }
    }

    fn parse_params(params_str: &str) -> (Vec<String>, HashMap<String, String>) {
        let mut params = Vec::new();
        let mut defaults = HashMap::new();

        if params_str.trim().is_empty() {
            return (params, defaults);
        }

        // Split by whitespace, but be smart about quoted strings
        let mut tokens = Vec::new();
        let mut current_token = String::new();
        let mut in_quotes = false;
        let mut quote_char = ' ';

        for ch in params_str.chars() {
            match ch {
                '\'' | '"' if !in_quotes => {
                    // Start of quoted string
                    in_quotes = true;
                    quote_char = ch;
                    // Don't include the quote in the token
                }
                ch if in_quotes && ch == quote_char => {
                    // End of quoted string
                    in_quotes = false;
                    // For empty quoted strings, we need to explicitly handle them
                    if current_token.is_empty() {
                        // This was an empty string like '' or ""
                        // We need to mark it as such so it doesn't get lost
                        current_token.push_str("__EMPTY_STRING__");
                    }
                    // Don't include the quote in the token
                }
                ' ' | '\t' | '\n' if !in_quotes => {
                    // Whitespace outside quotes - end current token
                    if !current_token.trim().is_empty() {
                        tokens.push(current_token.trim().to_string());
                        current_token.clear();
                    }
                }
                _ => {
                    // Regular character or whitespace inside quotes
                    current_token.push(ch);
                }
            }
        }

        // Don't forget the last token
        if !current_token.trim().is_empty() {
            tokens.push(current_token.trim().to_string());
        }

        // Special handling: if we ended inside quotes with empty content,
        // we had an empty quoted string at the end
        if in_quotes && current_token.is_empty() {
            tokens.push("__EMPTY_STRING__".to_string());
        }

        // Now process each token
        for token in tokens {
            Self::process_param(&token, &mut params, &mut defaults);
        }

        (params, defaults)
    }

    fn process_param(
        param: &str,
        params: &mut Vec<String>,
        defaults: &mut HashMap<String, String>,
    ) {
        if let Some(eq_pos) = param.find(":=") {
            // Parameter with default value: "param:=default"
            let param_name = param[..eq_pos].trim();
            let default_value = param[eq_pos + 2..].trim();

            // Handle the special empty string marker
            let clean_default = if default_value == "__EMPTY_STRING__" {
                ""
            } else {
                default_value
            };

            params.push(param_name.to_string());
            defaults.insert(param_name.to_string(), clean_default.to_string());
        } else {
            // Parameter without default value
            params.push(param.to_string());
        }
    }

    pub fn has_param(&self, name: &str) -> bool {
        self.params.contains(&name.to_string())
    }

    pub fn get_default(&self, name: &str) -> Option<&String> {
        self.defaults.get(name)
    }
}

#[derive(Debug)]
pub struct MacroTable {
    macros: HashMap<String, Macro>,
}

impl Default for MacroTable {
    fn default() -> Self {
        Self::new()
    }
}

impl MacroTable {
    pub fn new() -> Self {
        Self {
            macros: HashMap::new(),
        }
    }

    pub fn insert(&mut self, name: String, macro_def: Macro) {
        self.macros.insert(name, macro_def);
    }

    pub fn get(&self, name: &str) -> Option<&Macro> {
        self.macros.get(name)
    }

    pub fn contains(&self, name: &str) -> bool {
        self.macros.contains_key(name)
    }

    pub fn remove(&mut self, name: &str) -> Option<Macro> {
        self.macros.remove(name)
    }

    pub fn keys(&self) -> impl Iterator<Item = &String> {
        self.macros.keys()
    }

    pub fn values(&self) -> impl Iterator<Item = &Macro> {
        self.macros.values()
    }

    pub fn iter(&self) -> impl Iterator<Item = (&String, &Macro)> {
        self.macros.iter()
    }
}
