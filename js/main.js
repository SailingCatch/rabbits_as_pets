/* ==========================================================================
   Draws every chart listed in js/charts.js
   --------------------------------------------------------------------------
   For each chart:
     1. no spec yet?           -> show a "planned" note
     2. a data file missing?   -> show a "data needed" note naming the file
     3. otherwise              -> vegaEmbed draws the spec into its <div>

   THEME is a Vega-Lite "config" object passed to every chart, so fonts,
   colours and axis styling are set once here instead of in every spec.

   Charts marked fitWidth in js/charts.js are stacked views (vconcat), which
   Vega-Lite can't size to their box by itself. For those, the spec is
   loaded first and each view's width is set to the box's width (heights
   scale with it), so they fill the column on any screen.
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
  gum: "#00806a",
  wattle: "#b3820f",
  plum: "#a3478f",
  olive: "#6b8e23",
  neutral: "#a3aea8",
  // Ochre ramp for "how many" (light = few, dark = many)
  ochreRamp: ["#f6e7c8", "#e9c27f", "#d3913f", "#a9611f", "#6e3a12"],
};

// Categorical order: always assigned in this order, never cycled
const CATEGORICAL = [
  COLOURS.pet, COLOURS.pest, COLOURS.gum, COLOURS.wattle, COLOURS.plum, COLOURS.olive,
];

const FONT = "Bricolage Grotesque";

const THEME = {
  font: FONT,
  background: null,               // transparent: the page colour shows through
  view: { stroke: null },         // no box around each chart
  padding: { top: 4, right: 4, bottom: 4, left: 4 },

  // Newspaper-style axes: no axis lines or tick marks, faint gridlines only
  // on the value axis, muted labels. Specs can still turn things back on.
  axis: {
    labelColor: COLOURS.inkMuted,
    labelFontSize: 12,
    titleColor: COLOURS.inkMuted,
    titleFontSize: 12,
    titleFontWeight: 400,
    domain: false,
    ticks: false,
    labelPadding: 6,
    gridColor: "#dde3dc",
    gridWidth: 1,
  },
  axisBand: { grid: false },        // no gridlines between categories

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
    category: CATEGORICAL,
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

// For stacked charts: set every view's width to the box width, and scale
// fixed heights by the same amount so maps keep their shape.
async function fitToWidth(specPath, container) {
  const spec = await (await fetch(specPath)).json();
  const width = Math.floor(container.clientWidth) - 8;   // minus padding
  for (const view of spec.vconcat || []) {
    if (typeof view.width !== "number") continue;
    const scale = width / view.width;
    view.width = width;
    if (view.projection && typeof view.height === "number") {
      // Keep maps a sensible height on very wide screens
      view.height = Math.min(Math.round(view.height * scale), 620);
    }
  }
  return spec;
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
    const spec = chart.fitWidth ? await fitToWidth(chart.spec, container) : chart.spec;
    await vegaEmbed(container, spec, {
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
