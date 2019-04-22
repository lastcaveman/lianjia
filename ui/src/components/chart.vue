<template>
  <div>
    <v-chart :force-fit="true" :height="height" :data="data" :scale="scale">
      <v-tooltip/>
      <v-axis/>
      <v-legend/>
      <v-line position="month*value" color="city"/>
      <v-point position="month*value" color="city" :size="4" :v-style="style" :shape="'circle'"/>
    </v-chart>
  </div>
</template>

<script>
const DataSet = require("@antv/data-set");
const sourceData = [
  { month: "Jan", Tokyo: 7.0, London: 3.9, Hongkonk: 13 },
  { month: "Feb", Tokyo: 6.9, London: 4.2, Hongkonk: 13 },
  { month: "Mar", Tokyo: 9.5, London: 5.7, Hongkonk: 13 },
  { month: "Apr", Tokyo: 14.5, London: 8.5, Hongkonk: 13 },
  { month: "May", Tokyo: 18.4, London: 11.9, Hongkonk: 13 },
  { month: "Jun", Tokyo: 21.5, London: 15.2, Hongkonk: 13 },
  { month: "Jul", Tokyo: 25.2, London: 17.0, Hongkonk: 13 },
  { month: "Aug", Tokyo: 26.5, London: 16.6, Hongkonk: 13 },
  { month: "Sep", Tokyo: 23.3, London: 14.2, Hongkonk: 13 },
  { month: "Oct", Tokyo: 18.3, London: 10.3, Hongkonk: 13 },
  { month: "Nov", Tokyo: 13.9, London: 6.6, Hongkonk: 13 },
  { month: "Dec", Tokyo: 9.6, London: 4.8, Hongkonk: 13 }
];

const dv = new DataSet.View().source(sourceData);
dv.transform({
  type: "fold",
  fields: ["Tokyo", "London", "Hongkonk"],
  key: "city",
  value: "value"
});
const data = dv.rows;
console.log(dv.rows);
const scale = [
  {
    dataKey: "month",
    min: 0,
    max: 1
  }
];

export default {
  name: "chart",
  data() {
    return {
      data,
      scale,
      height: 400,
      style: { stroke: "#fff", lineWidth: 1 }
    };
  }
};
</script>
