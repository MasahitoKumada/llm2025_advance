## 7.3 アドバンスドコンペルール_ベンチマークの紹介

アドバンスドコンペでは、AgentBench というベンチマークを用います。
OS操作、DB操作、オンラインショッピング，推論パズルなど、実世界を模した8つの多様なインタラク ティブ環境を構築し、モデルが与えられたタスクを解くベンチマークです。
例：
- 家の中で「探す→拾う→きれいにする→置く」といった一連の物理的行動を計画、実行する
- 質問に対し、実際にSQLを実行して答える

今回はその内、2つのタスクを採用し、総合点で勝負します （※総合点の出し方は論文を踏襲．他の情報は最終結果発表時に発表）
- DB Bench：
	- テーブル情報と要求を受け取り，適切なクエリを組み立ててDBを操作するタスク
	- 150問（コンペの都合上減らしています）

- ALFWorld：
	- 環境描写＋タスク目標を受け取り，目標を達成する行動を出力するタスク
	- 50 問

LLMが与えられた指示に対して行動し、環境とインタラクションすることで行動を改善し、最終的に期待される応えを得ることができるかというエージェントの能力を試します。
タスク例＿DB Bench：
エージェント（LLM）はシステムから以下のようなプロンプトを受け取ります。
エージェントの記述スタイルなどの指示と、問題文と、テーブルの情報です。

User：
I will ask you a question，then you should help me operate a MySQL database with SQL to answer the question．
You have to explain the problem and your solution to me and write down your thoughts．
After thinking and explaining thoroughly，every round you can choose to operate or to answer．
your operation should be like this：
Action：Operation
＂sql
SELECT＊FROM table WHERE condition；
＂＂
You MUST put SQL in markdown format without any other comments．Your SQL should be in one line．
Every time you can only execute one SQL statement．I will only execute the statement in the first SQL code block．Every time you write a SQL ，I will executeect answer．
Your answer should be accurate．Your answer must be exactly the same as the correct answer．
If the question is about modifying the database，then after done operation，your answer field can be anything．
If your response cannot match any pattern I mentioned earlier，you will be judged as FAIL immediately．
Your input will be raw MySQL response，you have to deal with it by yourself it for you and give you the output．
If you are done operating，and you want to commit your final answer，then

write down：
Action：Answer
Final Answer：［＂ANSWER1＂，＂ANSWER2＂，．．．］
DO NOT write this pattern unless you are sure about your answer．I expect an accurate and correct answer．
\＃質問内容
Question：What is the Presentation of Credentials has a Termination of Mission listed as August 15，2000？
\＃テーブル情報
The name of this table is US Ambassadors and Envoy Extraordinary to Colombia， and the headers are Representative（TEXT），Title（TEXT）， Presentation of Credentials（TEXT），Termination of Mission（TEXT）， Appointed by（TEXT）．

これに対してエージェントは、どのような考え方をするかとクエリを組み立てます エージェントの回答例が以下です。

Agent：
The question asks me to find the＂Presentation of Credentials＂value for the row where＂Termination of Mission＂is＂August 15，2000＂．

This is a simple SELECT query with a WHERE clause filtering by the Termination of Mission column．

Action：Operation
＂＇sql
SELECT ‘Presentation of Credentials‘ FROM ˋUS Ambassadors and Envoy Extraordinary to Colombia’
WHERE ˋTermination of Missionˋ＝＇August 15，2000＇；

このエージェントの回答に対して、システム側はクエリを実行します。
クエリの実行結果をエージェントに返します。
＋－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
｜Presentation of Credentials｜
｜March 19， 1998 ｜

この結果を受け取り、エージェントは回答を作成します。

Agent：
The query returned＂March 19，1998＂as the Presentation of Credentials
for the ambassador whose Termination of Mission was August 15, 2000.

Action：Answer
Final Answer：［＂March 19，1998＂］
このFinal Answerの値がタスクの正解ラベルと一致していれば正解となります。

このサンプルは説明の為、 1 往復になってますが、実際はエージェントが間違えたクエリを組み立てたり、 することで、システムから返ってくるクエリ結果を元に自己修正を繰り返し回答にたどり着けるかという内容になります。

タスク例 ALF World：
エージェント（LLM）はシステムから以下のようなプロンプトを受け取ります． エージェントの記述スタイルなどの指示や注意についてです。

User：
Interact with a household to solve a task．Imagine you are an intelligent agent in a household environment and your target is to perform actions to complete the task goal．At the beginning of your interactions，you will be given the detailed description of the current environment and your goal to accomplish．For each of your turn，you will be given a list of actions which you can choose one to perform in this turn．You should choose from two actions：＂THOUGHT＂ or＂ACTION＂．If you choose＂THOUGHT＂，you should first think about the current condition and plan for your future actions，and then output your action in this turn．Your output must strictly follow this format：＂THOUGHT：your thoughts．
ACTION：your next action
＂；If you choose＂ACTION＂，you should directly output the action in this turn．Your output must strictly follow this format：＂
ACTION：your next action
＂．After your each turn，the environment will give you immediate feedback based on which you plan your next few steps．if the environment output＂Nothing happened＂，that means the previous action is invalid and you should try more options．
Reminder：
1．the action must be chosen from the given available actions．Any actions except provided available actions will be regarded as illegal．
2．Think when necessary，try to act directly more in the process．

これをもとに、例えば以下のようなタスクをシステムから受け取ります。
環境の情報と、達成すべき目標と、可能なアクション一覧です。
User：
\＃今置かれている環境
Here is your task．You are in the middle of a room．Looking quickly around you，you see a bathtubbasin 1 ，a cabinet 2 ，a cabinet 1 ， a countertop 1 ，a garbagecan 1 ，a handtowelholder 1 ，a $\operatorname{sinkbasin} 1$ ， a toilet 1 ，a toiletpaperhanger 1 ，and a towelholder 1 ．
\＃エージェントのタスク
Your task is to：put some soapbottle on garbagecan．
\＃現在取れる行動一覧
AVAILABLE ACTIONS：
go to bathtubbasin 1
go to cabinet 1
go to cabinet 2
go to countertop 1
go to garbagecan 1
go to handtowelholder 1
go to sinkbasin 1
go to toilet 1
go to toiletpaperhanger 1
go to towelholder 1

以降は、システムとインタラクションし、エージェントがアクション→システムがその結果を回答 → $\ldots$ を繰り返し、目標を達成できるよう繰り返します。
以下が例です。

Agent：
\＃思考
THOUGHT：I need to find a soapbottle and put it on garbagecan．I＇ll start searching in cabinets since soap items are often stored there．
\＃アクション
ACTION：go to cabinet 1

User：
\＃結果（キャビネット1が閉まってた）
The cabinet 1 is closed．
AVAILABLE ACTIONS：
open cabinet 1
go to bathtubbasin 1
go to cabinet 2
go to countertop 1
go to garbagecan 1
go to handtowelholder 1
go to sinkbasin 1
go to toilet 1
go to toiletpaperhanger 1
go to towelholder 1
Agent：
\＃キャビネット1を開ける
ACTION：open cabinet 1
User：
\＃キャビネット 1 を開けたら，石鹸が入ってた
You open the cabinet 1 ．The cabinet 1 is open．In it，you see a soapbottle 1.
AVAILABLE ACTIONS：
close cabinet 1
go to bathtubbasin 1
go to cabinet 2
go to countertop 1
go to garbagecan 1
go to handtowelholder 1
go to sinkbasin 1
go to toilet 1
go to toiletpaperhanger 1
go to towelholder 1
\＃石鹸をキャビネット 1 から取り出す選択肢が与えられた．
take soapbottle 1 from cabinet 1


※実際は、一連のやり取りで正解にたどり着く例が1－shot 例として与えられてからタスクがスタートします。

学習のヒント
採点結果に点数のみでなく，各種メトリクスが出るようになっています。それらを見て，どんな学習させるべきか考えられるかもしれません。

-----------------------------------------------------------------------------------------------------------------------------

## 7.4 アドバンスドコンペルール_提出物

提出するものは、以下のようなcsvファイルです。

\begin{tabular}{|l|l|}
\hline model_path & hf_token \\
\hline Qwen/Qwen3-4B-Instruct-2507 & hf_*** \\
\end{tabular}

model_path、hf_tokenカラムはテンプレートのまま編集せず、model_path直下にHuggingFaceのモデルパス、hf_token直下にご自身のREAD権限付きトー クンを記載してください。（評価時におけるレートリミット回避のためにREAD権限が必要になります） READ権限の取得の仕方は補足資料を確認してください。

また，以下の点に注意してください。
- モデルパスはHuggingFaceから取得できるものにしてください
- モデルのページにREADMEも記載してください。
- 運営がサンプルを提示するので，それに倣い記載してください
- モデルの公開設定はPublicにしてください

-----------------------------------------------------------------------------------------------------------------------------

## 7.5 アドバンスドコンペルール_運営からの配布物
配布時期はアドバンスドコンペスタート時を予定しています
※予定は予告なく変更の可能性があります。
- 標準コード（モデル学習コード）（予定）
- 改変自由
- HuggingFace READMEのサンプル出カセルもセットになります
- 学習用データ（予定）
- 運営作成の合成データ
- その他，ライセンスOKなデータセットを紹介します
- ※これらはスコアが確実に上がることを保証するものではありません．
- Omniキャンパス環境使用手順書
- ベンチマークの仕様上，推論コード単体で配布できないため開発環境を配布します
- Omniキャンパス開発環境でAgentBenchが動かせる手順書になります
- 推論実行のサンプルとしてご利用ください
- どのような開発環境かは「提供開発環境」の項を確認ください
－モデルホワイトリスト
－学習指定モデル（後述）以外に，合成や蒸留に使用してよいモデルのリストになります
※ 参加者自身の環境（Not開発環境）でAgentBenchを推論できるコードの配布は現在予定しておりません

-----------------------------------------------------------------------------------------------------------------------------

## 7.6 アドバンスドコンペルール_モデル関連

開発するモデルに係る制約は以下です。
－本コンペにおける，学習指定モデルは以下です
－Qwen／Qwen2．5－7B－Instruct
－Qwen／Qwen3－4B－Instruct－2507
- これ以外のモデルの使用は認めません．派生モデルも禁止です
- 提出するモデルは学習指定モデルを学習したモデルであること
- モデルアーキテクチャの変更は認めません
- Hugging Faceにモデルとしてアップロード可能であること
- モデルには必ず何かしらの変更を加える必要があります
- SFTやRLHF、DPOなどによりパラメータを更新すればその条件を満たします
- 量子化も変更にあたります
- モデル開発のあらゆる段階でAgentBench，およびALFworldのデータを用いることを禁止
- このデータを用いた合成データの生成も禁止
- メインコンペのリーダーボードを利用したチューニングもこの行為に含まれます
- 蒸留は利用可能
- ただし，教師モデルには別途提示するホワイトリストのモデルのみ用いること
- 最終的に採点するモデルのアーキテクチャは指定モデルと同一であり、かつ指定モデルを ベースとしている必要があります
－評価環境はL4 GPUインスタンスで稼働しているので、L4 GPU のVRAM 24GBで回らないようなモ デルの学習は行わないでください
※ ホワイトリストの詳細は、docs/モデルホワイトリスト.md を参照。


本コンペはバックエンドで参加者のモデルをロードし推論を行う都合上、モデルの形式に以下の厳格な指定があります。推論には vLLM の公式 Docker イメージを用い、以下のコマンドで起動します。 

この環境で動作しないモデルは評価不能となりますので注意してください。
＊＂bash
docker run－－runtime nvidia－－gpus all \}
－ipc＝host \}
vllm／vllm－openai：v0．13．0 \}
－model＂参加者の提出モデルパス＂\}
－max－model－len 8192 \}
－gpu－memory－utilization 0.95
＂＂

注意点
- アーキテクチャの変更禁止：指定モデルのアーキテクチャを変更することは認めません
- トークナイザーの変更制限：語彙の追加は禁止

語彙追加に伴い Embedding 層のパラメータサイズが変更されると、vLLMの起動時に形状不
- 致エラ一が発生するリスクが高いため
- アダプター（LoRA等）の扱い：
- LoRAなどのアダプターを用いる場合は、必ずペースモデルにマージした状態で提出してく ださい、実行時にアダプターを動的にロードする方式は不可とします
- 量子化：
- 運営側で－－quantization などの起動オプションは付与しません
- 量子化モデル（AWQ，GPTQ等）を提出する場合は、モデルの config.jsonに量子化設定（ quantization＿config）が正しく記述されており、vLLM が設定なしで自動認識できる形式 （AutoAWQ／AutoGPTQ 等で保存された形式）である必要があります
- Chat Templateの必須化：
- OpenAI互換のエンドポイント（http：／／localhost：8000／vl／chat／completions）を使用するため、 tokenizer＿config．json に正しいchat＿template が含まれていることを確認してください

事前に開発環境にてvllmによる推論テストが可能です。推論が回るかなどの確認にご利用ください。


-----------------------------------------------------------------------------------------------------------------------------

## 7.7 アドバンスドコンペルール＿データ関連

LLMの学習に用いるデータに係る制約は以下です。
- 合成データは利用可能とします
- ただし，別途提示するホワイトリストのモデルのみ用いること
- ホワイトリストモデルに対して量子化を行うのは自由です。
- アドバンスドコンペは自身でライセンス的に問題ないデータを探して学習に使用してOKです
- 運営が提供、または紹介するデータ以外を使う場合は以下の点に気を付けてください
- 非商用利用に制約のないライセンスのものを使用すること
- 許可なく取得、使用してよいと提供元が認めているデータのみを使用すること
- 運営が問い合わせに対応するのは、運営が提供および紹介したデータに限ります
- 有料のデータは使用禁止です
- 公開（誰もが無償でアクセス可）されていないデータの使用は禁止です
- 各種ライセンスの取り扱いには十分注意してください
- AgentBenchで用いられているデークは勿論、それらを模倣したようなデータは使用しないでください。

-----------------------------------------------------------------------------------------------------------------------------

## 補足

### データ作成について

LLMコンペを開催していると，データ合成についての許可•禁止の話を行う際に，「どこからがLLMに よるデータ合成ですか？」「この手法はデータ合成に該当しますか？」などといった質問をよく受け付けま す。
以下に例を挙げるので「これはLLMによるデータ合成、これはLLM以外の技術を使ったデータ作成」と判断してください。

なお，本コンペにおける「LLM」とは、言語を出力とするモデル全般とし、いわゆる言語モデルであっ ても言語を出力としないものはこれに含まれないものとします．

LLMを用いてないデータ作成の例
- データのクリーニング：
	- 正規表現やスクリプトを用いて以下のようなことをする．
	- 不要な文字の削除
	- フォーマットの統一
	- 重複排除
	- 人手による修正：
	- 誤字脱字の修正や、人間が内容を確認して行うアノテーション
	- 非生成的なデー夕拡張：
	- 類義語辞書（WordNet等）を用いた単語の置換、ランダムなノイズ付与など，LLMの推論能力に依存しない従来のデータ拡張手法
	- 本ドキュメントで述べているLLMの定義から外れるモデル（BERT、RoBERTa、DeBERTa等のエンコーダモデル）を使ったテキスト処理

LLMを用いたデータ作成（合成）の例
- OpenAI GPTシリーズ、Claude、Gemini、Llama等の生成AIモデル（APIおよびローカルモデルを含む）を使用して、新たなテキストデータを生成すること
	- LLMを使用して、既存のテキストを言い換え（Rephrasing）したり、要約したりすること
	- LLMの出力を教師データとして学習に使用すること

このように、ポイントは、「データを構築するプロセスにおいて，直接的にLLMが作成データに関与しているか」となります。
LLMを用いてない例は，ルールベース処理（正規表現、文字列操作、テンプレート処理）だったり，人手による作成（自ら記述や人手によるラベル付け，アノテーション）です。
LLMを用いたデータ作成（データ合成）の例は、LLMの重み（API、ローカル問わず）を利用して、LLMにテキ ストを生成させたり、識別させたりしています。

FAQ（よくある質問）
Q．データの前処理にChatGPTやCodexなどを使ってコードを書かせ、そのコードでデータを処理するのは、OKですか？
A．可能です。 「データを処理するコード」をLLMに書かせることは補助的な利用とみなされ許可します。 ただし、LLMそのものに「データの中身」を作らせたり書き換えさせたりすることは禁止です。

Q．データの品質チェック（フィルタリング）にLLMを使うのは？
A．禁止です。 「このデータは高品質か？」という判定をLLMに行わせ、その結果選別されたデータセット を使うことは、「LLMの知識を利用したデータセット構築」に該当するため禁止します。

また、昨今は翻訳にLLMを用いたものも多く登場していますが、これらを使って表現の違うテキストを得 ることもある種の合成です。
（本コンペではLLM翻訳、非LLM翻訳含めて一律禁止にしています $>8$ ．開発におけるツールの扱い）


### LLMモデル開発におけるお約束

評価データを学習に使うのはやめましょう。
これから試す対象であるベンチマークのデータ、評価データを学習することはカンニングしているよう なものです．これではベンチマークに対してモデルが優秀なのかどうか計ることができません。
これを「データリーク」や「汚染（Contamination）」と呼びます。
ベンチマークのデータを学習するのはやめましょう。
メインコンペについては運営が指定したデータのみ使用してもらいますが、アドバンスドコンペは参加者に皆さんがライセンス的に問題ないデータを自由に選んでもらえます。しかし、ベンチマークで使われ ているデータを使用するのはやめましょう。

ベンチマークで使用しているデータを意図せず使用されて，評価用のデータがトレーニングデータの一部と重複していた場合、モデルが単にデータを「記憶」しているだけにもかかわらず、その性能が過剰に評価される可能性があり，これもContaminationにあたります。

「今回試す対象のベンチマークでないから良いのでは」と思われるかもしれないですが、避けた方が無難です。

評価データを過剰に意識したデータ作成は避けましょう。
基本的にモデル開発コンペティションは、モデルの汎化性能を適正に評価することを目的としています そのため、評価データ（テストデータ）の統計的特徴を分析し、それに過剰に適合させた学習データを作成 する行為は、データリークに近しい行為と考えられ、避けた方が無難です。

過度な分析の禁止：
評価データの目視確認、テキストマイニング、分布分析などを行い、評価データの傾向（トピック、文体、キーワード分布など）を逆算•特定する行為は避けてください。

最適化の制限：
上記の分析結果に基づき、評価データに酷似した学習データを意図的に作成•選別することは、モデル の実用的な評価を損なうため控えてください。

許容範囲：
フォーマットの確認など、最低限のデータ確認は許容されますが、あくまで「未知のデータ」として扱うよう心がけてください。


ディスカッションや質問から、皆さまからどのラインまでOKか？の疑問がいくつかお寄せ頂いたので，例を記載します。
まず
- ＂AgentBench、およびALFWorldのデータを用いることを禁止＂→ カンニング防止
- ＂過度に意識しない＂→評価データに特化したデータ作成を防ぐ

が基本的な考え方になります。ベンチマークスコアの公平な評価（Contaminationの防止、過学習・リーク の防止）を目的としています。

データ作成NG例：
- ベンチマーク自体を＂流用＂すること：
- AgentBench／ALFWorldのGithub等から既存のデータファイルをダウンロードし、それを学習に使うこと。

- 分かりやすくNGな例
- ベンチマークの＂中身を模倣＂すること：
- AgentBenchやALFWorldのgithubにあるjsonデータ等（具体的な問題文や正解）を直接参照し、それを改変したり、学習データとして流用（2次利用など）すること

- これも分かりやすくNGな例
- ベンチマークへの＂過学習を狙ったプロンプト＂：
- LLMに対して「AgentBenchのデータセットのようなデータを作って」「ALFWorldの形式を真似して」といった指示を行い、ペンチマーク特有のクセや分布を模倣させること（これらはContaminationのリスクが高まります）
- AgentBenchを狙い撃ちしている＝過度に意識している，という解釈
- ベンチマークの＂具体的な内容を特定＂し、それに＂特化したデータ＂を作成すること＂
- ペンチマークの具体的な値（プロンプトなど）はもちろん、傾向などをテキストマイニング等で分析することも含まれます
- 2番目の事例より参照度合は下げてはいるが，AgentBenchを狙い撃ちしていると解釈
- 過学習・リーク狙いと解釈されるようなデータ作成全般

特に，許可しているホワイトリストモデルは強力であり、プロンプトの書き方次第では簡単に模倣データが作れてしまいます。（3番目の事例）


一方、本コンペティションは指定された形式（ALFWorld形式等）で動作するエージェントを開発すること が目的ですので、「タスクのフォーマット（アクションの書き方や環境の定義）」自体を学習させること は、必要不可欠であり、禁止事項ではありません。
ALFWorldを例に挙げると、原著論文において、タスクタイプ（Pick \＆Place等）、アクション形式（go to X等）、環境描写（＂You are in the middle of a room．．．＂）などの仕様が定義されており、これに基づいて作成す れば必然的に形式は類似します。これは「データそのものの流用」とは異なります。

データ作成OK例：
- 論文やドキュメントを読み、タスクの仕様（部屋の種類やアクションの構文など）を理解した上で、それらを再現するようにプロンプトを組んで作成したデータ
- タスクの仕様に合わせたシミュレータやプログラムを自作して作成したデータ
- 配布されたデータセット（運営作成のホワイトリストデータ: docs/dataset_rule.md, docs/モデルホワイトリスト.md 参照）を参考に、類似のロジックで作成したデータ
- AgentBench，ALFWorld以外のデータを用いたデータ合成

NG例では，評価データセットの「具体的な分布や正解」を模做することを指しており， OK 例では、タスクを解くための「一般的な形式やルール」を学習することをを指しています。

許容範囲にも書かれている通り、フォーマットの確認など、最低限のデータ確認は許容されますが、あくまで「未知のデータ」として扱うというように心がけていただければと思います。
