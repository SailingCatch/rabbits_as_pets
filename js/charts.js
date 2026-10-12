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
     play      optional: adds a Play button that moves a slider parameter
               smoothly, e.g. { param: "t", from: 2010, to: 2025, seconds: 15 }
   ========================================================================== */

const CHARTS = [
  // 01 A nation of pet lovers
  {
    id: "chart-01",
    spec: "specs/01-pet-ownership-waffle.vl.json",
    needs: ["data/ama/pets-in-australia-2025.csv"],
    idiom: "Small-multiple waffle charts",
  },
  {
    id: "chart-01b",
    spec: "specs/01b-one-in-65-pictogram.vl.json",
    needs: [],
    idiom: "Pictogram (Isotype)",
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
    // Alternative: specs/03-fences-map.vl.json (dots instead of hexagons;
    // needs data/ala/sightings-points.csv, and renderer: "canvas")
    spec: "specs/03-fences-hexmap.vl.json",
    needs: [
      "data/geo/australia-states.topojson",
      "data/geo/rabbit-proof-fences.geojson",
      "data/ala/sightings-hexbins.geojson",
    ],
    idiom: "Map: hexagon density map with lines",
  },

  // 03 The virus war
  {
    id: "chart-04",
    spec: "specs/04-rhdv2-dumbbell.vl.json",
    needs: ["data/ramsey/rhdv2-site-abundance.csv"],
    idiom: "Dumbbell chart (before → after)",
  },
  {
    id: "chart-04a",
    spec: "specs/04a-rhd-sites-small-multiples.vl.json",
    needs: ["data/anrd/rhd-sites.csv"],
    idiom: "Small-multiple line charts",
  },

  // 04 Still everywhere
  {
    id: "chart-05",
    spec: "specs/05-sightings-by-year-map.vl.json",
    needs: ["data/geo/australia-states.topojson", "data/ala/sightings-grid-by-year.csv"],
    idiom: "Map: gridded proportional symbols with a smooth time slider, plus yearly bar chart",
    fitWidth: true,
    renderer: "canvas",                     // redraws faster while playing
    play: { param: "t", from: 2010, to: 2025, seconds: 15 },
  },
  {
    id: "chart-06",
    // Alternative: specs/06-sightings-month-heatmap.vl.json
    // (needs data/ala/sightings-by-month.csv)
    spec: "specs/06-seasons-ridgeline.vl.json",
    needs: ["data/ala/sightings-by-state-month.csv"],
    idiom: "Ridgeline chart",
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
    // Alternative: specs/08-legal-status-choropleth.vl.json (real state
    // shapes; also needs the two data/geo files)
    spec: "specs/08-legal-status-tilemap.vl.json",
    needs: ["data/legal/rabbit-legal-status.csv"],
    idiom: "Map: hexagon tile map",
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
    // Alternative: specs/11-rspca-outcomes-stacked.vl.json (100% stacked bars)
    spec: "specs/11-rspca-outcomes-marimekko.vl.json",
    needs: ["data/rspca/other-animals-by-state.csv"],
    idiom: "Marimekko (mosaic) chart",
  },
];
