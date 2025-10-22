use crate::error::{Result, XacroError};
use crate::lexer::{Lexer, Token};
use crate::symbols::SymbolTable;
use crate::utils::resolve_package_path;
use once_cell::sync::Lazy;
use regex::Regex;
use std::path::Path;

pub fn eval_text(text: &str, symbols: &SymbolTable, current_file: Option<&Path>) -> Result<String> {
    let mut lexer = Lexer::new(text);
    let mut results = Vec::new();

    while let Some(token) = lexer.next() {
        match token {
            Token::Text(s) => results.push(s),
            Token::Expression(expr) => {
                let value = eval_expression(&expr, symbols)?;
                results.push(value);
            }
            Token::Extension(ext) => {
                let value = eval_extension(&ext, symbols, current_file)?;
                results.push(value);
            }
            Token::DollarBrace(s) => {
                results.push(s);
            }
        }
    }

    if results.len() == 1 {
        Ok(results[0].clone())
    } else {
        Ok(results.join(""))
    }
}

fn eval_expression(expr: &str, symbols: &SymbolTable) -> Result<String> {
    // Simple expression evaluator
    // This is a simplified version - a full implementation would need a proper parser

    let expr = expr.trim();

    // Handle simple variable references
    if is_simple_identifier(expr) {
        if let Some(value) = symbols.get(expr) {
            return Ok(value.clone());
        } else {
            return Err(XacroError::UndefinedSymbol(format!(
                "variable '{expr}' in simple lookup"
            )));
        }
    }

    // Handle math expressions
    if let Ok(result) = eval_math_expression(expr, symbols) {
        return Ok(result);
    }

    // Handle string literals - including empty strings
    if expr.starts_with('"') && expr.ends_with('"') && expr.len() >= 2 {
        return Ok(expr[1..expr.len() - 1].to_string());
    }

    if expr.starts_with('\'') && expr.ends_with('\'') && expr.len() >= 2 {
        return Ok(expr[1..expr.len() - 1].to_string());
    }

    // Special case: handle '' (empty string literal)
    if expr == "''" {
        return Ok(String::new());
    }

    // Special case: handle "" (empty string literal)
    if expr == "\"\"" {
        return Ok(String::new());
    }

    // Handle malformed strings (single quote at start but not properly closed)
    if expr.starts_with('\'') && !expr.ends_with('\'') {
        // Remove the leading quote for malformed strings like '0, '1, etc.
        return Ok(expr[1..].to_string());
    }

    if expr.starts_with('"') && !expr.ends_with('"') {
        // Remove the leading quote for malformed strings
        return Ok(expr[1..].to_string());
    }

    // Handle boolean literals
    match expr {
        "true" | "True" => {
            return Ok("true".to_string());
        }
        "false" | "False" => {
            return Ok("false".to_string());
        }
        _ => {}
    }

    // Handle numeric literals
    if let Ok(num) = expr.parse::<f64>() {
        return Ok(num.to_string());
    }

    // Check if expression contains operators - if so, evaluate as math expression
    let has_operators = expr.contains("==")
        || expr.contains("!=")
        || expr.contains(" or ")
        || expr.contains(" and ")
        || expr.contains(">=")
        || expr.contains("<=")
        || expr.contains('>')
        || expr.contains('<')
        || expr.contains('+')
        || expr.contains('-')
        || expr.contains('*')
        || expr.contains('/');

    if has_operators {
        return eval_math_expression(expr, symbols);
    }

    // If all else fails, try to evaluate as a string substitution
    eval_text_substitution(expr, symbols)
}

fn eval_math_expression(expr: &str, symbols: &SymbolTable) -> Result<String> {
    let expr = expr.trim();

    // Handle parentheses first
    if let Some(result) = eval_parentheses(expr, symbols)? {
        return Ok(result);
    }

    // Handle operators with proper precedence (lowest to highest)
    // Logical operators (lowest precedence) - try with spaces first, then without
    if let Some(pos) = find_operator_sequence_outside_parens(expr, " or ") {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 4..], symbols)?;
        let left_bool = parse_boolean(&left);
        let right_bool = parse_boolean(&right);
        let result = left_bool || right_bool;

        return Ok(result.to_string());
    }

    if let Some(pos) = find_operator_sequence_outside_parens(expr, " and ") {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 5..], symbols)?;
        let left_bool = parse_boolean(&left);
        let right_bool = parse_boolean(&right);
        return Ok((left_bool && right_bool).to_string());
    }

    // Comparison operators - try with and without spaces
    if let Some(pos) = find_operator_sequence_outside_parens(expr, "==") {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 2..], symbols)?;
        let result = left == right;

        return Ok(result.to_string());
    }

    if let Some(pos) = find_operator_sequence_outside_parens(expr, "!=") {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 2..], symbols)?;
        return Ok((left != right).to_string());
    }

    // Addition and subtraction
    if let Some(pos) = find_operator_outside_parens(expr, '+') {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 1..], symbols)?;
        if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
            return Ok((l + r).to_string());
        }
    }

    if let Some(pos) = find_operator_outside_parens(expr, '-') {
        if pos > 0 {
            // Not a negative number at the start
            let left = eval_expression(&expr[..pos], symbols)?;
            let right = eval_expression(&expr[pos + 1..], symbols)?;
            if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
                return Ok((l - r).to_string());
            }
        } else if pos == 0 {
            // Handle negative number at start: -expr becomes 0 - expr
            let right = eval_expression(&expr[1..], symbols)?;
            if let Ok(r) = right.parse::<f64>() {
                return Ok((-r).to_string());
            }
        }
    }

    // Multiplication and division (higher precedence)
    if let Some(pos) = find_operator_outside_parens(expr, '*') {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 1..], symbols)?;
        if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
            return Ok((l * r).to_string());
        }
    }

    if let Some(pos) = find_operator_outside_parens(expr, '/') {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 1..], symbols)?;
        if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
            if r != 0.0 {
                return Ok((l / r).to_string());
            } else {
                return Err(XacroError::Eval("Division by zero".to_string()));
            }
        }
    }

    // Handle function calls
    if expr.contains('(') && expr.ends_with(')') && !expr.starts_with('(') {
        return eval_function_call(expr, symbols);
    }

    Err(XacroError::Eval(format!(
        "Cannot evaluate math expression: {expr}"
    )))
}

fn eval_parentheses(expr: &str, symbols: &SymbolTable) -> Result<Option<String>> {
    // Handle parentheses by finding the outermost ones and evaluating the content
    // But only if the entire expression is wrapped in parentheses
    if expr.starts_with('(') && expr.ends_with(')') {
        // Check if these parentheses actually wrap the entire expression
        let mut paren_depth = 0;
        for (i, c) in expr.char_indices() {
            match c {
                '(' => paren_depth += 1,
                ')' => {
                    paren_depth -= 1;
                    // If we reach depth 0 before the end, these aren't wrapping parentheses
                    if paren_depth == 0 && i < expr.len() - 1 {
                        return Ok(None);
                    }
                }
                _ => {}
            }
        }
        // If we get here, the parentheses wrap the entire expression
        let inner = &expr[1..expr.len() - 1];
        return Ok(Some(eval_expression(inner, symbols)?));
    }
    Ok(None)
}

fn find_operator_outside_parens(expr: &str, op: char) -> Option<usize> {
    let mut paren_depth = 0;
    let mut last_pos = None;

    for (i, c) in expr.char_indices().rev() {
        match c {
            ')' => paren_depth += 1,
            '(' => paren_depth -= 1,
            _ if c == op && paren_depth == 0 => {
                last_pos = Some(i);
            }
            _ => {}
        }
    }

    last_pos
}

fn eval_function_call(expr: &str, symbols: &SymbolTable) -> Result<String> {
    let paren_pos = expr
        .find('(')
        .ok_or_else(|| XacroError::Eval("Invalid function call".to_string()))?;

    let func_name = expr[..paren_pos].trim();
    let args_str = &expr[paren_pos + 1..expr.len() - 1];

    match func_name {
        "sin" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::sin(num).to_string())
        }
        "cos" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::cos(num).to_string())
        }
        "tan" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::tan(num).to_string())
        }
        "sqrt" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::sqrt(num).to_string())
        }
        "abs" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(num.abs().to_string())
        }
        "min" => {
            let args: Vec<&str> = args_str.split(',').collect();
            if args.len() < 2 {
                return Err(XacroError::Eval(
                    "min() requires at least 2 arguments".to_string(),
                ));
            }
            let mut min_val = f64::INFINITY;
            for arg in args {
                let val = eval_expression(arg.trim(), symbols)?;
                let num: f64 = val
                    .parse()
                    .map_err(|_| XacroError::Type("Expected number".to_string()))?;
                min_val = min_val.min(num);
            }
            Ok(min_val.to_string())
        }
        "max" => {
            let args: Vec<&str> = args_str.split(',').collect();
            if args.len() < 2 {
                return Err(XacroError::Eval(
                    "max() requires at least 2 arguments".to_string(),
                ));
            }
            let mut max_val = f64::NEG_INFINITY;
            for arg in args {
                let val = eval_expression(arg.trim(), symbols)?;
                let num: f64 = val
                    .parse()
                    .map_err(|_| XacroError::Type("Expected number".to_string()))?;
                max_val = max_val.max(num);
            }
            Ok(max_val.to_string())
        }
        _ => Err(XacroError::Eval(format!("Unknown function: {func_name}"))),
    }
}

fn eval_extension(ext: &str, symbols: &SymbolTable, current_file: Option<&Path>) -> Result<String> {
    // Handle ROS substitution arguments
    let ext_trimmed = ext.trim();

    if ext_trimmed == "cwd" {
        if let Ok(cwd) = std::env::current_dir() {
            Ok(cwd.to_string_lossy().to_string())
        } else {
            Err(XacroError::Eval("Cannot get current directory".to_string()))
        }
    } else if ext_trimmed.starts_with("env ") {
        // Handle $(env ENVIRONMENT_VARIABLE)
        let var_name = ext_trimmed.strip_prefix("env ").unwrap().trim();

        match std::env::var(var_name) {
            Ok(value) => Ok(value),
            Err(_) => Err(XacroError::Eval(format!(
                "Environment variable not found: {var_name}"
            ))),
        }
    } else if ext_trimmed.starts_with("optenv ") {
        // Handle $(optenv ENVIRONMENT_VARIABLE) or $(optenv ENVIRONMENT_VARIABLE default_value)
        let args = ext_trimmed.strip_prefix("optenv ").unwrap().trim();
        let parts: Vec<&str> = args.splitn(2, ' ').collect();
        let var_name = parts[0];

        match std::env::var(var_name) {
            Ok(value) => Ok(value),
            Err(_) => {
                if parts.len() > 1 {
                    // Return default value if provided
                    Ok(parts[1].to_string())
                } else {
                    // Return empty string if no default value
                    Ok(String::new())
                }
            }
        }
    } else if ext_trimmed.starts_with("find ") {
        // Handle $(find package_name)
        let package_name = ext_trimmed.strip_prefix("find ").unwrap().trim();

        // First check ROS_PACKAGE_PATH environment variable
        if let Ok(ros_package_path) = std::env::var("ROS_PACKAGE_PATH") {
            for path in ros_package_path.split(':') {
                let full_path = Path::new(path);
                if full_path.ends_with(package_name) && full_path.exists() {
                    return Ok(full_path.to_string_lossy().to_string());
                }
                // Also check subdirectories
                let sub_path = full_path.join(package_name);
                if sub_path.exists() {
                    return Ok(sub_path.to_string_lossy().to_string());
                }
            }
        }

        // Fall back to original logic
        let base_path = if let Some(current) = current_file {
            current.parent().unwrap_or_else(|| Path::new("."))
        } else {
            Path::new(".")
        };

        if let Some(package_path) = resolve_package_path(package_name, base_path) {
            Ok(package_path.to_string_lossy().to_string())
        } else {
            Err(XacroError::Eval(format!(
                "Cannot find package: {package_name}"
            )))
        }
    } else if ext_trimmed.starts_with("arg ") {
        // Handle $(arg argument_name)
        let arg_name = ext_trimmed.strip_prefix("arg ").unwrap().trim();

        // Look up argument in symbol table
        if let Some(value) = symbols.get(arg_name) {
            Ok(value.clone())
        } else {
            // Return default value "false" for missing arguments (common in ROS)
            Ok("false".to_string())
        }
    } else if ext_trimmed.starts_with("eval ") {
        // Handle $(eval expression)
        let expr = ext_trimmed.strip_prefix("eval ").unwrap().trim();

        // Evaluate the expression using our expression evaluator
        eval_expression(expr, symbols)
    } else {
        // For other extensions, return as-is
        Ok(format!("$({ext})"))
    }
}

// Static regex for variable substitution (compiled once at startup)
static VAR_SUBSTITUTION_REGEX: Lazy<Regex> = Lazy::new(|| Regex::new(r"\$\{([^}]+)\}").unwrap());

fn eval_text_substitution(text: &str, symbols: &SymbolTable) -> Result<String> {
    // Replace variable references in text with optimized string building
    let mut result = String::new();
    let mut last_end = 0;
    let mut has_match = false;

    for cap in VAR_SUBSTITUTION_REGEX.captures_iter(text) {
        has_match = true;
        let full_match = cap.get(0).unwrap();
        let var_name = &cap[1];

        // Append text before this match
        result.push_str(&text[last_end..full_match.start()]);

        // Append variable value
        if let Some(value) = symbols.get(var_name) {
            result.push_str(value);
        } else {
            return Err(XacroError::UndefinedSymbol(format!(
                "{var_name} in expression '{text}'"
            )));
        }

        last_end = full_match.end();
    }

    // If no matches found, return original text
    if !has_match {
        return Ok(text.to_string());
    }

    // Append remaining text after last match
    result.push_str(&text[last_end..]);

    Ok(result)
}

fn is_simple_identifier(s: &str) -> bool {
    !s.is_empty()
        && s.chars().all(|c| c.is_alphanumeric() || c == '_')
        && !s.chars().next().unwrap().is_ascii_digit()
}

fn find_operator_sequence_outside_parens(expr: &str, op: &str) -> Option<usize> {
    let mut paren_depth = 0;
    let mut quote_char: Option<char> = None;
    let chars: Vec<char> = expr.chars().collect();

    for i in 0..=chars.len().saturating_sub(op.len()) {
        let ch = chars[i];

        // Handle quotes
        if quote_char.is_none() && (ch == '"' || ch == '\'') {
            quote_char = Some(ch);
            continue;
        } else if Some(ch) == quote_char {
            quote_char = None;
            continue;
        }

        // Skip if inside quotes
        if quote_char.is_some() {
            continue;
        }

        // Handle parentheses
        match ch {
            '(' => paren_depth += 1,
            ')' => paren_depth -= 1,
            _ => {}
        }

        // Check for operator at current position
        if paren_depth == 0 {
            let slice = &expr[i..];
            if slice.starts_with(op) {
                return Some(i);
            }
        }
    }

    None
}

fn parse_boolean(s: &str) -> bool {
    match s.trim().to_lowercase().as_str() {
        "true" | "1" => true,
        "false" | "0" | "" => false,
        _ => !s.trim().is_empty(), // Non-empty strings are truthy
    }
}
