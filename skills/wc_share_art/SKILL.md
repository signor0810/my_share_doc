---
name: wc_share_art
description: 僅在使用者明確輸入 /wc_share_art 時使用,其他情況一律不要使用或建議此 skill(即使使用者說「分享」「發布」「幫我分享這個檔案」也不行)。作用:把單檔 .html 發布到公開 GitHub Pages(signor0810/my_share_doc)並回傳任何人免登入可開的網址。Use ONLY when the user explicitly types /wc_share_art; never invoke on your own.
disable-model-invocation: true
---

# wc_share_art

把 `.html` 發布成公開網址。**此 skill 只能由使用者輸入 `/wc_share_art [檔案路徑] [--name slug]` 觸發。** 使用者只是說「分享一下」時不要執行,也不要主動提議。

repo 是**公開**的:發布後任何人都看得到。不要修改 `publish.py`,不要手動編輯 `index.html`。

以下 `<skill_dir>` 是本檔所在目錄;`python` 在沒有時改用 `python3`。

## 步驟

1. **決定檔案**
   - 有給路徑就用該路徑(必須是存在的 `.html` / `.htm`)。
   - 沒給路徑:取本次對話中最近產生或修改的 `.html`。無法確定時,列出候選並詢問使用者,**不要猜**。
   - 只發布使用者指定或確認的檔案。
   - 不必另外用 `ls` 檢查檔案;步驟 3 的掃描腳本會回報檔案是否讀得到。Windows 路徑在 shell 指令中一律改用正斜線(`C:/Users/...`)並加引號,避免反斜線被 shell 吃掉。
2. **找到 repo**:執行 `python <skill_dir>/scripts/resolve_repo.py`。
   - 成功時 stdout 是 repo 路徑(順序:環境變數 `WC_SHARE_REPO`,否則 `~/my_share_doc`;不存在會自動 `git clone`)。
   - 失敗(工作樹有未提交內容、不在 main 等)就停止,把錯誤訊息原樣回報,不要自行 stash、reset 或強推。
3. **掃描機密**:執行 `python <skill_dir>/scripts/scan_secrets.py <檔案>`。
   - 結束碼 `0`:繼續。
   - 結束碼 `2`:**停止**,把列出的項目(已遮罩)給使用者看,等使用者明確確認後才繼續。使用者沒回覆或拒絕就不發布。
4. **檢查覆蓋**:slug 是 `--name` 的值,沒給時是檔名(去副檔名、轉小寫、非英數字元換成 `-`)。若 `<repo>/artifacts/<slug>.html` 已存在,發布會**覆蓋已公開的文件**:先告訴使用者並等確認,除非使用者已明說要更新該文件。
5. **發布**:在 repo 目錄下執行
   `python publish.py <檔案絕對路徑> [--name slug]`
   不要加 `--no-push`,除非使用者要求。
6. **回報**:把 `publish.py` 最後印出的網址**原樣**貼給使用者,並註明「約 1 到 3 分鐘後生效」。若 `publish.py` 失敗(例如 push 失敗),回報完整錯誤,不要自行修復或改用其他方式推送。

## 注意

- 掃描只是輔助,抓不到所有機密;公開 repo 的 git 歷史刪不掉,推上去的內容視同永久公開。
- 一次只發布一個檔案;不要發布使用者沒指定的檔案。
- 不要把 token、憑證寫進任何檔案。
