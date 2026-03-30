import { useEffect, useState } from "react";
import { deleteHistoryItem, fetchHistory, generateQR } from "./api";

export default function App() {
  const [url, setUrl] = useState("");
  const [labelText, setLabelText] = useState("");
  const [labelPosition, setLabelPosition] = useState("Top");
  const [qrSrc, setQrSrc] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 履歴を読み込む
  const loadHistory = async () => {
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // QRコード生成
  const handleGenerate = async () => {
    if (!url) {
      setError("URLが空欄です");
      return;
    }

    const urlPattern = /^https?:\/\/.+/;
    if (!urlPattern.test(url)) {
      setError("有効なURLを入力してください（http:// または https://）");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const src = await generateQR(url, labelText, labelPosition);
      setQrSrc(src);
      await loadHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  // 履歴クリック
  const handleHistoryClick = (item) => {
    setUrl(item.url);
    setLabelText(item.label_text || "");
    setLabelPosition(item.label_position || "Top");
    setQrSrc(null);
  };

  // 履歴削除
  const handleDelete = async (id) => {
    try {
      await deleteHistoryItem(id);
      await loadHistory();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex p-6 gap-6 font-sans">
      
      {/* サイドバー */}
      <aside className="w-64 bg-white rounded-2xl shadow-md p-4">
        <h3 className="text-lg font-bold mb-4">生成履歴</h3>
  
        {history.length === 0 && (
          <p className="text-gray-400 text-sm">
            まだ履歴がありません
          </p>
        )}
  
        <div className="space-y-2">
          {history.map((item) => (
            <div key={item.id} className="flex items-center gap-2">
              <button
                onClick={() => handleHistoryClick(item)}
                className="flex-1 text-left px-3 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-sm truncate"
              >
                {item.url.slice(0, 25)}{" "}
                <span className="text-gray-500">
                  {item.label_text || "注釈なし"}
                </span>
              </button>
  
              <button
                onClick={() => handleDelete(item.id)}
                className="text-gray-400 hover:text-red-500"
              >
                🗑
              </button>
            </div>
          ))}
        </div>
      </aside>
  
      {/* メイン */}
      <main className="flex-1 flex justify-center">
        <div className="bg-white p-6 rounded-2xl shadow-md w-full max-w-md">
          
          <h1 className="text-xl font-bold mb-2 text-center">
            URL to QR Generator
          </h1>
          <p className="text-sm text-gray-500 mb-4 text-center">
            URLを入力してQRコードを生成できます
          </p>
  
          {/* URL入力 */}
          <label className="text-sm font-medium">URL</label>
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="border p-2 w-full rounded mt-1 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
  
          {/* 注釈 */}
          <details className="mb-4">
            <summary className="cursor-pointer text-sm font-medium mb-2">
              注釈（ラベル）の設定
            </summary>
  
            <label className="text-sm">表示する文字</label>
            <input
              value={labelText}
              onChange={(e) => setLabelText(e.target.value)}
              placeholder="例：公式LINEはこちら"
              className="border p-2 w-full rounded mt-1 mb-3"
            />
  
            <div className="flex gap-4">
              {["Top", "Bottom"].map((pos) => (
                <label key={pos} className="cursor-pointer text-sm">
                  <input
                    type="radio"
                    value={pos}
                    checked={labelPosition === pos}
                    onChange={() => setLabelPosition(pos)}
                    className="mr-1"
                  />
                  {pos}
                </label>
              ))}
            </div>
          </details>
  
          {/* エラー */}
          {error && (
            <p className="text-red-500 text-sm mb-2">
              {error}
            </p>
          )}
  
          {/* ボタン */}
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="bg-blue-500 text-white w-full py-2 rounded-lg hover:bg-blue-600 transition disabled:opacity-50"
          >
            {loading ? "生成中..." : "QRコードを生成"}
          </button>
  
          {/* 結果 */}
          {qrSrc && (
            <div className="mt-6 text-center">
              <img src={qrSrc} alt="QRコード" className="mx-auto w-64" />
  
              <a
                href={url}
                target="_blank"
                rel="noreferrer"
                className="block text-blue-500 mt-3 text-sm underline"
              >
                リンクを開く
              </a>
  
              <a href={qrSrc} download="qr_code.png">
                <button className="mt-2 text-sm bg-gray-200 px-3 py-1 rounded hover:bg-gray-300">
                  画像を保存
                </button>
              </a>
            </div>
          )}
  
        </div>
      </main>
  
    </div>
  ); 
}