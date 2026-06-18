/**
 * Wires @rato-guras-technology/nepali-date-picker to hidden inputs storing AD YYYY-MM-DD for Django.
 * Expects window.NepaliDatePicker (UMD) with .NepaliDate and .NepaliDatePicker.
 */
(function (global) {
  function getBundle() {
    return global.NepaliDatePicker;
  }

  function NepaliDateCls() {
    var b = getBundle();
    return b && b.NepaliDate;
  }

  function PickerCls() {
    var b = getBundle();
    return b && b.NepaliDatePicker;
  }

  function adYmdToBsObject(ymd) {
    if (!ymd || typeof ymd !== 'string') return null;
    var p = ymd.trim().split('-');
    if (p.length !== 3) return null;
    var g = new Date(
      parseInt(p[0], 10),
      parseInt(p[1], 10) - 1,
      parseInt(p[2], 10)
    );
    var ND = NepaliDateCls();
    if (!ND) return null;
    return ND.fromGregorian(g).toObject();
  }

  function bsObjectToAdYmd(bs) {
    var ND = NepaliDateCls();
    if (!ND || !bs) return '';
    // nepali-date-converter uses monthIndex (0-11) like JS Date.
    var nd = new ND(bs.year, bs.month, bs.day);
    // The NepaliDate instance from this picker library exposes `toGregorian()`
    // (not `toJsDate()`).
    var jsDate = null;
    if (typeof nd.toGregorian === 'function') {
      jsDate = nd.toGregorian();
    } else if (typeof nd.toJsDate === 'function') {
      jsDate = nd.toJsDate();
    }
    if (!jsDate) return '';
    var y = jsDate.getFullYear();
    var m = String(jsDate.getMonth() + 1).padStart(2, '0');
    var d = String(jsDate.getDate()).padStart(2, '0');
    return y + '-' + m + '-' + d;
  }

  /**
   * @param {string} visibleSelector - text input (readonly) for BS display
   * @param {string|HTMLInputElement} hiddenField - hidden input with name for form submit
   * @param {object} [options]
   * @param {boolean} [options.disablePastDates]
   * @param {function(object): void} [options.onSelect] - receives BS object
   */
  global.initNepaliDateHiddenField = function (visibleSelector, hiddenField, options) {
    var opts = options || {};
    var Picker = PickerCls();
    var hidden =
      typeof hiddenField === 'string'
        ? document.querySelector(hiddenField)
        : hiddenField;
    if (!Picker || !hidden) return null;

    var initial = hidden.value ? adYmdToBsObject(hidden.value) : null;

    var picker = new Picker(visibleSelector, {
      language: 'ne',
      primaryColor: '#4F46E5',
      closeOnSelect: true,
      disablePastDates: !!opts.disablePastDates,
      initialDate: initial || undefined,
      onDateSelect: function (bs) {
        hidden.value = bsObjectToAdYmd(bs);
        if (opts.onSelect) opts.onSelect(bs);
      },
    });

    if (!hidden.value) {
      hidden.value = bsObjectToAdYmd(picker.getDate());
    }

    return picker;
  };

  global.bsObjectToAdYmd = bsObjectToAdYmd;
  global.adYmdToBsObject = adYmdToBsObject;
})(typeof window !== 'undefined' ? window : global);
