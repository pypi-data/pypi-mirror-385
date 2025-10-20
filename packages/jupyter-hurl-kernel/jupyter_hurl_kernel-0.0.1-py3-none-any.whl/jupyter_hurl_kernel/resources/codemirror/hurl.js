// CodeMirror mode for Hurl syntax highlighting
// Based on Hurl syntax: https://hurl.dev/docs/manual.html

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("codemirror/lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["codemirror/lib/codemirror"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
  "use strict";

  CodeMirror.defineMode("hurl", function() {
    return {
      startState: function() {
        return {
          inSection: false,
          inHeader: false,
          inAssert: false
        };
      },

      token: function(stream, state) {
        // Magic lines
        if (stream.match(/^%%\s*(include|verbose)\b/)) {
          return "meta";
        }

        // HTTP methods at start of line
        if (stream.sol() && stream.match(/^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)\b/)) {
          return "keyword";
        }

        // URLs
        if (stream.match(/https?:\/\/[^\s]+/)) {
          return "string";
        }

        // Section headers
        if (stream.match(/^\[(QueryStringParams|FormParams|MultipartFormData|Cookies|Captures|Asserts|Options|BasicAuth)\]/)) {
          state.inSection = true;
          return "header";
        }

        // HTTP version and status
        if (stream.match(/^HTTP\/[\d.]+/)) {
          return "keyword";
        }
        if (stream.match(/^\d{3}\b/)) {
          return "number";
        }

        // Headers (key: value)
        if (stream.match(/^[A-Za-z][\w-]*:/)) {
          state.inHeader = true;
          return "attribute";
        }

        // Common assertions
        if (stream.match(/\b(status|header|cookie|body|bytes|xpath|jsonpath|regex|variable|duration|sha256|md5)\b/)) {
          return "builtin";
        }

        // Operators
        if (stream.match(/==|!=|>|<|>=|<=|contains|startsWith|endsWith|matches/)) {
          return "operator";
        }

        // Numbers
        if (stream.match(/\b\d+(\.\d+)?\b/)) {
          return "number";
        }

        // Strings in quotes
        if (stream.match(/"([^"\\]|\\.)*"/)) {
          return "string";
        }
        if (stream.match(/'([^'\\]|\\.)*'/)) {
          return "string";
        }

        // JSONPath expressions
        if (stream.match(/\$\.[^\s]+/)) {
          return "variable-2";
        }

        // XPath expressions
        if (stream.match(/\/\/[^\s]+/)) {
          return "variable-2";
        }

        // Comments
        if (stream.match(/#.*/)) {
          return "comment";
        }

        // JSON body delimiters
        if (stream.match(/[{}\[\]]/)) {
          return "bracket";
        }

        stream.next();
        return null;
      }
    };
  });

  CodeMirror.defineMIME("text/x-hurl", "hurl");
});
