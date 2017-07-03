# Network Programming with Python
2017/07/06

## 注意

**ここに書かれていることは実習室ネットワーク内でのみ実行すること。**

**特に、インターネットからアクセスできるネットワークにサーバを置くのは極めて危険性が高く、十分な理解と準備なしに行ってはいけない。**

## 準備

この実習ではLinux (Ubuntu)の上で行うことを前提としています。
WindowsやmacOSでも基本的に同じようにできるはずですが、コマンド等の詳細は異なることがあります。

この実習で使うファイル（このページを含む）はgithubでホストしています。
以下のコマンドでダウンロードしてください。

```
$ git clone https://github.com/shingoichii/netpgm.git
```

この実習ではPythonバージョン3を使います。
もしまだ入っていなかったら、apt等を使ってインストールしておいてください。
なおこれを明示するためにコマンド名として`python3`を使います。
各自の環境に合わせて（必要なら）書き換えてください。

以下のようにして、自分のコンピュータのIPアドレスを調べておいてください。

```
$ ifconfig -a
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.151  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::7271:bcff:fee9:a701  prefixlen 64  scopeid 0x20<link>
        ether 70:71:bc:e9:a7:01  txqueuelen 1000  (イーサネット)
（以下省略）
```

ここで、`inet`の次にあるのがIPv4アドレス、`inet6`の次にあるのがIPv6（のリンクローカル）アドレスです。
実習室のネットワークはIPv6では外部につながっていませんが、リンクローカルアドレスを使って実習室ネットワーク内での実験ができます。

以下の実行例では、IPアドレスの例として上の実行例の値を使います。
各自の環境に合わせて変更して実施してください。

## Pythonとネットワーク

Pythonでは高機能なネットワーク関係ライブラリが利用可能で、Webやメール、公開APIなどを容易に扱うことができます。

例えば次のone-liner

```
$ python3 -m http.server
```

を実行すると、Web (HTTP)サーバが起動します。
このHTTPサーバに接続するには、ブラウザで
`http://192.168.1.151:8000`
を開きます（デフォルトのポート番号は8000）。

#### 実習

1. 空でない（ファイルはサブディレクトリがある）ディレクトリをカレントディレクトリとして、上のone-linerを実行せよ。
1. ブラウザでアクセスすると、どのような表示になるか。
1. 簡単なHTMLファイルを`index.html`としてそのディレクトリに置いてみよ。ブラウザの表示はどうなるか。

## Network programming with Py

高機能なライブラリは便利ですが、実際どういう仕掛けでネットワーク越しにデータが送受信されているのかわからないので、トラブルが起きた時やパフォーマンスが思わしくない場合などに困ることがあります。
一度は、OSが提供する低レベルのネットワーク機能を体験しておくことを勧めます。

Unix/Linuxのnative languageはC言語なので、OSの機能ももともとはC言語で呼び出すようにできていますが、Pythonなど他の言語で利用するためのライブラリ（wrapperなどと呼ばれる）が用意されています。
この実習では、Pythonのsocketインターフェイスを使い、ネットワークを介してデータをやり取りするための最も基本的な部分を動かしてみます。

ネットワークでは一般には双方向にデータがやりとりされますが、ソフトウェア的には送信側と受信側に分けて考えると便利です。送信側をclientと呼び、受信側をserverと呼びます。
データは双方向にやりとりされるので紛らわしいですが、通信を始める側がclientで、clientからの接続を待っているのがserverということです。

### server

まずserver側のコード`tcps.py`を用意します。

```tcps.py
 1	#! /usr/bin/env python3
 2
 3	import socket
 4	import threading
 5
 6	bind_ip = "0.0.0.0"
 7	bind_port = 9999
 8
 9	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
10	server.bind((bind_ip, bind_port))
11	server.listen(5)
12
13	print("[*] listening on {}:{}".format(bind_ip, bind_port))
14
15	def handle_client(client_socket):
16	    request = client_socket.recv(1024)
17	    print("[*] received: {}".format(request.decode('utf-8')))
18	    client_socket.send("ACK".encode('utf-8'))
19	    client_socket.close()
20
21	while True:
22	    (client, addr) = server.accept()
23	    print("[*] accepted connection from {}:{}".format(addr[0], addr[1]))
24	    client_hander = threading.Thread(target=handle_client, args=(client,))
25	    client_hander.start()
```

基本的な流れは、

1. 9行目でsocketを生成 (socket)
1. 10行目でsocketにアドレスをつける (bind)
1. 11行目でclientからの接続を待つ (listen)
1. 21行目からのloopはclientから接続が来た時の処理
1. 22行目でclientからの接続を受け付ける (accept)
1. 24/25行目で受け付けたclientに対する処理をthreadとして開始する

となっています。

`bind`するアドレスを6行目の`bind_ip = "0.0.0.0"`としているのは、そのコンピュータの全てのネットワークインターフェイス[1]で接続を待つことを表しています。ポート番号は7行目、9999です。

>[1] コンピュータは一般には複数のネットワークインターフェイスを持ちます（複数の有線ネットワークとか、有線と無線とか）。IPv4では各インターフェイスに原則として一つのIPアドレスがつけられます。その他、「自分」を表す仮想インターフェイス（localhost）があり、`127.0.0.1`がつけられます。IPv6では各インターフェイスに複数のアドレスがつけられます。


15行目からの`handle_client`では

1. 16行目でclientが送信したデータを受信
1. 17行目でそれを表示
1. 18行目で返事（ACK: acknowledgement) を返す
1. 19行目でこのclientに対する処理を終了

と各clientに対する処理を記述しています。
複数のclientからの接続をそれぞれ処理するために、threadを使っています。

### client

次にclient側のコード`tcpc.py`を用意します。

```tcpc.py
 1	#! /usr/bin/env python3
 2
 3	import socket
 4
 5	target_host = "localhost"
 6	target_port = 9999
 7
 8	# creat a socket object
 9	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
10
11	# connect to server
12	client.connect((target_host, target_port))
13
14	# send data
15	client.send("hello".encode('utf-8'))
16
17	# receive data
18	response = client.recv(4096)
19
20	print(response.decode('utf-8'))
21
22	client.close()
```

基本的な流れは、

1. 9行目でsocketを生成
1. 12行目でserverに接続
1. 15行目でデータを送信
1. 18行目でデータを受信
1. 22行目でsocketを閉じる

となっています。

5行目でserver側のホスト名を指定しています。
serverと同じコンピュータ上で動かす際には`localhost`のままで良いですが、別のコンピュータと通信する際にはここに相手のIPアドレスを"192.168.1.151"のように入れてください。
7行目のポート番号はserverで指定したものと同一でなければなりません。

#### 実習

ターミナルを二つ開き、それぞれでtcps.pyとtcpc.pyを動かす。

1. tcps.pyを先に起動し、次にtcpc.pyを起動する。期待通りの出力が得られたか。
1. シェルの`&`を使って、tcpc.pyを複数起動したらどうなるか。
1. tcps.pyを^Cで終了し、tcpc.pyを起動したらどうなるか。
1. 2台のコンピュータを使い、tcpc.pyの`target_host`を適当に書き換えて通信を行ってみよ。

#### 注意

`tcps.py`, `tcpc.py`のいずれも、ネットワークで送られて来たデータをそのまま使っています（この場合、画面に表示）。
本来は、想定しないデータを含まないことを確認（sanitizationという）してから使うべきです。

## IP Multicast with Py

socketを使った通信の応用編として、IP multicastを使ったchatのようなものの例を示します。

Multicastというのは、１つの相手への通信であるunicast,
（あるネットワーク上の範囲の）全部への通信であるbroadcastの中間で、
一定のグループに属する（一般には複数の）相手への通信を表します。
IPでは、特定のIPアドレスで表されるmulticast groupにjoinという操作を行うことでグループを作ります。
clientは、multicast groupを表すIPアドレスに送信することで複数の相手に同時にデータを送ることができます。

プログラム`mcc.py`は少し長いのでここには示しません。使い方は以下の通りです。

```
$ mcc.py myname    # 受信
$ mcc.py -s myname # 送信（紛らわしいですがsenderのs）
```

`myname`には自分の名前を入れます（Unicode可）。

なおデフォルトではIPv6のmulticastを使います。

```
$ mcc.py -4 myname
$ mcc.py -4 -s myname
```

とするとIPv4になります。IPv4とIPv6に互換性はありません（相互に通信できない）。

受信モードでは、発言を受信して表示します。

送信モードを選ぶと、プロンプト

```
>>>
```

が表示されるので、発言を入力して改行を押すと送信されます。
^Dでプログラムが終了します。

IP multicastは信頼性のない通信（途中でデータが落ちたりエラーがあっても再送等の処理をしない）なので、発言しても受信されない場合があります。

#### 実習

1. ターミナルを二つ開き、一つで受信モード、もう一つで送信モードの`mcc.py`を起動する。
1. 送信モード側で何か発言する。

なお、実習時間内には怪しいbotが動いているので気をつけてください。

### Thanks

`mcc.py`は以下のコードを基にしています。

http://svn.python.org/projects/stackless/trunk/Demo/sockets/mcast.py
