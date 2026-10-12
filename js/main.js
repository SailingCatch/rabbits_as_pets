/* ==========================================================================
   Draws every chart listed in js/charts.js
   --------------------------------------------------------------------------
   For each chart:
     1. no spec yet?           -> show a "planned" note
     2. a data file missing?   -> show a "data needed" note naming the file
     3. otherwise              -> vegaEmbed draws the spec into its <div>

   THEME is a Vega-Lite "config" object passed to every chart, so fonts,
   colours and axis styling are set once here instead of in every spec.
   ========================================================================== */


/* ---- Shared chart theme ------------------------------------------------- */

// Same values as the tokens at the top of css/style.css
const COLOURS = {
  ink: "#1e2b2a",
  inkMuted: "#5b6b66",
  rule: "#c9d1c8",
  land: "#e3e8e1",
  pet: "#4a64b0",
  pest: "#c0662b",
  // Ochre ramp for "how many" (light = few, dark = many)
  ochreRamp: ["#f6e7c8", "#e9c27f", "#d3913f", "#a9611f", "#6e3a12"],
};

const FONT = "Bricolage Grotesque";

const THEME = {
  font: FONT,
  background: null,               // transparent: the page colour shows through
  view: { stroke: null },         // no box around each chart
  padding: { top: 4, right: 4, bottom: 4, left: 4 },

  axis: {
    labelColor: COLOURS.inkMuted,
    labelFontSize: 12,
    titleColor: COLOURS.ink,
    titleFontSize: 12,
    titleFontWeight: 500,
    domainColor: COLOURS.rule,
    tickColor: COLOURS.rule,
    gridColor: "#dde3dc",
  },

  legend: {
    labelColor: COLOURS.inkMuted,
    labelFontSize: 12,
    titleColor: COLOURS.ink,
    titleFontSize: 12,
    titleFontWeight: 500,
    labelLimit: 0,                 // 0 = never cut labels short with "…"
    titleLimit: 0,
    orient: "bottom",
    direction: "horizontal",
  },

  header: {                        // facet titles in small multiples
    labelColor: COLOURS.ink,
    labelFontSize: 13,
    labelFontWeight: 600,
  },

  text: { font: FONT, color: COLOURS.ink },

  range: {
    category: [COLOURS.pet, COLOURS.pest],
    ramp: COLOURS.ochreRamp,       // default for quantitative colour
    heatmap: COLOURS.ochreRamp,
  },
};


/* ---- Helpers ------------------------------------------------------------ */

// True if the file exists and has more than a header row.
// A CSV with only column names counts as "not filled in yet".
async function fileHasData(path) {
  try {
    const response = await fetch(path);
    if (!response.ok) return false;
    const text = await response.text();
    if (path.endsWith(".csv")) {
      return text.trim().split("\n").length > 1;
    }
    return text.trim().length > 0;
  } catch (error) {
    return false;
  }
}

// Replace the chart's <div> contents with a short dashed-border note.
function showNote(container, html) {
  container.innerHTML = `<div class="chart__note">${html}</div>`;
}


/* ---- Draw one chart ----------------------------------------------------- */

async function drawChart(chart) {
  const container = document.getElementById(chart.id);
  if (!container) {
    console.warn(`No <div id="${chart.id}"> in index.html`);
    return;
  }

  if (!chart.spec) {
    showNote(container, `Planned: ${chart.idiom}`);
    return;
  }

  // Check every data file before drawing, so a missing file gives a clear
  // message instead of an empty or half-drawn chart.
  const missing = [];
  for (const path of chart.needs) {
    if (!(await fileHasData(path))) missing.push(path);
  }
  if (missing.length > 0) {
    const list = missing.map((path) => `<code>${path}</code>`).join(", ");
    showNote(container, `Data needed: ${list}. See <code>data/README.md</code>.`);
    return;
  }

  try {
    await vegaEmbed(container, chart.spec, {
      config: THEME,
      actions: false,                       // hide the "..." export menu
      renderer: chart.renderer || "svg",    // canvas is faster for many points
    });
  } catch (error) {
    console.error(`Could not draw ${chart.id}`, error);
    showNote(container, `Could not draw this chart: ${error.message}`);
  }
}


/* ---- Draw them all ------------------------------------------------------ */

// Wait for the web fonts first, otherwise Vega measures label widths with
// the fallback font and the labels end up misplaced.
document.fonts.ready.then(() => {
  CHARTS.forEach(drawChart);
});
