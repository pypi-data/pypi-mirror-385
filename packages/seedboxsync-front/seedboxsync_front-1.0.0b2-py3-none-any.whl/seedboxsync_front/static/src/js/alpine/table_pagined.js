 /**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

/**
 * Build AlpineJS table pagined components.
 * @param {*} apiUrl
 * @param {*} perPage
 * @returns
 */
export function tablePaginedComponent(apiUrl, perPage = 20) {
  return {
    data: [],
    loading: true,
    error: false,
    page: 1,
    perPage,
    search: '',

    load() {
      this.loading = true;
      this.error = false;
      fetch(apiUrl)
        .then((r) => {
          if (!r.ok) throw new Error();
          return r.json();
        })
        .then((json) => {
          this.data = json.data;
          this.page = 1;
        })
        .catch(() => {
          this.error = true;
          this.data = [];
        })
        .finally(() => {
          this.loading = false;
        });
    },

    // Filter data based on search
    get filteredData() {
      if (!this.search) return this.data;
      const searchLower = this.search.toLowerCase();
      return this.data.filter(item =>
        Object.values(item).some(
          val => String(val).toLowerCase().includes(searchLower)
        )
      );
    },

    // PAgination based on search (or not)
    get totalPages() {
      return Math.ceil(this.filteredData.length / this.perPage);
    },

    get paginatedData() {
      const start = (this.page - 1) * this.perPage;
      return this.filteredData.slice(start, start + this.perPage);
    },

    get visiblePages() {
      const delta = 2;
      const pages = [];
      const start = Math.max(1, this.page - delta);
      const end = Math.min(this.totalPages, this.page + delta);

      if (start > 1) pages.push({ page: 1, isEllipsis: false });
      if (start > 2) pages.push({ page: null, isEllipsis: true });

      for (let i = start; i <= end; i++)
        pages.push({ page: i, isEllipsis: false });

      if (end < this.totalPages - 1)
        pages.push({ page: null, isEllipsis: true });
      if (end < this.totalPages)
        pages.push({ page: this.totalPages, isEllipsis: false });

      return pages;
    },

    // Watch search input and reset page to 1
    updateSearch(value) {
      this.search = value;
      this.page = 1;
    },

    // Init
    init() {
      this.load();
      window.addEventListener("force-refresh", () => this.load());
    },
  };
};
