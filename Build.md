# 开始指导

请务必将命令行工作目录切换到**app.py所在的文件夹**

在运行这些脚本的时候，请将语句**逐个**复制到命令行里面运行

如果你有一个PyCharm你可以省略1、2、4步骤，但是需要点击左下角终端形状的符号，输入第三步的命令安装依赖

## 1、安装python版本约为3.10
## 2、激活虚拟环境
```commandline
py -m venv venv
```
```commandline
./venv/Scripts/activate
```
## 3、安装依赖
检查命令提示符是否出现以"(venv)"开头
```commandline
pip install -r requirements.txt
```
## 4、运行app
```commandline
python app.py
```
留意输出中：
```text
Running on local URL:  xxxxxx
```
Ctrl+单击后面的“xxxxxx”部分，或者复制链接在浏览器打开，运行程序