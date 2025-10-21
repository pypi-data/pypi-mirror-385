/**
 * JupyterLab extension for Hurl syntax highlighting
 */
import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';
import { StreamLanguage, LanguageSupport } from '@codemirror/language';
/**
 * CodeMirror 6 StreamParser for Hurl
 */
const hurlStreamParser = {
    name: 'hurl',
    startState: () => ({
        inSection: null,
        inMultilineString: false,
        lineStart: true
    }),
    token: (stream, state) => {
        // Track if we're at the start of a line
        if (stream.sol()) {
            state.lineStart = true;
            state.inSection = null;
        }
        // Skip whitespace
        if (stream.eatSpace()) {
            return null;
        }
        // Comments
        if (stream.match(/#.*/)) {
            return 'comment';
        }
        // Magic lines
        if (state.lineStart && stream.match(/%%\s*(include|verbose)\s*$/)) {
            state.lineStart = false;
            return 'meta';
        }
        // HTTP methods
        if (state.lineStart && stream.match(/\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)\b/)) {
            state.lineStart = false;
            return 'keyword';
        }
        // URLs
        if (stream.match(/https?:\/\/[^\s]+/)) {
            return 'url';
        }
        // Section headers
        if (stream.match(/\[(QueryStringParams|FormParams|MultipartFormData|Cookies|Captures|Asserts|Options|BasicAuth)\]/)) {
            state.inSection = stream.current().slice(1, -1);
            return 'heading';
        }
        // HTTP version
        if (stream.match(/HTTP\/[\d.]+/)) {
            return 'keyword';
        }
        // HTTP status codes
        if (stream.match(/\b\d{3}\b/)) {
            return 'number';
        }
        // Headers
        if (stream.match(/[A-Za-z][A-Za-z0-9-]*\s*:/)) {
            return 'propertyName';
        }
        // Assertion keywords
        if (stream.match(/\b(status|header|cookie|body|bytes|xpath|jsonpath|regex|variable|duration|sha256|md5|count|isInteger|isFloat|isBoolean|isString|isCollection|exists|includes|startsWith|endsWith|contains|matches|equals)\b/)) {
            return 'typeName';
        }
        // Comparison operators
        if (stream.match(/==|!=|>=|<=|>|<|\b(not\s+)?(contains|startsWith|endsWith|matches|exists|includes|isInteger|isFloat|isBoolean|isString|isCollection)\b/)) {
            return 'operator';
        }
        // Numbers
        if (stream.match(/\b\d+\.?\d*([eE][+-]?\d+)?\b/)) {
            return 'number';
        }
        // Boolean values
        if (stream.match(/\b(true|false|null)\b/)) {
            return 'bool';
        }
        // Quoted strings
        if (stream.match(/"([^"\\]|\\.)*"/)) {
            return 'string';
        }
        if (stream.match(/'([^'\\]|\\.)*'/)) {
            return 'string';
        }
        // Triple-quoted strings
        if (stream.match(/```/)) {
            state.inMultilineString = !state.inMultilineString;
            return 'string';
        }
        if (state.inMultilineString) {
            stream.skipToEnd();
            return 'string';
        }
        // JSONPath expressions
        if (stream.match(/\$\.[a-zA-Z_][\w\[\].]*/)) {
            return 'variableName';
        }
        // XPath expressions
        if (stream.match(/\/\/[^\s]+|\/[a-zA-Z][^\s]*/)) {
            return 'variableName';
        }
        // JSON/bracket delimiters
        if (stream.match(/[{}\[\]()]/)) {
            return 'bracket';
        }
        // Colons
        if (stream.match(/:/)) {
            return 'operator';
        }
        // Commas
        if (stream.match(/,/)) {
            return null;
        }
        // Template expressions
        if (stream.match(/\{\{[^}]+\}\}/)) {
            return 'variableName';
        }
        // Capture any other word
        if (stream.match(/[a-zA-Z_][\w]*/)) {
            state.lineStart = false;
            return 'variableName';
        }
        // Move to next character
        stream.next();
        state.lineStart = false;
        return null;
    }
};
/**
 * Initialization data for the extension
 */
const plugin = {
    id: 'jupyterlab-hurl-extension:plugin',
    description: 'Adds Hurl syntax highlighting to JupyterLab',
    autoStart: true,
    requires: [IEditorLanguageRegistry],
    activate: (app, languages) => {
        console.log('JupyterLab Hurl extension is activated!');
        // Register the Hurl language
        const hurlLanguage = StreamLanguage.define(hurlStreamParser);
        languages.addLanguage({
            name: 'hurl',
            mime: 'text/x-hurl',
            extensions: ['.hurl'],
            support: new LanguageSupport(hurlLanguage)
        });
        console.log('Hurl language registered with MIME type: text/x-hurl');
    }
};
export default plugin;
