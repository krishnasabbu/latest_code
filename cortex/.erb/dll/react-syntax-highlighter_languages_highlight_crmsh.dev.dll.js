/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(global["webpackChunkrenderer"] = global["webpackChunkrenderer"] || []).push([["react-syntax-highlighter_languages_highlight_crmsh"],{

/***/ "./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/crmsh.js":
/*!************************************************************************************************!*\
  !*** ./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/crmsh.js ***!
  \************************************************************************************************/
/***/ ((module) => {

eval("/*\nLanguage: crmsh\nAuthor: Kristoffer Gronlund <kgronlund@suse.com>\nWebsite: http://crmsh.github.io\nDescription: Syntax Highlighting for the crmsh DSL\nCategory: config\n*/\n\n/** @type LanguageFn */\nfunction crmsh(hljs) {\n  const RESOURCES = 'primitive rsc_template';\n  const COMMANDS = 'group clone ms master location colocation order fencing_topology ' +\n      'rsc_ticket acl_target acl_group user role ' +\n      'tag xml';\n  const PROPERTY_SETS = 'property rsc_defaults op_defaults';\n  const KEYWORDS = 'params meta operations op rule attributes utilization';\n  const OPERATORS = 'read write deny defined not_defined in_range date spec in ' +\n      'ref reference attribute type xpath version and or lt gt tag ' +\n      'lte gte eq ne \\\\';\n  const TYPES = 'number string';\n  const LITERALS = 'Master Started Slave Stopped start promote demote stop monitor true false';\n\n  return {\n    name: 'crmsh',\n    aliases: [\n      'crm',\n      'pcmk'\n    ],\n    case_insensitive: true,\n    keywords: {\n      keyword: KEYWORDS + ' ' + OPERATORS + ' ' + TYPES,\n      literal: LITERALS\n    },\n    contains: [\n      hljs.HASH_COMMENT_MODE,\n      {\n        beginKeywords: 'node',\n        starts: {\n          end: '\\\\s*([\\\\w_-]+:)?',\n          starts: {\n            className: 'title',\n            end: '\\\\s*[\\\\$\\\\w_][\\\\w_-]*'\n          }\n        }\n      },\n      {\n        beginKeywords: RESOURCES,\n        starts: {\n          className: 'title',\n          end: '\\\\s*[\\\\$\\\\w_][\\\\w_-]*',\n          starts: {\n            end: '\\\\s*@?[\\\\w_][\\\\w_\\\\.:-]*'\n          }\n        }\n      },\n      {\n        begin: '\\\\b(' + COMMANDS.split(' ').join('|') + ')\\\\s+',\n        keywords: COMMANDS,\n        starts: {\n          className: 'title',\n          end: '[\\\\$\\\\w_][\\\\w_-]*'\n        }\n      },\n      {\n        beginKeywords: PROPERTY_SETS,\n        starts: {\n          className: 'title',\n          end: '\\\\s*([\\\\w_-]+:)?'\n        }\n      },\n      hljs.QUOTE_STRING_MODE,\n      {\n        className: 'meta',\n        begin: '(ocf|systemd|service|lsb):[\\\\w_:-]+',\n        relevance: 0\n      },\n      {\n        className: 'number',\n        begin: '\\\\b\\\\d+(\\\\.\\\\d+)?(ms|s|h|m)?',\n        relevance: 0\n      },\n      {\n        className: 'literal',\n        begin: '[-]?(infinity|inf)',\n        relevance: 0\n      },\n      {\n        className: 'attr',\n        begin: /([A-Za-z$_#][\\w_-]+)=/,\n        relevance: 0\n      },\n      {\n        className: 'tag',\n        begin: '</?',\n        end: '/?>',\n        relevance: 0\n      }\n    ]\n  };\n}\n\nmodule.exports = crmsh;\n\n\n//# sourceURL=webpack://renderer/./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/crmsh.js?");

/***/ })

}]);