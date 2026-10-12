/* ==========================================================================
   Chart registry
   --------------------------------------------------------------------------
   One entry per chart on the page, in story order. js/main.js loops over
   this list and draws each chart. Fields:

     id      the id of the empty <div> in index.html that the chart goes in
     spec    path to the Vega-Lite spec, or null if it isn't written yet
     needs   data files the spec loads; if any is missing or empty the page
             shows a note instead of a broken chart
     idiom   what kind of chart it is (shown in the "not built yet" note,
             and a handy checklist against the assignment's idiom count)
     renderer  optional: "canvas" for charts with thousands of marks,
               which draws much faster than the default "svg"
   ========================================================================== */

const CHARTS = [
  // Section 1 – wild rabbits are everywhere people live
  {
    id: "chart-01",
    spec: "specs/01-sightings-dot-map.vl.json",
    needs: ["data/geo/australia-states.topojson", "data/ala/sightings-points.csv"],
    idiom: "Map: dot map",
    renderer: "canvas",
  },

  // Section 2 – where you're allowed to keep one
  {
    id: "chart-02",
    spec: "specs/02-legal-status-choropleth.vl.json",
    needs: [
      "data/geo/australia-states.topojson",
      "data/geo/state-centroids.csv",
      "data/legal/rabbit-legal-status.csv",
    ],
    idiom: "Map: categorical choropleth",
  },

  // Section 3 – the wild population
  {
    id: "chart-03",
    spec: "specs/03-sightings-grid-small-multiples.vl.json",
    needs: ["data/geo/australia-states.topojson", "data/ala/sightings-grid-by-year.csv"],
    idiom: "Map: gridded proportional symbols, small multiples",
  },
  {
    id: "chart-04",
    spec: "specs/04-sightings-month-heatmap.vl.json",
    needs: ["data/ala/sightings-by-month.csv"],
    idiom: "Heatmap",
  },
  {
    id: "chart-05",
    spec: null,
    needs: [],
    idiom: "Ranked bar chart (sightings per 1,000 km²)",
  },

  // Section 4 – small pets in shelters
  {
    id: "chart-06",
    spec: "specs/06-rspca-proportional-symbols.vl.json",
    needs: [
      "data/geo/australia-states.topojson",
      "data/geo/state-centroids.csv",
      "data/rspca/other-animals-by-state.csv",
    ],
    idiom: "Map: proportional symbol map",
  },
  { id: "chart-07", spec: null, needs: [], idiom: "Heatmap (state × year)" },
  { id: "chart-08", spec: null, needs: [], idiom: "Line chart (or bump chart)" },
  { id: "chart-09", spec: null, needs: [], idiom: "Slope chart (2010–11 vs 2024–25)" },
  { id: "chart-10", spec: null, needs: [], idiom: "100% stacked bar chart" },

  // Section 5 – disease
  { id: "chart-11", spec: null, needs: [], idiom: "Waffle chart" },

  // Section 6 – care
  { id: "chart-12", spec: null, needs: [], idiom: "Dot plot" },
];
