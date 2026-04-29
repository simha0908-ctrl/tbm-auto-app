const CACHE_NAME = 'tbm-v1';

// 캐시할 앱 파일 목록
const APP_FILES = [
  './app_mockup.html',
  './manifest.json',
  './data.js',
  './page9_base.js',
  './tbm_base.js',
  './cl_p1_base.js',
  './cl_p2_base.js',
  './cl_p3_base.js',
  './cl_p4_base.js',
  './cl_p5_base.js',
  './cl_p6_base.js',
  './cl_p7_base.js',
  './cl_p8_base.js',
  './cl_p9_base.js',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

// 설치 — 앱 파일 전부 캐시
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(APP_FILES);
    })
  );
  self.skipWaiting();
});

// 활성화 — 이전 버전 캐시 삭제
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(key) { return key !== CACHE_NAME; })
            .map(function(key) { return caches.delete(key); })
      );
    })
  );
  self.clients.claim();
});

// 요청 처리
self.addEventListener('fetch', function(event) {
  const url = event.request.url;

  // Anthropic API — 항상 네트워크 (캐시 안 함)
  if (url.includes('api.anthropic.com') || url.includes('workers.dev')) {
    return;
  }

  // 폰트(Google) — 네트워크 우선, 실패 시 캐시
  if (url.includes('fonts.googleapis.com') || url.includes('fonts.gstatic.com')) {
    event.respondWith(
      fetch(event.request).catch(function() {
        return caches.match(event.request);
      })
    );
    return;
  }

  // 앱 파일 — 캐시 우선 (오프라인 동작)
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      return cached || fetch(event.request);
    })
  );
});
