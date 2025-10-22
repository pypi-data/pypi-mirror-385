use regex::Regex;

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    Text(String),
    Expression(String),
    Extension(String),
    DollarBrace(String),
}

pub struct Lexer {
    input: String,
    position: usize,
    dollar_dollar_brace_re: Regex,
    extension_re: Regex,
    text_re: Regex,
}

impl Lexer {
    pub fn new(input: &str) -> Self {
        Self {
            input: input.to_string(),
            position: 0,
            dollar_dollar_brace_re: Regex::new(r"^\$\$+(\{|\()").unwrap(),
            extension_re: Regex::new(r"^\$\([^)]*\)").unwrap(),
            text_re: Regex::new(r"[^$]+|\$[^{($]+|\$$").unwrap(),
        }
    }

    #[allow(clippy::should_implement_trait)]
    pub fn next(&mut self) -> Option<Token> {
        if self.position >= self.input.len() {
            return None;
        }

        let remaining = &self.input[self.position..];

        // Check for multiple $ followed by { or (
        if let Some(mat) = self.dollar_dollar_brace_re.find(remaining) {
            let matched = mat.as_str();
            self.position += mat.end();
            return Some(Token::DollarBrace(matched[1..].to_string())); // Remove first $
        }

        // Check for expressions ${...} with balanced braces
        if remaining.starts_with("${") {
            let mut depth = 1;
            let mut end_pos = 2;
            let bytes = remaining.as_bytes();

            while end_pos < bytes.len() && depth > 0 {
                match bytes[end_pos] {
                    b'{' => depth += 1,
                    b'}' => depth -= 1,
                    _ => {}
                }
                end_pos += 1;
            }

            if depth == 0 {
                let matched = &remaining[..end_pos];
                self.position += end_pos;
                let expr = &matched[2..matched.len() - 1]; // Remove ${ and }
                return Some(Token::Expression(expr.to_string()));
            }
        }

        // Check for extensions $(...)
        if let Some(mat) = self.extension_re.find(remaining) {
            let matched = mat.as_str();
            self.position += mat.end();
            let ext = &matched[2..matched.len() - 1]; // Remove $( and )
            return Some(Token::Extension(ext.to_string()));
        }

        // Check for text
        if let Some(mat) = self.text_re.find(remaining) {
            let matched = mat.as_str();
            self.position += mat.end();
            return Some(Token::Text(matched.to_string()));
        }

        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lexer_simple_text() {
        let mut lexer = Lexer::new("hello world");
        assert_eq!(lexer.next(), Some(Token::Text("hello world".to_string())));
        assert_eq!(lexer.next(), None);
    }

    #[test]
    fn test_lexer_expression() {
        let mut lexer = Lexer::new("${foo}");
        assert_eq!(lexer.next(), Some(Token::Expression("foo".to_string())));
        assert_eq!(lexer.next(), None);
    }

    #[test]
    fn test_lexer_extension() {
        let mut lexer = Lexer::new("$(find package)");
        assert_eq!(
            lexer.next(),
            Some(Token::Extension("find package".to_string()))
        );
        assert_eq!(lexer.next(), None);
    }

    #[test]
    fn test_lexer_mixed() {
        let mut lexer = Lexer::new("Hello ${name}, $(cwd)!");
        assert_eq!(lexer.next(), Some(Token::Text("Hello ".to_string())));
        assert_eq!(lexer.next(), Some(Token::Expression("name".to_string())));
        assert_eq!(lexer.next(), Some(Token::Text(", ".to_string())));
        assert_eq!(lexer.next(), Some(Token::Extension("cwd".to_string())));
        assert_eq!(lexer.next(), Some(Token::Text("!".to_string())));
        assert_eq!(lexer.next(), None);
    }

    #[test]
    fn test_lexer_nested_braces() {
        let mut lexer = Lexer::new("${(729.0/25.0)*(22.0/16.0)}");
        assert_eq!(
            lexer.next(),
            Some(Token::Expression("(729.0/25.0)*(22.0/16.0)".to_string()))
        );
        assert_eq!(lexer.next(), None);
    }
}
