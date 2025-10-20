import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Initialization data for the jupyterlab_block_copy extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_block_copy:plugin',
  description: 'A JupyterLab extension. block copy/cut events in jupyterLab',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
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
          ['copy', 'cut','contextmenu'].forEach(eventType => {
              document.addEventListener(eventType, blockEvent, { capture: true });
          });

          // Thêm chặn cụ thể cho notebook container (.jp-Notebook)
          const notebook = document.querySelector('.jp-Notebook');
          if (notebook) {
              ['copy', 'cut', 'contextmenu'].forEach(eventType => {
                  notebook.addEventListener(eventType, blockEvent, { capture: true });
              });
          }

          // Để theo dõi cells mới (CodeMirror editors)
          const observer = new MutationObserver(() => {
              const editors = document.querySelectorAll('.cm-editor, .CodeMirror');
              editors.forEach(editor => {
                  ['copy', 'cut','contextmenu'].forEach(eventType => {
                      editor.addEventListener(eventType, blockEvent, { capture: true });
                  });
              });
          });
          observer.observe(document.body, { childList: true, subtree: true });

          console.log('Full copy/cut blocking script injected!');
      }, 1000);  // Delay 1s để DOM load đầy đủ
    `;
    (document.head || document.documentElement).appendChild(script);
  }
};

export default plugin;
