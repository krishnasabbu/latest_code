/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(global["webpackChunkrenderer"] = global["webpackChunkrenderer"] || []).push([["react-syntax-highlighter_languages_highlight_twig"],{

/***/ "./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/twig.js":
/*!***********************************************************************************************!*\
  !*** ./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/twig.js ***!
  \***********************************************************************************************/
/***/ ((module) => {

eval("/*\nLanguage: Twig\nRequires: xml.js\nAuthor: Luke Holder <lukemh@gmail.com>\nDescription: Twig is a templating language for PHP\nWebsite: https://twig.symfony.com\nCategory: template\n*/\n\nfunction twig(hljs) {\n  var PARAMS = {\n    className: 'params',\n    begin: '\\\\(', end: '\\\\)'\n  };\n\n  var FUNCTION_NAMES = 'attribute block constant cycle date dump include ' +\n                  'max min parent random range source template_from_string';\n\n  var FUNCTIONS = {\n    beginKeywords: FUNCTION_NAMES,\n    keywords: {name: FUNCTION_NAMES},\n    relevance: 0,\n    contains: [\n      PARAMS\n    ]\n  };\n\n  var FILTER = {\n    begin: /\\|[A-Za-z_]+:?/,\n    keywords:\n      'abs batch capitalize column convert_encoding date date_modify default ' +\n      'escape filter first format inky_to_html inline_css join json_encode keys last ' +\n      'length lower map markdown merge nl2br number_format raw reduce replace ' +\n      'reverse round slice sort spaceless split striptags title trim upper url_encode',\n    contains: [\n      FUNCTIONS\n    ]\n  };\n\n  var TAGS = 'apply autoescape block deprecated do embed extends filter flush for from ' +\n    'if import include macro sandbox set use verbatim with';\n\n  TAGS = TAGS + ' ' + TAGS.split(' ').map(function(t){return 'end' + t}).join(' ');\n\n  return {\n    name: 'Twig',\n    aliases: ['craftcms'],\n    case_insensitive: true,\n    subLanguage: 'xml',\n    contains: [\n      hljs.COMMENT(/\\{#/, /#\\}/),\n      {\n        className: 'template-tag',\n        begin: /\\{%/, end: /%\\}/,\n        contains: [\n          {\n            className: 'name',\n            begin: /\\w+/,\n            keywords: TAGS,\n            starts: {\n              endsWithParent: true,\n              contains: [FILTER, FUNCTIONS],\n              relevance: 0\n            }\n          }\n        ]\n      },\n      {\n        className: 'template-variable',\n        begin: /\\{\\{/, end: /\\}\\}/,\n        contains: ['self', FILTER, FUNCTIONS]\n      }\n    ]\n  };\n}\n\nmodule.exports = twig;\n\n\n//# sourceURL=webpack://renderer/./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/twig.js?");

/***/ })

}]);