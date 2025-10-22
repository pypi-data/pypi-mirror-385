use crate::error::{Result, XacroError};
use std::collections::BTreeMap;

#[derive(Debug, Clone)]
pub enum XMLNode {
    Element(Element),
    Text(String),
    Comment(String),
}

#[derive(Debug, Clone)]
pub struct Element {
    pub name: String,
    pub attributes: BTreeMap<String, String>,
    pub children: Vec<XMLNode>,
    pub namespace: Option<String>,
    pub prefix: Option<String>,
}

impl Element {
    pub fn new(name: String) -> Self {
        Element {
            name,
            attributes: BTreeMap::new(),
            children: Vec::new(),
            namespace: None,
            prefix: None,
        }
    }

    pub fn parse(input: &[u8]) -> Result<Element> {
        let input_str = std::str::from_utf8(input)
            .map_err(|e| XacroError::Parse(format!("Invalid UTF-8: {e}")))?;

        let doc = roxmltree::Document::parse(input_str)
            .map_err(|e| XacroError::Parse(format!("XML parsing error: {e}")))?;

        let root = doc.root_element();
        parse_element(&root)
    }

    pub fn get_child(&self, name: &str) -> Option<&Element> {
        for child in &self.children {
            if let XMLNode::Element(elem) = child {
                if elem.name == name {
                    return Some(elem);
                }
            }
        }
        None
    }

    pub fn get_mut_child(&mut self, name: &str) -> Option<&mut Element> {
        for child in &mut self.children {
            if let XMLNode::Element(elem) = child {
                if elem.name == name {
                    return Some(elem);
                }
            }
        }
        None
    }

    pub fn write_to(&self, w: &mut Vec<u8>) -> Result<()> {
        write_element(self, w, 0)?;
        Ok(())
    }
}

fn parse_element(node: &roxmltree::Node) -> Result<Element> {
    let mut element = Element::new(node.tag_name().name().to_string());

    // Handle namespace
    if let Some(namespace) = node.tag_name().namespace() {
        if !namespace.is_empty() {
            element.namespace = Some(namespace.to_string());
        }
    }

    // Check for xacro prefix in the name
    let tag_name = node.tag_name().name();
    if tag_name.starts_with("xacro:") {
        element.prefix = Some("xacro".to_string());
        element.name = tag_name.strip_prefix("xacro:").unwrap().to_string();
    }

    // Parse attributes
    for attr in node.attributes() {
        let attr_name = if let Some(prefix) = attr.namespace() {
            if !prefix.is_empty() {
                format!("{}:{}", prefix, attr.name())
            } else {
                attr.name().to_string()
            }
        } else {
            attr.name().to_string()
        };
        element
            .attributes
            .insert(attr_name, attr.value().to_string());
    }

    // Parse children
    for child in node.children() {
        match child.node_type() {
            roxmltree::NodeType::Element => {
                element
                    .children
                    .push(XMLNode::Element(parse_element(&child)?));
            }
            roxmltree::NodeType::Text => {
                let text = child.text().unwrap_or("");
                if !text.trim().is_empty() {
                    element.children.push(XMLNode::Text(text.to_string()));
                }
            }
            roxmltree::NodeType::Comment => {
                if let Some(text) = child.text() {
                    element.children.push(XMLNode::Comment(text.to_string()));
                }
            }
            _ => {}
        }
    }

    Ok(element)
}

fn write_element(element: &Element, w: &mut Vec<u8>, indent: usize) -> Result<()> {
    let indent_str = "  ".repeat(indent);

    // Start tag
    w.extend_from_slice(indent_str.as_bytes());
    w.push(b'<');
    w.extend_from_slice(element.name.as_bytes());

    // Write attributes
    for (key, value) in &element.attributes {
        w.push(b' ');
        w.extend_from_slice(key.as_bytes());
        w.extend_from_slice(b"=\"");
        write_escaped_attr(value, w);
        w.push(b'"');
    }

    if element.children.is_empty() {
        // Self-closing tag
        w.extend_from_slice(b" />");
        w.push(b'\n');
    } else {
        w.push(b'>');

        // Check if we have only text content
        let only_text =
            element.children.len() == 1 && matches!(&element.children[0], XMLNode::Text(_));

        if !only_text {
            w.push(b'\n');
        }

        // Write children
        for child in &element.children {
            match child {
                XMLNode::Element(child_elem) => {
                    write_element(child_elem, w, indent + 1)?;
                }
                XMLNode::Text(text) => {
                    if !only_text {
                        w.extend_from_slice("  ".repeat(indent + 1).as_bytes());
                    }
                    write_escaped_text(text, w);
                    if !only_text {
                        w.push(b'\n');
                    }
                }
                XMLNode::Comment(comment) => {
                    w.extend_from_slice("  ".repeat(indent + 1).as_bytes());
                    w.extend_from_slice(b"<!--");
                    w.extend_from_slice(comment.as_bytes());
                    w.extend_from_slice(b"-->");
                    w.push(b'\n');
                }
            }
        }

        // End tag
        if !only_text {
            w.extend_from_slice(indent_str.as_bytes());
        }
        w.extend_from_slice(b"</");
        w.extend_from_slice(element.name.as_bytes());
        w.push(b'>');
        w.push(b'\n');
    }

    Ok(())
}

fn write_escaped_attr(s: &str, w: &mut Vec<u8>) {
    for ch in s.chars() {
        match ch {
            '&' => w.extend_from_slice(b"&amp;"),
            '<' => w.extend_from_slice(b"&lt;"),
            '>' => w.extend_from_slice(b"&gt;"),
            '"' => w.extend_from_slice(b"&quot;"),
            '\'' => w.extend_from_slice(b"&apos;"),
            _ => {
                let mut buf = [0; 4];
                let len = ch.encode_utf8(&mut buf).len();
                w.extend_from_slice(&buf[..len]);
            }
        }
    }
}

fn write_escaped_text(s: &str, w: &mut Vec<u8>) {
    for ch in s.chars() {
        match ch {
            '&' => w.extend_from_slice(b"&amp;"),
            '<' => w.extend_from_slice(b"&lt;"),
            '>' => w.extend_from_slice(b"&gt;"),
            _ => {
                let mut buf = [0; 4];
                let len = ch.encode_utf8(&mut buf).len();
                w.extend_from_slice(&buf[..len]);
            }
        }
    }
}
