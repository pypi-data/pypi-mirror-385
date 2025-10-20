# -*- coding: utf-8 -*-
# 版权所有 2021 深圳米筐科技有限公司（下称“米筐科技”）
#
# 除非遵守当前许可，否则不得使用本软件。
#
#     * 非商业用途（非商业用途指个人出于非商业目的使用本软件，或者高校、研究所等非营利机构出于教育、科研等目的使用本软件）：
#         遵守 Apache License 2.0（下称“Apache 2.0 许可”），
#         您可以在以下位置获得 Apache 2.0 许可的副本：http://www.apache.org/licenses/LICENSE-2.0。
#         除非法律有要求或以书面形式达成协议，否则本软件分发时需保持当前许可“原样”不变，且不得附加任何条件。
#
#     * 商业用途（商业用途指个人出于任何商业目的使用本软件，或者法人或其他组织出于任何目的使用本软件）：
#         未经米筐科技授权，任何个人不得出于任何商业目的使用本软件（包括但不限于向第三方提供、销售、出租、出借、转让本软件、
#         本软件的衍生产品、引用或借鉴了本软件功能或源代码的产品或服务），任何法人或其他组织不得出于任何目的使用本软件，
#         否则米筐科技有权追究相应的知识产权侵权责任。
#         在此前提下，对本软件的使用同样需要遵守 Apache 2.0 许可，Apache 2.0 许可与本许可冲突之处，以本许可为准。
#         详细的授权流程，请联系 public@ricequant.com 获取。

from matplotlib import rcParams, pyplot as plt
from matplotlib.font_manager import findfont, FontProperties

from rqalpha.utils.logger import system_log
from rqalpha.utils.i18n import gettext as _

from .utils import IndicatorInfo, LineInfo, SpotInfo

plt.style.use('ggplot')

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = [
    'Microsoft Yahei', 'Heiti SC', 'Heiti TC', 'STHeiti', 'WenQuanYi Zen Hei',
    'WenQuanYi Micro Hei', "文泉驿微米黑", 'SimHei', 'Arial Unicode MS'
] + rcParams['font.sans-serif']
rcParams['axes.unicode_minus'] = False

font = findfont(FontProperties(family=['sans-serif']))
if "/matplotlib/" in font:
    system_log.warn("PLOT: Missing Chinese fonts. Fallback to English.")
    LABEL_FONT_SIZE = 9
    _ = lambda txt: txt
    SUPPORT_CHINESE = False
else:
    LABEL_FONT_SIZE = 11
    SUPPORT_CHINESE = True

TITLE_FONT_SIZE = 16

RED = "#aa4643"
BLUE = "#4572a7"
YELLOW = "#F3A423"
BLACK = "#000000"

IMG_WIDTH = 15

# 两部分的相对高度
PLOT_TITLE_HEIGHT = 1
INDICATOR_AREA_HEIGHT = 3
PLOT_AREA_HEIGHT = 5
USER_PLOT_AREA_HEIGHT = 2

LINE_STRATEGY = LineInfo(_("Strategy"), RED, 1, 2)
LINE_BENCHMARK = LineInfo(_("Benchmark"), BLUE, 1, 2)
LINE_EXCESS = LineInfo(_("Excess"), YELLOW, 1, 2)
LINE_WEEKLY = LineInfo(_("Weekly"), RED, 0.6, 2)
LINE_WEEKLY_BENCHMARK = LineInfo(_("BenchmarkWeekly"), BLUE, 0.6, 2)

MAX_DD = SpotInfo(_("MaxDrawDown"), "v", "Green", 8, 0.7)
MAX_DDD = SpotInfo(_("MaxDDD"), "D", "Blue", 8, 0.7)
OPEN_POINT = SpotInfo(_("Open"), "P", "#FF7F50", 8, 0.9)
CLOSE_POINT = SpotInfo(_("Close"), "X", "#008B8B", 8, 0.9)


class PlotTemplate:
    """ 作图模版 """

    def __init__(self, p_nav, b_nav):
        self.p_nav = p_nav
        self.b_nav = b_nav

    # 指标的宽高
    INDICATOR_WIDTH = 0
    INDICATOR_VALUE_HEIGHT = 0
    INDICATOR_LABEL_HEIGHT = 0

    # 指标
    INDICATORS = []
    WEEKLY_INDICATORS = []
    EXCESS_INDICATORS = []

    @property
    def geometric_excess_returns(self):
        return self.p_nav / self.b_nav - 1


class DefaultPlot(PlotTemplate):
    """ 基础 """

    # 指标的宽高
    INDICATOR_WIDTH = 0.15
    INDICATOR_VALUE_HEIGHT = 0.15
    INDICATOR_LABEL_HEIGHT = 0.1

    INDICATORS = [[
        IndicatorInfo("total_returns", _("TotalReturns"), RED, "{0:.3%}", 11, 1),
        IndicatorInfo("annualized_returns", _("AnnualReturns"), RED, "{0:.3%}", 11, 1),
        IndicatorInfo("alpha", _("Alpha"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("beta", _("Beta"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("sharpe", _("Sharpe"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("sortino", _("Sortino"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("weekly_ulcer_index", _("WeeklyUlcerIndex"), BLACK, "{0:.4}", 11, 1.4),
    ], [
        IndicatorInfo("benchmark_total_returns", _("BenchmarkReturns"), BLUE, "{0:.3%}", 11, 1),
        IndicatorInfo("benchmark_annualized_returns", _("BenchmarkAnnual"), BLUE, "{0:.3%}", 11, 1),
        IndicatorInfo("volatility", _("Volatility"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("tracking_error", _("TrackingError"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("downside_risk", _("DownsideRisk"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("information_ratio", _("InformationRatio"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("weekly_ulcer_performance_index", _("WeeklyUlcerPerformanceIndex"), BLACK, "{0:.4}", 11, 1.4),
    ], [
        IndicatorInfo("excess_cum_returns", _("ExcessCumReturns"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("win_rate", _("WinRate"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("weekly_win_rate", _("WeeklyWinRate"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("profit_loss_rate", _("ProfitLossRate"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("max_drawdown", _("MaxDrawDown"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("max_dd_ddd", _("MaxDD/MaxDDD"), BLACK, "{}", 6, 1),
        IndicatorInfo("weekly_excess_ulcer_index", _("WeeklyExcessUlcerIndex"), BLACK, "{0:.4}", 11, 1.4),
    ]]

    WEEKLY_INDICATORS = [[
        IndicatorInfo("weekly_alpha", _("WeeklyAlpha"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("weekly_beta", _("WeeklyBeta"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("weekly_sharpe", _("WeeklySharpe"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("weekly_information_ratio", _("WeeklyInfoRatio"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("weekly_tracking_error", _("WeeklyTrackingError"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("weekly_max_drawdown", _("WeeklyMaxDrawdown"), BLACK, "{0:.3%}", 11, 1),
    ]]

    EXCESS_INDICATORS = [[
        IndicatorInfo("excess_returns", _("ExcessReturns"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_annual_returns", _("ExcessAnnual"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_sharpe", _("ExcessSharpe"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("excess_volatility", _("ExcessVolatility"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_max_drawdown", _("ExcessMaxDD"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_max_dd_ddd", _("ExcessMaxDD/ExcessMaxDDD"), BLACK, "{}", 6, 1),
        IndicatorInfo("weekly_excess_ulcer_performance_index", _("WeeklyExcessUlcerPerformanceIndex"), BLACK, "{0:.4}", 11, 1.4),
    ]]


class RiceQuant(PlotTemplate):
    # 指标的宽高
    INDICATOR_WIDTH = 0.22
    INDICATOR_VALUE_HEIGHT = 0.15
    INDICATOR_LABEL_HEIGHT = 0.1

    INDICATORS = [[
        IndicatorInfo("total_returns", _("TotalReturns"), RED, "{0:.3%}", 11, 1),
        IndicatorInfo("annualized_returns", _("AnnualReturns"), RED, "{0:.3%}", 11, 1),
        IndicatorInfo("alpha", _("Alpha"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("beta", _("Beta"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("win_rate", _("WinRate"), BLACK, "{0:.3%}", 11, 1),
    ], [
        IndicatorInfo("sharpe", _("Sharpe"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("weekly_sharpe", _("WeeklySharpe"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("monthly_sharpe", _("MonthlySharpe"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("information_ratio", _("InformationRatio"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("sortino", _("Sortino"), BLACK, "{0:.4}", 11, 1),
    ], [
        IndicatorInfo("volatility", _("Volatility"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("weekly_volatility", _("WeeklyVolatility"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("monthly_volatility", _("MonthlyVolatility"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("max_drawdown", _("MaxDrawDown"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("max_dd_ddd", _("MaxDD/MaxDDD"), BLACK, "{}", 6, 1),
    ]]

    EXCESS_INDICATORS = [[
        IndicatorInfo("benchmark_total_returns", _("BenchmarkReturns"), BLUE, "{0:.3%}", 11, 1),
        IndicatorInfo("benchmark_annualized_returns", _("BenchmarkAnnual"), BLUE, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_returns", _("ExcessReturns"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_annual_returns", _("ExcessAnnual"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_cum_returns", _("ExcessCumReturns"), BLACK, "{0:.3%}", 11, 1),
    ], [
        IndicatorInfo("excess_sharpe", _("ExcessSharpe"), BLACK, "{0:.4}", 11, 1),
        IndicatorInfo("excess_volatility", _("ExcessVolatility"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_win_rate", _("ExcessWinRate"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_max_drawdown", _("ExcessMaxDD"), BLACK, "{0:.3%}", 11, 1),
        IndicatorInfo("excess_max_dd_ddd", _("ExcessMaxDD/ExcessMaxDDD"), BLACK, "{}", 6, 1),
    ]]

    WEEKLY_INDICATORS = []


PLOT_TEMPLATE: dict = {
    "default": DefaultPlot,
    "ricequant": RiceQuant
}