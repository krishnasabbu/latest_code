/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(global["webpackChunkrenderer"] = global["webpackChunkrenderer"] || []).push([["react-syntax-highlighter_languages_highlight_apache"],{

/***/ "./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/apache.js":
/*!*************************************************************************************************!*\
  !*** ./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/apache.js ***!
  \*************************************************************************************************/
/***/ ((module) => {

eval("/*\nLanguage: Apache config\nAuthor: Ruslan Keba <rukeba@gmail.com>\nContributors: Ivan Sagalaev <maniac@softwaremaniacs.org>\nWebsite: https://httpd.apache.org\nDescription: language definition for Apache configuration files (httpd.conf & .htaccess)\nCategory: common, config\nAudit: 2020\n*/\n\n/** @type LanguageFn */\nfunction apache(hljs) {\n  const NUMBER_REF = {\n    className: 'number',\n    begin: /[$%]\\d+/\n  };\n  const NUMBER = {\n    className: 'number',\n    begin: /\\d+/\n  };\n  const IP_ADDRESS = {\n    className: \"number\",\n    begin: /\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}(:\\d{1,5})?/\n  };\n  const PORT_NUMBER = {\n    className: \"number\",\n    begin: /:\\d{1,5}/\n  };\n  return {\n    name: 'Apache config',\n    aliases: [ 'apacheconf' ],\n    case_insensitive: true,\n    contains: [\n      hljs.HASH_COMMENT_MODE,\n      {\n        className: 'section',\n        begin: /<\\/?/,\n        end: />/,\n        contains: [\n          IP_ADDRESS,\n          PORT_NUMBER,\n          // low relevance prevents us from claming XML/HTML where this rule would\n          // match strings inside of XML tags\n          hljs.inherit(hljs.QUOTE_STRING_MODE, { relevance: 0 })\n        ]\n      },\n      {\n        className: 'attribute',\n        begin: /\\w+/,\n        relevance: 0,\n        // keywords aren’t needed for highlighting per se, they only boost relevance\n        // for a very generally defined mode (starts with a word, ends with line-end\n        keywords: {\n          nomarkup:\n            'order deny allow setenv rewriterule rewriteengine rewritecond documentroot ' +\n            'sethandler errordocument loadmodule options header listen serverroot ' +\n            'servername'\n        },\n        starts: {\n          end: /$/,\n          relevance: 0,\n          keywords: { literal: 'on off all deny allow' },\n          contains: [\n            {\n              className: 'meta',\n              begin: /\\s\\[/,\n              end: /\\]$/\n            },\n            {\n              className: 'variable',\n              begin: /[\\$%]\\{/,\n              end: /\\}/,\n              contains: [\n                'self',\n                NUMBER_REF\n              ]\n            },\n            IP_ADDRESS,\n            NUMBER,\n            hljs.QUOTE_STRING_MODE\n          ]\n        }\n      }\n    ],\n    illegal: /\\S/\n  };\n}\n\nmodule.exports = apache;\n\n\n//# sourceURL=webpack://renderer/./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/apache.js?");

/***/ })

}]);