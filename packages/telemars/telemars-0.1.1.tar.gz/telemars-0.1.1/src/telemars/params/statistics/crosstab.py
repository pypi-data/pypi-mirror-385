from enum import Enum


class K7Statistic(Enum):
    """Статистики отчета Crosstab набора данных "Big TV" и "Внедомашний просмотр"."""

    # Суммарные статистики.
    CUM_REACH000 = 'CumReach000'
    SPOT_BY_BREAKS_CUM_REACH000 = 'SpotByBreaksCumReach000'
    CUM_REACH_PER = 'CumReachPer'
    SPOT_BY_BREAKS_CUM_REACH_PER = 'SpotByBreaksCumReachPer'
    RTG000_SUM = 'Rtg000Sum'
    SPOT_BY_BREAKS_RTG000_SUM = 'SpotByBreaksRtg000Sum'
    SPOT_BY_BREAKS_SALES_RTG000_SUM = 'SpotByBreaksSalesRtg000Sum'
    RTG_PER_SUM = 'RtgPerSum'
    SPOT_BY_BREAKS_RTG_PER_SUM = 'SpotByBreaksRtgPerSum'
    SPOT_BY_BREAKS_STAND_RTG_PER_SUM = 'SpotByBreaksStandRtgPerSum'
    SPOT_BY_BREAKS_SALES_RTG_PER_SUM = 'SpotByBreaksSalesRtgPerSum'
    SPOT_BY_BREAKS_STAND_SALES_RTG_PER_SUM = 'SpotByBreaksStandSalesRtgPerSum'
    DURATION_SUM = 'DurationSum'
    QUANTITY_SUM = 'QuantitySum'
    CONSOLIDATED_COST_SUM_RUB = 'ConsolidatedCostSumRUB'
    CONSOLIDATED_COST_SUM_USD = 'ConsolidatedCostSumUSD'

    # Средние статистики.
    SPOT_BY_BREAKS_AV_REACH000 = 'SpotByBreaksAvReach000'
    SPOT_BY_BREAKS_AV_REACH_PER = 'SpotByBreaksAvReachPer'
    SPOT_BY_BREAKS_OTS000_AVG = 'SpotByBreaksOTS000Avg'
    SPOT_BY_BREAKS_OTS_PER_AVG = 'SpotByBreaksOTSPerAvg'
    RTG000_AVG = 'Rtg000Avg'
    SPOT_BY_BREAKS_RTG000_AVG = 'SpotByBreaksRtg000Avg'
    SPOT_BY_BREAKS_SALES_RTG000_AVG = 'SpotByBreaksSalesRtg000Avg'
    RTG_PER_AVG = 'RtgPerAvg'
    SPOT_BY_BREAKS_RTG_PER_AVG = 'SpotByBreaksRtgPerAvg'
    SPOT_BY_BREAKS_STAND_RTG_PER_AVG = 'SpotByBreaksStandRtgPerAvg'
    SPOT_BY_BREAKS_SALES_RTG_PER_AVG = 'SpotByBreaksSalesRtgPerAvg'
    SPOT_BY_BREAKS_STAND_SALES_RTG_PER_AVG = 'SpotByBreaksStandSalesRtgPerAvg'
    UNIVERSE000_AVG = 'Universe000Avg'
    SAMPLE_AVG = 'SampleAvg'
    DURATION_AVG = 'DurationAvg'
