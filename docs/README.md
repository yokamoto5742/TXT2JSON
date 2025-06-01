# カルテ記載JSON変換アプリ

カルテ記載のテキストデータを構造化されたJSON形式に変換するWindowsアプリケーションです。
SOAP記録（主観的情報、客観的情報、評価、計画）の解析と自動整理機能を提供します。

## 主な機能

### 📝 テキスト変換機能
- カルテ記載テキストの自動解析
- SOAP記録の構造化（S: 主観的情報、O: 客観的情報、A: 評価、P: 計画）
- 日時・診療科・内容の自動分類
- 重複データの除去と統合

### 📋 クリップボード監視
- リアルタイムクリップボード監視
- 自動テキスト追加機能
- コピー通知システム

### 🖱️ 自動化機能
- マウス操作の自動実行
- SOAPデータの自動コピー
- 外部アプリケーション連携

### 🔧 確認・編集機能
- テキスト内容の確認画面
- 印刷機能
- 統計情報表示（行数・文字数）

## システム要件

- **OS**: Windows 10/11
- **Python**: 3.10以上
- **追加ソフト**: AutoHotkey v2.0（マウス操作自動化用）

## インストール

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd medical-text-converter
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 設定ファイルの編集
`utils/config.ini`を環境に合わせて編集してください：

```ini
[Appearance]
window_width = 1100
window_height = 800
text_area_font_size = 12
text_area_font_name = MS Gothic

[Paths]
operation_file_path = C:\path\to\mouseoperation.exe
soap_copy_file_path = C:\path\to\soapcopy.exe
```

## 使用方法

### 1. アプリケーションの起動
```bash
python main.py
```

### 2. 基本的な使用フロー

#### 新規データ入力
1. **「新規登録」**ボタンをクリック
2. クリップボード監視が開始されます
3. 電子カルテからテキストをコピーすると自動で入力エリアに追加

#### JSON変換
1. **「JSON形式変換」**ボタンをクリック
2. 変換されたJSONが下部エリアに表示
3. 自動的にクリップボードにコピー

### 3. 自動化機能

#### マウス操作設定
- **「詳細検索設定」**：定義済みのマウス操作を実行
- **「カルテコピー」**：SOAPデータの自動コピー

### 4. 確認・編集
- **「確認画面」**：別ウィンドウでテキスト内容を確認・編集
- 印刷機能も利用可能

## テキスト形式の例

### 入力例
```
2024/01/15(月)（入院 5日目）
内科 田中医師 外来 09:30
S > 
頭痛が続いている。昨夜はよく眠れなかった。
O > 
血圧：120/80mmHg、体温：36.8℃
A > 
症状は改善傾向。経過観察継続。
P > 
現在の薬物療法を継続。1週間後に再診。
```

### 変換後JSON例
```json
[
  {
    "timestamp": "2024-01-15T09:30:00Z",
    "department": "内科",
    "subject": "頭痛が続いている。昨夜はよく眠れなかった。",
    "object": "血圧：120/80mmHg、体温：36.8℃",
    "assessment": "症状は改善傾向。経過観察継続。",
    "plan": "現在の薬物療法を継続。1週間後に再診。"
  }
]
```

## 設定項目

### 外観設定
- ウィンドウサイズ・位置
- フォント設定
- ボタンサイズ

### パス設定
- マウス操作実行ファイルのパス
- SOAPコピー実行ファイルのパス

## トラブルシューティング

### よくある問題

#### クリップボード監視が動作しない
- アプリケーションを管理者権限で実行してください
- セキュリティソフトがクリップボードアクセスをブロックしている可能性があります

#### マウス操作が実行されない
- `config.ini`の実行ファイルパスを確認してください


## 開発者向け情報

### プロジェクト構造
```
├── main.py                    # メインアプリケーション
├── requirements.txt           # 依存関係
├── version.py                # バージョン情報
├── services/                 # サービス層
│   ├── mouse_automation.py   # マウス操作自動化
│   ├── txt_editor.py        # テキストエディタ
│   └── txt_parse.py         # テキストパース処理
└── utils/                   # ユーティリティ
    ├── config_manager.py    # 設定管理
    ├── config.ini          # 設定ファイル
    ├── mouseoperation.ahk  # マウス操作スクリプト
    └── soapcopy.ahk       # SOAPコピースクリプト
```

### 主要クラス・関数

#### `MedicalTextConverter`（main.py）
- メインGUIアプリケーションクラス
- クリップボード監視、JSON変換、UI管理

#### `parse_medical_text()`（txt_parse.py）
- 医療テキストの解析とSOAP構造化
- 日時・診療科・内容の分類処理

#### `TextEditor`（txt_editor.py）
- テキスト確認・編集用のサブウィンドウ

### カスタマイズ

#### 新しいSOAPセクションの追加
`txt_parse.py`の`soap_mapping`辞書を編集：
```python
soap_mapping = {
    'S': 'subject',
    'O': 'object', 
    'A': 'assessment',
    'P': 'plan',
    'F': 'comment',
    'サ': 'summary',
    '新': 'new_section'  # 新しいセクション
}
```

## ライセンス

このプロジェクトのライセンス情報については、LICENSEファイルを参照してください。

## 貢献

バグ報告や機能要望は、GitHubのIssuesページでお知らせください。
