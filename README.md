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
