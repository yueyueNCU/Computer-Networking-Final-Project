# 規章
## Github 使用教學
###  如何使用SSH key(設定後不需要每次手動輸入密碼，自動與 GitHub 連線，節省時間)
1. 用以下指令產生你的SSH key，然後一路按enter 或 有說要Yes/No就輸入Yes
    ```
    ssh-keygen -t ed25519 -C "{your_email@example.com}"
    ```
2. 將SSH public key複製起來
    ```
    cat ~/.ssh/id_ed25519.pub | clip
    ```
3. 在github頭像 -> Setting -> SSH and GPG keys -> New SSH key
![key 輸入畫面](./img/ssh_github.png)
4. 用以下指令測試是否已經可以連接github
    ```
    ssh -T git@github.com
    ```
### 如何合作 

> [!TIP] 
> 如果還沒設定過git，先去安裝
> https://git-scm.com/install/windows

#### 我們先設定有3種分支(branches)，以下是分支結構
1. main (不能亂動)
    * 定義： 這是 Demo 當天要跑的版本。
    * 規則：
        1. 絕對禁止直接 Push 程式碼進去。
        2. 只有當 dev 分支測試沒問題，且準備好要交作業或報告時，才從 dev 合併過來。
    * 目的： 保命。就算dev版本爛掉了，至少還有一個能動的版本可以拿去 Demo。
2. dev (測試區)
    * 定義： 大家程式碼「會合」的地方。
    * 規則：
        1. 這是你們平常主要的合併目標。
        2. 這裡的程式碼可能會壞掉（因為大家剛合併），這很正常 (前後端對接就在這裡測試)。
3. feature/你的名字-功能 (自己實作功能地方)
    * 定義： 這是你真正寫程式的地方。
    * 命名建議： feature/yueyue-seat-grid、feature/ian-map-ui。
    * 規則：
        1. 一個功能開一個分支，做完就合併回 dev，然後刪除這個分支。
        2. 在這個分支裡，你愛怎麼改都可以，完全不會影響到隊友。

#### 怎麼開分支，然後coding
以下會直接開啟一個分支並自動切換分支
```
git switch -c {新的分支名稱}
```
就可以開始coding了
#### 我們每個人寫完程式碼時要怎麼上傳到github 

> [!NOTE]
> 以下是git 狀態圖，以下四個狀態都是在本機進行
> 1. untracked: 檔案是新的，Git 知道它存在於工作目錄，但尚未納入版本控制。
> 2. unmodified: 檔案已經被 Git 追蹤，且其內容與上次commit的內容完全一致。
> 3. modified: 檔案已經被 Git 追蹤，但有被跟改，使其與上次提交不同。
> 4. staged (已暫存): 檔案的特定版本已經被標記，準備好包含在下一次push中。
> ![git 狀態圖](./img/git_status_lifecycle.png)

1. 檢查自己改了甚麼地方，並確認自己所在的分支
    ```
    git status
    ```
2. 將更改檔案或新檔案加入git版本控制
    ```
    git add .
    ```
3. 先拉取最新 dev
    ```
    git fetch origin
    git merge origin/dev
    ```
3. 將這次修改內容放到Staged區域
    ```
    git commit -m "your comment about this push"
    ```
4. 將這次修改上傳到github
    > [!NOTE]
    > 如果是初次推送或建立追蹤時用以下指令，以後都可以用最下面的
    > ```
    > git push -u origin {你的分支名稱}
    > ```
    ```
    git push
    ```

> [!CAUTION]
> 如果第三步發生衝突，這代表你寫的code跟別人有重疊到，
> 而衝突檔案會標記: 
> ```
> <<<<<<< HEAD
> 你的修改
> =======
> 別人的修改 (dev 分支)
> >>>>>> origin/dev
> ```
> 處理方式: 
> 1. 決定要保留哪一段或手動合併兩段
> 2. 刪掉 <<<<<<<, =======, >>>>>>> 標記
> 3. 儲存檔案



> [!IMPORTANT]
> 在開始新的一輪寫code時，要再次把dev最新狀態抓下來，再開一個分支
> 1. 首先切回dev分支
>    ```
>    git switch dev
>    ```
> 2. 同步dev最新狀態
>    ```
>    git pull
>    ```
> 3. 開啟新的一輪coding(功能實作)
>    ```
>    git switch -c {新的分支名稱}
>    ```
> 4. 後續動作一樣

#### 如何合併回dev分支
1. 完成push程式碼到你自己的分支後
2. 到Github網頁開啟pull request
3. (希望)會先跑git action測測看測試是不是通過
3. 這階段會需要至少通過一名組員review後，才能合併