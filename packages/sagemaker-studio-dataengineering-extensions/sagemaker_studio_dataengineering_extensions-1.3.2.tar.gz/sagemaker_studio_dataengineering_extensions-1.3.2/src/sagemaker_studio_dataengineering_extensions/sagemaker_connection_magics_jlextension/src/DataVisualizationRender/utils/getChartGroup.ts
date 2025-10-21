const XY_CHARTS: string[] = ["LINE", "BAR", "SCATTER", "AREA"];
const CATEGORY_CHARTS: string[] = ["PIE", "FUNNEL"];
const FINANCIAL_CHARTS: string[] = ["CANDLESTICK"];
const CUMULATIVE_CHARTS: string[] = ["WATERFALL"];
const DISTRIBUTION_CHARTS: string[] = ["HISTOGRAM"];
const BOX_CHARTS: string[] = ["BOX"]
const HEATMAP: string[] = ["HEATMAP"]

export enum ChartGroup {
  XY = 'XY',
  CATEGORY = 'CATEGORY',
  FINANCIAL = 'FINANCIAL',
  CUMULATIVE = 'CUMULATIVE',
  DISTRIBUTION = 'DISTRIBUTION',
  BOX = 'BOX',
  HEATMAP = 'HEATMAP'
}

export function inferChartGroup(chartType: string) {
  if (XY_CHARTS.includes(chartType)) {
    return ChartGroup.XY
  }
  else if (CATEGORY_CHARTS.includes(chartType)) {
    return ChartGroup.CATEGORY
  }
  else if (FINANCIAL_CHARTS.includes(chartType)) {
    return ChartGroup.FINANCIAL
  }
  else if (CUMULATIVE_CHARTS.includes(chartType)) {
    return ChartGroup.CUMULATIVE
  }
  else if (DISTRIBUTION_CHARTS.includes(chartType)) {
    return ChartGroup.DISTRIBUTION
  }
  else if (BOX_CHARTS.includes(chartType)) {
    return ChartGroup.BOX
  }
  else if (HEATMAP.includes(chartType)) {
    return ChartGroup.HEATMAP
  }
  else {
    throw new Error(`Unknown chart type: ${chartType}`)
  }
}