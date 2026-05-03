const CACHE_NAME = 'tbm-v2';

const STATIC_FILES = [
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

// 설치 — 정적 파일만 사전 캐시
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(STATIC_FILES);
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

  // Anthropic API — 항상 네트워크
  if (url.includes('api.anthropic.com') || url.includes('workers.dev')) {
    return;
  }

  // 폰트 — 네트워크 우선, 실패 시 캐시
  if (url.includes('fonts.googleapis.com') || url.includes('fonts.gstatic.com')) {
    event.respondWith(
      fetch(event.request).catch(function() {
        return caches.match(event.request);
      })
    );
    return;
  }

  // index.html — 네트워크 우선 (항상 최신 버전), 실패 시 캐시
  if (url.endsWith('/') || url.includes('index.html')) {
    event.respondWith(
      fetch(event.request).then(function(response) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, clone);
        });
        return response;
      }).catch(function() {
        return caches.match(event.request);
      })
    );
    return;
  }

  // 나머지 정적 파일 — 캐시 우선 (빠른 로딩 + 오프라인)
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      return cached || fetch(event.request).then(function(response) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, clone);
        });
        return response;
      });
    })
  );
});
