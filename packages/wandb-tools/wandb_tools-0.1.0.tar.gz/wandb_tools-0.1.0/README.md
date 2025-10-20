# Wandb-Local

## Server

### 1. Launch Server
```bash
python3 serve.py --project <project name> --port <port>
```
- 建立名稱為 `<user name>-wandb-<project name>` container
- 預設的存儲目錄是 `/volume/share/wandb-local/volume/<project name>`

若要使用預設路徑外的儲存目錄，可以指定 `--volume` 參數，例如
```bash
python3 serve.py --project <project name> --port <port> --volume /volume/share/wandb-local/volume/trade-richardwang/
```

### 2. Registration
1. 瀏覽器打開 `http://<host ip>:<port>`
   - `<host ip>` 為當初執行 server 啟動程式的機器的 IP，例如 10.11.60.1
2. 點擊 login 並註冊此部屬上的帳戶，建議設置:
   - Full name: Sinopac  
   - E-mail: 123@sinopac.com
   - Username: sinopac
   - Pssword: 123@sinopac.com

## Client

### Configure connection
<api-key> 可在右上角機器人頭像 -> User Settings -> Danger Zone -> API keys -> Reveal 中找到

#### 寫在 dot env 檔案
設置於 `.env` 檔案
```
WANDB_BASE_URL=http:/<host ip>:<port>
WANDB_API_KEY=<api-key>
```

#### 寫在 Python 檔案
```python
os.environ["WANDB_BASE_URL"] = "http:/<host ip>:<port>"
os.environ["WANDB_API_KEY"] = "<api-key>"
```

### Best practices

#### Programmatically cleanup cache
wandb use `./cache/local` to save artifacts even they are uploaded to server.
```python
c = wandb.wandb_sdk.wandb_artifacts.get_artifacts_cache()
c.cleanup(int(10e9)) # up to 10GB cache
```

#### Do not log system metrics
System metrics are frequent and many, which can put a lot of pressure on a local server.
```python
wandb.init(
    ...
    settings=wandb.Settings(
        _disable_stats=True,
        _disable_machine_info=True,
    )
)
```