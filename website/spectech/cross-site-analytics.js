(function () {
  'use strict';

  var counterId = 107569860;

  function sendGoal(name) {
    if (typeof window.ym === 'function') window.ym(counterId, 'reachGoal', name);
  }

  function decorateCommercialLink(link) {
    try {
      var url = new URL(link.getAttribute('href'), window.location.origin);
      if (url.hostname !== 'special-tech.ru' && url.hostname !== 'www.special-tech.ru') return;
      if (!url.searchParams.has('utm_source')) url.searchParams.set('utm_source', 'specialtechnology.ru');
      if (!url.searchParams.has('utm_medium')) url.searchParams.set('utm_medium', 'referral');
      if (!url.searchParams.has('utm_campaign')) url.searchParams.set('utm_campaign', 'cross_site_navigation');
      link.href = url.toString();
    } catch (error) {
      return;
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[href]').forEach(decorateCommercialLink);
  });

  document.addEventListener('click', function (event) {
    var link = event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if (!link) return;

    try {
      var url = new URL(link.getAttribute('href'), window.location.origin);
      if (url.hostname === 'special-tech.ru' || url.hostname === 'www.special-tech.ru') {
        sendGoal('commercial_site_click');
      } else if (url.hostname === window.location.hostname && url.pathname === '/calculator.html') {
        sendGoal('calculator_click');
      }
    } catch (error) {
      return;
    }
  });
})();
