export const SECTOR_MAP = {
  "科技": "Technology",
  "医疗保健": "Healthcare",
  "金融服务": "Financial Services",
  "必需消费品": "Consumer Defensive",
  "非必需消费品": "Consumer Cyclical",
  "工业": "Industrials",
  "能源": "Energy",
  "公用事业": "Utilities",
  "通信服务": "Communication Services",
  "房地产": "Real Estate",
  "基础材料": "Basic Materials",
} as const;

export const SECTORS_CN = Object.keys(SECTOR_MAP) as Array<keyof typeof SECTOR_MAP>;
export const SECTORS_EN = Object.values(SECTOR_MAP);
