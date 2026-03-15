// 格式化金额（美元）
export const formatCurrency = (value: number | undefined): string => {
  if (value === undefined || value === null) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

// 格式化百分比
export const formatPercent = (value: number | undefined, decimals: number = 2): string => {
  if (value === undefined || value === null) return '-'
  return `${(value * 100).toFixed(decimals)}%`
}

// 格式化数字（带千分位）
export const formatNumber = (value: number | undefined, decimals: number = 0): string => {
  if (value === undefined || value === null) return '-'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

// 格式化日期
export const formatDate = (date: string | Date): string => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('zh-CN')
}
