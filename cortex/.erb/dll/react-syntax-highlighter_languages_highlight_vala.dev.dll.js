/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(global["webpackChunkrenderer"] = global["webpackChunkrenderer"] || []).push([["react-syntax-highlighter_languages_highlight_vala"],{

/***/ "./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/vala.js":
/*!***********************************************************************************************!*\
  !*** ./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/vala.js ***!
  \***********************************************************************************************/
/***/ ((module) => {

eval("/*\nLanguage: Vala\nAuthor: Antono Vasiljev <antono.vasiljev@gmail.com>\nDescription: Vala is a new programming language that aims to bring modern programming language features to GNOME developers without imposing any additional runtime requirements and without using a different ABI compared to applications and libraries written in C.\nWebsite: https://wiki.gnome.org/Projects/Vala\n*/\n\nfunction vala(hljs) {\n  return {\n    name: 'Vala',\n    keywords: {\n      keyword:\n        // Value types\n        'char uchar unichar int uint long ulong short ushort int8 int16 int32 int64 uint8 ' +\n        'uint16 uint32 uint64 float double bool struct enum string void ' +\n        // Reference types\n        'weak unowned owned ' +\n        // Modifiers\n        'async signal static abstract interface override virtual delegate ' +\n        // Control Structures\n        'if while do for foreach else switch case break default return try catch ' +\n        // Visibility\n        'public private protected internal ' +\n        // Other\n        'using new this get set const stdout stdin stderr var',\n      built_in:\n        'DBus GLib CCode Gee Object Gtk Posix',\n      literal:\n        'false true null'\n    },\n    contains: [\n      {\n        className: 'class',\n        beginKeywords: 'class interface namespace',\n        end: /\\{/,\n        excludeEnd: true,\n        illegal: '[^,:\\\\n\\\\s\\\\.]',\n        contains: [ hljs.UNDERSCORE_TITLE_MODE ]\n      },\n      hljs.C_LINE_COMMENT_MODE,\n      hljs.C_BLOCK_COMMENT_MODE,\n      {\n        className: 'string',\n        begin: '\"\"\"',\n        end: '\"\"\"',\n        relevance: 5\n      },\n      hljs.APOS_STRING_MODE,\n      hljs.QUOTE_STRING_MODE,\n      hljs.C_NUMBER_MODE,\n      {\n        className: 'meta',\n        begin: '^#',\n        end: '$',\n        relevance: 2\n      }\n    ]\n  };\n}\n\nmodule.exports = vala;\n\n\n//# sourceURL=webpack://renderer/./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/vala.js?");

/***/ })

}]);