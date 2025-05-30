/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(global["webpackChunkrenderer"] = global["webpackChunkrenderer"] || []).push([["react-syntax-highlighter_languages_highlight_openscad"],{

/***/ "./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/openscad.js":
/*!***************************************************************************************************!*\
  !*** ./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/openscad.js ***!
  \***************************************************************************************************/
/***/ ((module) => {

eval("/*\nLanguage: OpenSCAD\nAuthor: Dan Panzarella <alsoelp@gmail.com>\nDescription: OpenSCAD is a language for the 3D CAD modeling software of the same name.\nWebsite: https://www.openscad.org\nCategory: scientific\n*/\n\nfunction openscad(hljs) {\n  const SPECIAL_VARS = {\n    className: 'keyword',\n    begin: '\\\\$(f[asn]|t|vp[rtd]|children)'\n  };\n  const LITERALS = {\n    className: 'literal',\n    begin: 'false|true|PI|undef'\n  };\n  const NUMBERS = {\n    className: 'number',\n    begin: '\\\\b\\\\d+(\\\\.\\\\d+)?(e-?\\\\d+)?', // adds 1e5, 1e-10\n    relevance: 0\n  };\n  const STRING = hljs.inherit(hljs.QUOTE_STRING_MODE, {\n    illegal: null\n  });\n  const PREPRO = {\n    className: 'meta',\n    keywords: {\n      'meta-keyword': 'include use'\n    },\n    begin: 'include|use <',\n    end: '>'\n  };\n  const PARAMS = {\n    className: 'params',\n    begin: '\\\\(',\n    end: '\\\\)',\n    contains: [\n      'self',\n      NUMBERS,\n      STRING,\n      SPECIAL_VARS,\n      LITERALS\n    ]\n  };\n  const MODIFIERS = {\n    begin: '[*!#%]',\n    relevance: 0\n  };\n  const FUNCTIONS = {\n    className: 'function',\n    beginKeywords: 'module function',\n    end: /=|\\{/,\n    contains: [\n      PARAMS,\n      hljs.UNDERSCORE_TITLE_MODE\n    ]\n  };\n\n  return {\n    name: 'OpenSCAD',\n    aliases: [ 'scad' ],\n    keywords: {\n      keyword: 'function module include use for intersection_for if else \\\\%',\n      literal: 'false true PI undef',\n      built_in: 'circle square polygon text sphere cube cylinder polyhedron translate rotate scale resize mirror multmatrix color offset hull minkowski union difference intersection abs sign sin cos tan acos asin atan atan2 floor round ceil ln log pow sqrt exp rands min max concat lookup str chr search version version_num norm cross parent_module echo import import_dxf dxf_linear_extrude linear_extrude rotate_extrude surface projection render children dxf_cross dxf_dim let assign'\n    },\n    contains: [\n      hljs.C_LINE_COMMENT_MODE,\n      hljs.C_BLOCK_COMMENT_MODE,\n      NUMBERS,\n      PREPRO,\n      STRING,\n      SPECIAL_VARS,\n      MODIFIERS,\n      FUNCTIONS\n    ]\n  };\n}\n\nmodule.exports = openscad;\n\n\n//# sourceURL=webpack://renderer/./node_modules/react-syntax-highlighter/node_modules/highlight.js/lib/languages/openscad.js?");

/***/ })

}]);