# ppget

**PubMed文献を簡単にダウンロードできるシンプルなCLIツール**

[日本語版README](README_ja.md) | [English](README.md)

`ppget` は、PubMedから文献データを検索・ダウンロードするためのコマンドラインツールです。
[EDirect](https://www.ncbi.nlm.nih.gov/books/NBK179288/)のような複雑な設定は不要で、**すぐに使い始められます**。

## ✨ 特徴

- 🚀 **インストール不要** - `uvx`で即座に実行可能
- 📝 **CSV/JSON対応** - スプレッドシートでも、プログラムでも扱いやすい
- 🔍 **柔軟な検索** - PubMed検索構文（AND, OR, MeSHなど）をフルサポート
- 📊 **メタデータ保存** - 検索クエリや取得日時を自動記録
- 🎯 **シンプルなAPI** - 分かりやすいオプション設計

## 🚀 クイックスタート

### インストール不要で使う（推奨）

[uv](https://github.com/astral-sh/uv)がインストール済みなら、**インストールせずに即座に実行できます**：

```bash
# 基本的な使い方
uvx ppget "machine learning AND medicine"

# 取得件数を指定
uvx ppget "COVID-19 vaccine" -l 50

# JSON形式で保存
uvx ppget "cancer immunotherapy" -f json
```

### インストールして使う

頻繁に使う場合はインストールもできます：

```bash
# pipでインストール
pip install ppget

# uvでインストール
uv tool install ppget

# 実行
ppget "your search query"
```

## 📖 使い方

### 基本的な使い方

```bash
# シンプルな検索（デフォルトでCSV形式、100件まで）
ppget "diabetes treatment"

# 検索結果の例：
# Searching PubMed...
# Query: 'diabetes treatment'
# Max results: 100
# ✓ Found 100 articles
# ✓ Saved 100 articles to pubmed_20251018_143022.csv
# ✓ Metadata saved to pubmed_20251018_143022.meta.json
```

### オプション一覧

```bash
ppget [検索クエリ] [オプション]

必須引数:
  query                 検索クエリ

オプション:
  -l, --limit          最大取得件数（デフォルト: 100）
  -o, --output         出力先（ファイルまたはディレクトリ）
  -f, --format         出力形式: csv または json（デフォルト: csv）
  -e, --email          メールアドレス（API制限緩和用）
  -h, --help           ヘルプを表示
```

### 高度な使い方

#### 1. 取得件数を変更

```bash
# 200件まで取得
ppget "machine learning healthcare" -l 200
```

#### 2. 出力形式を指定

```bash
# JSON形式で保存
ppget "spine surgery" -f json

# デフォルトはCSV形式（Excelで開ける）
ppget "orthopedics" -f csv
```

#### 3. ファイル名を指定

```bash
# ファイルパスを直接指定
ppget "cancer research" -o results/cancer_papers.csv

# ディレクトリを指定（ファイル名は自動生成）
ppget "neuroscience" -o ./data/

# 拡張子で形式も指定できる
ppget "cardiology" -o heart_disease.json
```

#### 4. メールアドレスを指定（API制限緩和）

NCBIのAPIは、メールアドレスを指定すると制限が緩和されます：

```bash
ppget "genomics" -e your.email@example.com -l 500
```

#### 5. PubMed検索構文を活用

```bash
# AND検索
ppget "machine learning AND radiology"

# OR検索
ppget "COVID-19 OR SARS-CoV-2"

# MeSHタームで検索
ppget "Diabetes Mellitus[MeSH] AND Drug Therapy[MeSH]"

# 年度で絞り込み
ppget "cancer immunotherapy AND 2024[PDAT]"

# 著者名で検索
ppget "Smith J[Author]"

# 複雑な検索
ppget "(machine learning OR deep learning) AND (radiology OR imaging) AND 2023:2024[PDAT]"
```

## 📁 出力形式

### CSV形式（デフォルト）

スプレッドシートで開きやすい形式です。同時にメタデータファイル（`.meta.json`）も生成されます。

```
pubmed_20251018_143022.csv          # 論文データ
pubmed_20251018_143022.meta.json    # 検索メタデータ
```

**CSVの列：**
- `pubmed_id` - PubMed ID
- `title` - タイトル
- `abstract` - 要旨
- `journal` - ジャーナル名
- `publication_date` - 出版日
- `doi` - DOI
- `authors` - 著者リスト（セミコロン区切り）
- `keywords` - キーワード（セミコロン区切り）
- `conclusions` - 結論
- `methods` - 方法
- `results` - 結果
- `copyrights` - 著作権情報

### JSON形式

プログラムで処理しやすい形式です。検索メタデータもファイル内に含まれます。

```json
{
  "search_metadata": {
    "query": "machine learning",
    "search_date": "2025-10-18 14:30:22",
    "retrieved_results": 100
  },
  "articles": [
    {
      "pubmed_id": "12345678",
      "title": "...",
      "abstract": "...",
      ...
    }
  ]
}
```

## 🆚 EDirectとの比較

| 特徴 | ppget | EDirect |
|------|------|---------|
| インストール | 不要（`uvx`で即実行） | 複雑なセットアップが必要 |
| 使いやすさ | 1コマンドで完結 | 複数コマンドの組み合わせ |
| 出力形式 | CSV/JSON | XML/テキスト |
| メタデータ | 自動保存 | 手動で管理 |
| 学習コスト | 低い | 高い |

### EDirectの例（複雑）

```bash
# EDirectでの検索（複数ステップが必要）
esearch -db pubmed -query "machine learning" | \
efetch -format abstract | \
xtract -pattern PubmedArticle -element MedlineCitation/PMID,ArticleTitle
```

### ppgetの例（シンプル）

```bash
# ppgetなら1コマンド
ppget "machine learning"
```

## 💡 使用例

### 研究論文の収集

```bash
# 特定のトピックの最新論文を収集
ppget "CRISPR gene editing" -l 100 -o crispr_papers.csv

# 複数の検索を一度に実行
ppget "diabetes treatment 2024[PDAT]" -o diabetes_2024.csv
ppget "cancer immunotherapy 2024[PDAT]" -o cancer_2024.csv
```

### データ分析用

```bash
# JSON形式で取得してPythonで分析
ppget "artificial intelligence healthcare" -f json -l 500 -o ai_health.json

# Pythonでの読み込み例
import json
with open('ai_health.json') as f:
    data = json.load(f)
    articles = data['articles']
    # 分析処理...
```

### 文献レビュー

```bash
# CSVで取得してExcelで管理
ppget "systematic review AND meta-analysis" -l 200 -o reviews.csv

# → Excelで開いて、タイトルやアブストラクトをレビュー
```

## 🤝 貢献

バグ報告や機能リクエストは [Issues](https://github.com/masaki39/ppget/issues) へお願いします。

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) をご覧ください。

## 🙏 謝辞

このツールは [pymed-paperscraper](https://github.com/nils-herrmann/pymed-paperscraper) を使用しています。

---

**簡単に、すぐに、PubMed検索を始めましょう！**

```bash
uvx ppget "your research topic"
```
