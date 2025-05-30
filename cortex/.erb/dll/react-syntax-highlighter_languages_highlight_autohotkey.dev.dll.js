/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(global["webpackChunkrenderer"] = global["webpackChunkrenderer"] || []).push([["react-syntax-highlighter_languages_highlight_autohotkey"],{

/***/ "./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/autohotkey.js":
/*!*****************************************************************************************************!*\
  !*** ./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/autohotkey.js ***!
  \*****************************************************************************************************/
/***/ ((module) => {

eval("/*\nLanguage: AutoHotkey\nAuthor: Seongwon Lee <dlimpid@gmail.com>\nDescription: AutoHotkey language definition\nCategory: scripting\n*/\n\n/** @type LanguageFn */\nfunction autohotkey(hljs) {\n  const BACKTICK_ESCAPE = {\n    begin: '`[\\\\s\\\\S]'\n  };\n\n  return {\n    name: 'AutoHotkey',\n    case_insensitive: true,\n    aliases: ['ahk'],\n    keywords: {\n      keyword: 'Break Continue Critical Exit ExitApp Gosub Goto New OnExit Pause return SetBatchLines SetTimer Suspend Thread Throw Until ahk_id ahk_class ahk_pid ahk_exe ahk_group',\n      literal: 'true false NOT AND OR',\n      built_in: 'ComSpec Clipboard ClipboardAll ErrorLevel'\n    },\n    contains: [\n      BACKTICK_ESCAPE,\n      hljs.inherit(hljs.QUOTE_STRING_MODE, {\n        contains: [BACKTICK_ESCAPE]\n      }),\n      hljs.COMMENT(';', '$', {\n        relevance: 0\n      }),\n      hljs.C_BLOCK_COMMENT_MODE,\n      {\n        className: 'number',\n        begin: hljs.NUMBER_RE,\n        relevance: 0\n      },\n      {\n        // subst would be the most accurate however fails the point of\n        // highlighting. variable is comparably the most accurate that actually\n        // has some effect\n        className: 'variable',\n        begin: '%[a-zA-Z0-9#_$@]+%'\n      },\n      {\n        className: 'built_in',\n        begin: '^\\\\s*\\\\w+\\\\s*(,|%)'\n        // I don't really know if this is totally relevant\n      },\n      {\n        // symbol would be most accurate however is highlighted just like\n        // built_in and that makes up a lot of AutoHotkey code meaning that it\n        // would fail to highlight anything\n        className: 'title',\n        variants: [\n          {\n            begin: '^[^\\\\n\";]+::(?!=)'\n          },\n          {\n            begin: '^[^\\\\n\";]+:(?!=)',\n            // zero relevance as it catches a lot of things\n            // followed by a single ':' in many languages\n            relevance: 0\n          }\n        ]\n      },\n      {\n        className: 'meta',\n        begin: '^\\\\s*#\\\\w+',\n        end: '$',\n        relevance: 0\n      },\n      {\n        className: 'built_in',\n        begin: 'A_[a-zA-Z0-9]+'\n      },\n      {\n        // consecutive commas, not for highlighting but just for relevance\n        begin: ',\\\\s*,'\n      }\n    ]\n  };\n}\n\nmodule.exports = autohotkey;\n\n\n//# sourceURL=webpack://renderer/./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/autohotkey.js?");

/***/ })

}]);