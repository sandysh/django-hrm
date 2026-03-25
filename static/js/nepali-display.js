/**
 * Replaces English calendar text with Bikram Sambat (Nepali) using nepali-date-converter (NepaliDate).
 * Mark nodes: class "js-nepali-date" and data-nepali-ad="YYYY-MM-DD" or ISO datetime.
 * Optional: data-nepali-mode="date|datetime|datetime_secs|time|auto" (default auto).
 */
(function () {
  function getNepaliDateCtor() {
    if (typeof NepaliDate === 'undefined') return null;
    return NepaliDate.default ? NepaliDate.default : NepaliDate;
  }

  function parseAd(attr) {
    if (!attr || !String(attr).trim()) return null;
    var s = String(attr).trim();
    if (s.length === 10 && s[4] === '-' && s[7] === '-') {
      var p = s.split('-');
      return new Date(
        parseInt(p[0], 10),
        parseInt(p[1], 10) - 1,
        parseInt(p[2], 10)
      );
    }
    var d = new Date(s);
    return isNaN(d.getTime()) ? null : d;
  }

  function pad2(n) {
    return ('0' + n).slice(-2);
  }

  function formatNepali(adDate, mode) {
    if (!adDate || isNaN(adDate.getTime())) return null;
    var ND = getNepaliDateCtor();
    if (!ND) return null;
    ND.language = 'np';
    var np = new ND(adDate);
    if (mode === 'time') {
      return (
        pad2(adDate.getHours()) +
        ':' +
        pad2(adDate.getMinutes()) +
        ':' +
        pad2(adDate.getSeconds())
      );
    }
    if (mode === 'datetime_secs') {
      return (
        np.format('DD MMMM YYYY', 'np') +
        ', ' +
        pad2(adDate.getHours()) +
        ':' +
        pad2(adDate.getMinutes()) +
        ':' +
        pad2(adDate.getSeconds())
      );
    }
    if (mode === 'datetime') {
      return (
        np.format('DD MMMM YYYY', 'np') +
        ', ' +
        pad2(adDate.getHours()) +
        ':' +
        pad2(adDate.getMinutes())
      );
    }
    return np.format('ddd, DD MMMM YYYY', 'np');
  }

  function inferMode(el, raw) {
    var explicit = el.getAttribute('data-nepali-mode');
    if (explicit && explicit !== 'auto') return explicit;
    if (raw.indexOf('T') >= 0 || raw.length > 10) {
      return el.hasAttribute('data-nepali-time-secs')
        ? 'datetime_secs'
        : 'datetime';
    }
    return 'date';
  }

  function run() {
    var nodes = document.querySelectorAll('.js-nepali-date[data-nepali-ad]');
    nodes.forEach(function (el) {
      var raw = el.getAttribute('data-nepali-ad');
      if (!raw) return;
      var d = parseAd(raw);
      if (!d) return;
      var mode = inferMode(el, raw);
      var out = formatNepali(d, mode);
      if (out) el.textContent = out;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

  window.refreshNepaliDates = run;

  window.updateLiveNepaliDate = function (el) {
    var ND = getNepaliDateCtor();
    if (!ND || !el) return;
    ND.language = 'np';
    el.textContent = new ND().format('ddd, DD MMMM YYYY', 'np');
  };
})();
