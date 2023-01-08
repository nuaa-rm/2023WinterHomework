# 长空御风2023年视觉组寒假作业判题机

## 如何使用
1. 安装python依赖前需要安装数个系统级依赖，对于ubuntu，可以执行
   ```bash
   sudo apt install python3-pip python3-dev python3-gi python3-gi-cairo \
                    gir1.2-gtk-3.0 libwebkit2gtk python3-tk
   ```
2. 安装依赖
    ```bash
    pip install -r requirements.txt
    ```
3. 编辑`config.py`，在其中填入可执行文件路径
4. 运行`main.py`

## 如何部署
由于判题机必须保证不可篡改性，代码在部署到实际环境时必须对关键代码执行加密，
此处使用cython将代码编译为c++后再编译为.so文件  
1. 修改`build.sh`L15处的平台字符串，如果无法确定平台字符串，
   可以执行一次`easycython updater.py`，即可看到平台字符串，
   执行后请删除生成的build文件夹和.so .c .html文件
2. 在本目录下执行`build.sh`，程序会自动编译到`dist`文件夹下
3. 将`dist`文件夹下的文件复制到实际环境中，执行`main.py`即可，
   如果已经在实际环境，记得删除其他代码
