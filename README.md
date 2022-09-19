# 概要
Auth0(https://auth0.com/jp)でOIDC(OpenID Connect)に則った形で通信ができるかを確認するために作成したクライアント.<BR>

# Lib Install
必要なライブラリは下記のコマンドで取得できる. <BR>
```$ pip install -r requirements.txt```

# 事前設定
このアプリは、Auth0(https://auth0.com/jp)の環境に対して通信を行う.<BR>
使用する場合、Auth0の設定をしていただき、OIDCに則った形で通信できるように設定をする必要がある.<BR>
設定方法はDYOR.<BR>
<BR>
.envのファイルにはAuth0の設定を基に必要な変更を加えてください.
```  
AUTH0_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AUTH0_CLIENT_SECRET=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
AUTH0_DOMAIN=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
APP_SECRET_KEY=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
REDIRECT_URI=BBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
AUDIENCE=CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
```

# 実行方法  
```
python server.py
```

# デモ
`demo.zip`ファイルにデモ動画を配置しています。
