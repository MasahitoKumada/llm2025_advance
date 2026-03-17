#!/usr/bin/env python3
"""
ALFWorld v6データセットをHugging Face Hubにアップロードするスクリプト

使用方法:
    python scripts/upload_alfworld_v6.py

必要な環境変数:
    HF_TOKEN: Hugging Face APIトークン（オプション、引数でも指定可能）
"""

import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="ALFWorld v6データセットをHugging Face Hubにアップロード"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=os.environ.get("HF_TOKEN"),
        help="Hugging Face APIトークン（環境変数HF_TOKENでも設定可能）",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="kmd2525/sft_alfworld_trajectory_dataset_v6",
        help="アップロード先のリポジトリID",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="inputs/ALFWorld/v6/train.json",
        help="アップロードするデータセットファイル",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="プライベートリポジトリとしてアップロード",
    )

    args = parser.parse_args()

    # トークンの確認
    if not args.token:
        print("エラー: Hugging Face APIトークンが必要です")
        print("  --token オプションで指定するか、環境変数 HF_TOKEN を設定してください")
        return 1

    # インポート（必要なライブラリの確認）
    try:
        from huggingface_hub import login, HfApi
        from datasets import Dataset
    except ImportError as e:
        print(f"エラー: 必要なライブラリがインストールされていません: {e}")
        print("  pip install huggingface_hub datasets")
        return 1

    # ファイルの存在確認
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {input_path}")
        return 1

    print("=" * 60)
    print("ALFWorld v6データセット アップロード")
    print("=" * 60)
    print(f"  入力ファイル: {input_path}")
    print(f"  アップロード先: {args.repo_id}")
    print(f"  公開設定: {'プライベート' if args.private else '公開'}")
    print()

    # Hugging Faceにログイン
    print("[1/4] Hugging Faceにログイン中...")
    login(token=args.token)

    # ログイン確認
    api = HfApi()
    try:
        user_info = api.whoami()
        print(f"  ✓ ログイン成功: {user_info['name']}")
    except Exception as e:
        print(f"  ✗ ログイン失敗: {e}")
        return 1

    # データセットを読み込む
    print("\n[2/4] データセットを読み込み中...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  ✓ 読み込み完了: {len(data)} サンプル")

    # Hugging Face Datasetに変換
    print("\n[3/4] Hugging Face Dataset形式に変換中...")
    ds = Dataset.from_list(data)
    print(f"  ✓ 変換完了: {len(ds)} サンプル")
    print(f"  カラム: {ds.column_names}")

    # アップロード
    print("\n[4/4] Hugging Face Hubにアップロード中...")
    ds.push_to_hub(
        args.repo_id,
        private=args.private,
    )

    print("\n" + "=" * 60)
    print("✓ アップロード完了!")
    print("=" * 60)
    print(f"  リポジトリURL: https://huggingface.co/datasets/{args.repo_id}")
    print(f"  サンプル数: {len(ds)}")

    return 0


if __name__ == "__main__":
    exit(main())
