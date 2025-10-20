"""

交互模式下绘制相关图形，如K线图，美式K线图
"""
from __future__ import annotations
import atexit as atexit
from datetime import date
from datetime import datetime
from datetime import timedelta
from hikyuu import analysis
from hikyuu.analysis.analysis import analysis_sys_list
from hikyuu.analysis.analysis import analysis_sys_list_multi
from hikyuu.analysis.analysis import combinate_ind_analysis
from hikyuu.analysis.analysis import combinate_ind_analysis_multi
from hikyuu import core
from hikyuu import cpp
import hikyuu.cpp.core310
from hikyuu.cpp.core310 import ABS
from hikyuu.cpp.core310 import ACOS
from hikyuu.cpp.core310 import AD
from hikyuu.cpp.core310 import ADVANCE
from hikyuu.cpp.core310 import AF_EqualWeight
from hikyuu.cpp.core310 import AF_FixedWeight
from hikyuu.cpp.core310 import AF_FixedWeightList
from hikyuu.cpp.core310 import AF_MultiFactor
from hikyuu.cpp.core310 import AGG_COUNT
from hikyuu.cpp.core310 import AGG_FUNC
from hikyuu.cpp.core310 import AGG_MAD
from hikyuu.cpp.core310 import AGG_MAX
from hikyuu.cpp.core310 import AGG_MEAN
from hikyuu.cpp.core310 import AGG_MEDIAN
from hikyuu.cpp.core310 import AGG_MIN
from hikyuu.cpp.core310 import AGG_PROD
from hikyuu.cpp.core310 import AGG_QUANTILE
from hikyuu.cpp.core310 import AGG_STD
from hikyuu.cpp.core310 import AGG_SUM
from hikyuu.cpp.core310 import AGG_VAR
from hikyuu.cpp.core310 import ALIGN
from hikyuu.cpp.core310 import AMA
from hikyuu.cpp.core310 import ASIN
from hikyuu.cpp.core310 import ATAN
from hikyuu.cpp.core310 import ATR
from hikyuu.cpp.core310 import AVEDEV
from hikyuu.cpp.core310 import AllocateFundsBase
from hikyuu.cpp.core310 import BACKSET
from hikyuu.cpp.core310 import BARSCOUNT
from hikyuu.cpp.core310 import BARSLAST
from hikyuu.cpp.core310 import BARSLASTCOUNT
from hikyuu.cpp.core310 import BARSSINCE
from hikyuu.cpp.core310 import BARSSINCEN
from hikyuu.cpp.core310 import BETWEEN
from hikyuu.cpp.core310 import BLOCKSETNUM
from hikyuu.cpp.core310 import BUSINESS
from hikyuu.cpp.core310 import Block
from hikyuu.cpp.core310 import BlockInfoDriver
from hikyuu.cpp.core310 import BorrowRecord
from hikyuu.cpp.core310 import BrokerPositionRecord
from hikyuu.cpp.core310 import CEILING
from hikyuu.cpp.core310 import CN_Bool
from hikyuu.cpp.core310 import CN_OPLine
from hikyuu.cpp.core310 import CONTEXT
from hikyuu.cpp.core310 import CONTEXT_K
from hikyuu.cpp.core310 import CORR
from hikyuu.cpp.core310 import COS
from hikyuu.cpp.core310 import COST
from hikyuu.cpp.core310 import COUNT
from hikyuu.cpp.core310 import CROSS
from hikyuu.cpp.core310 import CVAL
from hikyuu.cpp.core310 import CYCLE
from hikyuu.cpp.core310 import C_AMO
from hikyuu.cpp.core310 import C_CLOSE
from hikyuu.cpp.core310 import C_HIGH
from hikyuu.cpp.core310 import C_KDATA
from hikyuu.cpp.core310 import C_LOW
from hikyuu.cpp.core310 import C_OPEN
from hikyuu.cpp.core310 import C_VOL
from hikyuu.cpp.core310 import ConditionBase
from hikyuu.cpp.core310 import Constant
from hikyuu.cpp.core310 import CostRecord
from hikyuu.cpp.core310 import DATE
from hikyuu.cpp.core310 import DAY
from hikyuu.cpp.core310 import DECLINE
from hikyuu.cpp.core310 import DEVSQ
from hikyuu.cpp.core310 import DIFF
from hikyuu.cpp.core310 import DISCARD
from hikyuu.cpp.core310 import DMA
from hikyuu.cpp.core310 import DOWNNDAY
from hikyuu.cpp.core310 import DROPNA
from hikyuu.cpp.core310 import DataDriverFactory
from hikyuu.cpp.core310 import Datetime
from hikyuu.cpp.core310 import DatetimeList
from hikyuu.cpp.core310 import Days
from hikyuu.cpp.core310 import EMA
from hikyuu.cpp.core310 import EVERY
from hikyuu.cpp.core310 import EV_Bool
from hikyuu.cpp.core310 import EV_TwoLine
from hikyuu.cpp.core310 import EXIST
from hikyuu.cpp.core310 import EXP
from hikyuu.cpp.core310 import EnvironmentBase
from hikyuu.cpp.core310 import FILTER
from hikyuu.cpp.core310 import FINANCE
from hikyuu.cpp.core310 import FLOOR
from hikyuu.cpp.core310 import FundsRecord
from hikyuu.cpp.core310 import GROUP_COUNT
from hikyuu.cpp.core310 import GROUP_FUNC
from hikyuu.cpp.core310 import GROUP_MAX
from hikyuu.cpp.core310 import GROUP_MEAN
from hikyuu.cpp.core310 import GROUP_MIN
from hikyuu.cpp.core310 import GROUP_PROD
from hikyuu.cpp.core310 import GROUP_SUM
from hikyuu.cpp.core310 import HHV
from hikyuu.cpp.core310 import HHVBARS
from hikyuu.cpp.core310 import HKUException
from hikyuu.cpp.core310 import HOUR
from hikyuu.cpp.core310 import HSL
from hikyuu.cpp.core310 import Hours
from hikyuu.cpp.core310 import IC
from hikyuu.cpp.core310 import ICIR
from hikyuu.cpp.core310 import IF
from hikyuu.cpp.core310 import INBLOCK
from hikyuu.cpp.core310 import INDEXA
from hikyuu.cpp.core310 import INDEXADV
from hikyuu.cpp.core310 import INDEXC
from hikyuu.cpp.core310 import INDEXDEC
from hikyuu.cpp.core310 import INDEXH
from hikyuu.cpp.core310 import INDEXL
from hikyuu.cpp.core310 import INDEXO
from hikyuu.cpp.core310 import INDEXV
from hikyuu.cpp.core310 import INSUM
from hikyuu.cpp.core310 import INTPART
from hikyuu.cpp.core310 import IR
from hikyuu.cpp.core310 import ISINF
from hikyuu.cpp.core310 import ISINFA
from hikyuu.cpp.core310 import ISLASTBAR
from hikyuu.cpp.core310 import ISNA
from hikyuu.cpp.core310 import IndParam
from hikyuu.cpp.core310 import Indicator
from hikyuu.cpp.core310 import IndicatorImp
from hikyuu.cpp.core310 import JUMPDOWN
from hikyuu.cpp.core310 import JUMPUP
from hikyuu.cpp.core310 import KALMAN
from hikyuu.cpp.core310 import KDATA_PART
from hikyuu.cpp.core310 import KData
from hikyuu.cpp.core310 import KDataDriver
from hikyuu.cpp.core310 import KDataToHdf5Importer
from hikyuu.cpp.core310 import KRecord
from hikyuu.cpp.core310 import KRecordList
from hikyuu.cpp.core310 import LAST
from hikyuu.cpp.core310 import LASTVALUE
from hikyuu.cpp.core310 import LASTVALUE as CONST
from hikyuu.cpp.core310 import LIUTONGPAN as CAPITAL
from hikyuu.cpp.core310 import LIUTONGPAN
from hikyuu.cpp.core310 import LLV
from hikyuu.cpp.core310 import LLVBARS
from hikyuu.cpp.core310 import LN
from hikyuu.cpp.core310 import LOG
from hikyuu.cpp.core310 import LOG_LEVEL
from hikyuu.cpp.core310 import LONGCROSS
from hikyuu.cpp.core310 import LoanRecord
from hikyuu.cpp.core310 import MA
from hikyuu.cpp.core310 import MACD
from hikyuu.cpp.core310 import MAX
from hikyuu.cpp.core310 import MDD
from hikyuu.cpp.core310 import MF_EqualWeight
from hikyuu.cpp.core310 import MF_ICIRWeight
from hikyuu.cpp.core310 import MF_ICWeight
from hikyuu.cpp.core310 import MF_Weight
from hikyuu.cpp.core310 import MIN
from hikyuu.cpp.core310 import MINUTE
from hikyuu.cpp.core310 import MM_FixedCapital
from hikyuu.cpp.core310 import MM_FixedCapitalFunds
from hikyuu.cpp.core310 import MM_FixedCount
from hikyuu.cpp.core310 import MM_FixedCountTps
from hikyuu.cpp.core310 import MM_FixedPercent
from hikyuu.cpp.core310 import MM_FixedRisk
from hikyuu.cpp.core310 import MM_FixedUnits
from hikyuu.cpp.core310 import MM_Nothing
from hikyuu.cpp.core310 import MM_WilliamsFixedRisk
from hikyuu.cpp.core310 import MOD
from hikyuu.cpp.core310 import MONTH
from hikyuu.cpp.core310 import MRR
from hikyuu.cpp.core310 import MarketInfo
from hikyuu.cpp.core310 import Microseconds
from hikyuu.cpp.core310 import Milliseconds
from hikyuu.cpp.core310 import Minutes
from hikyuu.cpp.core310 import MoneyManagerBase
from hikyuu.cpp.core310 import MultiFactorBase
from hikyuu.cpp.core310 import NDAY
from hikyuu.cpp.core310 import NORM_MinMax
from hikyuu.cpp.core310 import NORM_NOTHING
from hikyuu.cpp.core310 import NORM_Quantile
from hikyuu.cpp.core310 import NORM_Quantile_Uniform
from hikyuu.cpp.core310 import NORM_Zscore
from hikyuu.cpp.core310 import NOT
from hikyuu.cpp.core310 import NormalizeBase
from hikyuu.cpp.core310 import OrderBrokerBase
from hikyuu.cpp.core310 import PF_Simple
from hikyuu.cpp.core310 import PF_WithoutAF
from hikyuu.cpp.core310 import PG_FixedHoldDays
from hikyuu.cpp.core310 import PG_FixedPercent
from hikyuu.cpp.core310 import PG_NoGoal
from hikyuu.cpp.core310 import POS
from hikyuu.cpp.core310 import POW
from hikyuu.cpp.core310 import PRICELIST
from hikyuu.cpp.core310 import PRICELIST as VALUE
from hikyuu.cpp.core310 import Parameter
from hikyuu.cpp.core310 import Performance
from hikyuu.cpp.core310 import Portfolio
from hikyuu.cpp.core310 import PositionRecord
from hikyuu.cpp.core310 import PositionRecordList
from hikyuu.cpp.core310 import ProfitGoalBase
from hikyuu.cpp.core310 import QUANTILE_TRUNC
from hikyuu.cpp.core310 import Query
from hikyuu.cpp.core310 import RANK
from hikyuu.cpp.core310 import RECOVER_BACKWARD
from hikyuu.cpp.core310 import RECOVER_EQUAL_BACKWARD
from hikyuu.cpp.core310 import RECOVER_EQUAL_FORWARD
from hikyuu.cpp.core310 import RECOVER_FORWARD
from hikyuu.cpp.core310 import REF
from hikyuu.cpp.core310 import REFX
from hikyuu.cpp.core310 import REPLACE
from hikyuu.cpp.core310 import RESULT
from hikyuu.cpp.core310 import REVERSE
from hikyuu.cpp.core310 import ROC
from hikyuu.cpp.core310 import ROCP
from hikyuu.cpp.core310 import ROCR
from hikyuu.cpp.core310 import ROCR100
from hikyuu.cpp.core310 import ROUND
from hikyuu.cpp.core310 import ROUNDDOWN
from hikyuu.cpp.core310 import ROUNDUP
from hikyuu.cpp.core310 import RSI
from hikyuu.cpp.core310 import SAFTYLOSS
from hikyuu.cpp.core310 import SCFilter_AmountLimit
from hikyuu.cpp.core310 import SCFilter_Group
from hikyuu.cpp.core310 import SCFilter_IgnoreNan
from hikyuu.cpp.core310 import SCFilter_LessOrEqualValue
from hikyuu.cpp.core310 import SCFilter_Price
from hikyuu.cpp.core310 import SCFilter_TopN
from hikyuu.cpp.core310 import SE_EvaluateOptimal
from hikyuu.cpp.core310 import SE_Fixed
from hikyuu.cpp.core310 import SE_MaxFundsOptimal
from hikyuu.cpp.core310 import SE_MultiFactor
from hikyuu.cpp.core310 import SE_MultiFactor2
from hikyuu.cpp.core310 import SE_PerformanceOptimal
from hikyuu.cpp.core310 import SE_Signal
from hikyuu.cpp.core310 import SGN
from hikyuu.cpp.core310 import SG_Add
from hikyuu.cpp.core310 import SG_AllwaysBuy
from hikyuu.cpp.core310 import SG_And
from hikyuu.cpp.core310 import SG_Band
from hikyuu.cpp.core310 import SG_Bool
from hikyuu.cpp.core310 import SG_Buy
from hikyuu.cpp.core310 import SG_Cross
from hikyuu.cpp.core310 import SG_CrossGold
from hikyuu.cpp.core310 import SG_Cycle
from hikyuu.cpp.core310 import SG_Div
from hikyuu.cpp.core310 import SG_Flex
from hikyuu.cpp.core310 import SG_Mul
from hikyuu.cpp.core310 import SG_OneSide
from hikyuu.cpp.core310 import SG_Or
from hikyuu.cpp.core310 import SG_Sell
from hikyuu.cpp.core310 import SG_Single
from hikyuu.cpp.core310 import SG_Single2
from hikyuu.cpp.core310 import SG_Sub
from hikyuu.cpp.core310 import SIN
from hikyuu.cpp.core310 import SLICE
from hikyuu.cpp.core310 import SLOPE
from hikyuu.cpp.core310 import SMA
from hikyuu.cpp.core310 import SPEARMAN
from hikyuu.cpp.core310 import SP_FixedPercent
from hikyuu.cpp.core310 import SP_FixedValue
from hikyuu.cpp.core310 import SQRT
from hikyuu.cpp.core310 import STDEV as STD
from hikyuu.cpp.core310 import STDEV
from hikyuu.cpp.core310 import STDP
from hikyuu.cpp.core310 import ST_FixedPercent
from hikyuu.cpp.core310 import ST_Indicator
from hikyuu.cpp.core310 import ST_Saftyloss
from hikyuu.cpp.core310 import SUM
from hikyuu.cpp.core310 import SUMBARS
from hikyuu.cpp.core310 import SYS_Simple
from hikyuu.cpp.core310 import SYS_WalkForward
from hikyuu.cpp.core310 import ScoreRecord
from hikyuu.cpp.core310 import ScoreRecordList
from hikyuu.cpp.core310 import ScoresFilterBase
from hikyuu.cpp.core310 import Seconds
from hikyuu.cpp.core310 import SelectorBase
from hikyuu.cpp.core310 import SignalBase
from hikyuu.cpp.core310 import SlippageBase
from hikyuu.cpp.core310 import SpotRecord
from hikyuu.cpp.core310 import Stock
from hikyuu.cpp.core310 import StockManager
from hikyuu.cpp.core310 import StockTypeInfo
from hikyuu.cpp.core310 import StockWeight
from hikyuu.cpp.core310 import StockWeightList
from hikyuu.cpp.core310 import StoplossBase
from hikyuu.cpp.core310 import Strategy
from hikyuu.cpp.core310 import StrategyContext
from hikyuu.cpp.core310 import System
from hikyuu.cpp.core310 import SystemPart
from hikyuu.cpp.core310 import SystemWeight
from hikyuu.cpp.core310 import SystemWeightList
from hikyuu.cpp.core310 import TAN
from hikyuu.cpp.core310 import TA_ACCBANDS
from hikyuu.cpp.core310 import TA_ACOS
from hikyuu.cpp.core310 import TA_AD
from hikyuu.cpp.core310 import TA_ADD
from hikyuu.cpp.core310 import TA_ADOSC
from hikyuu.cpp.core310 import TA_ADX
from hikyuu.cpp.core310 import TA_ADXR
from hikyuu.cpp.core310 import TA_APO
from hikyuu.cpp.core310 import TA_AROON
from hikyuu.cpp.core310 import TA_AROONOSC
from hikyuu.cpp.core310 import TA_ASIN
from hikyuu.cpp.core310 import TA_ATAN
from hikyuu.cpp.core310 import TA_ATR
from hikyuu.cpp.core310 import TA_AVGDEV
from hikyuu.cpp.core310 import TA_AVGPRICE
from hikyuu.cpp.core310 import TA_BBANDS
from hikyuu.cpp.core310 import TA_BETA
from hikyuu.cpp.core310 import TA_BOP
from hikyuu.cpp.core310 import TA_CCI
from hikyuu.cpp.core310 import TA_CDL2CROWS
from hikyuu.cpp.core310 import TA_CDL3BLACKCROWS
from hikyuu.cpp.core310 import TA_CDL3INSIDE
from hikyuu.cpp.core310 import TA_CDL3LINESTRIKE
from hikyuu.cpp.core310 import TA_CDL3OUTSIDE
from hikyuu.cpp.core310 import TA_CDL3STARSINSOUTH
from hikyuu.cpp.core310 import TA_CDL3WHITESOLDIERS
from hikyuu.cpp.core310 import TA_CDLABANDONEDBABY
from hikyuu.cpp.core310 import TA_CDLADVANCEBLOCK
from hikyuu.cpp.core310 import TA_CDLBELTHOLD
from hikyuu.cpp.core310 import TA_CDLBREAKAWAY
from hikyuu.cpp.core310 import TA_CDLCLOSINGMARUBOZU
from hikyuu.cpp.core310 import TA_CDLCONCEALBABYSWALL
from hikyuu.cpp.core310 import TA_CDLCOUNTERATTACK
from hikyuu.cpp.core310 import TA_CDLDARKCLOUDCOVER
from hikyuu.cpp.core310 import TA_CDLDOJI
from hikyuu.cpp.core310 import TA_CDLDOJISTAR
from hikyuu.cpp.core310 import TA_CDLDRAGONFLYDOJI
from hikyuu.cpp.core310 import TA_CDLENGULFING
from hikyuu.cpp.core310 import TA_CDLEVENINGDOJISTAR
from hikyuu.cpp.core310 import TA_CDLEVENINGSTAR
from hikyuu.cpp.core310 import TA_CDLGAPSIDESIDEWHITE
from hikyuu.cpp.core310 import TA_CDLGRAVESTONEDOJI
from hikyuu.cpp.core310 import TA_CDLHAMMER
from hikyuu.cpp.core310 import TA_CDLHANGINGMAN
from hikyuu.cpp.core310 import TA_CDLHARAMI
from hikyuu.cpp.core310 import TA_CDLHARAMICROSS
from hikyuu.cpp.core310 import TA_CDLHIGHWAVE
from hikyuu.cpp.core310 import TA_CDLHIKKAKE
from hikyuu.cpp.core310 import TA_CDLHIKKAKEMOD
from hikyuu.cpp.core310 import TA_CDLHOMINGPIGEON
from hikyuu.cpp.core310 import TA_CDLIDENTICAL3CROWS
from hikyuu.cpp.core310 import TA_CDLINNECK
from hikyuu.cpp.core310 import TA_CDLINVERTEDHAMMER
from hikyuu.cpp.core310 import TA_CDLKICKING
from hikyuu.cpp.core310 import TA_CDLKICKINGBYLENGTH
from hikyuu.cpp.core310 import TA_CDLLADDERBOTTOM
from hikyuu.cpp.core310 import TA_CDLLONGLEGGEDDOJI
from hikyuu.cpp.core310 import TA_CDLLONGLINE
from hikyuu.cpp.core310 import TA_CDLMARUBOZU
from hikyuu.cpp.core310 import TA_CDLMATCHINGLOW
from hikyuu.cpp.core310 import TA_CDLMATHOLD
from hikyuu.cpp.core310 import TA_CDLMORNINGDOJISTAR
from hikyuu.cpp.core310 import TA_CDLMORNINGSTAR
from hikyuu.cpp.core310 import TA_CDLONNECK
from hikyuu.cpp.core310 import TA_CDLPIERCING
from hikyuu.cpp.core310 import TA_CDLRICKSHAWMAN
from hikyuu.cpp.core310 import TA_CDLRISEFALL3METHODS
from hikyuu.cpp.core310 import TA_CDLSEPARATINGLINES
from hikyuu.cpp.core310 import TA_CDLSHOOTINGSTAR
from hikyuu.cpp.core310 import TA_CDLSHORTLINE
from hikyuu.cpp.core310 import TA_CDLSPINNINGTOP
from hikyuu.cpp.core310 import TA_CDLSTALLEDPATTERN
from hikyuu.cpp.core310 import TA_CDLSTICKSANDWICH
from hikyuu.cpp.core310 import TA_CDLTAKURI
from hikyuu.cpp.core310 import TA_CDLTASUKIGAP
from hikyuu.cpp.core310 import TA_CDLTHRUSTING
from hikyuu.cpp.core310 import TA_CDLTRISTAR
from hikyuu.cpp.core310 import TA_CDLUNIQUE3RIVER
from hikyuu.cpp.core310 import TA_CDLUPSIDEGAP2CROWS
from hikyuu.cpp.core310 import TA_CDLXSIDEGAP3METHODS
from hikyuu.cpp.core310 import TA_CEIL
from hikyuu.cpp.core310 import TA_CMO
from hikyuu.cpp.core310 import TA_CORREL
from hikyuu.cpp.core310 import TA_COS
from hikyuu.cpp.core310 import TA_COSH
from hikyuu.cpp.core310 import TA_DEMA
from hikyuu.cpp.core310 import TA_DIV
from hikyuu.cpp.core310 import TA_DX
from hikyuu.cpp.core310 import TA_EMA
from hikyuu.cpp.core310 import TA_EXP
from hikyuu.cpp.core310 import TA_FLOOR
from hikyuu.cpp.core310 import TA_HT_DCPERIOD
from hikyuu.cpp.core310 import TA_HT_DCPHASE
from hikyuu.cpp.core310 import TA_HT_PHASOR
from hikyuu.cpp.core310 import TA_HT_SINE
from hikyuu.cpp.core310 import TA_HT_TRENDLINE
from hikyuu.cpp.core310 import TA_HT_TRENDMODE
from hikyuu.cpp.core310 import TA_IMI
from hikyuu.cpp.core310 import TA_KAMA
from hikyuu.cpp.core310 import TA_LINEARREG
from hikyuu.cpp.core310 import TA_LINEARREG_ANGLE
from hikyuu.cpp.core310 import TA_LINEARREG_INTERCEPT
from hikyuu.cpp.core310 import TA_LINEARREG_SLOPE
from hikyuu.cpp.core310 import TA_LN
from hikyuu.cpp.core310 import TA_LOG10
from hikyuu.cpp.core310 import TA_MA
from hikyuu.cpp.core310 import TA_MACD
from hikyuu.cpp.core310 import TA_MACDEXT
from hikyuu.cpp.core310 import TA_MACDFIX
from hikyuu.cpp.core310 import TA_MAMA
from hikyuu.cpp.core310 import TA_MAVP
from hikyuu.cpp.core310 import TA_MAX
from hikyuu.cpp.core310 import TA_MAXINDEX
from hikyuu.cpp.core310 import TA_MEDPRICE
from hikyuu.cpp.core310 import TA_MFI
from hikyuu.cpp.core310 import TA_MIDPOINT
from hikyuu.cpp.core310 import TA_MIDPRICE
from hikyuu.cpp.core310 import TA_MIN
from hikyuu.cpp.core310 import TA_MININDEX
from hikyuu.cpp.core310 import TA_MINMAX
from hikyuu.cpp.core310 import TA_MINMAXINDEX
from hikyuu.cpp.core310 import TA_MINUS_DI
from hikyuu.cpp.core310 import TA_MINUS_DM
from hikyuu.cpp.core310 import TA_MOM
from hikyuu.cpp.core310 import TA_MULT
from hikyuu.cpp.core310 import TA_NATR
from hikyuu.cpp.core310 import TA_OBV
from hikyuu.cpp.core310 import TA_PLUS_DI
from hikyuu.cpp.core310 import TA_PLUS_DM
from hikyuu.cpp.core310 import TA_PPO
from hikyuu.cpp.core310 import TA_ROC
from hikyuu.cpp.core310 import TA_ROCP
from hikyuu.cpp.core310 import TA_ROCR
from hikyuu.cpp.core310 import TA_ROCR100
from hikyuu.cpp.core310 import TA_RSI
from hikyuu.cpp.core310 import TA_SAR
from hikyuu.cpp.core310 import TA_SAREXT
from hikyuu.cpp.core310 import TA_SIN
from hikyuu.cpp.core310 import TA_SINH
from hikyuu.cpp.core310 import TA_SMA
from hikyuu.cpp.core310 import TA_SQRT
from hikyuu.cpp.core310 import TA_STDDEV
from hikyuu.cpp.core310 import TA_STOCH
from hikyuu.cpp.core310 import TA_STOCHF
from hikyuu.cpp.core310 import TA_STOCHRSI
from hikyuu.cpp.core310 import TA_SUB
from hikyuu.cpp.core310 import TA_SUM
from hikyuu.cpp.core310 import TA_T3
from hikyuu.cpp.core310 import TA_TAN
from hikyuu.cpp.core310 import TA_TANH
from hikyuu.cpp.core310 import TA_TEMA
from hikyuu.cpp.core310 import TA_TRANGE
from hikyuu.cpp.core310 import TA_TRIMA
from hikyuu.cpp.core310 import TA_TRIX
from hikyuu.cpp.core310 import TA_TSF
from hikyuu.cpp.core310 import TA_TYPPRICE
from hikyuu.cpp.core310 import TA_ULTOSC
from hikyuu.cpp.core310 import TA_VAR
from hikyuu.cpp.core310 import TA_WCLPRICE
from hikyuu.cpp.core310 import TA_WILLR
from hikyuu.cpp.core310 import TA_WMA
from hikyuu.cpp.core310 import TC_FixedA
from hikyuu.cpp.core310 import TC_FixedA2015
from hikyuu.cpp.core310 import TC_FixedA2017
from hikyuu.cpp.core310 import TC_TestStub
from hikyuu.cpp.core310 import TC_Zero
from hikyuu.cpp.core310 import TIME
from hikyuu.cpp.core310 import TIMELINE
from hikyuu.cpp.core310 import TIMELINEVOL
from hikyuu.cpp.core310 import TR
from hikyuu.cpp.core310 import TURNOVER
from hikyuu.cpp.core310 import TimeDelta
from hikyuu.cpp.core310 import TimeLineList
from hikyuu.cpp.core310 import TimeLineRecord
from hikyuu.cpp.core310 import TradeCostBase
from hikyuu.cpp.core310 import TradeManager
from hikyuu.cpp.core310 import TradeRecord
from hikyuu.cpp.core310 import TradeRecordList
from hikyuu.cpp.core310 import TradeRequest
from hikyuu.cpp.core310 import TransList
from hikyuu.cpp.core310 import TransRecord
from hikyuu.cpp.core310 import UPNDAY
from hikyuu.cpp.core310 import UTCOffset
from hikyuu.cpp.core310 import VAR
from hikyuu.cpp.core310 import VARP
from hikyuu.cpp.core310 import VIGOR
from hikyuu.cpp.core310 import WEAVE
from hikyuu.cpp.core310 import WEEK
from hikyuu.cpp.core310 import WINNER
from hikyuu.cpp.core310 import WITHDAY
from hikyuu.cpp.core310 import WITHHALFYEAR
from hikyuu.cpp.core310 import WITHHOUR
from hikyuu.cpp.core310 import WITHHOUR2
from hikyuu.cpp.core310 import WITHHOUR4
from hikyuu.cpp.core310 import WITHKTYPE
from hikyuu.cpp.core310 import WITHMIN
from hikyuu.cpp.core310 import WITHMIN15
from hikyuu.cpp.core310 import WITHMIN30
from hikyuu.cpp.core310 import WITHMIN5
from hikyuu.cpp.core310 import WITHMIN60
from hikyuu.cpp.core310 import WITHMONTH
from hikyuu.cpp.core310 import WITHQUARTER
from hikyuu.cpp.core310 import WITHWEEK
from hikyuu.cpp.core310 import WITHYEAR
from hikyuu.cpp.core310 import WMA
from hikyuu.cpp.core310 import YEAR
from hikyuu.cpp.core310 import ZHBOND10
from hikyuu.cpp.core310 import ZONGGUBEN
from hikyuu.cpp.core310 import ZSCORE
from hikyuu.cpp.core310 import __init__ as old_Query_init
from hikyuu.cpp.core310 import active_device
from hikyuu.cpp.core310 import backtest
from hikyuu.cpp.core310 import batch_calculate_inds
from hikyuu.cpp.core310 import can_upgrade
from hikyuu.cpp.core310 import close_ostream_to_python
from hikyuu.cpp.core310 import close_spend_time
from hikyuu.cpp.core310 import combinate_ind
from hikyuu.cpp.core310 import combinate_index
from hikyuu.cpp.core310 import crtBrokerTM
from hikyuu.cpp.core310 import crtSEOptimal
from hikyuu.cpp.core310 import crtTM
from hikyuu.cpp.core310 import crt_pf_strategy
from hikyuu.cpp.core310 import crt_sys_strategy
from hikyuu.cpp.core310 import dates_to_np
from hikyuu.cpp.core310 import dates_to_pa
from hikyuu.cpp.core310 import df_to_krecords
from hikyuu.cpp.core310 import fetch_trial_license
from hikyuu.cpp.core310 import find_optimal_system
from hikyuu.cpp.core310 import find_optimal_system_multi
from hikyuu.cpp.core310 import get_block
from hikyuu.cpp.core310 import get_business_name
from hikyuu.cpp.core310 import get_data_from_buffer_server
from hikyuu.cpp.core310 import get_date_range
from hikyuu.cpp.core310 import get_funds_list
from hikyuu.cpp.core310 import get_inds_view
from hikyuu.cpp.core310 import get_inds_view_pyarrow
from hikyuu.cpp.core310 import get_kdata
from hikyuu.cpp.core310 import get_last_version
from hikyuu.cpp.core310 import get_log_level
from hikyuu.cpp.core310 import get_market_view
from hikyuu.cpp.core310 import get_market_view_pyarrow
from hikyuu.cpp.core310 import get_spot_from_buffer_server
from hikyuu.cpp.core310 import get_stock
from hikyuu.cpp.core310 import get_system_part_enum
from hikyuu.cpp.core310 import get_system_part_name
from hikyuu.cpp.core310 import get_version
from hikyuu.cpp.core310 import get_version_git
from hikyuu.cpp.core310 import get_version_with_build
from hikyuu.cpp.core310 import hikyuu_init
from hikyuu.cpp.core310 import inner_analysis_sys_list
from hikyuu.cpp.core310 import inner_combinate_ind_analysis
from hikyuu.cpp.core310 import inner_combinate_ind_analysis_with_block
from hikyuu.cpp.core310 import is_valid_license
from hikyuu.cpp.core310 import isinf
from hikyuu.cpp.core310 import isnan
from hikyuu.cpp.core310 import krecords_to_df
from hikyuu.cpp.core310 import krecords_to_np
from hikyuu.cpp.core310 import krecords_to_pa
from hikyuu.cpp.core310 import open_ostream_to_python
from hikyuu.cpp.core310 import open_spend_time
from hikyuu.cpp.core310 import parallel_run_pf
from hikyuu.cpp.core310 import parallel_run_sys
from hikyuu.cpp.core310 import positions_to_df
from hikyuu.cpp.core310 import positions_to_np
from hikyuu.cpp.core310 import positions_to_pa
from hikyuu.cpp.core310 import register_extra_ktype
from hikyuu.cpp.core310 import release_extra_ktype
from hikyuu.cpp.core310 import remove_license
from hikyuu.cpp.core310 import roundDown
from hikyuu.cpp.core310 import roundEx
from hikyuu.cpp.core310 import roundUp
from hikyuu.cpp.core310 import run_in_strategy
from hikyuu.cpp.core310 import scorerecords_to_df
from hikyuu.cpp.core310 import scorerecords_to_np
from hikyuu.cpp.core310 import set_log_level
from hikyuu.cpp.core310 import set_python_in_interactive
from hikyuu.cpp.core310 import set_python_in_jupyter
from hikyuu.cpp.core310 import spot_agent_is_connected
from hikyuu.cpp.core310 import spot_agent_is_running
from hikyuu.cpp.core310 import start_data_server
from hikyuu.cpp.core310 import start_spot_agent
from hikyuu.cpp.core310 import stop_data_server
from hikyuu.cpp.core310 import stop_spot_agent
from hikyuu.cpp.core310 import systemweights_to_df
from hikyuu.cpp.core310 import systemweights_to_np
from hikyuu.cpp.core310 import timeline_to_df
from hikyuu.cpp.core310 import timeline_to_np
from hikyuu.cpp.core310 import timeline_to_pa
from hikyuu.cpp.core310 import toPriceList
from hikyuu.cpp.core310 import trades_to_df
from hikyuu.cpp.core310 import trades_to_np
from hikyuu.cpp.core310 import trades_to_pa
from hikyuu.cpp.core310 import translist_to_df
from hikyuu.cpp.core310 import translist_to_np
from hikyuu.cpp.core310 import translist_to_pa
from hikyuu.cpp.core310 import view_license
from hikyuu.cpp.core310 import weights_to_df
from hikyuu.cpp.core310 import weights_to_np
from hikyuu.cpp.core310 import weights_to_pa
from hikyuu.draw.drawplot.common import get_draw_title
from hikyuu import extend
from hikyuu.extend import DatetimeList_to_df
from hikyuu.extend import DatetimeList_to_np
from hikyuu.extend import Datetime_date
from hikyuu.extend import Datetime_datetime
from hikyuu.extend import Parameter_items
from hikyuu.extend import Parameter_iter
from hikyuu.extend import Parameter_keys
from hikyuu.extend import Parameter_to_dict
from hikyuu.extend import TimeDelta_timedelta
from hikyuu.extend import new_Query_init
from hikyuu import hub
from hikyuu.hub import add_local_hub
from hikyuu.hub import add_remote_hub
from hikyuu.hub import build_hub
from hikyuu.hub import get_current_hub
from hikyuu.hub import get_hub_name_list
from hikyuu.hub import get_hub_path
from hikyuu.hub import get_part
from hikyuu.hub import get_part_info
from hikyuu.hub import get_part_list
from hikyuu.hub import get_part_module
from hikyuu.hub import get_part_name_list
from hikyuu.hub import print_part_info
from hikyuu.hub import print_part_info as help_part
from hikyuu.hub import remove_hub
from hikyuu.hub import search_part
from hikyuu.hub import update_hub
from hikyuu.indicator import indicator
from hikyuu.indicator.indicator import concat_to_df
from hikyuu.indicator.indicator import df_to_ind
from hikyuu.indicator import pyind
from hikyuu.indicator.pyind import KDJ
from hikyuu import trade_manage
from hikyuu.trade_manage import broker
from hikyuu.trade_manage.broker import OrderBrokerWrap
from hikyuu.trade_manage.broker import TestOrderBroker
from hikyuu.trade_manage.broker import crtOB
from hikyuu.trade_manage import broker_easytrader
from hikyuu.trade_manage.broker_easytrader import EasyTraderOrderBroker
from hikyuu.trade_manage import broker_mail
from hikyuu.trade_manage.broker_mail import MailOrderBroker
from hikyuu.trade_manage import trade
from hikyuu.trade_manage.trade import Performance_to_df
from hikyuu.trade_sys import trade_sys
from hikyuu.trade_sys.trade_sys import crtAF
from hikyuu.trade_sys.trade_sys import crtCN
from hikyuu.trade_sys.trade_sys import crtEV
from hikyuu.trade_sys.trade_sys import crtMF
from hikyuu.trade_sys.trade_sys import crtMM
from hikyuu.trade_sys.trade_sys import crtPG
from hikyuu.trade_sys.trade_sys import crtSE
from hikyuu.trade_sys.trade_sys import crtSG
from hikyuu.trade_sys.trade_sys import crtSP
from hikyuu.trade_sys.trade_sys import crtST
from hikyuu.trade_sys.trade_sys import part_clone
from hikyuu.trade_sys.trade_sys import part_init
from hikyuu.trade_sys.trade_sys import part_iter
from hikyuu import util
from hikyuu.util.check import HKUCheckError
from hikyuu.util.check import hku_catch
from hikyuu.util.check import hku_check
from hikyuu.util.check import hku_check_ignore
from hikyuu.util.check import hku_check_throw
from hikyuu.util.check import hku_run_ignore_exception
from hikyuu.util.check import hku_to_async
from hikyuu.util.mylog import LoggingContext
from hikyuu.util.mylog import add_class_logger_handler
from hikyuu.util.mylog import capture_multiprocess_all_logger
from hikyuu.util.mylog import class_logger
from hikyuu.util.mylog import hku_benchmark
from hikyuu.util.mylog import hku_debug as hku_trace
from hikyuu.util.mylog import hku_debug
from hikyuu.util.mylog import hku_debug_if as hku_trace_if
from hikyuu.util.mylog import hku_debug_if
from hikyuu.util.mylog import hku_error
from hikyuu.util.mylog import hku_error_if
from hikyuu.util.mylog import hku_fatal
from hikyuu.util.mylog import hku_fatal_if
from hikyuu.util.mylog import hku_info
from hikyuu.util.mylog import hku_info_if
from hikyuu.util.mylog import hku_warn
from hikyuu.util.mylog import hku_warn_if
from hikyuu.util.mylog import set_my_logger_file
from hikyuu.util.mylog import spend_time
from hikyuu.util.mylog import with_trace
from hikyuu.util.notebook import in_interactive_session
from hikyuu.util.notebook import in_ipython_frontend
from hikyuu.util.timeout import timeout
import io as io
import locale as locale
import logging as logging
import math as math
import matplotlib as matplotlib
from matplotlib.font_manager import FontManager
from matplotlib.image import imread
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.pyplot import axes
from matplotlib.pyplot import draw
from matplotlib.pyplot import figure
from matplotlib.pyplot import gca
from matplotlib.pyplot import gcf
from matplotlib.pyplot import ylabel
from matplotlib.ticker import FixedLocator
from matplotlib.ticker import FuncFormatter
import numpy as np
import os as os
import pandas as pd
from pathlib import Path
import pickle as pickle
import seaborn as sns
import sys as sys
import traceback as traceback
__all__: list[str] = ['ABS', 'ACOS', 'AD', 'ADVANCE', 'AF_EqualWeight', 'AF_FixedWeight', 'AF_FixedWeightList', 'AF_MultiFactor', 'AGG_COUNT', 'AGG_FUNC', 'AGG_MAD', 'AGG_MAX', 'AGG_MEAN', 'AGG_MEDIAN', 'AGG_MIN', 'AGG_PROD', 'AGG_QUANTILE', 'AGG_STD', 'AGG_SUM', 'AGG_VAR', 'ALIGN', 'AMA', 'AMO', 'ASIN', 'ATAN', 'ATR', 'AVEDEV', 'AllocateFundsBase', 'BACKSET', 'BARSCOUNT', 'BARSLAST', 'BARSLASTCOUNT', 'BARSSINCE', 'BARSSINCEN', 'BASE_DIR', 'BETWEEN', 'BLOCKSETNUM', 'BUSINESS', 'Block', 'BlockInfoDriver', 'BorrowRecord', 'BrokerPositionRecord', 'CAPITAL', 'CEILING', 'CLOSE', 'CN_Bool', 'CN_OPLine', 'CONST', 'CONTEXT', 'CONTEXT_K', 'CORR', 'COS', 'COST', 'COUNT', 'CROSS', 'CVAL', 'CYCLE', 'C_AMO', 'C_CLOSE', 'C_HIGH', 'C_KDATA', 'C_LOW', 'C_OPEN', 'C_VOL', 'ConditionBase', 'Constant', 'CostRecord', 'DATE', 'DAY', 'DEBUG', 'DECLINE', 'DEVSQ', 'DIFF', 'DISCARD', 'DMA', 'DOWNNDAY', 'DRAWBAND', 'DRAWBMP', 'DRAWICON', 'DRAWIMG', 'DRAWLINE', 'DRAWNULL', 'DRAWNUMBER', 'DRAWNUMBER_FIX', 'DRAWRECTREL', 'DRAWSL', 'DRAWTEXT', 'DRAWTEXT_FIX', 'DROPNA', 'DataDriverFactory', 'Datetime', 'DatetimeList', 'DatetimeList_to_df', 'DatetimeList_to_np', 'Datetime_date', 'Datetime_datetime', 'Days', 'EMA', 'ERROR', 'EVERY', 'EV_Bool', 'EV_TwoLine', 'EXIST', 'EXP', 'EasyTraderOrderBroker', 'EnvironmentBase', 'FATAL', 'FILTER', 'FINANCE', 'FLOOR', 'FixedLocator', 'FontManager', 'FuncFormatter', 'FundsRecord', 'GROUP_COUNT', 'GROUP_FUNC', 'GROUP_MAX', 'GROUP_MEAN', 'GROUP_MIN', 'GROUP_PROD', 'GROUP_SUM', 'HHV', 'HHVBARS', 'HIGH', 'HKUCheckError', 'HKUException', 'HOUR', 'HSL', 'Hours', 'IC', 'ICIR', 'ICON_PATH', 'IF', 'INBLOCK', 'INDEXA', 'INDEXADV', 'INDEXC', 'INDEXDEC', 'INDEXH', 'INDEXL', 'INDEXO', 'INDEXV', 'INFO', 'INSUM', 'INTPART', 'IR', 'ISINF', 'ISINFA', 'ISLASTBAR', 'ISNA', 'IndParam', 'Indicator', 'IndicatorImp', 'JUMPDOWN', 'JUMPUP', 'KALMAN', 'KDATA', 'KDATA_PART', 'KDJ', 'KData', 'KDataDriver', 'KDataToHdf5Importer', 'KRecord', 'KRecordList', 'LAST', 'LASTVALUE', 'LIUTONGPAN', 'LLV', 'LLVBARS', 'LN', 'LOG', 'LOG_LEVEL', 'LONGCROSS', 'LOW', 'Line2D', 'LoanRecord', 'LoggingContext', 'MA', 'MACD', 'MAX', 'MDD', 'MF_EqualWeight', 'MF_ICIRWeight', 'MF_ICWeight', 'MF_Weight', 'MIN', 'MINUTE', 'MM_FixedCapital', 'MM_FixedCapitalFunds', 'MM_FixedCount', 'MM_FixedCountTps', 'MM_FixedPercent', 'MM_FixedRisk', 'MM_FixedUnits', 'MM_Nothing', 'MM_WilliamsFixedRisk', 'MOD', 'MONTH', 'MRR', 'MailOrderBroker', 'MarketInfo', 'Microseconds', 'Milliseconds', 'Minutes', 'MoneyManagerBase', 'MultiFactorBase', 'NDAY', 'NORM_MinMax', 'NORM_NOTHING', 'NORM_Quantile', 'NORM_Quantile_Uniform', 'NORM_Zscore', 'NOT', 'NormalizeBase', 'OFF', 'OPEN', 'OrderBrokerBase', 'OrderBrokerWrap', 'PF_Simple', 'PF_WithoutAF', 'PG_FixedHoldDays', 'PG_FixedPercent', 'PG_NoGoal', 'PLOYLINE', 'POS', 'POW', 'PRICELIST', 'Parameter', 'Parameter_items', 'Parameter_iter', 'Parameter_keys', 'Parameter_to_dict', 'Path', 'Performance', 'Performance_to_df', 'Portfolio', 'PositionRecord', 'PositionRecordList', 'ProfitGoalBase', 'QUANTILE_TRUNC', 'Query', 'RANK', 'RECOVER_BACKWARD', 'RECOVER_EQUAL_BACKWARD', 'RECOVER_EQUAL_FORWARD', 'RECOVER_FORWARD', 'REF', 'REFX', 'REPLACE', 'RESULT', 'REVERSE', 'RGB', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'ROUND', 'ROUNDDOWN', 'ROUNDUP', 'RSI', 'Rectangle', 'SAFTYLOSS', 'SCFilter_AmountLimit', 'SCFilter_Group', 'SCFilter_IgnoreNan', 'SCFilter_LessOrEqualValue', 'SCFilter_Price', 'SCFilter_TopN', 'SE_EvaluateOptimal', 'SE_Fixed', 'SE_MaxFundsOptimal', 'SE_MultiFactor', 'SE_MultiFactor2', 'SE_PerformanceOptimal', 'SE_Signal', 'SGN', 'SG_Add', 'SG_AllwaysBuy', 'SG_And', 'SG_Band', 'SG_Bool', 'SG_Buy', 'SG_Cross', 'SG_CrossGold', 'SG_Cycle', 'SG_Div', 'SG_Flex', 'SG_Mul', 'SG_OneSide', 'SG_Or', 'SG_Sell', 'SG_Single', 'SG_Single2', 'SG_Sub', 'SHOWICONS', 'SIN', 'SLICE', 'SLOPE', 'SMA', 'SPEARMAN', 'SP_FixedPercent', 'SP_FixedValue', 'SQRT', 'STD', 'STDEV', 'STDP', 'STICKLINE', 'ST_FixedPercent', 'ST_Indicator', 'ST_Saftyloss', 'SUM', 'SUMBARS', 'SYS_Simple', 'SYS_WalkForward', 'ScoreRecord', 'ScoreRecordList', 'ScoresFilterBase', 'Seconds', 'SelectorBase', 'SignalBase', 'SlippageBase', 'SpotRecord', 'Stock', 'StockFuncFormatter', 'StockManager', 'StockTypeInfo', 'StockWeight', 'StockWeightList', 'StoplossBase', 'Strategy', 'StrategyContext', 'System', 'SystemPart', 'SystemWeight', 'SystemWeightList', 'TAN', 'TA_ACCBANDS', 'TA_ACOS', 'TA_AD', 'TA_ADD', 'TA_ADOSC', 'TA_ADX', 'TA_ADXR', 'TA_APO', 'TA_AROON', 'TA_AROONOSC', 'TA_ASIN', 'TA_ATAN', 'TA_ATR', 'TA_AVGDEV', 'TA_AVGPRICE', 'TA_BBANDS', 'TA_BETA', 'TA_BOP', 'TA_CCI', 'TA_CDL2CROWS', 'TA_CDL3BLACKCROWS', 'TA_CDL3INSIDE', 'TA_CDL3LINESTRIKE', 'TA_CDL3OUTSIDE', 'TA_CDL3STARSINSOUTH', 'TA_CDL3WHITESOLDIERS', 'TA_CDLABANDONEDBABY', 'TA_CDLADVANCEBLOCK', 'TA_CDLBELTHOLD', 'TA_CDLBREAKAWAY', 'TA_CDLCLOSINGMARUBOZU', 'TA_CDLCONCEALBABYSWALL', 'TA_CDLCOUNTERATTACK', 'TA_CDLDARKCLOUDCOVER', 'TA_CDLDOJI', 'TA_CDLDOJISTAR', 'TA_CDLDRAGONFLYDOJI', 'TA_CDLENGULFING', 'TA_CDLEVENINGDOJISTAR', 'TA_CDLEVENINGSTAR', 'TA_CDLGAPSIDESIDEWHITE', 'TA_CDLGRAVESTONEDOJI', 'TA_CDLHAMMER', 'TA_CDLHANGINGMAN', 'TA_CDLHARAMI', 'TA_CDLHARAMICROSS', 'TA_CDLHIGHWAVE', 'TA_CDLHIKKAKE', 'TA_CDLHIKKAKEMOD', 'TA_CDLHOMINGPIGEON', 'TA_CDLIDENTICAL3CROWS', 'TA_CDLINNECK', 'TA_CDLINVERTEDHAMMER', 'TA_CDLKICKING', 'TA_CDLKICKINGBYLENGTH', 'TA_CDLLADDERBOTTOM', 'TA_CDLLONGLEGGEDDOJI', 'TA_CDLLONGLINE', 'TA_CDLMARUBOZU', 'TA_CDLMATCHINGLOW', 'TA_CDLMATHOLD', 'TA_CDLMORNINGDOJISTAR', 'TA_CDLMORNINGSTAR', 'TA_CDLONNECK', 'TA_CDLPIERCING', 'TA_CDLRICKSHAWMAN', 'TA_CDLRISEFALL3METHODS', 'TA_CDLSEPARATINGLINES', 'TA_CDLSHOOTINGSTAR', 'TA_CDLSHORTLINE', 'TA_CDLSPINNINGTOP', 'TA_CDLSTALLEDPATTERN', 'TA_CDLSTICKSANDWICH', 'TA_CDLTAKURI', 'TA_CDLTASUKIGAP', 'TA_CDLTHRUSTING', 'TA_CDLTRISTAR', 'TA_CDLUNIQUE3RIVER', 'TA_CDLUPSIDEGAP2CROWS', 'TA_CDLXSIDEGAP3METHODS', 'TA_CEIL', 'TA_CMO', 'TA_CORREL', 'TA_COS', 'TA_COSH', 'TA_DEMA', 'TA_DIV', 'TA_DX', 'TA_EMA', 'TA_EXP', 'TA_FLOOR', 'TA_HT_DCPERIOD', 'TA_HT_DCPHASE', 'TA_HT_PHASOR', 'TA_HT_SINE', 'TA_HT_TRENDLINE', 'TA_HT_TRENDMODE', 'TA_IMI', 'TA_KAMA', 'TA_LINEARREG', 'TA_LINEARREG_ANGLE', 'TA_LINEARREG_INTERCEPT', 'TA_LINEARREG_SLOPE', 'TA_LN', 'TA_LOG10', 'TA_MA', 'TA_MACD', 'TA_MACDEXT', 'TA_MACDFIX', 'TA_MAMA', 'TA_MAVP', 'TA_MAX', 'TA_MAXINDEX', 'TA_MEDPRICE', 'TA_MFI', 'TA_MIDPOINT', 'TA_MIDPRICE', 'TA_MIN', 'TA_MININDEX', 'TA_MINMAX', 'TA_MINMAXINDEX', 'TA_MINUS_DI', 'TA_MINUS_DM', 'TA_MOM', 'TA_MULT', 'TA_NATR', 'TA_OBV', 'TA_PLUS_DI', 'TA_PLUS_DM', 'TA_PPO', 'TA_ROC', 'TA_ROCP', 'TA_ROCR', 'TA_ROCR100', 'TA_RSI', 'TA_SAR', 'TA_SAREXT', 'TA_SIN', 'TA_SINH', 'TA_SMA', 'TA_SQRT', 'TA_STDDEV', 'TA_STOCH', 'TA_STOCHF', 'TA_STOCHRSI', 'TA_SUB', 'TA_SUM', 'TA_T3', 'TA_TAN', 'TA_TANH', 'TA_TEMA', 'TA_TRANGE', 'TA_TRIMA', 'TA_TRIX', 'TA_TSF', 'TA_TYPPRICE', 'TA_ULTOSC', 'TA_VAR', 'TA_WCLPRICE', 'TA_WILLR', 'TA_WMA', 'TC_FixedA', 'TC_FixedA2015', 'TC_FixedA2017', 'TC_TestStub', 'TC_Zero', 'TICKLEFT', 'TICKRIGHT', 'TIME', 'TIMELINE', 'TIMELINEVOL', 'TR', 'TRACE', 'TURNOVER', 'TestOrderBroker', 'TimeDelta', 'TimeDelta_timedelta', 'TimeLineList', 'TimeLineRecord', 'TradeCostBase', 'TradeManager', 'TradeRecord', 'TradeRecordList', 'TradeRequest', 'TransList', 'TransRecord', 'UPNDAY', 'UTCOffset', 'VALUE', 'VAR', 'VARP', 'VIGOR', 'VOL', 'WARN', 'WEAVE', 'WEEK', 'WINNER', 'WITHDAY', 'WITHHALFYEAR', 'WITHHOUR', 'WITHHOUR2', 'WITHHOUR4', 'WITHKTYPE', 'WITHMIN', 'WITHMIN15', 'WITHMIN30', 'WITHMIN5', 'WITHMIN60', 'WITHMONTH', 'WITHQUARTER', 'WITHWEEK', 'WITHYEAR', 'WMA', 'YEAR', 'ZHBOND10', 'ZONGGUBEN', 'ZSCORE', 'active_device', 'add_class_logger_handler', 'add_local_hub', 'add_remote_hub', 'adjust_axes_show', 'analysis', 'analysis_sys_list', 'analysis_sys_list_multi', 'atexit', 'ax_draw_macd', 'ax_draw_macd2', 'ax_set_locator_formatter', 'axes', 'backtest', 'batch_calculate_inds', 'broker', 'broker_easytrader', 'broker_mail', 'build_hub', 'can_upgrade', 'capture_multiprocess_all_logger', 'class_logger', 'close_ostream_to_python', 'close_spend_time', 'cnplot', 'combinate_ind', 'combinate_ind_analysis', 'combinate_ind_analysis_multi', 'combinate_index', 'concat_to_df', 'constant', 'core', 'cpp', 'create_figure', 'create_four_axes_figure', 'create_one_axes_figure', 'create_three_axes_figure', 'create_two_axes_figure', 'crtAF', 'crtBrokerTM', 'crtCN', 'crtEV', 'crtMF', 'crtMM', 'crtOB', 'crtPG', 'crtSE', 'crtSEOptimal', 'crtSG', 'crtSP', 'crtST', 'crtTM', 'crt_pf_strategy', 'crt_sys_strategy', 'current_path', 'date', 'dates_to_np', 'dates_to_pa', 'datetime', 'df_to_ind', 'df_to_krecords', 'dll_directory', 'draw', 'evplot', 'extend', 'fetch_trial_license', 'figure', 'find_optimal_system', 'find_optimal_system_multi', 'fm_logger', 'gca', 'gcf', 'getDayLocatorAndFormatter', 'getMinLocatorAndFormatter', 'get_block', 'get_business_name', 'get_current_hub', 'get_data_from_buffer_server', 'get_date_range', 'get_draw_title', 'get_funds_list', 'get_hub_name_list', 'get_hub_path', 'get_inds_view', 'get_inds_view_pyarrow', 'get_kdata', 'get_last_version', 'get_log_level', 'get_market_view', 'get_market_view_pyarrow', 'get_part', 'get_part_info', 'get_part_list', 'get_part_module', 'get_part_name_list', 'get_spot_from_buffer_server', 'get_stock', 'get_system_part_enum', 'get_system_part_name', 'get_version', 'get_version_git', 'get_version_with_build', 'help_part', 'hikyuu_init', 'hku_benchmark', 'hku_catch', 'hku_check', 'hku_check_ignore', 'hku_check_throw', 'hku_debug', 'hku_debug_if', 'hku_error', 'hku_error_if', 'hku_fatal', 'hku_fatal_if', 'hku_info', 'hku_info_if', 'hku_logger', 'hku_run_ignore_exception', 'hku_to_async', 'hku_trace', 'hku_trace_if', 'hku_warn', 'hku_warn_if', 'hub', 'ibar', 'iheatmap', 'imread', 'in_interactive_session', 'in_ipython_frontend', 'indicator', 'inner_analysis_sys_list', 'inner_combinate_ind_analysis', 'inner_combinate_ind_analysis_with_block', 'io', 'iplot', 'is_valid_license', 'isinf', 'isnan', 'kplot', 'krecords_to_df', 'krecords_to_np', 'krecords_to_pa', 'locale', 'logging', 'math', 'matplotlib', 'mkplot', 'new_Query_init', 'new_path', 'np', 'old_Query_init', 'open_ostream_to_python', 'open_spend_time', 'os', 'parallel_run_pf', 'parallel_run_sys', 'part_clone', 'part_init', 'part_iter', 'pd', 'pickle', 'positions_to_df', 'positions_to_np', 'positions_to_pa', 'print_part_info', 'pyind', 'rcParams', 'register_extra_ktype', 'release_extra_ktype', 'remove_hub', 'remove_license', 'roundDown', 'roundEx', 'roundUp', 'run_in_strategy', 'scorerecords_to_df', 'scorerecords_to_np', 'search_part', 'set_log_level', 'set_mpl_params', 'set_my_logger_file', 'set_python_in_interactive', 'set_python_in_jupyter', 'sgplot', 'sns', 'spend_time', 'spot_agent_is_connected', 'spot_agent_is_running', 'start_data_server', 'start_spot_agent', 'stop_data_server', 'stop_spot_agent', 'sys', 'sys_heatmap', 'sys_performance', 'sysplot', 'systemweights_to_df', 'systemweights_to_np', 'timedelta', 'timeline_to_df', 'timeline_to_np', 'timeline_to_pa', 'timeout', 'tm_heatmap', 'tm_performance', 'toPriceList', 'traceback', 'trade', 'trade_manage', 'trade_sys', 'trades_to_df', 'trades_to_np', 'trades_to_pa', 'translist_to_df', 'translist_to_np', 'translist_to_pa', 'update_hub', 'util', 'view_license', 'weights_to_df', 'weights_to_np', 'weights_to_pa', 'with_trace', 'ylabel']
class StockFuncFormatter:
    """
    用于坐标轴显示日期
        关于matplotlib中FuncFormatter的使用方法，请参见：
        http://matplotlib.sourceforge.net/examples/api/date_index_formatter.html
        
    """
    def __call__(self, x, pos = None):
        ...
    def __init__(self, ix2date):
        ...
def DRAWBAND(val1: hikyuu.cpp.core310.Indicator, color1 = 'm', val2: hikyuu.cpp.core310.Indicator = None, color2 = 'b', kdata = None, alpha = 0.2, new = False, axes = None, linestyle = '-'):
    """
    画出带状线
    
        用法:DRAWBAND(val1, color1, val2, color2), 当 val1 > val2 时,在 val1 和 val2 之间填充 color1;
        当 val1 < val2 时,填充 color2,这里的颜色均使用 matplotlib 颜色代码.
        例如:DRAWBAND(OPEN, 'r', CLOSE, 'b')
    
        Args:
            val1 (Indicator): 指标1
            color1 (str, optional): 颜色1. Defaults to 'm'.
            val2 (Indicator, optional): 指标2. Defaults to None.
            color2 (str, optional): 颜色2. Defaults to 'b'.
            kdata (_type_, optional): 指定指标上下文. Defaults to None.
            alpha (float, optional): 透明度. Defaults to 0.2.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 在指定的坐标轴中绘制. Defaults to None.
            linestyle (str, optional): 包络线类型. Defaults to '-'.
        
    """
def DRAWICON(cond: hikyuu.cpp.core310.Indicator, price: hikyuu.cpp.core310.Indicator, type: int, kdata: hikyuu.cpp.core310.KData = None, new = False, axes = None, *args, **kwargs):
    """
    绘制内置 icon
    
        用法:DRAWICON(cond,price,1),当条件 cond 满足时,在 price 位置编号为1的内置图标
        例如:DRAWICON(O>C,CLOSE, 1)。
    
        可以使用 SHOWICONS() 显示所有内置图标。
    
        Args:
            cond (Indicator): 指定条件
            price (Indicator): 指定价格
            type (int): icon 编号
            kdata (KData, optional): 指定上下文. Defaults to None.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 在指定坐标轴中绘制. Defaults to None.
        
    """
def DRAWIMG(cond: hikyuu.cpp.core310.Indicator, price: hikyuu.cpp.core310.Indicator, img: str, kdata: hikyuu.cpp.core310.KData = None, new = False, axes = None, *args, **kwargs):
    """
    画图片
    
        用法:DRAWIMG(cond,price,'图像文件文件名'),当条件 cond 满足时,在 price 位置画指定的图片
        例如:DRAWIMG(O>C,CLOSE, '123.png')。
    
        Args:
            cond (Indicator): 指定条件
            price (Indicator): 指定价格
            img (str): 图像文件名
            kdata (KData, optional): 指定上下文. Defaults to None.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 在指定坐标轴中绘制. Defaults to None.
        
    """
def DRAWLINE(cond1: hikyuu.cpp.core310.Indicator, price1: hikyuu.cpp.core310.Indicator, cond2: hikyuu.cpp.core310.Indicator, price2: hikyuu.cpp.core310.Indicator, expand: int = 0, kdata: hikyuu.cpp.core310.KData = None, color: str = 'm', new = False, axes = None, *args, **kwargs):
    """
    在图形上绘制直线段。
    
        用法：DRAWLINE(cond1, price1, cond2, price2, expand)
        当COND1条件满足时，在PRICE1位置画直线起点，当COND2条件满足时，在PRICE2位置画直线终点，EXPAND为延长类型。
        例如：DRAWLINE(HIGH>=HHV(HIGH,20),HIGH,LOW<=LLV(LOW,20),LOW,1)表示在创20天新高与创20天新低之间画直线并且向右延长
    
        Args:
            cond1 (Indicator): 条件1
            price1 (Indicator): 位置1
            cond2 (Indicator): 条件2
            price2 (Indicator): 位置2
            expand (int, optional): 0: 不延长 | 1: 向右延长 | 10: 向左延长 | 11: 双向延长. Defaults to 0.
            kdata (KData, optional): 指定的上下文. Defaults to None.
            color (str, optional): 指定颜色. Defaults to 'm'.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 指定的坐标轴. Defaults to None.
        
    """
def DRAWNUMBER(cond: hikyuu.cpp.core310.Indicator, price: hikyuu.cpp.core310.Indicator, number: hikyuu.cpp.core310.Indicator, kdata: hikyuu.cpp.core310.KData = None, color: str = 'm', new = False, axes = None, *args, **kwargs):
    """
    画出数字.
    
        用法:DRAWNUMBER(cond, price, number),当 cond 条件满足时,在 price 位置书写数字 number.
        例如:DRAWNUMBER(CLOSE/OPEN>1.08,LOW,C)表示当日实体阳线大于8%时在最低价位置显示收盘价。
    
        Args:
            cond (Indicator): 条件
            price (Indicator): 绘制位置
            number (Indicator): 待绘制数字
            kdata (KData, optional): 指定的上下文. Defaults to None.
            color (str, optional): 指定颜色. Defaults to 'm'.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 指定的坐标轴. Defaults to None.
        
    """
def DRAWNUMBER_FIX(cond: hikyuu.cpp.core310.Indicator, x: float, y: float, type: int, number: float, kdata: hikyuu.cpp.core310.KData = None, color: str = 'm', new = False, axes = None, *args, **kwargs):
    """
    固定位置显示数字.
    
        用法:DRAWNUMBER_FIX(cond,x,y,type,number), cond 中一般需要加 ISLASTBAR, 当 cond 条件满足时,
        在当前指标窗口内 (x, y) 位置书写数字 number, x,y为书写点在窗口中相对于左上角的百分比,type:0为左对齐,1为右对齐。
    
        例如:DRAWNUMBER_FIX(ISLASTBAR() & (CLOSE/OPEN>1.08), 0.5,0.5,0,C)表示最后一个交易日实体阳线大于8%时在窗口中间位置显示收盘价
    
        Args:
            cond (Indicator): _description_
            x (float): _description_
            y (float): _description_
            type (int): _description_
            number (Indicator): _description_
            kdata (KData, optional): _description_. Defaults to None.
            color (str, optional): _description_. Defaults to 'm'.
            new (bool, optional): _description_. Defaults to False.
            axes (_type_, optional): _description_. Defaults to None.
        
    """
def DRAWRECTREL(left: int, top: int, right: int, bottom: int, color = 'm', frame = True, fill = True, alpha = 0.1, new = False, axes = None, *args, **kwargs):
    """
    相对位置上画矩形.
    
        注意：原点为坐标轴左上角(0, 0)，和 matplotlib 不同。
        用法: DRAWRECTREL(left,top,right,bottom,color), 以图形窗口 (left, top) 为左上角, (right, bottom) 为
             右下角绘制矩形, 坐标单位是窗口沿水平和垂直方向的1/1000,取值范围是0—999,超出范围则可能显示在图形窗口外,矩形
             中间填充颜色COLOR,COLOR为0表示不填充.
        例如:DRAWRECTREL(0,0,500,500,RGB(255,255,0)) 表示在图形最左上部1/4位置用黄色绘制矩形
    
        Args:
            left (int): 左上角x
            top (int): 左上角y
            right (int): 右下角x
            bottom (int): 右下角y
            color (str, optional): 指定颜色. Defaults to 'm'.
            frame (bool, optional): 添加边框. Defaults to False.
            fill (bool, optional): 颜色填充. Defaults to True.
            alpha (float, optional): 透明度. Defaults to 0.1.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 指定的坐标轴. Defaults to None.
        
    """
def DRAWSL(cond: hikyuu.cpp.core310.Indicator, price: hikyuu.cpp.core310.Indicator, slope: typing.Union[hikyuu.cpp.core310.Indicator, float, int], length: typing.Union[hikyuu.cpp.core310.Indicator, float, int], direct: int, kdata: hikyuu.cpp.core310.KData = None, color: str = 'm', new = False, axes = None, *args, **kwargs):
    """
    绘制斜线.
    
        用法:DRAWSL(cond,price,slope,length,diect),当 cond 条件满足时,在 price 位置画斜线, slope 为斜率, 
        lengh为长度, direct 为0向右延伸,1向左延伸,2双向延伸。
    
        注意:
        1. K线间的纵向高度差为 slope;
        2. slope 为 0 时, 为水平线;
        3. slope 为 10000 时, 为垂直线, length 为向上的像素高度, direct 表示向上或向下延伸
        4. slope 和 length 支持变量;
    
        Args:
            cond (Indicator): 条件指标
            price (Indicator): 价格
            slope (int|float|Indicator): 斜率
            length (int|float|Indicator): 长度
            direct (int): 方向
            kdata (KData, optional): 指定的上下文. Defaults to None.
            color (str, optional): 颜色. Defaults to 'm'.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 指定的坐标轴. Defaults to None.
        
    """
def DRAWTEXT(cond: hikyuu.cpp.core310.Indicator, price: hikyuu.cpp.core310.Indicator, text: str, kdata: hikyuu.cpp.core310.KData = None, color: str = 'm', new = False, axes = None, *args, **kwargs):
    """
    在图形上显示文字。
    
        用法: DRAWTEXT(cond, price, text), 当 cond 条件满足时, 在 price 位置书写文字 text。
        例如: DRAWTEXT(CLOSE/OPEN>1.08,LOW,'大阳线')表示当日实体阳线大于8%时在最低价位置显示'大阳线'字样.
    
        Args:
            cond (Indicator): 条件
            price (Indicator): 显示位置
            text (str): 待显示文字
            kdata (KData, optional): 指定的上下文. Defaults to None.
            color (str, optional): 指定颜色. Defaults to 'm'.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 指定的坐标轴. Defaults to None.
        
    """
def DRAWTEXT_FIX(cond: hikyuu.cpp.core310.Indicator, x: float, y: float, type: int, text: str, kdata: hikyuu.cpp.core310.KData = None, color: str = 'm', new = False, axes = None, *args, **kwargs):
    """
    固定位置显示文字
    
        用法:DRAWTEXT_FIX(cond,x y, text), cond 中一般需要加 ISLASTBAR,当 cond 条件满足时,
        在当前指标窗口内(X,Y)位置书写文字TEXT,X,Y为书写点在窗口中相对于左上角的百分比
    
        例如:DRAWTEXT_FIX(ISLASTBAR() & (CLOSE/OPEN>1.08),0.5,0.5,0,'大阳线')表示最后一个交易日实体阳线
        大于8%时在窗口中间位置显示'大阳线'字样.
    
        Args:
            cond (Indicator): 条件
            x (float): x轴坐标
            y (float): y轴坐标
            type (int, optional): 0 左对齐 | 1 右对齐. 
            text (str): 待显示文字
            kdata (KData, optional): 指定的上下文. Defaults to None.
            color (str, optional): 指定颜色. Defaults to 'm'.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 指定坐标轴. Defaults to None.
        
    """
def PLOYLINE(cond: hikyuu.cpp.core310.Indicator, price: hikyuu.cpp.core310.Indicator, kdata: hikyuu.cpp.core310.KData = None, color: str = 'm', linewidth = 1.0, new = False, axes = None, *args, **kwargs):
    """
    在图形上绘制折线段。
    
        用法：PLOYLINE(COND，PRICE)，当COND条件满足时，以PRICE位置为顶点画折线连接。
        例如：PLOYLINE(HIGH>=HHV(HIGH,20),HIGH, kdata=k)表示在创20天新高点之间画折线。
    
        Args:
            cond (Indicator): 指定条件
            price (Indicator): 位置
            kdata (KData, optional): 指定的上下文. Defaults to None.
            color (str, optional): 颜色. Defaults to 'b'.
            linewidth (float, optional): 宽度. Defaults to 1.0.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 指定的axes. Defaults to None.
        
    """
def RGB(r: int, g: int, b: int):
    ...
def SHOWICONS():
    """
    显示所有内置图标
    """
def STICKLINE(cond: hikyuu.cpp.core310.Indicator, price1: hikyuu.cpp.core310.Indicator, price2: hikyuu.cpp.core310.Indicator, width: float = 2.0, empty: bool = False, color = 'm', alpha = 1.0, kdata = None, new = False, axes = None):
    """
    在满足cond的条件下，在 price1 和 price2 之间绘制一个宽度为 width 的柱状图。
    
        注意: cond, price1, price2 应含有数据，否则请指定 kdata 作为指标计算的上下文
    
        参数说明:
            cond (Indicator): 条件表达式，用于确定是否绘制柱状线
            price1 (Indicator): 第一个价格
            price2 (Indicator): 第二个价格
            width (float, optional): 柱状宽度. Defaults to 2.0.
            empty (bool, optional): 空心. Defaults to False.
            kdata (_type_, optional): 指定的上下文K线. Defaults to None.
            new (bool, optional): 在新窗口中绘制. Defaults to False.
            axes (_type_, optional): 在指定的坐标轴中绘制. Defaults to None.
            color (str, optional): 颜色. Defaults to 'm'.
            alpha (float, optional): 透明度. Defaults to 1.0.
        
    """
def adjust_axes_show(axeslist):
    """
    用于调整上下紧密相连的坐标轴显示时，其上一坐标轴最小值刻度和下一坐标轴最大值刻度
        显示重叠的问题。
    
        :param axeslist: 上下相连的坐标轴列表 (ax1,ax2,...)
        
    """
def ax_draw_macd(axes, kdata, n1 = 12, n2 = 26, n3 = 9):
    """
    绘制MACD
    
        :param axes: 指定的坐标轴
        :param KData kdata: KData
        :param int n1: 指标 MACD 的参数1
        :param int n2: 指标 MACD 的参数2
        :param int n3: 指标 MACD 的参数3
        
    """
def ax_draw_macd2(axes, ref, kdata, n1 = 12, n2 = 26, n3 = 9):
    """
    绘制MACD。
        当BAR值变化与参考序列ref变化不一致时，显示为灰色，
        当BAR和参考序列ref同时上涨，显示红色
        当BAR和参考序列ref同时下跌，显示绿色
    
        :param axes: 指定的坐标轴
        :param ref: 参考序列，EMA
        :param KData kdata: KData
        :param int n1: 指标 MACD 的参数1
        :param int n2: 指标 MACD 的参数2
        :param int n3: 指标 MACD 的参数3
        
    """
def ax_set_locator_formatter(axes, dates, typ):
    """
     设置指定坐标轴的日期显示，根据指定的K线类型优化X轴坐标显示
    
        :param axes: 指定的坐标轴
        :param dates: Datetime构成可迭代序列
        :param Query.KType typ: K线类型
        
    """
def cnplot(cn, new = True, axes = None, kdata = None, upcolor = 'red', downcolor = 'blue', alpha = 0.2):
    """
    绘制系统有效条件
    
        :param ConditionBase cn: 系统有效条件
        :param new: 仅在未指定axes的情况下生效，当为True时，创建新的窗口对象并在其中进行绘制
        :param axes: 指定在那个轴对象中进行绘制
        :param KData kdata: 指定的KData，如该值为None，则认为该系统有效条件已经
                            指定了交易对象，否则，使用该参数作为交易对象
        :param upcolor: 有效数时的颜色
        :param downcolor: 无效时的颜色
        :param alpha: 透明度
        
    """
def create_figure(n = 1, figsize = (10, 8)):
    """
    生成含有指定坐标轴数量的窗口，最大只支持4个坐标轴。
    
        :param int n: 坐标轴数量
        :param figsize: (宽, 高)
        :return: (ax1, ax2, ...) 根据指定的坐标轴数量而定，超出[1,4]个坐标轴时，返回None
        
    """
def create_four_axes_figure(figsize = (10, 8)):
    """
    生成一个含有4个坐标轴的figure，并返回坐标轴列表
    
        :param figsize: (宽, 高)
        :return: (ax1, ax2, ax3, ax4)
        
    """
def create_one_axes_figure(figsize = (10, 6)):
    """
    生成一个仅含有1个坐标轴的figure，并返回其坐标轴对象
    
        :param figsize: (宽, 高)
        :return: ax
        
    """
def create_three_axes_figure(figsize = (10, 8)):
    """
    生成一个含有3个坐标轴的figure，并返回坐标轴列表
    
        :param figsize: (宽, 高)
        :return: (ax1, ax2, ax3)
        
    """
def create_two_axes_figure(figsize = (10, 8)):
    """
    生成一个含有2个坐标轴的figure，并返回坐标轴列表
    
        :param figsize: (宽, 高)
        :return: (ax1, ax2)
        
    """
def evplot(ev, ref_kdata, new = True, axes = None, upcolor = 'red', downcolor = 'blue', alpha = 0.2):
    """
    绘制市场有效判断
    
        :param EnvironmentBase cn: 系统有效条件
        :param KData ref_kdata: 用于日期参考
        :param new: 仅在未指定axes的情况下生效，当为True时，创建新的窗口对象并在其中进行绘制
        :param axes: 指定在那个轴对象中进行绘制
        :param upcolor: 有效时的颜色
        :param downcolor: 无效时的颜色
        :param alpha: 透明度
        
    """
def getDayLocatorAndFormatter(dates):
    """
    获取显示日线时使用的Major Locator和Major Formatter
    """
def getMinLocatorAndFormatter(dates):
    """
    获取显示分钟线时使用的Major Locator和Major Formatter
    """
def ibar(indicator, new = True, axes = None, kref = None, legend_on = False, text_on = False, text_color = 'k', label = None, width = 0.4, color = 'r', edgecolor = 'r', zero_on = False, *args, **kwargs):
    """
    绘制indicator柱状图
    
        :param Indicator indicator: Indicator实例
        :param axes:       指定的坐标轴
        :param new:        是否在新窗口中显示，只在没有指定axes时生效
        :param kref:       参考的K线数据，以便绘制日期X坐标
        :param legend_on:  是否打开图例
        :param text_on:    是否在左上角显示指标名称及其参数
        :param text_color: 指标名称解释文字的颜色，默认为黑色
        :param str label:  label显示文字信息，text_on 及 legend_on 为 True 时生效
        :param zero_on:    是否需要在y=0轴上绘制一条直线
        :param width:      Bar的宽度
        :param color:      Bar的颜色
        :param edgecolor:  Bar边缘颜色
        :param args:       pylab plot参数
        :param kwargs:     pylab plot参数
        
    """
def iheatmap(ind, axes = None):
    """
    
        绘制指标收益年-月收益热力图
    
        指标收益率 = (当前月末值 - 上月末值) / 上月末值 * 100
    
        指标应已计算（即有值），且为时间序列
    
        :param ind: 指定指标
        :param axes: 绘制的轴对象，默认为None，表示创建新的轴对象
        :return: None
        
    """
def iplot(indicator, new = True, axes = None, kref = None, legend_on = False, text_on = False, text_color = 'k', zero_on = False, label = None, linestyle = '-', *args, **kwargs):
    """
    绘制indicator曲线
    
        :param Indicator indicator: indicator实例
        :param axes:            指定的坐标轴
        :param new:             是否在新窗口中显示，只在没有指定axes时生效
        :param kref:            参考的K线数据，以便绘制日期X坐标
        :param legend_on:       是否打开图例
        :param text_on:         是否在左上角显示指标名称及其参数
        :param text_color:      指标名称解释文字的颜色，默认为黑色
        :param zero_on:         是否需要在y=0轴上绘制一条直线
        :param str label:       label显示文字信息，text_on 及 legend_on 为 True 时生效
        :param args:            pylab plot参数
        :param kwargs:          pylab plot参数，如：marker（标记类型）、
                                 markerfacecolor（标记颜色）、
                                 markeredgecolor（标记的边缘颜色）
        
    """
def kplot(kdata, new = True, axes = None, colorup = 'r', colordown = 'g'):
    """
    绘制K线图
    
        :param KData kdata: K线数据
        :param bool new:    是否在新窗口中显示，只在没有指定axes时生效
        :param axes:        指定的坐标轴
        :param colorup:     the color of the rectangle where close >= open
        :param colordown:   the color of the rectangle where close < open
        
    """
def mkplot(kdata, new = True, axes = None, colorup = 'r', colordown = 'g', ticksize = 3):
    """
    绘制美式K线图
    
        :param KData kdata: K线数据
        :param bool new:    是否在新窗口中显示，只在没有指定axes时生效
        :param axes:        指定的坐标轴
        :param colorup:     the color of the lines where close >= open
        :param colordown:   the color of the lines where close < open
        :param ticksize:    open/close tick marker in points
        
    """
def set_mpl_params():
    """
    设置交互及中文环境参数
    """
def sgplot(sg, new = True, axes = None, style = 1, kdata = None):
    """
    绘制买入/卖出信号
    
        :param SignalBase sg: 信号指示器
        :param new: 仅在未指定axes的情况下生效，当为True时，创建新的窗口对象并在其中进行绘制
        :param axes: 指定在那个轴对象中进行绘制
        :param style: 1 | 2 信号箭头绘制样式
        :param KData kdata: 指定的KData（即信号发生器的交易对象），
                           如该值为None，则认为该信号发生器已经指定了交易对象，
                           否则，使用该参数作为交易对象
        
    """
def sys_heatmap(sys, axes = None):
    """
    
        绘制系统收益年-月收益热力图
        
    """
def sys_performance(sys, ref_stk = None):
    """
    
        绘制系统绩效，即账户累积收益率曲线
    
        :param SystemBase | PortfolioBase sys: SYS或PF实例
        :param Stock ref_stk: 参考股票, 默认为沪深300: sh000300, 绘制参考标的的收益曲线
        :return: None
        
    """
def sysplot(sys, new = True, axes = None, style = 1, only_draw_close = False):
    """
    绘制系统实际买入/卖出信号
    
        :param SystemBase sys: 系统实例
        :param new:   仅在未指定axes的情况下生效，当为True时，
                       创建新的窗口对象并在其中进行绘制
        :param axes:  指定在那个轴对象中进行绘制
        :param style: 1 | 2 信号箭头绘制样式
        :param bool only_draw_close: 不绘制K线，仅绘制 close
        
    """
def tm_heatmap(tm, start_date, end_date = None, axes = None):
    """
    
        绘制账户收益年-月收益热力图
    
        :param tm: 交易账户
        :param start_date: 开始日期
        :param end_date: 结束日期，默认为今天
        :param axes: 绘制的轴对象，默认为None，表示创建新的轴对象
        :return: None
        
    """
def tm_performance(tm: hikyuu.cpp.core310.TradeManager, query: hikyuu.cpp.core310.Query, ref_stk: hikyuu.cpp.core310.Stock = None):
    """
    
        绘制系统绩效，即账户累积收益率曲线
    
        :param SystemBase | PortfolioBase sys: SYS或PF实例
        :param Stock ref_stk: 参考股票, 默认为沪深300: sh000300, 绘制参考标的的收益曲线
        :return: None
        
    """
AMO: hikyuu.cpp.core310.Indicator  # value = Indicator{...
BASE_DIR: str = '/app/hikyuu/hikyuu'
CLOSE: hikyuu.cpp.core310.Indicator  # value = Indicator{...
DEBUG: hikyuu.cpp.core310.LOG_LEVEL  # value = <LOG_LEVEL.DEBUG: 1>
DRAWNULL: float  # value = nan
ERROR: hikyuu.cpp.core310.LOG_LEVEL  # value = <LOG_LEVEL.ERROR: 4>
FATAL: hikyuu.cpp.core310.LOG_LEVEL  # value = <LOG_LEVEL.FATAL: 5>
HIGH: hikyuu.cpp.core310.Indicator  # value = Indicator{...
ICON_PATH: str = '/app/hikyuu/hikyuu/draw/drawplot'
INFO: hikyuu.cpp.core310.LOG_LEVEL  # value = <LOG_LEVEL.INFO: 2>
KDATA: hikyuu.cpp.core310.Indicator  # value = Indicator{...
LOW: hikyuu.cpp.core310.Indicator  # value = Indicator{...
OFF: hikyuu.cpp.core310.LOG_LEVEL  # value = <LOG_LEVEL.OFF: 6>
OPEN: hikyuu.cpp.core310.Indicator  # value = Indicator{...
TICKLEFT: int = 0
TICKRIGHT: int = 1
TRACE: hikyuu.cpp.core310.LOG_LEVEL  # value = <LOG_LEVEL.TRACE: 0>
VOL: hikyuu.cpp.core310.Indicator  # value = Indicator{...
WARN: hikyuu.cpp.core310.LOG_LEVEL  # value = <LOG_LEVEL.WARN: 3>
constant: hikyuu.cpp.core310.Constant  # value = <hikyuu.cpp.core310.Constant object>
current_path: str = '/usr/lib/x86_64-linux-gnu:/usr/lib/aarch64-linux-gnu:/opt/miniconda3/lib'
dll_directory: str = '/app/hikyuu/hikyuu/cpp'
fm_logger: logging.Logger  # value = <Logger matplotlib.font_manager (INFO)>
hku_logger: logging.Logger  # value = <Logger hikyuu (INFO)>
new_path: str = '/app/hikyuu/hikyuu/cpp:/usr/lib/x86_64-linux-gnu:/usr/lib/aarch64-linux-gnu:/opt/miniconda3/lib'
rcParams: matplotlib.RcParams  # value = RcParams({'_internal.classic_mode': False,...
DRAWBMP = DRAWIMG
