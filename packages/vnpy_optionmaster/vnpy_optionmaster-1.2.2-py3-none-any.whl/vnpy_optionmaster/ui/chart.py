import pyqtgraph as pg
from typing import cast

from vnpy.trader.ui import QtWidgets, QtCore, QtGui
from vnpy.trader.event import EVENT_TIMER

from ..base import PortfolioData, OptionData
from ..engine import OptionEngine, Event, EventEngine
from ..time import ANNUAL_DAYS

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')                    # noqa
import matplotlib.pyplot as plt             # noqa
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # noqa
from matplotlib.figure import Figure        # noqa
from mpl_toolkits.mplot3d import Axes3D     # noqa
from pylab import mpl                       # noqa

plt.style.use("dark_background")
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']   # set font for Chinese
mpl.rcParams['axes.unicode_minus'] = False


class OptionVolatilityChart(QtWidgets.QWidget):

    signal_timer: QtCore.Signal = QtCore.Signal(Event)

    def __init__(self, option_engine: OptionEngine, portfolio_name: str) -> None:
        """"""
        super().__init__()

        self.option_engine: OptionEngine = option_engine
        self.event_engine: EventEngine = option_engine.event_engine
        self.portfolio_name: str = portfolio_name

        self.timer_count: int = 0
        self.timer_trigger: int = 3

        self.chain_checks: dict[str, QtWidgets.QCheckBox] = {}
        self.put_curves: dict[str, pg.PlotCurveItem] = {}
        self.call_curves: dict[str, pg.PlotCurveItem] = {}
        self.pricing_curves: dict[str, pg.PlotCurveItem] = {}

        self.colors: list = [
            (255, 0, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 0, 255),
            (0, 128, 0),
            (19, 234, 201),
            (195, 46, 212),
            (250, 194, 5),
            (0, 114, 189),
        ]

        self.init_ui()
        self.register_event()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("波动率曲线")

        # Create checkbox for each chain
        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        portfolio: PortfolioData = self.option_engine.get_portfolio(self.portfolio_name)

        chain_symbols: list = list(portfolio.chains.keys())
        chain_symbols.sort()

        hbox.addStretch()

        for chain_symbol in chain_symbols:
            chain_check: QtWidgets.QCheckBox = QtWidgets.QCheckBox()
            chain_check.setText(chain_symbol.split(".")[0])
            chain_check.setChecked(True)
            chain_check.stateChanged.connect(self.update_curve_visible)

            hbox.addWidget(chain_check)
            self.chain_checks[chain_symbol] = chain_check

        hbox.addStretch()

        # Create graphics window
        pg.setConfigOptions(antialias=True)

        graphics_window: pg.GraphicsLayoutWidget = pg.GraphicsLayoutWidget()
        self.impv_chart = graphics_window.addPlot(title="隐含波动率曲线")
        self.impv_chart.showGrid(x=True, y=True)
        self.impv_chart.setLabel("left", "波动率")
        self.impv_chart.setLabel("bottom", "行权价")
        self.impv_chart.addLegend()
        self.impv_chart.setMenuEnabled(False)
        self.impv_chart.setMouseEnabled(False, False)

        for chain_symbol in chain_symbols:
            self.add_impv_curve(chain_symbol)

        # Set Layout
        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(graphics_window)
        self.setLayout(vbox)

    def register_event(self) -> None:
        """"""
        self.signal_timer.connect(self.process_timer_event)

        self.event_engine.register(EVENT_TIMER, self.signal_timer.emit)

    def process_timer_event(self, event: Event) -> None:
        """"""
        self.timer_count += 1
        if self.timer_count < self.timer_trigger:
            return
        self.timer_trigger = 0

        self.update_curve_data()

    def add_impv_curve(self, chain_symbol: str) -> None:
        """"""
        symbol_size: int = 14
        symbol: str = chain_symbol.split(".")[0]
        color: tuple = self.colors.pop(0)
        pen: QtGui.QPen = pg.mkPen(color, width=2)

        self.call_curves[chain_symbol] = self.impv_chart.plot(
            symbolSize=symbol_size,
            symbol="t1",
            name=symbol + " 看涨",
            pen=pen,
            symbolBrush=color
        )
        self.put_curves[chain_symbol] = self.impv_chart.plot(
            symbolSize=symbol_size,
            symbol="t",
            name=symbol + " 看跌",
            pen=pen,
            symbolBrush=color
        )
        self.pricing_curves[chain_symbol] = self.impv_chart.plot(
            symbolSize=symbol_size,
            symbol="o",
            name=symbol + " 定价",
            pen=pen,
            symbolBrush=color
        )

    def update_curve_data(self) -> None:
        """"""
        portfolio: PortfolioData = self.option_engine.get_portfolio(self.portfolio_name)

        for chain in portfolio.chains.values():
            call_impv: list = []
            put_impv: list = []
            pricing_impv: list = []
            strike_prices: list = []

            for index in chain.indexes:
                call: OptionData = chain.calls[index]
                call_impv.append(call.mid_impv * 100)
                pricing_impv.append(call.pricing_impv * 100)
                strike_prices.append(call.strike_price)

                put: OptionData = chain.puts[index]
                put_impv.append(put.mid_impv * 100)

            self.call_curves[chain.chain_symbol].setData(
                y=call_impv,
                x=strike_prices
            )
            self.put_curves[chain.chain_symbol].setData(
                y=put_impv,
                x=strike_prices
            )
            self.pricing_curves[chain.chain_symbol].setData(
                y=pricing_impv,
                x=strike_prices
            )

    def update_curve_visible(self) -> None:
        """"""
        self.impv_chart.clear()

        for chain_symbol, checkbox in self.chain_checks.items():
            if checkbox.isChecked():
                call_curve: pg.PlotCurveItem = self.call_curves[chain_symbol]
                put_curve: pg.PlotCurveItem = self.put_curves[chain_symbol]
                pricing_curve: pg.PlotCurveItem = self.pricing_curves[chain_symbol]

                self.impv_chart.addItem(call_curve)
                self.impv_chart.addItem(put_curve)
                self.impv_chart.addItem(pricing_curve)


class ScenarioAnalysisChart(QtWidgets.QWidget):
    """"""

    def __init__(self, option_engine: OptionEngine, portfolio_name: str) -> None:
        """"""
        super().__init__()

        self.option_engine: OptionEngine = option_engine
        self.portfolio_name: str = portfolio_name

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("情景分析")

        # Create widgets
        self.price_change_spin: QtWidgets.QSpinBox = QtWidgets.QSpinBox()
        self.price_change_spin.setSuffix("%")
        self.price_change_spin.setMinimum(2)
        self.price_change_spin.setValue(10)

        self.impv_change_spin: QtWidgets.QSpinBox = QtWidgets.QSpinBox()
        self.impv_change_spin.setSuffix("%")
        self.impv_change_spin.setMinimum(2)
        self.impv_change_spin.setValue(10)

        self.time_change_spin: QtWidgets.QSpinBox = QtWidgets.QSpinBox()
        self.time_change_spin.setSuffix("日")
        self.time_change_spin.setMinimum(0)
        self.time_change_spin.setValue(1)

        self.target_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.target_combo.addItems([
            "盈亏",
            "Delta",
            "Gamma",
            "Theta",
            "Vega"
        ])

        button: QtWidgets.QPushButton = QtWidgets.QPushButton("执行分析")
        button.clicked.connect(self.run_analysis)

        # Create charts
        fig: Figure = Figure()
        canvas: FigureCanvas = FigureCanvas(fig)

        ax = fig.add_subplot(projection="3d")
        self.ax = cast(Axes3D, ax)
        self.ax.set_xlabel("价格涨跌 %")
        self.ax.set_ylabel("波动率涨跌 %")
        self.ax.set_zlabel("盈亏")

        # Set layout
        hbox1: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox1.addWidget(QtWidgets.QLabel("目标数据"))
        hbox1.addWidget(self.target_combo)
        hbox1.addWidget(QtWidgets.QLabel("时间衰减"))
        hbox1.addWidget(self.time_change_spin)
        hbox1.addStretch()

        hbox2: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox2.addWidget(QtWidgets.QLabel("价格变动"))
        hbox2.addWidget(self.price_change_spin)
        hbox2.addWidget(QtWidgets.QLabel("波动率变动"))
        hbox2.addWidget(self.impv_change_spin)
        hbox2.addStretch()
        hbox2.addWidget(button)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(canvas)

        self.setLayout(vbox)

    def run_analysis(self) -> None:
        """"""
        # Generate range
        portfolio: PortfolioData = self.option_engine.get_portfolio(self.portfolio_name)

        price_change_range = self.price_change_spin.value()
        price_changes = np.arange(-price_change_range, price_change_range + 1) / 100

        impv_change_range = self.impv_change_spin.value()
        impv_changes = np.arange(-impv_change_range, impv_change_range + 1) / 100

        time_change = self.time_change_spin.value() / ANNUAL_DAYS
        target_name = self.target_combo.currentText()

        # Check underlying price exists
        for underlying in portfolio.underlyings.values():
            if not underlying.mid_price:
                QtWidgets.QMessageBox.warning(
                    self,
                    "无法执行情景分析",
                    f"标的物{underlying.symbol}当前中间价为{underlying.mid_price}",
                    QtWidgets.QMessageBox.Ok
                )
                return

        # Run analysis calculation
        pnls: list = []
        deltas: list = []
        gammas: list = []
        thetas: list = []
        vegas: list = []

        for impv_change in impv_changes:
            pnl_buf: list = []
            delta_buf: list = []
            gamma_buf: list = []
            theta_buf: list = []
            vega_buf: list = []

            for price_change in price_changes:
                portfolio_pnl = 0
                portfolio_delta = 0.0
                portfolio_gamma = 0
                portfolio_theta = 0
                portfolio_vega = 0

                # Calculate underlying pnl
                for underlying in portfolio.underlyings.values():
                    if not underlying.net_pos:
                        continue

                    value = underlying.mid_price * underlying.net_pos * underlying.size
                    portfolio_pnl += value * price_change
                    portfolio_delta += value / 100

                # Calculate option pnl
                for option in portfolio.options.values():
                    if not option.net_pos:
                        continue

                    new_underlying_price = option.underlying.mid_price * (1 + price_change)
                    new_time_to_expiry = max(option.time_to_expiry - time_change, 0)
                    new_mid_impv = option.mid_impv * (1 + impv_change)

                    new_price, delta, gamma, theta, vega = option.calculate_greeks(
                        new_underlying_price,
                        option.strike_price,
                        option.interest_rate,
                        new_time_to_expiry,
                        new_mid_impv,
                        option.option_type
                    )

                    # 添加对option.tick为None的检查
                    if option.tick is None:
                        diff = 0
                    else:
                        diff = new_price - option.tick.last_price
                    multiplier = option.net_pos * option.size

                    portfolio_pnl += diff * multiplier
                    portfolio_delta += delta * multiplier
                    portfolio_gamma += gamma * multiplier
                    portfolio_theta += theta * multiplier
                    portfolio_vega += vega * multiplier

                pnl_buf.append(portfolio_pnl)
                delta_buf.append(portfolio_delta)
                gamma_buf.append(portfolio_gamma)
                theta_buf.append(portfolio_theta)
                vega_buf.append(portfolio_vega)

            pnls.append(pnl_buf)
            deltas.append(delta_buf)
            gammas.append(gamma_buf)
            thetas.append(theta_buf)
            vegas.append(vega_buf)

        # Plot chart
        if target_name == "盈亏":
            target_data: list = pnls
        elif target_name == "Delta":
            target_data = deltas
        elif target_name == "Gamma":
            target_data = gammas
        elif target_name == "Theta":
            target_data = thetas
        else:
            target_data = vegas

        self.update_chart(price_changes * 100, impv_changes * 100, target_data, target_name)

    def update_chart(
        self,
        price_changes: np.ndarray,
        impv_changes: np.ndarray,
        target_data: list[list[float]],
        target_name: str
    ) -> None:
        """"""
        self.ax.clear()

        price_changes, impv_changes = np.meshgrid(price_changes, impv_changes)

        self.ax.set_zlabel(target_name)
        self.ax.plot_surface(
            X=price_changes,
            Y=impv_changes,
            Z=np.array(target_data),
            rstride=1,
            cstride=1,
            cmap='coolwarm'
        )
