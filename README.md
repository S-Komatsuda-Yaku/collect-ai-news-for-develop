# collect-ai-news-for-develop
AI駆動開発のニュースを毎日収集する

## 保存先

毎日のニュースは、次の階層で保存します。

```text
aI_knowledge/YYYY/MMDD.md
```

## GitHubへの公開

Codexの「毎朝のAI変化ニュース」タスクがニュースを生成した後、ルートの
`publish-news.sh` を実行します。このスクリプトは `main` を最新化し、対象の
Markdownだけをコミットして `origin/main` へ直接プッシュします。

手動で公開する場合:

```bash
./publish-news.sh aI_knowledge/2026/0823.md
```

## Phase 1: 最新ナレッジの判定

毎週日曜9:17（Asia/Tokyo）に、GitHub Actionsの
`Update news knowledge index` が次を実行します。Actions画面からの手動実行も可能です。

1. Markdownをニュース項目単位に分割
2. OpenAI APIで要約、エンティティ、主張を構造化
3. Embeddingで既存の有効なニュースから類似候補を検索
4. LLMで `new / related / duplicate / update / correction / uncertain` を判定
5. 高確信度の更新・訂正だけ旧項目を無効化
6. `knowledge/latest.json` に有効な項目だけを出力

過去のMarkdownは削除しません。判定履歴は `knowledge/items.jsonl`、検索用の
Embeddingは `knowledge/embeddings.jsonl` に保存されます。

### 必須設定

GitHubリポジトリの `Settings > Secrets and variables > Actions` で、Repository
Secretを追加してください。

| 種別 | 名前 | 用途 |
| --- | --- | --- |
| Secret | `OPENAI_API_KEY` | OpenAI APIの認証 |

APIキーはRepository Variableやソースコードには保存しないでください。

### 任意設定

以下はRepository Variablesとして変更できます。未設定時は表の既定値を使います。

| 名前 | 既定値 | 用途 |
| --- | --- | --- |
| `OPENAI_MODEL` | `gpt-5.4-mini` | 構造化・関係判定モデル |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | 類似検索モデル |
| `OPENAI_EMBEDDING_DIMENSIONS` | `256` | 保存するベクトルの次元数 |
| `CANDIDATE_LIMIT` | `5` | LLMへ渡す過去候補の上限 |
| `CANDIDATE_THRESHOLD` | `0.65` | LLM判定へ進める候補類似度 |
| `AUTO_SUPERSEDE_CONFIDENCE` | `0.90` | 旧項目を自動無効化する最低確信度 |

初回実行時は既存の全Markdownをインデックス化します。以後は週次実行時に、未処理または
変更されたニュース項目だけを処理します。

## Phase 2: GitHub IssueからのRAG質問

Issue作成画面で「ナレッジへの質問」テンプレートを選び、質問を投稿してください。
テンプレートを使わない通常のIssueでも利用できます。Owner、Member、Collaboratorが
Issueを作成・編集・再オープンすると、`Answer knowledge question` Actionsが次を実行します。

1. 質問をEmbedding化
2. `knowledge/latest.json` の有効ナレッジだけを横断検索
3. 類似度上位のナレッジをLLMへ提示
4. ナレッジだけを根拠に回答を生成
5. 元Markdownと原典URL付きでIssueへコメント

回答後の追加質問は、同じIssueへ次の形式でコメントしてください。

```text
/ask 追加の質問内容
```

通常のコメントではActionsは起動しません。回答に必要な情報が有効ナレッジ内にない場合は、
外部知識で補完せず、情報不足であることを回答します。APIの不正利用を防ぐため、回答を
起動できるのはリポジトリのOwner、Member、Collaboratorが投稿した質問に限定しています。

RAGでは既存の `OPENAI_API_KEY`、`OPENAI_EMBEDDING_MODEL`、
`OPENAI_EMBEDDING_DIMENSIONS` を共用します。次のRepository Variablesを任意設定できます。

| 名前 | 既定値 | 用途 |
| --- | --- | --- |
| `RAG_MODEL` | `OPENAI_MODEL` または `gpt-5.4-mini` | 回答生成モデル |
| `RAG_TOP_K` | `8` | 回答生成へ渡す有効ナレッジ件数 |
