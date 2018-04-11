set DEPOT_TOOLS_WIN_TOOLCHAIN=0
set GYP_GENERATORS=msvs-ninja,ninja
set GYP_MSVS_VERSION=2017
set DEPOT_TOOLS_UPDATE=0
set GYP_MSVS_OVERRIDE_PATH=C:/Program Files (x86)/Microsoft Visual Studio/2017/Community
set WINDOWSSDKDIR=C:/Program Files (x86)/Windows Kits/10

buildtools\win\gn.exe gen out/vs --ide=vs2017 --sln=hello --args="is_debug=true is_component_build=true target_cpu =\"x86\" is_clang = false"