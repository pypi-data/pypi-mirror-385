/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Build AlpineJS lock box components.
 * @param {*} apiUrl
 * @param {*} refreshMs
 * @returns
 */
export function lockBoxComponent(url, refreshMs = 30000) {
  return {
    loading: true,
    error: null,
    lockData: null,
    lockMessage: "",

    async init() {
      await this.loadLock();
      if (refreshMs > 0) {
        setInterval(() => this.loadLock(), refreshMs);
      }
    },

    async loadLock() {
      this.loading = true;
      this.error = null;
      try {
        const res = await fetch(url);

        if (res.status === 404) {
          // Specific handling for never launched
          this.lockData = null;
          this.lockMessage = Translations.never_launched;
          this.loading = false;
          return;
        };

        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const json = await res.json();
        this.lockData = json.data;

        if (this.lockData.locked) {
          this.lockMessage = `${Translations.in_progress_since} ${new Date(this.lockData.locked_at).toLocaleString(undefined, dateTimeOption)}`;
        } else {
          this.lockMessage = `${Translations.completed_since} ${new Date(this.lockData.unlocked_at).toLocaleString(undefined, dateTimeOption)}`;
        }
      } catch (e) {
        this.error = Translations.error_loading_lock_status;
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
  };
}