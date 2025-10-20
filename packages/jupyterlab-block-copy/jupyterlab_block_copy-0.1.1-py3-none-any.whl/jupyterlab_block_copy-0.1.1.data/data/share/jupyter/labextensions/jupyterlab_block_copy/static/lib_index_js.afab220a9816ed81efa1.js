"use strict";
(self["webpackChunkjupyterlab_block_copy"] = self["webpackChunkjupyterlab_block_copy"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/**
 * Initialization data for the jupyterlab_block_copy extension.
 */
const plugin = {
    id: 'jupyterlab_block_copy:plugin',
    description: 'A JupyterLab extension. block copy/cut events in jupyterLab',
    autoStart: true,
    activate: (app) => {
        console.log('JupyterLab extension jupyterlab_block_copy is activated!');
        // Inject script để chặn events
        const script = document.createElement('script');
        script.textContent = `
      setTimeout(function() {
          // Helper function để chặn event
          function blockEvent(e) {
              e.preventDefault();
              e.stopPropagation();
              e.stopImmediatePropagation();
              return false;
          }

          // Chặn trên document (toàn bộ)
          ['copy', 'cut', 'paste', 'contextmenu'].forEach(eventType => {
              document.addEventListener(eventType, blockEvent, { capture: true });
          });

          // Thêm chặn cụ thể cho notebook container (.jp-Notebook)
          const notebook = document.querySelector('.jp-Notebook');
          if (notebook) {
              ['copy', 'cut', 'paste', 'contextmenu'].forEach(eventType => {
                  notebook.addEventListener(eventType, blockEvent, { capture: true });
              });
          }

          // Để theo dõi cells mới (CodeMirror editors)
          const observer = new MutationObserver(() => {
              const editors = document.querySelectorAll('.cm-editor, .CodeMirror');
              editors.forEach(editor => {
                  ['copy', 'cut', 'paste', 'contextmenu'].forEach(eventType => {
                      editor.addEventListener(eventType, blockEvent, { capture: true });
                  });
              });
          });
          observer.observe(document.body, { childList: true, subtree: true });

          console.log('Full copy/paste blocking script injected!');
      }, 1000);  // Delay 1s để DOM load đầy đủ
    `;
        (document.head || document.documentElement).appendChild(script);
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.afab220a9816ed81efa1.js.map