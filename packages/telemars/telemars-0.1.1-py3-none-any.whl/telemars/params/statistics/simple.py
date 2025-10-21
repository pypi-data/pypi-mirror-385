from enum import Enum


class K7Statistic(Enum):
    """Статистики отчета Simple набора данных "Big TV" и "Внедомашний просмотр"."""

    REACH000 = 'Reach000'
    SPOT_BY_BREAKS_REACH000 = 'SpotByBreaksReach000'
    REACH_PER = 'ReachPer'
    SPOT_BY_BREAKS_REACH_PER = 'SpotByBreaksReachPer'
    RTG000 = 'Rtg000'
    SPOT_BY_BREAKS_RTG000 = 'SpotByBreaksRtg000'
    SPOT_BY_BREAKS_SALES_RTG000 = 'SpotByBreaksSalesRtg000'
    RTG_PER = 'RtgPer'
    SPOT_BY_BREAKS_RTG_PER = 'SpotByBreaksRtgPer'
    SPOT_BY_BREAKS_STAND_RTG_PER = 'SpotByBreaksStandRtgPer'
    SPOT_BY_BREAKS_SALES_RTG_PER = 'SpotByBreaksSalesRtgPer'
    SPOT_BY_BREAKS_STAND_SALES_RTG_PER = 'SpotByBreaksStandSalesRtgPer'
    UNIVERSE000 = 'Universe000'
    SAMPLE = 'Sample'
    DURATION = 'Duration'
    QUANTITY = 'Quantity'
    CONSOLIDATED_COST_RUB = 'ConsolidatedCostRUB'
    CONSOLIDATED_COST_USD = 'ConsolidatedCostUSD'
