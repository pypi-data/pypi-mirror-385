// callback to listen to dom changes
(() => {
  // Check if the observer already exists
  if (!window.domUpdateObserver) {
    const observer = new MutationObserver((mutations) => {
      const now = Date.now();
      window.localStorage.setItem('lastDomChange', now);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    window.domUpdateObserver = observer;
  }
})();
