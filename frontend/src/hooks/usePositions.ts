import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Position, OpenPositionRequest } from '@/types/position'

export function usePositions() {
  return useQuery({
    queryKey: ['positions'],
    queryFn: async () => {
      const res = await api.get('/trading/positions')
      return res.data as Position[]
    },
    refetchInterval: 5000,
  })
}

export function useOpenPosition() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: OpenPositionRequest) => {
      const res = await api.post('/trading/positions', data)
      return res.data as Position
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] })
    },
  })
}

export function useClosePosition() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ positionId, exitPrice }: { positionId: string; exitPrice: number }) => {
      const res = await api.post(`/trading/positions/${positionId}/close`, { exit_price: exitPrice })
      return res.data as Position
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] })
    },
  })
}
