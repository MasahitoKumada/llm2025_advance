# v2 vs v1 スコア低下の詳細分析レポート

## エグゼクティブサマリー

v2モデルはv1と比較して**Total Score が -0.58pt 低下**（3.5987 → 3.0144）しました。本分析では、ALFWorldとDBBenchの両タスクにおける失敗パターンを特定し、根本原因と改善提案を行います。

---

## 1. スコア比較

### 1.1 総合スコア

| Version | Total Score | ALFWorld | DBBench | 差分 |
|---------|-------------|----------|---------|------|
| v1 | **3.5987** | 42% (21/50) | 51.6% | - |
| v2 | **3.0144** | 32% (16/50) | 46.4% | **-0.58pt** |

### 1.2 設定の違い

| 項目 | v1 | v2 |
|------|----|----|
| データセット | ALFWorld v5のみ (2,502件) | ALFWorld v4+v5 + DBBench v3+v4 (~7,400件) |
| 学習率 | 2e-6 | 1e-6 |
| エポック | 2 | 2 |
| データ比率 | ALFWorld 100% | ALFWorld 65% : DBBench 35% |

---

## 2. ALFWorld 詳細分析

### 2.1 ステータス別集計

| ステータス | v1 | v2 | 変化 |
|------------|-----|-----|------|
| completed (成功) | 42% (21/50) | 32% (16/50) | **-10pt** |
| agent invalid action | 26% (13/50) | 38% (19/50) | **+12pt** ⚠️ |
| task limit reached | 32% (16/50) | 30% (15/50) | -2pt |

### 2.2 タスクタイプ別成功率 (v2)

| タスクタイプ | 成功/全体 | 成功率 | 評価 |
|--------------|-----------|--------|------|
| put | 9/18 | 50.0% | △ |
| heat | 4/7 | 57.1% | ○ |
| cool | 2/5 | 40.0% | △ |
| clean | 1/4 | 25.0% | ✗ |
| **put_two** | 0/8 | **0.0%** | **✗✗ 全滅** |
| **examine** | 0/8 | **0.0%** | **✗✗ 全滅** |

### 2.3 失敗パターン詳細

#### パターン1: Invalid Action (38%)
モデルが出力するアクションが利用可能なコマンドリストにマッチしない。

**具体例:**
```
モデル出力: "put peppershaker 2 in/on drawer 1"
期待される形式: "move peppershaker 2 to drawer 1"
結果: システムは最も近いコマンドを選択 → "close drawer 1" が実行される
```

**原因分析:**
- ALFWorldのSFTデータセットで `put X in/on Y` 形式で学習
- 実際のAgentBenchでは `move X to Y` 形式が必要
- データセットと評価環境のアクションフォーマットの乖離

#### パターン2: ループ (task limit reached)
同じ場所を何度も行き来し、タスクが完了しない。

**具体例:**
```
Round 20-35: cabinet 1 → cabinet 4 → cabinet 1 → cabinet 4 (無限ループ)
```

**原因分析:**
- 「次にどこを探すべきか」の判断ができていない
- 探索済みの場所を再訪問するパターン
- put_two タスクで特に顕著（2つ目のオブジェクト探索で破綻）

#### パターン3: タスク混同
タスク目的と異なるオブジェクトを操作する。

**具体例:**
```
タスク: "put two cd in safe"
モデルの行動: creditcard を取得して safe に入れる
結果: 失敗
```

---

## 3. DBBench 詳細分析

### 3.1 カテゴリ別精度比較

| カテゴリ | v1 | v2 | 変化 | 評価 |
|----------|-----|-----|------|------|
| other | 71.4% | 42.9% | **-28.5pt** | ⚠️ 大幅低下 |
| counting | 45.5% | 18.2% | **-27.3pt** | ⚠️ 大幅低下 |
| comparison | 44.4% | 33.3% | -11.1pt | 低下 |
| ranking | 50.0% | 50.0% | 0pt | 維持 |
| aggregation-SUM | 33.3% | 33.3% | 0pt | 維持 |
| aggregation-MIN | 40.0% | 60.0% | **+20pt** | ✓ 改善 |
| aggregation-MAX | 0.0% | 16.7% | **+16.7pt** | ✓ 改善 |
| aggregation-AVG | 57.1% | 71.4% | **+14.3pt** | ✓ 改善 |

### 3.2 SQLタイプ別精度

| SQLタイプ | v1 | v2 | 変化 |
|-----------|-----|-----|------|
| SELECT | 44.3% | 39.3% | -5pt |
| INSERT | 30.4% | 34.8% | +4.4pt |
| UPDATE | 80.0% | 65.0% | **-15pt** |

### 3.3 所見

DBBenchでは一部改善（aggregation系）が見られるものの、全体としては低下。特に:
- **other, counting カテゴリが大幅低下**：これらは複雑な推論を必要とするカテゴリ
- **UPDATE精度が低下**：v1で高精度だった部分が落ちている

---

## 4. 根本原因の特定

### 4.1 最も可能性が高い原因

#### 原因1: 混合学習によるタスク干渉 (Catastrophic Interference)
**確信度: 高**

- ALFWorldとDBBenchは全く異なる出力フォーマット
  - ALFWorld: 自然言語アクション（`go to X`, `take X from Y`）
  - DBBench: SQL文（`SELECT`, `INSERT`, `UPDATE`）
- 混合データセットで学習することで、各タスクの専門性が希薄化
- 証拠: ALFWorldの invalid action が26%→38%に増加

#### 原因2: アクションフォーマットの不一致
**確信度: 高**

- SFTデータセットでは `put X in/on Y` 形式で学習
- AgentBench評価環境では `move X to Y` が正しいコマンド
- モデルは学習したフォーマットを出力するが、システムにマッチしない

#### 原因3: 学習率の低下
**確信度: 中**

- v1: 2e-6、v2: 1e-6（半分）
- より大きなデータセットに対して学習率が低すぎる可能性
- 収束が不十分な可能性

### 4.2 可能性が低い原因

- ~~データ品質の問題~~: v4+v5データセットは品質管理済み
- ~~モデルアーキテクチャの問題~~: 同じQwen3-4B-Instructベース

---

## 5. v3への具体的改善提案

### 5.1 最優先: タスク分離学習

```
提案: ALFWorldとDBBenchを別々のモデルとして学習
- モデルA: ALFWorld専用 (v5データセットのみ)
- モデルB: DBBench専用 (v3+v4データセットのみ)
```

**理由:**
- 混合学習による干渉を完全に排除
- 各タスクで最適なパフォーマンスを達成

### 5.2 高優先: アクションフォーマットの修正

ALFWorldのSFTデータセット生成時に:
```
❌ 現在: "put X in/on Y"
✓ 修正: "move X to Y"
```

AgentBenchの実際のコマンド形式に合わせる。

### 5.3 中優先: put_two と examine タスクの強化

これらのタスクタイプが全滅（0/8）しているため:
- データセットにこれらのタスクパターンを増量
- 特に「2つ目のオブジェクト探索」のトレースを追加

### 5.4 低優先: 学習率の調整

混合学習を続ける場合:
```
現在: LR = 1e-6
提案: LR = 2e-6 (v1と同じ)
または Warmup + Cosine Scheduleの導入
```

---

## 6. 検証のためのログ

分析に使用したログファイル:
- ALFWorld: [`omnicamp/outputs/v2/Agent-Bench/alfworld-vllm/vllm-model/alfworld-std/runs.jsonl`](../omnicamp/outputs/v2/Agent-Bench/alfworld-vllm/vllm-model/alfworld-std/runs.jsonl)
- DBBench: [`omnicamp/outputs/v2/Agent-Bench/dbbench-vllm/vllm-model/dbbench-std/runs.jsonl`](../omnicamp/outputs/v2/Agent-Bench/dbbench-vllm/vllm-model/dbbench-std/runs.jsonl)
- v1 LB: [`omnicamp/outputs/v1/LB/output.log`](../omnicamp/outputs/v1/LB/output.log)
- v2 LB: [`omnicamp/outputs/v2/LB/output.log`](../omnicamp/outputs/v2/LB/output.log)

---

## 7. 結論

v2のスコア低下の**主要因は混合学習によるタスク干渉**と考えられます。ALFWorldとDBBenchは出力フォーマットが根本的に異なるため、1つのモデルで両方を扱うことで専門性が失われています。

**推奨アクション:**
1. v3ではタスク分離学習を採用（最も効果的）
2. アクションフォーマットをAgentBench評価環境に合わせる
3. put_two/examine タスクのデータを増量

---

*分析日: 2026-02-27*
*分析者: Debug Agent*
