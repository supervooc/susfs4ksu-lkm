/**
 * 显示层动态：在静态托管（GitHub Pages）下把 hero 里的版本号刷新为上游最新。
 *
 * 服务端渲染的快照值仍然在 HTML 里，脚本失败或限流时页面保持原样；
 * 成功时用最新 Release tag 覆盖，并缓存 10 分钟，避免每次访问都打 GitHub API。
 */
(() => {
  const pill = document.querySelector('[data-release-pill]');
  const tagEl = pill && pill.querySelector('[data-release-tag]');
  if (!tagEl) return;

  const API = 'https://api.github.com/repos/inforcqb/susfs4ksu-for-lkm/releases/latest';
  const CACHE_KEY = 'susfs-release-tag';
  const TTL = 10 * 60 * 1000;

  const apply = (tag) => {
    if (typeof tag !== 'string' || !tag) return;
    if (tag !== tagEl.textContent) tagEl.textContent = tag;
  };

  const readCache = () => {
    try {
      const raw = window.localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const data = JSON.parse(raw);
      if (!data || typeof data.tag !== 'string' || typeof data.ts !== 'number') return null;
      if (Date.now() - data.ts > TTL) return null;
      return data.tag;
    } catch (error) {
      return null;
    }
  };

  const writeCache = (tag) => {
    try {
      window.localStorage.setItem(CACHE_KEY, JSON.stringify({ tag: tag, ts: Date.now() }));
    } catch (error) {
      // 隐私模式 / 存储被禁用时忽略
    }
  };

  const cached = readCache();
  if (cached) {
    apply(cached);
    return;
  }

  if (!('fetch' in window)) return;

  fetch(API, { headers: { Accept: 'application/vnd.github+json' } })
    .then((response) => (response.ok ? response.json() : null))
    .then((data) => {
      if (!data || typeof data.tag_name !== 'string') return;
      apply(data.tag_name);
      writeCache(data.tag_name);
    })
    .catch(() => {
      // 断网或限流：保留服务端快照
    });
})();
