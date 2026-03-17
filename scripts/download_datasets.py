#!/usr/bin/env python3
"""
データセットダウンロードスクリプト

LLMエージェントコンペティションで使用する9種類のデータセットを
Hugging Faceからダウンロードし、ローカルに保存します。

ALFWorld用（5種類）: inputs/ALFWorld/v1〜v5/
DBBench用（4種類）: inputs/DBBench/v1〜v4/
"""

import json
from pathlib import Path

from datasets import load_dataset


# データセット定義
ALFWORLD_DATASETS = {
    "v1": "u-10bei/sft_alfworld_trajectory_dataset",
    "v2": "u-10bei/sft_alfworld_trajectory_dataset_v2",
    "v3": "u-10bei/sft_alfworld_trajectory_dataset_v3",
    "v4": "u-10bei/sft_alfworld_trajectory_dataset_v4",
    "v5": "u-10bei/sft_alfworld_trajectory_dataset_v5",
}

DBBENCH_DATASETS = {
    "v1": "u-10bei/dbbench_sft_dataset_react",
    "v2": "u-10bei/dbbench_sft_dataset_react_v2",
    "v3": "u-10bei/dbbench_sft_dataset_react_v3",
    "v4": "u-10bei/dbbench_sft_dataset_react_v4",
}


def get_project_root():
    """
    プロジェクトルートディレクトリを取得する。

    Returns:
        Path: プロジェクトルートのパス
    """
    return Path(__file__).parent.parent


def create_output_directory(path):
    """
    出力ディレクトリを作成する。

    Args:
        path (Path): 作成するディレクトリのパス
    """
    path.mkdir(parents=True, exist_ok=True)


def download_and_save_dataset(dataset_name, output_dir, version):
    """
    データセットをダウンロードしてJSON形式で保存する。

    Args:
        dataset_name (str): Hugging Faceのデータセット名
        output_dir (Path): 保存先ディレクトリ
        version (str): バージョン名（例: v1, v2）

    Returns:
        bool: ダウンロード成功時True、失敗時False
    """
    try:
        print(f"  ダウンロード中: {dataset_name}")
        dataset = load_dataset(dataset_name)

        # 全splitを保存
        for split_name, split_data in dataset.items():
            output_path = output_dir / f"{split_name}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    split_data.to_list(),
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            print(f"    保存完了: {output_path} ({len(split_data)} 件)")

        return True

    except Exception as e:
        print(f"  エラー: {dataset_name} - {e}")
        return False


def download_alfworld_datasets(inputs_dir):
    """
    ALFWorld用データセットをすべてダウンロードする。

    Args:
        inputs_dir (Path): inputs/ディレクトリのパス

    Returns:
        dict: バージョンごとの成功/失敗結果
    """
    print("\n" + "=" * 60)
    print("ALFWorld データセットのダウンロード")
    print("=" * 60)

    results = {}
    total = len(ALFWORLD_DATASETS)

    datasets_items = ALFWORLD_DATASETS.items()
    for idx, (version, dataset_name) in enumerate(datasets_items, 1):
        print(f"\n[{idx}/{total}] {version}")
        output_dir = inputs_dir / "ALFWorld" / version
        create_output_directory(output_dir)
        results[version] = download_and_save_dataset(
            dataset_name, output_dir, version
        )

    return results


def download_dbbench_datasets(inputs_dir):
    """
    DBBench用データセットをすべてダウンロードする。

    Args:
        inputs_dir (Path): inputs/ディレクトリのパス

    Returns:
        dict: バージョンごとの成功/失敗結果
    """
    print("\n" + "=" * 60)
    print("DBBench データセットのダウンロード")
    print("=" * 60)

    results = {}
    total = len(DBBENCH_DATASETS)

    datasets_items = DBBENCH_DATASETS.items()
    for idx, (version, dataset_name) in enumerate(datasets_items, 1):
        print(f"\n[{idx}/{total}] {version}")
        output_dir = inputs_dir / "DBBench" / version
        create_output_directory(output_dir)
        results[version] = download_and_save_dataset(
            dataset_name, output_dir, version
        )

    return results


def print_summary(alfworld_results, dbbench_results):
    """
    ダウンロード結果のサマリーを表示する。

    Args:
        alfworld_results (dict): ALFWorldのダウンロード結果
        dbbench_results (dict): DBBenchのダウンロード結果
    """
    print("\n" + "=" * 60)
    print("ダウンロード結果サマリー")
    print("=" * 60)

    print("\n【ALFWorld】")
    for version, success in alfworld_results.items():
        status = "✓ 成功" if success else "✗ 失敗"
        print(f"  {version}: {status}")

    print("\n【DBBench】")
    for version, success in dbbench_results.items():
        status = "✓ 成功" if success else "✗ 失敗"
        print(f"  {version}: {status}")

    # 総合結果
    total = len(alfworld_results) + len(dbbench_results)
    success_count = (
        sum(alfworld_results.values()) + sum(dbbench_results.values())
    )
    print(f"\n総合: {success_count}/{total} 件成功")


def main():
    """
    メイン関数。全データセットをダウンロードする。
    """
    print("データセットダウンロードスクリプトを開始します")

    # プロジェクトルートとinputsディレクトリを設定
    project_root = get_project_root()
    inputs_dir = project_root / "inputs"

    print(f"保存先: {inputs_dir}")

    # データセットをダウンロード
    alfworld_results = download_alfworld_datasets(inputs_dir)
    dbbench_results = download_dbbench_datasets(inputs_dir)

    # サマリー表示
    print_summary(alfworld_results, dbbench_results)

    print("\n完了しました。")


if __name__ == "__main__":
    main()
