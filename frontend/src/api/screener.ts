import client from './client'
import type { ScreenCriteria, ScreenResponse } from '../types/screener'

export async function screenStocks(criteria: ScreenCriteria): Promise<ScreenResponse> {
  const response = await client.post('/api/screen', criteria)
  return response.data
}
