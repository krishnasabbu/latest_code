/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(global["webpackChunkrenderer"] = global["webpackChunkrenderer"] || []).push([["react-syntax-highlighter_languages_highlight_nix"],{

/***/ "./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/nix.js":
/*!**********************************************************************************************!*\
  !*** ./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/nix.js ***!
  \**********************************************************************************************/
/***/ ((module) => {

eval("/*\nLanguage: Nix\nAuthor: Domen Kožar <domen@dev.si>\nDescription: Nix functional language\nWebsite: http://nixos.org/nix\n*/\n\nfunction nix(hljs) {\n  const NIX_KEYWORDS = {\n    keyword:\n      'rec with let in inherit assert if else then',\n    literal:\n      'true false or and null',\n    built_in:\n      'import abort baseNameOf dirOf isNull builtins map removeAttrs throw ' +\n      'toString derivation'\n  };\n  const ANTIQUOTE = {\n    className: 'subst',\n    begin: /\\$\\{/,\n    end: /\\}/,\n    keywords: NIX_KEYWORDS\n  };\n  const ATTRS = {\n    begin: /[a-zA-Z0-9-_]+(\\s*=)/,\n    returnBegin: true,\n    relevance: 0,\n    contains: [\n      {\n        className: 'attr',\n        begin: /\\S+/\n      }\n    ]\n  };\n  const STRING = {\n    className: 'string',\n    contains: [ ANTIQUOTE ],\n    variants: [\n      {\n        begin: \"''\",\n        end: \"''\"\n      },\n      {\n        begin: '\"',\n        end: '\"'\n      }\n    ]\n  };\n  const EXPRESSIONS = [\n    hljs.NUMBER_MODE,\n    hljs.HASH_COMMENT_MODE,\n    hljs.C_BLOCK_COMMENT_MODE,\n    STRING,\n    ATTRS\n  ];\n  ANTIQUOTE.contains = EXPRESSIONS;\n  return {\n    name: 'Nix',\n    aliases: [ \"nixos\" ],\n    keywords: NIX_KEYWORDS,\n    contains: EXPRESSIONS\n  };\n}\n\nmodule.exports = nix;\n\n\n//# sourceURL=webpack://renderer/./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/nix.js?");

/***/ })

}]);