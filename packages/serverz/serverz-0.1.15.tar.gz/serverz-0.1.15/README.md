使用以下方式进行server 和测试 配置对应测试环境 
uv run pytest -s tests/test_main.py::test_get_id_from_name 
uv run python -m clientz.server 80 --prod

docker-compose build --no-cache

# C语言相关使用方式

## 文本内容
├── CMakeLists.txt
├── LICENSE
├── Readme.md
├── conanfile.txt
└── src
    ├── workspace
        ├── main.cpp
        ├── show.cpp
        └── show.h

## build
cd build
conan install .. -of . --build missing
### 构建Cmake
cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release# or Debug



# clientz

# 正式启动
<!-- cd src; python -m clientz.server 8008 -->
python -m clientz.server --prod

# 测试启动
python -m src.clientz.server

基本只需要修改
core.py 
config.yaml


