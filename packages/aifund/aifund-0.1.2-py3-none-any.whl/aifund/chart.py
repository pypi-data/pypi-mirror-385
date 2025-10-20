import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid
from pathlib import Path


class StockKlineChart:
    def __init__(self, df: pd.DataFrame, stock_code: str):
        """
        初始化 K 线图表对象

        :param df: 股票数据 DataFrame
                    可包含中文或英文列名:
                    中文: 日期, 开盘, 收盘, 最低, 最高, 成交量
                    英文: date, open, close, low, high, vol
        :param stock_code: 股票代码
        """
        self.df = df.copy()
        self.stock_code = stock_code

        # 自动统一列名为中文
        self._normalize_columns()

        # 按日期排序，确保数据按时间顺序排列
        self.df = self.df.sort_values("日期")

        # 样式参数
        self.color_up = "#ef232a"  # 阳线颜色
        self.color_down = "#14b143"  # 阴线颜色
        self.ma_periods = [5, 10, 20]
        self.ma_colors = {5: "#FF0000", 10: "#0000FF", 20: "#00FF00"}

    # === 新增：列名自动适配函数 ===
    def _normalize_columns(self):
        """
        自动检测并统一列名为中文
        """
        mapping = {
            "date": "日期",
            "open": "开盘",
            "close": "收盘",
            "low": "最低",
            "high": "最高",
            "vol": "成交量",
            "turnover": "成交额",  # 备用，不强制要求
            "code": "代码",
            "name": "名称"
        }

        # 当前列名全转为小写，用于匹配
        lower_cols = {col.lower(): col for col in self.df.columns}

        for en, zh in mapping.items():
            if en in lower_cols and zh not in self.df.columns:
                self.df.rename(columns={lower_cols[en]: zh}, inplace=True)

        required_cols = ["日期", "开盘", "收盘", "最低", "最高", "成交量"]
        missing = [c for c in required_cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"缺少必要列: {missing}")

    def _prepare_data(self):
        """ 处理数据：提取 K 线数据、计算移动均线、设置成交量颜色 """
        self.dates = self.df['日期'].tolist()  # 提取日期列表
        self.kline_data = self.df[["开盘", "收盘", "最低", "最高"]].values.tolist()  # 提取 K 线数据

        # 计算移动平均线
        for period in self.ma_periods:
            self.df[f'MA{period}'] = (
                self.df['收盘']
                .rolling(window=period)
                .mean()
                .bfill()  # 处理 NaN 值（前向填充）
                .round(2)  # 保留两位小数
            )

        # 计算成交量颜色标记（1: 上涨, -1: 下跌）
        self.df['color'] = self.df.apply(
            lambda x: 1 if x['收盘'] >= x['开盘'] else -1,
            axis=1
        )
        self.df['index_vol'] = range(len(self.df))  # 给成交量数据添加索引
        self.macd_()
        self.rsi_()

    def macd_(self):
        # MACD (12,26,9)
        ema12 = self.df["收盘"].ewm(span=12, adjust=False).mean()
        ema26 = self.df["收盘"].ewm(span=26, adjust=False).mean()
        self.df["DIF"] = ema12 - ema26
        self.df["DEA"] = self.df["DIF"].ewm(span=9, adjust=False).mean()
        self.df["MACD"] = 2 * (self.df["DIF"] - self.df["DEA"])

    def rsi_(self):
        # RSI(14)
        delta = self.df["收盘"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(14).mean()
        avg_loss = pd.Series(loss).rolling(14).mean()
        rs = avg_gain / avg_loss
        self.df["RSI"] = 100 - (100 / (1 + rs))

    def create_chart(self):
        """ 生成 K 线图表 """
        self._prepare_data()  # 处理数据

        # ================== K 线图配置 ==================
        kline = (
            Kline()
            .add_xaxis(self.dates)  # 设置 X 轴日期
            .add_yaxis(
                series_name="K线",  # K 线名称
                y_axis=self.kline_data,  # K 线数据（开盘、收盘、最低、最高）
                itemstyle_opts=opts.ItemStyleOpts(
                    color=self.color_up,  # 阳线颜色
                    color0=self.color_down,  # 阴线颜色
                    border_color="#ef232a",
                    border_color0="#14b143"
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="股票K线走势图",  # 图表标题
                    subtitle=f"股票代码：{self.stock_code}",  # 副标题
                    pos_left="left"  # 标题位置
                ),
                legend_opts=opts.LegendOpts(
                    is_show=True,  # 是否显示图例
                    pos_top=10,  # 图例位置（顶部）
                    pos_left="center"  # 居中对齐
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",  # X 轴类型（类别）
                    axislabel_opts=opts.LabelOpts(rotate=0),  # X 轴标签角度
                    splitline_opts=opts.SplitLineOpts(is_show=True)  # 是否显示网格线
                ),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,  # Y 轴是否自适应缩放
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True,  # 是否显示网格背景
                        areastyle_opts=opts.AreaStyleOpts(opacity=1)  # 设置透明度
                    )
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",  # 触发方式：鼠标悬浮时显示
                    axis_pointer_type="cross",  # 坐标轴指示器类型（十字指示）
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=False,  # 是否显示数据缩放控件
                        type_="inside",  # 缩放类型：内部滑动
                        xaxis_index=[0, 1],  # 作用于 X 轴
                        range_start=80,  # 初始显示范围
                        range_end=100
                    ),
                    opts.DataZoomOpts(
                        is_show=True,  # 显示滑动条缩放
                        xaxis_index=[0, 1],
                        type_="slider",
                        pos_top="100%",  # 位置：底部
                        range_start=80,
                        range_end=100
                    )
                ],
                # 坐标轴指示器
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777")
                )
            )
        )

        # ================== 移动平均线配置 ==================
        line = Line().add_xaxis(self.dates)
        for period in self.ma_periods:
            line.add_yaxis(
                series_name=f"MA{period}",
                y_axis=self.df[f'MA{period}'].tolist(),
                is_smooth=True,  # 平滑曲线
                symbol="none",  # 取消数据点标记
                linestyle_opts=opts.LineStyleOpts(
                    color=self.ma_colors[period],  # 颜色
                    width=2  # 线宽
                ),
                label_opts=opts.LabelOpts(is_show=False)  # 隐藏数据标签
            )

        # 叠加 K 线和均线
        overlap_kline = kline.overlap(line)

        # ================== 成交量柱状图 ==================
        vol_bar = (
            Bar()
            .add_xaxis(self.dates)
            .add_yaxis(
                series_name="成交量",
                y_axis=self.df[['index_vol', '成交量', 'color']].values.tolist(),
                label_opts=opts.LabelOpts(is_show=False),  # 隐藏标签
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=1,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False)
                ),
                yaxis_opts=opts.AxisOpts(is_show=False),
                legend_opts=opts.LegendOpts(is_show=False),
                visualmap_opts=opts.VisualMapOpts(
                    is_show=False,
                    dimension=2,  # 颜色映射使用的维度（color）
                    series_index=4,  # 作用于第 5 个系列（成交量）
                    is_piecewise=True,  # 分段显示
                    pieces=[
                        {"value": 1, "color": self.color_up},  # 上涨颜色
                        {"value": -1, "color": self.color_down}  # 下跌颜色
                    ]
                )
            )
        )

        # ========== MACD ==========
        bar_macd = (
            Bar()
            .add_xaxis(self.dates)
            .add_yaxis("MACD", self.df["MACD"].round(2).tolist(), yaxis_index=2)
        )
        line_dif = (
            Line()
            .add_xaxis(self.dates)
            .add_yaxis("DIF", self.df["DIF"].round(2).tolist(), is_smooth=True)
            .add_yaxis("DEA", self.df["DEA"].round(2).tolist(), is_smooth=True)
        )
        bar_macd.overlap(line_dif)

        # ========== RSI ==========
        line_rsi = (
            Line()
            .add_xaxis(self.dates)
            .add_yaxis("RSI(14)", self.df["RSI"].round(2).tolist(), is_smooth=True)
        )

        # ================== 组合图表 ==================
        grid = (
            Grid(init_opts=opts.InitOpts(
                width="98vw",
                height="95vh",
                animation_opts=opts.AnimationOpts(animation=False)  # 关闭动画
            ))
            .add(overlap_kline, grid_opts=opts.GridOpts(pos_top="10%", height="60%", pos_left="30px", pos_right="10px"))
            .add(vol_bar, grid_opts=opts.GridOpts(pos_top="73%", height="20%", pos_left="30px", pos_right="10px"))
            .add(bar_macd, grid_opts=opts.GridOpts(pos_left="8%", pos_right="8%", pos_top="66%", height="15%"))
            .add(line_rsi, grid_opts=opts.GridOpts(pos_left="8%", pos_right="8%", pos_top="84%", height="12%"))
        )

        return grid

    def render(self, file_path: str = "stock_kline.html"):
        """ 渲染并保存 K 线图 """
        chart = self.create_chart()
        chart.render(file_path)
        print(f"K 线图已保存为 {file_path}")


def normalize_file_path(file_path: str = "stock_kline.html", code: str = "000001") -> str:
    p = Path(file_path)

    # 如果传的是目录（无扩展名）
    if p.suffix == "":
        # 确保最后路径为目录，然后添加默认文件名
        p = p / "stock_kline.html"

    # 取文件名与扩展名
    stem, suffix = p.stem, p.suffix

    # 在文件名后面追加 code
    new_name = f"{stem}_{code}{suffix}"

    # 返回完整路径
    return str(p.with_name(new_name))


def stock_chart(code="159915", start_date="20230101", end_date="20251201", adjust="qfq", file_path: str = "stock_kline.html"):
    import akshare as ak

    # 获取股票数据
    df = ak.stock_zh_a_hist(
        symbol=code,  # 股票代码
        period="daily",  # 日线数据
        start_date=start_date,  # 起始日期
        end_date=end_date,  # 结束日期
        adjust=adjust  # 前复权处理
    )

    file_path = normalize_file_path(file_path, code)
    # 创建 K 线图实例
    _chart = StockKlineChart(df=df, stock_code=code)
    _chart.render(file_path)
