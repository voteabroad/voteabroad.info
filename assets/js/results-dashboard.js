(function () {
  'use strict';

  var SUMMARY_URL = 'files/results-summary-2024.json';
  var MAX_TABLE_ROWS = 80;
  var state = {
    data: null,
    level: 'countries',
    query: '',
    country: '',
    sort: 'responses',
  };

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function formatNumber(value) {
    return Number(value || 0).toLocaleString('ru-RU');
  }

  function percent(count, total) {
    if (!total) {
      return '0.0';
    }
    return ((count / total) * 100).toFixed(1);
  }

  function candidateLabel(candidate) {
    return candidate.name_ru + ' / ' + candidate.name_en;
  }

  function getCandidate(key) {
    return state.data.candidates.find(function (candidate) {
      return candidate.key === key;
    });
  }

  function topCandidate(row) {
    return state.data.candidates
      .filter(function (candidate) {
        return candidate.key !== 'no_answer';
      })
      .map(function (candidate) {
        return {
          key: candidate.key,
          count: row.candidates[candidate.key] || 0,
        };
      })
      .sort(function (a, b) {
        return b.count - a.count;
      })[0];
  }

  function renderSummaryCards() {
    var totals = state.data.totals;
    var cards = [
      ['Ответов', 'Responses', totals.responses],
      ['Стран', 'Countries', totals.countries],
      ['Городов', 'Cities', totals.cities],
      ['Участков', 'Stations', totals.stations],
    ];

    qs('[data-results-summary]').innerHTML = cards.map(function (card) {
      return '<div class="results-summary-card">' +
        '<span>' + card[0] + ' / ' + card[1] + '</span>' +
        '<strong>' + formatNumber(card[2]) + '</strong>' +
        '</div>';
    }).join('');
  }

  function renderCandidateBars(row) {
    var total = row.responses;
    qs('[data-results-bars]').innerHTML = state.data.candidates.map(function (candidate) {
      var count = row.candidates[candidate.key] || 0;
      var pct = percent(count, total);
      return '<div class="candidate-result">' +
        '<div class="candidate-result__top">' +
        '<strong>' + candidateLabel(candidate) + '</strong>' +
        '<span>' + pct + '% · ' + formatNumber(count) + '</span>' +
        '</div>' +
        '<div class="candidate-result__track">' +
        '<span style="width:' + pct + '%"></span>' +
        '</div>' +
        '</div>';
    }).join('');
  }

  function renderCountryOptions() {
    var select = qs('[data-results-country]');
    select.innerHTML = '<option value="">Все страны / All countries</option>' +
      state.data.countries.map(function (country) {
        return '<option value="' + country.code + '">' + country.name + '</option>';
      }).join('');
  }

  function filteredRows() {
    var rows = state.data[state.level].slice();
    var query = state.query.trim().toLowerCase();
    var country = state.country;

    if (country) {
      rows = rows.filter(function (row) {
        return String(row.country_code || row.code) === country;
      });
    }

    if (query) {
      rows = rows.filter(function (row) {
        return [
          row.name,
          row.country_name,
          row.city_name,
          row.code,
        ].join(' ').toLowerCase().indexOf(query) !== -1;
      });
    }

    rows.sort(function (a, b) {
      if (state.sort === 'name') {
        return a.name.localeCompare(b.name);
      }
      if (state.sort === 'davankov') {
        return (b.candidates.davankov / b.responses) - (a.candidates.davankov / a.responses);
      }
      if (state.sort === 'putin') {
        return (b.candidates.putin / b.responses) - (a.candidates.putin / a.responses);
      }
      return b.responses - a.responses;
    });

    return rows;
  }

  function rowPlace(row) {
    if (state.level === 'countries') {
      return row.name;
    }
    if (state.level === 'cities') {
      return row.name + ', ' + row.country_name;
    }
    return 'УИК ' + row.code + ' / Station ' + row.code + '<br><small>' + row.city_name + ', ' + row.country_name + '</small>';
  }

  function renderTable() {
    var rows = filteredRows();
    var visibleRows = rows.slice(0, MAX_TABLE_ROWS);
    var tbody = qs('[data-results-table] tbody');

    tbody.innerHTML = visibleRows.map(function (row) {
      var leader = topCandidate(row);
      var leaderCandidate = getCandidate(leader.key);
      return '<tr>' +
        '<td>' + rowPlace(row) + '</td>' +
        '<td>' + formatNumber(row.responses) + '</td>' +
        '<td>' + percent(row.candidates.davankov, row.responses) + '%</td>' +
        '<td>' + percent(row.candidates.putin, row.responses) + '%</td>' +
        '<td>' + candidateLabel(leaderCandidate) + '<br><small>' + percent(leader.count, row.responses) + '% · ' + formatNumber(leader.count) + '</small></td>' +
        '</tr>';
    }).join('');

    qs('[data-results-count]').textContent = 'Показано ' + formatNumber(visibleRows.length) + ' из ' + formatNumber(rows.length) + ' / Showing ' + formatNumber(visibleRows.length) + ' of ' + formatNumber(rows.length);
  }

  function render() {
    renderCandidateBars(state.data.totals);
    renderTable();
  }

  function bindControls() {
    qsa('[data-results-level]').forEach(function (button) {
      button.addEventListener('click', function () {
        qsa('[data-results-level]').forEach(function (item) {
          item.classList.remove('is-active');
        });
        button.classList.add('is-active');
        state.level = button.getAttribute('data-results-level');
        renderTable();
      });
    });

    qs('[data-results-search]').addEventListener('input', function (event) {
      state.query = event.target.value;
      renderTable();
    });

    qs('[data-results-country]').addEventListener('change', function (event) {
      state.country = event.target.value;
      renderTable();
    });

    qs('[data-results-sort]').addEventListener('change', function (event) {
      state.sort = event.target.value;
      renderTable();
    });
  }

  function init() {
    var root = qs('[data-results-dashboard]');
    if (!root) {
      return;
    }

    fetch(SUMMARY_URL)
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Could not load results summary');
        }
        return response.json();
      })
      .then(function (data) {
        state.data = data;
        root.classList.remove('is-loading');
        renderSummaryCards();
        renderCountryOptions();
        bindControls();
        render();
      })
      .catch(function () {
        root.innerHTML = '<p class="results-error">Не удалось загрузить сводку результатов. Используйте ссылки на исходные данные выше. / Could not load the results summary. Please use the source links above.</p>';
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
