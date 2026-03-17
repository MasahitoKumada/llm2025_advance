#!/usr/bin/env python3
"""
ALFWorld v6 データセット作成スクリプト

v5データセットから以下のクリーニングを行い、高品質なv6データセットを作成します：
1. 失敗トラジェクトリーの除外（trajectory_outcome == "failure"）
2. "Nothing happens."を含むトラジェクトリーの除外
3. 成功パターンのみ保持

使用方法:
    python scripts/create_alfworld_v6.py

出力:
    - inputs/ALFWorld/v6/train.json
    - inputs/ALFWorld/v6/train.parquet
"""
import json
from pathlib import Path
from typing import Any
import pandas as pd


def load_v5_dataset(input_path: str) -> list[dict[str, Any]]:
    """v5データセットを読み込む"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def contains_nothing_happens(messages: list[dict[str, str]]) -> bool:
    """
    トラジェクトリーに"Nothing happens."が含まれているかチェック

    "Nothing happens."は無効なアクションの結果として返される応答
    """
    for msg in messages:
        content = msg.get("content", "")
        if "Nothing happens." in content:
            return True
    return False


def is_failure_trajectory(metadata: dict[str, Any]) -> bool:
    """失敗トラジェクトリーかどうかチェック"""
    return metadata.get("trajectory_outcome") == "failure"


def filter_trajectory(sample: dict[str, Any]) -> tuple[bool, str | None]:
    """
    トラジェクトリーをフィルタリング

    Returns:
        (keep: bool, reason: str | None) - 保持するかどうかと除外理由
    """
    messages = sample.get("messages", [])
    metadata = sample.get("metadata", {})

    # 1. 失敗トラジェクトリーを除外
    if is_failure_trajectory(metadata):
        return False, "failure_trajectory"

    # 2. "Nothing happens."を含むトラジェクトリーを除外
    if contains_nothing_happens(messages):
        return False, "contains_nothing_happens"

    # 3. 成功トラジェクトリーのみ保持
    if metadata.get("trajectory_outcome") != "success":
        return False, "not_success"

    return True, None


def create_v6_dataset(v5_data: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    v6データセットを作成

    Returns:
        (filtered_data, stats) - フィルタリング後のデータと統計情報
    """
    filtered_data = []
    stats = {
        "total": len(v5_data),
        "kept": 0,
        "removed_failure_trajectory": 0,
        "removed_nothing_happens": 0,
        "removed_not_success": 0,
    }

    for sample in v5_data:
        keep, reason = filter_trajectory(sample)

        if keep:
            filtered_data.append(sample)
            stats["kept"] += 1
        else:
            if reason == "failure_trajectory":
                stats["removed_failure_trajectory"] += 1
            elif reason == "contains_nothing_happens":
                stats["removed_nothing_happens"] += 1
            elif reason == "not_success":
                stats["removed_not_success"] += 1

    return filtered_data, stats


def save_dataset(data: list[dict[str, Any]], output_dir: str) -> None:
    """データセットをJSON形式とParquet形式で保存"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # JSON形式で保存
    json_path = output_path / "train.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON保存: {json_path}")

    # Parquet形式で保存
    parquet_path = output_path / "train.parquet"
    df = pd.DataFrame(data)
    df.to_parquet(parquet_path, index=False)
    print(f"✓ Parquet保存: {parquet_path}")


def print_stats(stats: dict[str, int]) -> None:
    """統計情報を表示"""
    print("\n" + "=" * 60)
    print("ALFWorld v6 データセット作成完了")
    print("=" * 60)

    print(f"\n【統計情報】")
    print(f"  v5データセット: {stats['total']} サンプル")
    print(f"  v6データセット: {stats['kept']} サンプル")
    print(f"  削減率: {(1 - stats['kept'] / stats['total']) * 100:.1f}%")

    print(f"\n【除外理由内訳】")
    print(f"  失敗トラジェクトリー: {stats['removed_failure_trajectory']} サンプル")
    print(f"  'Nothing happens.'含む: {stats['removed_nothing_happens']} サンプル")
    print(f"  成功以外: {stats['removed_not_success']} サンプル")

    total_removed = stats['total'] - stats['kept']
    print(f"\n  合計除外: {total_removed} サンプル")


def analyze_v6_quality(data: list[dict[str, Any]]) -> None:
    """v6データセットの品質を分析"""
    print("\n" + "=" * 60)
    print("v6データセット品質分析")
    print("=" * 60)

    # タスクタイプ別の内訳
    task_types = {}
    difficulties = {}
    step_counts = []

    for sample in data:
        metadata = sample.get("metadata", {})

        task_type = metadata.get("task_type", "unknown")
        task_types[task_type] = task_types.get(task_type, 0) + 1

        difficulty = metadata.get("difficulty", "unknown")
        difficulties[difficulty] = difficulties.get(difficulty, 0) + 1

        num_steps = metadata.get("num_steps", 0)
        step_counts.append(num_steps)

    print(f"\n【タスクタイプ別内訳】")
    for task_type, count in sorted(task_types.items(), key=lambda x: -x[1]):
        pct = count / len(data) * 100
        print(f"  {task_type}: {count} ({pct:.1f}%)")

    print(f"\n【難易度別内訳】")
    for difficulty, count in sorted(difficulties.items()):
        pct = count / len(data) * 100
        print(f"  {difficulty}: {count} ({pct:.1f}%)")

    if step_counts:
        print(f"\n【ステップ数統計】")
        print(f"  最小: {min(step_counts)}")
        print(f"  最大: {max(step_counts)}")
        print(f"  平均: {sum(step_counts) / len(step_counts):.1f}")


def main():
    """メイン処理"""
    # パス設定
    input_path = "inputs/ALFWorld/v5/train.json"
    output_dir = "inputs/ALFWorld/v6"

    print("=" * 60)
    print("ALFWorld v6 データセット作成")
    print("=" * 60)
    print(f"\n入力: {input_path}")
    print(f"出力: {output_dir}")

    # v5データセット読み込み
    print(f"\n[INFO] v5データセット読み込み中...")
    v5_data = load_v5_dataset(input_path)
    print(f"  読み込み完了: {len(v5_data)} サンプル")

    # フィルタリング
    print(f"\n[INFO] データクリーニング実行中...")
    v6_data, stats = create_v6_dataset(v5_data)

    # 統計情報表示
    print_stats(stats)

    # 品質分析
    analyze_v6_quality(v6_data)

    # 保存
    print(f"\n[INFO] データセット保存中...")
    save_dataset(v6_data, output_dir)

    print("\n" + "=" * 60)
    print("完了")
    print("=" * 60)
    print(f"\n次のステップ:")
    print(f"  1. Hugging Face Hub にアップロード")
    print(f"     python scripts/download_datasets.py --upload --task alfworld --version 6")
    print(f"  2. notebooks/コード_SFT_v5.ipynb でSFT実行")


if __name__ == "__main__":
    main()
