/**
 * Bikram Sambat line under each AD day in FullCalendar month grid (uses nepali-date-converter UMD from base).
 */
(function (global) {
  function nepaliCtor() {
    if (typeof global.NepaliDate === 'undefined') return null;
    return global.NepaliDate.default ? global.NepaliDate.default : global.NepaliDate;
  }

  global.appendNepaliBsToFullCalendarDay = function (info) {
    var Ctor = nepaliCtor();
    if (!Ctor || !info || !info.el) return;
    Ctor.language = 'np';
    var np = new Ctor(info.date);
    var frame = info.el.querySelector('.fc-daygrid-day-frame');
    if (!frame) return;
    var sub = document.createElement('div');
    sub.className = 'fc-nepali-bs';
    sub.style.cssText =
      'font-size:0.65rem;opacity:0.85;text-align:center;line-height:1.2;padding-bottom:3px';
    sub.textContent = np.format('DD MMMM YYYY', 'np');
    frame.appendChild(sub);
  };
})(typeof window !== 'undefined' ? window : global);
