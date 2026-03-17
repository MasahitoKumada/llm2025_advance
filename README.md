# LLM2025 Advanced Competition - AgentBench SFT

大規模言語モデル講座2025応用編 最終課題コンペティション（アドバンスドコンペ）の開発記録です。

## 📊 最終成果

| 指標 | ベースライン | 最終モデル（v6） | 改善幅 |
|------|-------------|-----------------|--------|
| **総合スコア** | - | **4.4809** | - |
| **ALFWorld成功率** | 26% (13/50) | **64% (32/50)** | **+38pt** |
| **DBBench精度** | 53.7% | **52.5%** | -1.2pt |

- **最終順位**: 49位
- **最終モデル**: [kmd2525/test105_v6](https://huggingface.co/kmd2525/test105_v6)

## 🎯 概要

AgentBenchベンチマークを用いたLLMエージェントのファインチューニングプロジェクト。
- **タスク**: ALFWorld（家庭内物体操作）+ DBBench（SQL操作）
- **手法**: SFT（Supervised Fine-Tuning）+ LoRA
- **ベースモデル**: Qwen/Qwen3-4B-Instruct-2507

## 🔑 成功のキーポイント

1. **学習率の最適化**: 2e-6 → 1e-6への変更でInvalid action率を26%→10%に大幅改善
2. **データセット高品質化**: 失敗トラジェクトリーと"Nothing happens."パターンの除去
3. **ALFWorld単体でのSFT**: 混合学習は両タスクを低下させることが判明、ALFWorld特化が有効

## 📁 プロジェクト構成

```
.
├── analysis/           # 分析ドキュメント
├── docs/              # コンペルール、データセットルール等
├── images/            # 可視化画像
├── information/       # 他参加者からの知見
├── inputs/            # 学習データセット
│   ├── ALFWorld/      # ALFWorld v1-v6
│   └── DBBench/       # DBBench v1-v4
├── notebooks/         # SFT学習用Notebook
├── omnicamp/          # AgentBench実行ログ
│   └── outputs/       # v1-v8の実験結果
├── outputs/           # 提出用CSVファイル
├── plans/             # 戦略ドキュメント、開発ドキュメント
└── scripts/           # 実行スクリプト
```

## 📈 実験経緯

| Version | Score | ALF | DB | 主な変更 | 結果 |
|---------|-------|-----|-----|---------|------|
| ベースライン | - | 26% | 53.7% | - | - |
| **v1** | **3.60** | 42% | 51.6% | ALF v5でSFT | ✅ 成功 |
| v2 | 3.01 | 32% | 46.4% | 混合学習 | ❌ 両方低下 |
| v3 | 3.00 | 30% | 47.9% | エポック3, LoRA拡大 | ❌ 過学習 |
| **v4** | **4.12** | 54% | 53.1% | LR=1e-6に変更 | ✅ 大幅改善 |
| **v5** | **4.31** | 58% | 54.0% | データセット高品質化 | ✅ 改善 |
| **v6** | **4.48** | 64% | 52.5% | エポック3 | ✅ **最高スコア** |

## 🛠️ 最終モデル（v6）の設定

```yaml
# ベースモデル
BASE_MODEL: Qwen/Qwen3-4B-Instruct-2507

# 学習パラメータ
MAX_SEQ_LEN: 2048
EPOCHS: 3
LEARNING_RATE: 1e-6
WARMUP_RATIO: 0.1
BATCH_SIZE: 2
GRADIENT_ACCUMULATION_STEPS: 4

# LoRA設定
LORA_R: 64
LORA_ALPHA: 128
LORA_DROPOUT: 0
TARGET_MODULES: all-linear

# データセット
DATASET: ALFWorld v6（高品質化済み、1,966サンプル）
```

## 📚 関連資料

- [開発ドキュメント（詳細版）](plans/開発ドキュメント_アドバンスドコンペ.md)
- [AgentBench論文](https://arxiv.org/abs/2308.03688)
- [ALFWorld論文](https://arxiv.org/abs/2010.03768)
- [使用データセット](https://huggingface.co/datasets/kmd2525/sft_alfworld_trajectory_dataset_v6)

## 📝 ライセンス

本プロジェクトは学習目的で作成されたものです。

## 🙏 謝辞

- 松尾研究室・GENIAC運営チームの皆様
- 他の参加者の皆様（Slackでの知見共有）
- Qwen、Unsloth、vLLMなどのオープンソースコミュニティ
