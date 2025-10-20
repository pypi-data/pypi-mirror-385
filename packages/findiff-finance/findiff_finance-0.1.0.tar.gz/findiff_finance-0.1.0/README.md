
FinDiff

Diffusion-based, teacher-aligned data augmentation for time-series finance
面向策略稳定性的“生成 → 打分筛选 → 门控/回退 → 时序评估”流水线。

⸻

目录
	•	特点
	•	安装
	•	快速开始
	•	用你的 CSV 直接产出报告（本地）
	•	Docker 运行
	•	没有数据？先跑演示
	•	用代码调用
	•	接入你自己的模型
	•	配置速览
	•	报告与可视化
	•	项目结构
	•	开发与测试
	•	常见问题
	•	许可与数据合规
	•	联系方式

⸻

特点
	•	可控生成：轻量扩散（DDPM 风格），按时间/统计条件生成“近似真实”的样本
	•	Teacher 对齐：打分后仅保留“对策略有益”的子集（k-top/阈值）
	•	安全门控：Auto Gate（先验）+ Eval Gate（CV/Test）；不满足就自动回退 baseline
	•	客观评估：Purged Rolling CV + 留出 Test（embargo 防泄露），提供 Sharpe/Calmar/Vol/Var 的均值
	•	模型开放：支持 sklearn / PyTorch / 任意框架（最小接口 fit/predict 或 fit_with_df）
	•	即开即用：一行命令读取你的 CSV → 产出 report.html（含 Baseline vs Augmented 对比与 Δ）

⸻

安装

需要 Python ≥ 3.9（如需 GPU，请先按 PyTorch 官网上的指引安装匹配版本）

pip install -e ".[dev]"
# 可选：设置日志等级
# export FINDIFF_LOGLEVEL=INFO  # or DEBUG/WARN/ERROR


⸻

快速开始

用你的 CSV 直接产出报告（本地）

python scripts/run_demo.py \
  --csv your.csv \
  --date-col date \
  --label-col y \
  --features-cols auto \
  --out artifacts/csv_run

# macOS 快捷打开
open artifacts/csv_run/report.html

说明：
	•	--features-cols auto：自动将所有数值列（排除时间/标签）当作特征
	•	也可手动指定：--features-cols "f1,f2,f3"

Docker 运行

docker build -t findiff:dev .
mkdir -p artifacts
docker run --rm \
  -e FINDIFF_LOGLEVEL=INFO \
  -v "$(pwd)/artifacts:/app/artifacts" \
  findiff:dev \
  python scripts/run_demo.py \
    --csv /app/path/to/your.csv \
    --date-col date --label-col y \
    --features-cols auto \
    --out artifacts/csv_run

容器内路径以 /app/... 为根（Dockerfile 的 WORKDIR /app）。

没有数据？先跑演示

python scripts/run_demo.py --out artifacts/demo_run
open artifacts/demo_run/report.html

产出目录包含：
	•	metrics.json：最终（已门控/可能回退后）的指标
	•	logs.json：CV 折详情、门控/回退、baseline 与 augmented 两套指标
	•	report.html：CV 柱状、Test NAV、PSI 热图、Baseline vs Augmented 对比表（含 Δ）

⸻

用代码调用

from findiff import default_cfg, deep_update
from findiff.pipeline import FinDiff
from findiff.train import TorchTimeSeriesRegressor
from findiff.dataio import load_timeseries_csv

df = load_timeseries_csv("your.csv", time_col="date",
                         feature_cols=["f1","f2","f3"], label_col="y")

cfg = deep_update(default_cfg(), {
  "data": {"freq": "B"},
  "generator": {"epochs": 2, "steps": 200, "sample_ratio": {"normal": 0.3}},
  "mix": {"real_to_synth": "1.0:0.4"},
  "train": {
    "eval_metrics": ["sharpe","calmar","sharpe_p5","vol","var"],
    "ann_factor": 252,
    "cv": {"enable": True, "n_folds": 5, "embargo": 63, "train_window": 504}
  },
  "security": {"eval_gate": True, "accept_if": {"cv_sharpe_mean_min": 0.0}}
})

model = TorchTimeSeriesRegressor(in_dim=3, window=64, hidden=128,
                                 epochs=4, batch_size=256)

res = FinDiff(model, df, "date", ["f1","f2","f3"], "y").run()
print(res.metrics)                    # 按选择（augmented/baseline）输出的最终指标
print(res.logs["selected_variant"])   # "augmented" | "baseline"


⸻

接入你自己的模型

方式 1：数组接口（最小）

class MyModel:
    def fit(self, X, y, **kwargs): ...
    def predict(self, X): ...
# X: [N, n_features], y: [N]

方式 2：DataFrame 接口（更灵活）

class MyModel:
    def fit_with_df(self, train_df, feature_cols, label_col, **kwargs): ...
    def predict(self, X): ...
# 你可以在 fit_with_df 里自己做滑窗/归一化/DataLoader 等

sklearn 示例

from sklearn.linear_model import Ridge
class SKRidge:
    def __init__(self, alpha=1.0):
        self.m = Ridge(alpha=alpha)
    def fit(self, X, y, **kwargs): self.m.fit(X, y)
    def predict(self, X): return self.m.predict(X)


⸻

配置速览
	•	data.freq：时间频率（如 "B" 工作日 / "D" 自然日），影响窗口与禁距（embargo）
	•	generator：epochs/steps/edit_last_steps/guidance_scale、n_samples 或 sample_ratio.normal
	•	teacher.select_rule.k_top：保留前 k 比例的生成样本（0–1）
	•	mix.real_to_synth：真实:合成比例（如 "1.0:0.4"）
	•	train.cv：enable、scheme(sliding/expanding)、train_window、n_folds、embargo、min_train_rows
	•	security：auto_gate_synth/gate_if、eval_gate/accept_if、fallback_mix

内置 validate_cfg() 做强校验与合理回退（类型、范围、默认值），并通过 FINDIFF_LOGLEVEL 打印告警。

⸻

报告与可视化

report.html 包含：
	•	Selected Summary：被选方案（Augmented/Baseline）的关键指标
	•	Baseline vs Augmented：两边指标与 Δ（Aug−Base）对比表
	•	CV per-fold：每折 Sharpe 柱状
	•	Test NAV：测试集净值曲线
	•	PSI Heatmap：真实 vs 合成的特征分布偏移（每特征一个 PSI）

若提供 test_returns，还会展示 Newey-West 与 MBB（移动区块自助法）估计的显著性信息。

⸻

项目结构

.
├── src/findiff/
│   ├── config.py        # default_cfg / deep_update / get_splits
│   ├── data.py          # prepare_df / build_conditions
│   ├── dataio.py        # load_timeseries_csv
│   ├── gen.py           # DDPMGenerator（轻量）
│   ├── guard.py         # 泄露检查
│   ├── logging_util.py  # 统一日志
│   ├── metrics.py       # Sharpe/Calmar/Vol/Var...
│   ├── mix.py           # blend_real_synth
│   ├── pipeline.py      # 主流程（CV、门控、回退、评估）
│   ├── plotting.py      # 可视化
│   ├── reporting.py     # report.html
│   ├── score.py         # teacher 打分示例（可替换）
│   ├── stats.py         # Newey-West & bootstrap
│   ├── train.py         # fit_and_eval / TorchTimeSeriesRegressor
│   └── validators.py    # 配置校验
├── scripts/
│   ├── run_demo.py        # CSV or Dummy → 报告
│   ├── make_dummy_data.py # 造演示数据
│   └── __init__.py
├── tests/
├── artifacts/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pyproject.toml
├── README.md
└── LICENSE


⸻

开发与测试

# 代码规范
ruff check .
black --check .

# 单测 & 覆盖率
pytest -q
pytest --cov=findiff --cov-report=term-missing
pytest --cov=findiff --cov-report=html && open htmlcov/index.html

可视化/示例模块的覆盖率不做强制，可在 pyproject.toml 的 coverage 配置里 omit。

⸻

常见问题
	•	ImportError: No module named scripts
重新构建镜像，或确保在项目根目录运行：
docker build -t findiff:dev . → docker run ... python scripts/run_demo.py ...
	•	Docker 无法连接 daemon
启动 Docker Desktop 或 Colima，再 docker ps 重试。
	•	GPU/内存不足
先用默认轻量配置；Docker Desktop → Settings → Resources 调到 ≥4GB。
	•	报告不显示对比表
需要同时存在 logs["baseline"] 与 logs["augmented"]；启用 security.eval_gate=True 会自动比较。

⸻

许可与数据合规
	•	代码：Apache-2.0（见 LICENSE）
	•	数据：请仅使用你有权使用的数据。部分竞赛数据（如 Kaggle）可能限制“仅用于比赛/论坛”，不可用于产品或公开演示。

⸻

联系方式

维护者：yanllinc@berkeley.edu
或在 GitHub Issues 反馈问题/建议。

