"""电商销售数据分析
读取 data/orders.csv，计算核心指标，输出 4 张图表到 charts/。
运行：python analysis.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 中文字体：Windows 用 SimHei；其他系统可换成 Noto Sans CJK
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]
for f in FONT_CANDIDATES:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.abspath(__file__))
CHARTS = os.path.join(BASE, "charts")
os.makedirs(CHARTS, exist_ok=True)

df = pd.read_csv(os.path.join(BASE, "data", "orders.csv"))
valid = df[~df["是否退货"]]

monthly = df.groupby("月份")["金额"].sum().reset_index(name="销售额")
monthly_valid = valid.groupby("月份")["金额"].sum().reset_index(name="净销售额")
monthly = monthly.merge(monthly_valid, on="月份")

cat = df.groupby("品类").agg(销售额=("金额", "sum"), 退货率=("是否退货", "mean")).reset_index()
cat["销售额占比"] = cat["销售额"] / cat["销售额"].sum()

channel = df.groupby("渠道").agg(销售额=("金额", "sum"), 退货率=("是否退货", "mean")).reset_index()
region = valid.groupby("地区")["金额"].sum().sort_values(ascending=False).reset_index()

# 图 1：月度趋势
plt.figure(figsize=(9, 4.2))
plt.plot(monthly["月份"], monthly["销售额"], marker="o", color="#2E86DE", label="销售额")
plt.plot(monthly["月份"], monthly["净销售额"], marker="s", color="#27AE60", label="扣除退货后")
plt.xticks(rotation=45)
plt.ylabel("销售额（元）")
plt.title("2025 年月度销售额趋势")
plt.legend()
plt.grid(alpha=.25)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, "01_月度趋势.png"), dpi=180)
plt.close()

# 图 2：品类销售额
plt.figure(figsize=(8, 4.2))
cs = cat.sort_values("销售额")
plt.barh(cs["品类"], cs["销售额"], color="#5DADE2")
plt.xlabel("销售额（元）")
plt.title("各品类销售额")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, "02_品类销售.png"), dpi=180)
plt.close()

# 图 3：渠道销售额与退货率
plt.figure(figsize=(8, 4.4))
cs = channel.sort_values("销售额", ascending=False)
x = np.arange(len(cs))
ax1 = plt.gca()
ax1.bar(x, cs["销售额"], color="#5DADE2")
ax1.set_ylabel("销售额（元）")
ax1.set_xticks(x)
ax1.set_xticklabels(cs["渠道"])
ax2 = ax1.twinx()
ax2.plot(x, cs["退货率"], color="#E74C3C", marker="o")
ax2.set_ylabel("退货率")
for i, v in enumerate(cs["退货率"]):
    ax2.annotate(f"{v:.1%}", (i, v), textcoords="offset points", xytext=(0, 8), ha="center", color="#C0392B", fontsize=9)
plt.title("各渠道销售额与退货率")
ax1.grid(axis="y", alpha=.25)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, "03_渠道对比.png"), dpi=180)
plt.close()

# 图 4：地区分布
plt.figure(figsize=(8, 4.2))
plt.bar(region["地区"], region["金额"], color="#48C9B0")
plt.ylabel("净销售额（元）")
plt.title("各地区销售额（已剔除退货）")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS, "04_地区分布.png"), dpi=180)
plt.close()

# 指标
print(f"订单数：{len(df):,}")
print(f"总销售额：{df['金额'].sum():,.0f} 元")
print(f"净销售额：{valid['金额'].sum():,.0f} 元")
print(f"退货率：{df['是否退货'].mean():.1%}")
print(f"客单价：{df['金额'].mean():.0f} 元")
print(f"峰值月份：{monthly.loc[monthly['销售额'].idxmax(), '月份']}")
print(f"第一大品类：{cat.loc[cat['销售额'].idxmax(), '品类']}（{cat['销售额占比'].max():.1%}）")
print(f"退货率最高品类：{cat.loc[cat['退货率'].idxmax(), '品类']}（{cat['退货率'].max():.1%}）")
print(f"退货率最高渠道：{channel.loc[channel['退货率'].idxmax(), '渠道']}（{channel['退货率'].max():.1%}）")
print(f"第一大地区：{region.iloc[0]['地区']}（{region.iloc[0]['金额']/region['金额'].sum():.1%}）")
