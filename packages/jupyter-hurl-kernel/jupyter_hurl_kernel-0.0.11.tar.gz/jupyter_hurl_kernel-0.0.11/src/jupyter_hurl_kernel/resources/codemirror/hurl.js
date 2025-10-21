// CodeMirror mode for Hurl syntax highlighting
// Based on Hurl syntax: https://hurl.dev/docs/manual.html

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("codemirror/lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["codemirror/lib/codemirror"], mod);
  else if (typeof CodeMirror != "undefined") // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
  "use strict";

  if (!CodeMirror) return;

  CodeMirror.defineMode("hurl", function(config, parserConfig) {
    return {
      startState: function() {
        return {
          inSection: null,        // Track current section type
          inMultilineString: false,
          lineStart: true
        };
      },

      token: function(stream, state) {
        // Track if we're at the start of a line
        if (stream.sol()) {
          state.lineStart = true;
          state.inSection = null; // Reset section tracking at line start
        }

        // Skip whitespace but track position
        if (stream.eatSpace()) {
          return null;
        }

        // Comments (# at any position)
        if (stream.match(/#.*/)) {
          return "comment";
        }

        // Magic lines (must be at start of line)
        if (state.lineStart && stream.match(/%%\s*(include|verbose)\s*$/)) {
          state.lineStart = false;
          return "meta";
        }

        // HTTP methods (must be at start of line)
        if (state.lineStart && stream.match(/\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)\b/)) {
          state.lineStart = false;
          return "keyword";
        }

        // URLs (after HTTP methods or standalone)
        if (stream.match(/https?:\/\/[^\s]+/)) {
          return "string-2";
        }

        // Section headers like [QueryStringParams], [Asserts], etc.
        if (stream.match(/\[(QueryStringParams|FormParams|MultipartFormData|Cookies|Captures|Asserts|Options|BasicAuth)\]/)) {
          state.inSection = stream.current().slice(1, -1); // Store section name
          return "header";
        }

        // HTTP version (HTTP/1.1, HTTP/2, etc.)
        if (stream.match(/HTTP\/[\d.]+/)) {
          return "keyword";
        }

        // HTTP status codes (200, 404, etc.)
        if (stream.match(/\b\d{3}\b/)) {
          return "number";
        }

        // Headers (Content-Type:, Authorization:, etc.)
        // More strict: must be at start of line or after whitespace
        if (stream.match(/[A-Za-z][A-Za-z0-9-]*\s*:/)) {
          return "attribute";
        }

        // Assertion keywords (specific to Hurl)
        if (stream.match(/\b(status|header|cookie|body|bytes|xpath|jsonpath|regex|variable|duration|sha256|md5|count|isInteger|isFloat|isBoolean|isString|isCollection|exists|includes|startsWith|endsWith|contains|matches|equals)\b/)) {
          return "builtin";
        }

        // Comparison operators
        if (stream.match(/==|!=|>=|<=|>|<|\b(not\s+)?(contains|startsWith|endsWith|matches|exists|includes|isInteger|isFloat|isBoolean|isString|isCollection)\b/)) {
          return "operator";
        }

        // Numbers (integers and floats)
        if (stream.match(/\b\d+\.?\d*([eE][+-]?\d+)?\b/)) {
          return "number";
        }

        // Boolean values
        if (stream.match(/\b(true|false|null)\b/)) {
          return "atom";
        }

        // Quoted strings (double quotes)
        if (stream.match(/"([^"\\]|\\.)*"/)) {
          return "string";
        }

        // Quoted strings (single quotes)
        if (stream.match(/'([^'\\]|\\.)*'/)) {
          return "string";
        }

        // Triple-quoted strings (multiline strings in Hurl)
        if (stream.match(/```/)) {
          state.inMultilineString = !state.inMultilineString;
          return "string";
        }

        if (state.inMultilineString) {
          stream.skipToEnd();
          return "string";
        }

        // JSONPath expressions ($.path.to.value)
        if (stream.match(/\$\.[a-zA-Z_][\w\[\].]*/)) {
          return "variable-2";
        }

        // XPath expressions (//path or /path)
        if (stream.match(/\/\/[^\s]+|\/[a-zA-Z][^\s]*/)) {
          return "variable-2";
        }

        // JSON/bracket delimiters
        if (stream.match(/[{}\[\]()]/)) {
          return "bracket";
        }

        // Colons (for key-value pairs)
        if (stream.match(/:/)) {
          return "operator";
        }

        // Commas
        if (stream.match(/,/)) {
          return null;
        }

        // Template expressions {{variable}}
        if (stream.match(/\{\{[^}]+\}\}/)) {
          return "variable";
        }

        // Capture any other word/identifier
        if (stream.match(/[a-zA-Z_][\w]*/)) {
          state.lineStart = false;
          return "variable";
        }

        // Move to next character if nothing matched
        stream.next();
        state.lineStart = false;
        return null;
      },

      lineComment: "#"
    };
  });

  CodeMirror.defineMIME("text/x-hurl", "hurl");

  // Also register common file extension
  CodeMirror.modeInfo.push({
    name: "Hurl",
    mime: "text/x-hurl",
    mode: "hurl",
    ext: ["hurl"]
  });
});
