/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Settable modal with confirmation and call API.
 *
 * @returns
 */
export function modalConfirmCallComponent() {
  return {
    isActive: false,
    title: "",
    content: "",
    apiUrl: "",
    apiMethod: "POST",
    loading: false,
    error: false,

    open(title, content, url = "", method = "POST") {
      this.title = title;
      this.content = content;
      this.apiUrl = url;
      this.apiMethod = method;
      this.isActive = true;
      this.loading = false;
      this.error = false;
    },

    close() {
      this.isActive = false;
      this.loading = false;
      this.error = false;
    },

    async confirm() {
      if (!this.apiUrl) {
        this.close();
        return;
      }
      this.loading = true;
      this.error = false;

      try {
        const response = await fetch(this.apiUrl, { method: this.apiMethod });
        if (!response.ok) throw new Error("API call failed");
        window.dispatchEvent(new CustomEvent("force-refresh")); // REfresh all components
        this.close();
      } catch (e) {
        console.error(e);
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
  };
}

/**
 * Open modal outside Alpine.
 *
 * @param {*} url
 * @param {*} title
 * @param {*} content
 * @param {*} method
 */
export function openModalConfirmCall(url, title, content, method = "POST") {
  const modal = document.querySelector("#modalConfirmCallComponent").__modal;
  modal.open(title, content, url, method);
}