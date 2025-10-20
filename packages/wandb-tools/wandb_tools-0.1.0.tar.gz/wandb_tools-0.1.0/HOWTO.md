- [取得資料](#取得資料)
  - [設置基本 WandB 連線](#設置基本-wandb-連線)
  - [篩選特定實驗 runs](#篩選特定實驗-runs)
- [生成表格](#生成表格)
  - [生成基本實驗結果表格](#生成基本實驗結果表格)
  - [生成多設置比較表格](#生成多設置比較表格)
- [自訂表格設定](#自訂表格設定)
  - [自訂指標顯示格式](#自訂指標顯示格式)
  - [控制超參數分組方式](#控制超參數分組方式)
- [處理缺失資料和異常值](#處理缺失資料和異常值)

# 取得資料

## 設置基本 WandB 連線

當您需要從 WandB project 中獲取實驗資料時，必須先建立 `ResultTable` 並驗證能否取得有效的實驗資料。系統會在初始化時立即檢查篩選條件，確保後續操作有有效的資料來源。

When 初始化 `ResultTable` 
```python
from wandb_tools.table import ResultTable

# 基本設置
table = ResultTable(
    wandb_project="nlp-experiments",
    wandb_entity="my-team", # 無提供則使用環境變數 WANDB_ENTITY，無環境變數則預設為 "sinopac"
    wandb_api_key="...", # 無提供則使用環境變數 WANDB_API_KEY，無環境變數則拋出錯誤
    wandb_base_url="...",  # 無提供則使用環境變數 WANDB_BASE_URL，無環境變數則預設為 "https://api.wandb.ai"
)
```

Then 系統將建立與 WandB API 的連線並驗證資料可用性
- 立即檢查篩選條件，確保有符合條件的 runs
- 如果沒有找到符合條件的 runs，立即拋出 `ValueError`

## 篩選特定實驗 runs

當您需要從大量實驗中篩選出特定的 runs 進行分析時，可使用 WandB API 的 MongoDB 查詢語法來精確控制資料範圍。這有助於比較特定實驗組別或排除有問題的 runs。

When 在初始化時設定篩選條件
```python
table = ResultTable(
    wandb_project="nlp-experiments",
    filters={                                          # 使用 MongoDB 查詢語法
        "config.model_type": "transformer",           # 篩選特定超參數值
        "summary_metrics.accuracy": {"$gt": 0.8},     # 篩選指標表現
        "tags": {"$in": ["baseline", "experiment-v2"]}, # 篩選包含特定標籤
        "display_name": {"$regex": "^run-.*"},         # 篩選名稱符合特定格式
    }
)
```

Then 內部篩選出符合所有條件的 runs。如果沒有 runs 符合篩選條件，系統將拋出 `ValueError`

說明：
- 所有篩選條件都使用 AND 邏輯組合
- 支援 MongoDB 查詢語法的所有操作符：`$gt`, `$lt`, `$gte`, `$lte`, `$in`, `$nin`, `$regex`, `$exists` 等
- 常用篩選欄位：`config.*`（超參數）、`summary_metrics.*`（指標）、`tags`（標籤）、`display_name`（名稱）、`state`（狀態）
- 不論是否提供 `filters`，預設都會自動加上 `"state": "finished"` 條件，除非您明確指定其他狀態

# 生成表格

## 生成基本實驗結果表格

當您想要比較不同超參數設置下的實驗表現時，基本的實驗結果表格能自動分組並統計各組的指標表現。系統會自動偵測有變化的超參數作為分組依據，並計算每組的統計摘要。

When 呼叫 `generate()` 方法
```python
result_df = table.generate()
print(result_df)
```

Then 得到一個 DataFrame 格式的實驗結果表格
- Index: 自動偵測的分組超參數組合（如 batch_size, learning_rate）
- Columns: 指標名稱（如 accuracy, f1_score）加上 n_runs, hours
- Values: 每個超參數組合的「平均值 ± 標準差」格式

範例輸出：
```
                    accuracy      f1_score    n_runs   hours
batch_size lr
32         0.001   0.85 ± 0.01  0.80 ± 0.01    5     2.5 ± 0.1
           0.01    0.82 ± 0.02  0.78 ± 0.02    5     2.3 ± 0.2
64         0.001   0.88 ± 0.01  0.83 ± 0.01    5     3.1 ± 0.1
           0.01    0.85 ± 0.02  0.80 ± 0.02    5     2.9 ± 0.2
```

- `n_runs` 顯示該超參數組合的實驗次數
- `hours` 實驗的運行多少小時
- 只會顯示 project 中 runs 間有差異的超參數
- 超參數在欄位中的順序按照該超參數不同值的數量排列，值越少的超參數排在越前面

## 生成多設置比較表格

當您需要比較同一組超參數在不同設置（如資料集）下的表現時，多設置表格提供更直觀的橫向比較檢視。此功能將表示設置的超參數的值作為欄位，其他變化超參數作為列索引，除了各設置的表現外，也會自動計算跨設置的平均表現。

Given 實驗中有一個代表不同設置的超參數（如 `dataset_name`）

When 呼叫 `generate_multisetting()` 並指定代表設置的超參數名稱
```python
comparison_df = table.generate_multisetting("dataset_name")
print(comparison_df)
```

Then 得到一個多層次的比較表格，包含各設置間的平均表現
- Index: 多層索引，包含其他分組超參數和指標名稱
- Columns: "Avg." 欄位（所有設置的平均）+ 各設置超參數的不同值
- Values: 每個設置-超參數組合的統計摘要

範例輸出：
```
                                 Avg.       dataset1    dataset2     dataset3
batch_size lr    Metric
32         0.001 accuracy    0.85 ± 0.03  0.85 ± 0.01  0.87 ± 0.01  0.82 ± 0.01
                 f1_score    0.80 ± 0.02  0.80 ± 0.01  0.82 ± 0.01  0.78 ± 0.01
                 n_runs             5           5           5           5
                 hours        2.5 ± 0.3   2.5 ± 0.1   2.3 ± 0.1   2.7 ± 0.1
           0.01  accuracy    0.82 ± 0.03  0.82 ± 0.02  0.84 ± 0.02  0.79 ± 0.02
                 f1_score    0.78 ± 0.02  0.78 ± 0.02  0.80 ± 0.02  0.75 ± 0.02
                 n_runs             5           5           5           5
                 hours        2.5 ± 0.3   2.5 ± 0.1   2.3 ± 0.1   2.7 ± 0.1
```

- "Avg." 欄位計算該超參數組合在所有設置下的平均表現
- 如果某超參數組合在部分設置上沒有值，該組合的 Avg. 顯示為 N/A
- 指定的設置超參數（dataset_name）不會出現在索引中，而是成為欄位標題
- 每個指標都有獨立的一列，方便比較同一指標在不同設置下的表現
- 超參數在索引中的順序按照該超參數不同值的數量排列，值越少的超參數排在越前面
- 超參數在索引中的順序按照該超參數不同值的數量排列，值越少的超參數排在越前面

# 自訂表格設定

## 自訂指標顯示格式

當您需要控制表格中顯示哪些指標以及如何格式化這些指標時，可透過指標設定來客製化輸出格式。這包括選擇特定指標、調整數值精度、以及百分比轉換等功能。

Given 您想要自訂指標的顯示方式

When 在初始化 `ResultTable` 時指定指標相關參數
```python
table = ResultTable(
    wandb_project="nlp-experiments",
    metric_names=["accuracy", "precision", "recall"],  # 只顯示特定指標
    metric_round_digit=2,  # 小數點後2位
    metric_percentize=["accuracy", "precision"],  # 轉換為百分比
)


result_df = table.generate()
```
- `metric_names` 列表的元素可以是 regex pattern 字串或字串

Then 表格將按照指定的格式顯示指標

```
                    accuracy(%)   precision(%)  recall     n_runs  hours
batch_size lr
32         0.001    85.2 ± 1.1    80.5 ± 1.2   0.78 ± 0.01   5    2.5 ± 0.1
64         0.001    88.1 ± 0.9    83.2 ± 1.0   0.81 ± 0.02   5    3.1 ± 0.1
```
- 只包含 `metric_names` 中指定的指標
- 數值四捨五入到指定的小數位數。 hours 永遠保留1位小數
- 對使用百分比轉換的指標
    - 同時轉換平均值和標準差
    - 忽視 metric_round_digit 設定，乘以100後保留1位小數
    - 指標名稱自動加上 "(%)" 後綴

## 控制超參數分組方式

當您需要精確控制哪些超參數用於分組時，可透過包含或排除特定超參數來客製化表格的索引結構。這對於排除不重要的參數（如隨機種子）或強制包含特定參數很有用。

Given 您的實驗包含多個超參數，但只想用部分參數進行分組

When 設定 `hparam_exclude` 或 `hparam_include` 參數
```python
# 將特定參數從分組依據中排除
table = ResultTable(
    wandb_project="nlp-experiments",
    hparam_exclude=["seed"]  # 排除這些參數
)

# 強制顯示特定參數，即使它們不是分組依據
table = ResultTable(
    wandb_project="nlp-experiments", 
    hparam_include=["batch_size", "learning_rate"]
)
```

Then 表格的索引將根據指定的參數控制進行調整

- `hparam_exclude`: 強制將指定超參數從分組依據中排除，並且不會顯示於結果表格
- `hparam_include`: 強制顯示指定超參數，即使它們在所有 runs 中值相同


# 處理缺失資料和異常值

當您的實驗資料中存在缺失的指標值或異常情況時，系統提供穩健的處理機制來確保表格生成的可靠性。系統會根據可用資料的數量自動選擇適當的顯示格式。

Given 您的實驗資料中可能存在缺失或異常的指標值

When 系統遇到不同資料狀況時會自動處理
```python
table = ResultTable(
    wandb_project="nlp-experiments",
    metric_names=["accuracy", "f1_score"]
)

# 即使部分 runs 缺少某些指標，系統仍會生成表格
result_df = table.generate()
```

Then 系統將根據資料狀況採用不同的顯示策略
- 群組內所有 runs 都缺少某指標：該群組在該指標顯示 "N/A"
- 群組內只有一個 run：直接顯示該 run 的數值
- 群組內有多個 runs：顯示「平均值 ± 標準差」格式

範例輸出（處理各種資料狀況）：
```
                    accuracy      f1_score    n_runs
batch_size lr
32         0.001   0.85 ± 0.01  N/A            5    # 有任一 run 缺少 f1_score
           0.01    0.82          0.78          1    # 只有一個 run
64         0.001   0.88 ± 0.02  0.83 ± 0.01    3    # 多個 runs 正常統計
```

- "N/A" 表示該超參數組合任一 runs 都缺少此指標
- 單一數值（如 0.82）表示該組合只有一個有效的 run，不計算標準差
- 「平均值 ± 標準差」用於有多個有效 runs 的情況
- 系統自動排除包含 None 或 NaN 的 runs
- `n_runs` 欄位反映實際用於該列統計的 runs 數量
- 標準差計算使用 Bessel's correction (ddof=1)
- 超參數在索引中的順序按照該超參數不同值的數量排列，值越少的超參數排在越前面

