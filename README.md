# gn_template
Use gn to manage and compile cross-platform code.

## 说明
这个工程是使用gn来管理和编译跨平台的代码的模板。相关的脚本是取自Chromium工程。Chromium工程能够很好支持windows、linux、mac、android、ios等平台的编译。

## 使用方法
因为gn一直在更新，所以没有把相关配置放到仓库里。相关目录需要从chromium工程中复制过来。
1. 从chromium的代码目录复制build目录到本目录。build目录里面包含了跨平台编译所需要的各种配置。
2. 从chromium的代码目录复制build_overrides目录到本目录。
3. 从chromium的代码目录复制buildtools目录到本目录。这个目录包含了gn的可执行文件。
4. 如果需要支持clang编译，从chromium的代码目录复制tools\clang和third_party\llvm-build目录到本目录。
5. 在windows平台，使用vs2017编译，先运行vs_gen.bat生成工程，再运行vs_build.bat开始编译。
6. 在windows平台，使用clang编译，先运行clang_gen.bat生成工程，再运行clang_build.bat开始编译。