## **AgentBench概要**

### 【AgentBenchとは】

LLMを単なるチャットボットとしてではなく、観測・推論・行動を反復しながらタスクを遂行するAIエージェントとして評価するために設計された包括的なベンチマークである

清華大学の研究チームによって2023年に発表され、LLMが実際のコンピュータ環境やウェブ上でどれだけ複雑なタスクを完遂できるかを判定する

### 【特徴】

従来のベンチマーク（MMLU）が知識の正解率を問う一問一答形式だったのに対し、以下の点を重視している

- 多段階の推論と行動 ... ゴールに到達するために考える→実行する→結果を見る→修正するというサイクルを繰り返す能力を評価する

- 実環境とのインタラクション ... シミュレーションではなく、実際のOS(Bashコマンド)やデータベース(SQL）を操作させる

- 多様なドメイン ... 単一タスクではなく、8つの異なる環境を用意して総合力を測る

上記の点により、LLMが単に賢い応答を返すだけでなく、長期的なプランニングや方針の実行力を備えているかどうかを見極めることができる

### 【評価される8つの環境（タスク）】

AgentBenchには8種類の異なる環境タスクが含まれており、コード系、ゲーム系、Web系の３カテゴリに分類される

Code
- OS（Operating System）：Ubuntu環境でのファイル操作、権限設定などのBash操作
- DB（Database）　　　　：実際のMySQLデータベースに対する複雑なSQLクエリ実行
- KG（Knowledge Graph）：知識グラフを探索して、複雑な質問に回答する

Game
- DCG（Digital Card Game）　　：戦略カードゲームをプレイし、ルール理解と勝利戦略を評価
- LTP（Lateral Thinking Puzzle）：水平思考クイズで推論能力判定
- HH（Household）　　　　　　：仮想の室内で「冷蔵庫から卵をとる」などの家事タスク(ALFWorld)

Web
- WS（Web shopping）：ECサイトで希望の商品を検索し、カートに入れる(Webshop)
- WB（Web Browsing）：複数のWebページを横断して情報を収集・操作する

各環境のデータセットやシナリオは、新規に作成されたものと既存ベンチマークの改良版が組み合わされており、LLMが文字ベースで対話・操作できる形に調整されている

こうした多様なタスク設計によって、LLMの指示追従、コード生成、知識検索、論理推論、常識的推論といったコア能力を総合的に評価できるようになっている

### 【Agent Benchの重要性】

これまでのLLM評価では、「文章は上手、実際の仕事は苦手」というギャップが課題だった

AgentBenchの結果から以下のことがわかっている

GPT-4などのトップモデルと下位モデルの差 ... 単純な知識問題以上にエージェントとしての粘り強さやエラー修正能力で大きな差が出る

コード学習の重要性 ... コードデータを多く含むモデルは、OSやDB操作だけでなく論理的な手順が必要なタスク全般で高い性能を示す傾向がある

### 【評価方法】

各タスク環境はユーザ（環境）とエージェント（モデル）が交互にメッセージをやり取りする対話形式で進行する

モデルにはThought（思考）やAction（行動）を明示するフォーマットで回答させ、環境側がその行動の結果や次の観測をテキストで返す仕組みとなっている

この対話を、定められた最大のターン数まで繰り返し、タスクの成功・失敗やスコアを判定する

モデルの応答は温度0(貪欲デコード)で生成され、再現性を担保している

評価プロセスは自動化されており、各環境には正解判定スクリプトやチェック機構が用意されていて、人手を介さずに結果の正誤やタスク完了を判断する

さらに評価用のツールキットは、サーバ・クライアントアーキテクチャで構成されており、各タスク環境はDockerコンテナ内で独立実行される

### 【評価指標】

AgentBenchでは各環境ごとに適切な自動評価指標が定義されている、主要な指標は以下である

成功率(Success Rate,SR):

    タスク要求を最後まで正しく達成できた割合を示す指標
    例えばOS環境なら「正しいコマンドで目的の情報を取得できたか」、家事タスクなら「指示された物体操作を完遂できたか」などゴールに到達したかどうかを成否を判定する

F1スコア:

    抽出型の質問応答タスクでは、部分的な正解度合いを測るためにF1値が使われる
    Knowledge Graphの問答環境では、モデルの返答を正解の集合と比較し、適合率・再現率の調和平均であるF1スコアを計算して回答の正確さを評価する

報酬スコア(Reward):

    途中の行動ごとに得点が定義されているタスクでは、累積報酬を指標とする
    例えばWebショッピングでは、「正しい商品にたどり着いたか」や「無駄のない操作」に応じてスコアリングする報酬関数が用意されている
    デジタルカードゲームでもゲーム内での勝利に対応する報酬値を計測している

進行度(Game Progress):

    明確な成功/失敗ではなく、どこまで目標に近づいたかを測る指標
    Lateral Thinking Puzzleでは、制限ターン内に謎の核心部分（事実の箇条書きのうち何項目か）を解明できた割合でゲーム進行度を評価する

総合スコア:

    複数タスクの成績をまとめた総合評価指標(Overall AgentBench Score)
    各環境のスコアは難易度に応じて重み付けを調整した上で平均され、一つのスコアに集約される


これらの評価指標に加え、以下のような各エージェントのエラー要因も詳細に記録している

- モデルの出力形式が指示通りでないフォーマットエラー
- 許可されない無効なアクションを実行しようとしたケース
- プロンプト長制限を超えて、コンテキストが溢れたケース
- 規定のターン数内にタスクを完了できなかったケース

## C DATABASE 概要

- 本章は、LLMのデータベース操作能力（SQLによるSELECT / INSERT / UPDATE）を評価するためのデータセット設計・構築・検証方法を説明する
- 既存Text-to-SQLデータセットを基盤としつつ、**更新系操作を含む実行可能DBタスク**へ拡張している点が特徴

---

## C.1 Dataset Details（データセット詳細）

### 目的と基本設計

- LLMが**実データベースに対して操作を行い、結果を確認しながら推論できるか**を評価する
- 単なるSQL生成ではなく、**状態遷移を伴うDB操作の正しさ**を評価対象とする

### データソース

- 以下の既存QA / Text-to-SQL系データセットを再利用・統合する
    - WikiSQL
    - WikiTableQuestions
    - SQA
    - HybridaQA
    - FeTaQA
- 多様な指示形式・テーブル構造を確保することを目的とする

### データ拡張（リーク回避を含む）

- gpt-3.5-turbo を用いてデータ拡張を実施
- テーブルのヘッダ情報と元データを入力し、新規データを生成
    - 新しい行データを10行生成
    - SQLクエリを5件生成
    - 各SQL文を意味保持のまま言い換え
- 妥当なサンプルのみをフィルタリングし、最終的に300件を採用する

### タスク分類

- データは以下3種類のDB操作に分類される
    - SELECT
    - INSERT
    - UPDATE

### 各サンプルの構成要素

- Instruction
    - 問題設定とエージェントに求められる行動を記述
- Table Info
    - テーブル名およびカラム名などのメタ情報
- Table Content
    - 初期状態のテーブル内容
- Correct Answer
    - SELECT：正解テキスト
    - INSERT / UPDATE：正しく更新されたテーブルのハッシュ値

---

## C.1 Evaluation Setup（評価方法）

### 評価フロー全体

- 評価は「実DB環境での操作」を前提に、以下の手順で行う

### Initialization

- テーブル内容から初期SQLスクリプトを生成する
- Docker上のMySQLによりDBを初期化し、外部から操作可能にする

### Interaction

- エージェントは以下を含む応答を繰り返す
    - 推論（思考過程の説明）
    - 実行可能なSQL文
- SQLを実行し、その結果を即時エージェントに返す
- 最終回答の確定、またはエラー発生までループする

### Checking（正誤判定）

- SELECT
    - 正解テキストと比較
    - 順序は不問、完全一致を要求
    - 数値は表記揺れを許容
- INSERT / UPDATE
    - 操作後テーブルのハッシュ値を正解ハッシュと比較

### 評価指標

- Success Rate を使用する
- 3カテゴリ（SELECT / INSERT / UPDATE）の成功率をマクロ平均する

---

## C.2 Data Augmentation（データ拡張の詳細）

### 背景

- 既存SQL系データセットは「問い合わせ（SELECT）」中心であり、
    
    **挿入・更新操作が不足している**という課題がある
    

### Insertタスク生成

- テーブル名・ヘッダ・元データからINSERT用SQLを5件生成
- 意味を保ったまま文表現を言い換える

### Updateタスク生成

- 生成済みINSERT文を入力としてUPDATE文を5件生成
- 同様に言い換えを実施する

### 品質保証

- すべての拡張クエリはユニットテストを通過することを必須とする

### SELECTクエリの細分類

- 既存データから以下のタイプに分類して評価に利用する
    - Counting
    - Aggregation（MIN / MAX / AVG / SUM）
    - Ranking
    - Comparison
    - Other（該当しないもの）

---

## C.3 Prompt Example（プロンプト設計）

プロンプトの例：

```
User:
I will ask you a question, then you should help me operate a MySQL
database with SQL to answer the question.
You have to explain the problem and your solution to me and write down
your thoughts.
After thinking and explaining thoroughly, every round you can choose to
operate or to answer.
your operation should be like this:
Action: Operation
‘‘‘sql
SELECT * FROM table WHERE condition;
‘‘‘
You MUST put SQL in markdown format without any other comments. Your SQL
should be in one line.

Every time you can only execute one SQL statement. I will only execute
the statement in the first SQL code block. Every time you write a SQL
, I will execute it for you and give you the output.
If you are done operating, and you want to commit your final answer, then
write down:
Action: Answer
Final Answer: ["ANSWER1", "ANSWER2", ...]
DO NOT write this pattern unless you are sure about your answer. I expect
an accurate and correct answer.
Your answer should be accurate. Your answer must be exactly the same as
the correct answer.
If the question is about modifying the database, then after done
operation, your answer field can be anything.
If your response cannot match any pattern I mentioned earlier, you will
be judged as FAIL immediately.
Your input will be raw MySQL response, you have to deal with it by
yourself.
```

### 基本方針

- LLMを「DB操作可能なエージェント」として扱う
- 推論と操作を明示的に分離させる

### 応答フォーマットの制約

- 各ターンで実行可能なのはSQL文1つのみ
- SQLはMarkdownのコードブロックで1行記述する
- 操作終了時は
    - Action: Answer
    - Final Answer: [...]
        
        の形式で最終回答を返す
        
- 指定フォーマットを外れると即FAILとなる

---

## C.4 Study on Bias in Data Augmentation
（拡張データのバイアス検証）

### 目的

- gpt-3.5-turboによる拡張が**特定操作に有利・不利なバイアス**を生んでいないかを検証した

### 検証方法

- 一部データを Claude-2 により再アノテーション
- gpt-4 / gpt-3.5-turbo による評価結果と比較する

### 結果と解釈

- 元データと再生成データで**性能傾向が概ね一致**
    - gpt-4はUPDATEが苦手、INSERTが得意
    - gpt-3.5-turboはUPDATEで高スコア
- データ拡張手法が**相対的な性能関係を歪めていない**ことを示唆している

---

## G HOUSE-HOLDING (ALFWorld) 概要

- 本章は、家庭内作業を模した**テキストベースのインタラクティブ環境**における、LLMの**長期計画・逐次意思決定能力**を評価する設定を説明する
- 評価基盤として **ALFWorld** を用い、高レベル目標を**一連の原子的行動**へ分解・実行できるかを測る
    
    ---
    

## G.1 Dataset Details（データセット詳細）

### 環境とタスクの性質

- ALFWorld は、家庭内シナリオを模した**テキスト環境**を提供する
- エージェントは、
    - 環境記述と
    - 達成すべき目標（例：物体を特定位置に置く）
        
        を与えられ、**複数ステップの行動計画**を立てて実行する
        
- 各行動後に**即時フィードバック**が返り、計画を動的に更新できる

### 各サンプルの構成要素

- Environment Description
    - 家庭内環境の詳細説明
    - エージェントの初期位置
    - 部屋内の物体とIDのスナップショット
- Objective
    - 達成すべき最終目標
    - 探索と多段推論を要する高レベル指示
- Simulated Environment
    - 各行動に対する環境の反応
    - タスク完了判定を含む

### データセットの範囲と分類

- ALFWorld の **out-of-distribution eval split** から、解ける問題134件を使用する
- 問題は以下6カテゴリに分類される
    - pick and place
    - pick clean then place
    - pick heat then place
    - pick cool then place
    - look at obj
    - pick two obj

### Evaluation Setup（評価設定）

- 問題の複雑さと出力形式の厳格さを考慮し、**1-shot評価**を採用する
- 各カテゴリについて、同カテゴリの訓練データから比較的単純で完全な成功例を1つ提示する
- ReAct（Yao et al., 2023）に準拠したプロンプトと例示を使用する
- 出力形式が不正な場合は、BLEU により有効な行動候補との類似度を計算し、最も近い行動を採用する

### 評価プロセス

- Initialization
    - タスク概要と1つの成功例を提示する
    - 環境の詳細と達成目標を明示する
- Interaction
    - モデルは思考（THOUGHT）と行動（ACTION）を生成する
    - 環境は行動結果を返す
    - 成功するか、最大行動数に達するまで反復する
    - 同一出力を3回連続で生成した場合は、**反復による失敗**と判定する

### 評価指標

- 指標は **Success Rate** のみを用いる
- 成功タスク数 ÷ 総タスク数 で算出する

---

## G.2 Prompt Example（プロンプト設計）

プロンプトの例：

```
Interact with a household to solve a task. Imagine you are an intelligent
agent in a household environment and your target is to perform
actions to complete the task goal. At the beginning of your
interactions, you will be given the detailed description of the
current environment and your goal to accomplish. For each of your
turn, you will be given a list of actions which you can choose one to
perform in this turn. You should choose from two actions: \"THOUGHT
\" or \"ACTION\". If you choose \"THOUGHT\", you should first think
about the current condition and plan for your future actions, and
then output your action in this turn. Your output must strictly
follow this format:\"THOUGHT: your thoughts.\n ACTION: your next
action\n\"; If you choose \"ACTION\", you should directly output the
action in this turn. Your output must strictly follow this format:\"
ACTION: your next action\n\". After your each turn, the environment
will give you immediate feedback based on which you plan your next
few steps. if the environment output \"Nothing happened\", that means
the previous action is invalid and you should try more options.

Reminder:
1. the action must be chosen from the given available actions. Any
actions except provided available actions will be regarded as illegal
.
2. Think when necessary, try to act directly more in the process.
```

### 設計方針

- シミュレータが受け付ける**合法コマンド形式**に厳密に合わせる
- 1-shot設定として、**成功例を指示文の後に連結**する

### 基本指示

- エージェントを「家庭内で行動する知的主体」として位置づける
- 各ターンで選択できるのは以下の2種のみ
    - THOUGHT：状況分析と計画立案（必要な場合のみ）
    - ACTION：次に実行する行動
- 出力フォーマットは厳密に規定され、逸脱は無効とする
- 無効行動が返った場合、環境は “Nothing happened” を返す

### 運用上の注意

- 行動は必ず**提示された選択肢から選ぶ**
- 可能な限り思考を省略し、直接行動することを推奨する
- エージェントを目的達成によりよく導くために、各カテゴリごとに1つずつ成功例を用意
- 成功例：

```
User: You are in the middle of a room. Looking quickly around you, you
see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop
1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a
sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a
towelholder 1. Your task is to: put some spraybottle on toilet.

Agent: THOUGHT: The task is to put some spraybottle on toilet, so first i
need to search the room for some spraybottle. After finding the
spraybottle, i need to take it to the toilet. I wil start my search
on cabinets.
ACTION: go to cabinet 1
User: On the cabinet 1, you see a cloth 1, a soapbar 1, a soapbottle 1.
Agent: ACTION: go to cabinet 2
User: The cabinet 2 is closed.
Agent: ACTION: open cabinet 2
User: You open the cabinet 2. The cabinet 2 is open. In it, you see a
candle 1, and a spraybottle 2.
Agent: ACTION: take spraybottle 2 from cabinet 2
User: You pick up the spraybottle 2 from the cabinet 2.
Agent: ACTION: go to toilet 1
User: On the toilet 1, you see a soapbottle 2.
Agent: ACTION: put spraybottle 2 in/on toilet 1
User: You put the spraybottle 2 in/on the toilet 1.
```

# 参考サイト

https://www.emergentmind.com/topics/agentbench

https://arxiv.org/abs/2308.03688
