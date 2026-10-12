/* ==========================================================================
   Chart registry
   --------------------------------------------------------------------------
   One entry per chart on the page, in story order. js/main.js loops over
   this list and draws each chart. Fields:

     id        the id of the empty <div> in index.html that the chart goes in
     spec      path to the Vega-Lite spec, or null if it isn't written yet
     needs     data files the spec loads; if any is missing or empty the page
               shows a note instead of a broken chart
     idiom     what kind of chart it is (shown in the "not built yet" note,
               and a handy checklist against the assignment's idiom count)
     renderer  optional: "canvas" for charts with thousands of marks,
               which draws much faster than the default "svg"
     fitWidth  optional: true for stacked charts (vconcat) that should be
               stretched to the column width (see fitToWidth in main.js)
   ========================================================================== */

const CHARTS = [
  // 01 A nation of pet lovers
  {
    id: "chart-01",
    spec: "specs/01-pet-ownership-waffle.vl.json",
    needs: ["data/ama/pets-in-australia-2025.csv"],
    idiom: "Small-multiple waffle charts",
  },

  // 02 From a few rabbits to 600 million
  {
    id: "chart-02",
    spec: "specs/02-history-timeline.vl.json",
    needs: ["data/history/timeline.csv"],
    idiom: "Annotated timeline",
  },
  {
    id: "chart-03",
    spec: "specs/03-fences-map.vl.json",
    needs: [
      "data/geo/australia-states.topojson",
      "data/geo/rabbit-proof-fences.geojson",
      "data/ala/sightings-points.csv",
    ],
    idiom: "Map: lines over a dot map",
    renderer: "canvas",
  },

  // 03 The virus war
  {
    id: "chart-04",
    spec: "specs/04-rhdv2-slope.vl.json",
    needs: ["data/ramsey/rhdv2-site-abundance.csv"],
    idiom: "Slope chart (log scale)",
  },

  // 04 Still everywhere
  {
    id: "chart-05",
    spec: "specs/05-sightings-by-year-map.vl.json",
    needs: ["data/geo/australia-states.topojson", "data/ala/sightings-grid-by-year.csv"],
    idiom: "Map: gridded proportional symbols, linked to a clickable year bar chart",
    fitWidth: true,
  },
  {
    id: "chart-06",
    spec: "specs/06-sightings-month-heatmap.vl.json",
    needs: ["data/ala/sightings-by-month.csv"],
    idiom: "Heatmap",
  },
  {
    id: "chart-07",
    spec: "specs/07-sightings-density-choropleth.vl.json",
    needs: [
      "data/ala/sightings-by-state-year.csv",
      "data/geo/state-centroids.csv",
      "data/geo/australia-states.topojson",
    ],
    idiom: "Map: choropleth (log colour scale)",
  },

  // 05 The rules, and the risks
  {
    id: "chart-08",
    spec: "specs/08-legal-status-choropleth.vl.json",
    needs: [
      "data/geo/australia-states.topojson",
      "data/geo/state-centroids.csv",
      "data/legal/rabbit-legal-status.csv",
    ],
    idiom: "Map: categorical choropleth",
  },
  {
    id: "chart-09",
    spec: "specs/09-virus-samples-waffle.vl.json",
    needs: ["data/peng/lagovirus-samples.csv"],
    idiom: "Waffle chart",
  },

  // 06 When it doesn't work out
  {
    id: "chart-10",
    spec: "specs/10-rspca-proportional-symbols.vl.json",
    needs: [
      "data/geo/australia-states.topojson",
      "data/geo/state-centroids.csv",
      "data/rspca/other-animals-by-state.csv",
    ],
    idiom: "Map: proportional symbol map",
  },
  {
    id: "chart-11",
    spec: "specs/11-rspca-outcomes-stacked.vl.json",
    needs: ["data/rspca/other-animals-by-state.csv"],
    idiom: "100% stacked bar chart",
  },
];
