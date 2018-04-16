#!/usr/bin/env python
# encoding: utf-8

__author__ = 'jiajie.pjj@alibaba-inc.com'

import os
import sys
import shutil
import argparse
import logging
import tempfile
import zipfile
import subprocess

def get_current_directory():
  ''' get the script current directory.'''

  current_directory = os.path.split(os.path.realpath(__file__))[0]
  return current_directory

def get_chromium_buildtools_directories():
  ''' get chromium buildtools directories list.'''

  directory_list = [
    r'build',
    r'build_overrides',
    r'buildtools',
    r'testing',
    r'third_party\ced',
    r'third_party\googletest',
    r'third_party\icu',
    r'third_party\libxml',
    r'third_party\llvm-build',
    r'third_party\modp_b64',
    r'third_party\win_build_output',
    r'third_party\zlib',
    r'tools\clang',
    r'tools\win\DebugVisualizers',
  ]
  return directory_list

def copy_buildtools(dst_directory, chromium_src_directory):
  '''copy buildtoos directory from chromium src to dst.'''

  src_directories = get_chromium_buildtools_directories()
  for d in src_directories:
    from_directory = os.path.join(chromium_src_directory, d)
    to_directory = os.path.join(dst_directory, d)
    if not os.path.exists(from_directory):
      logging.error("src path %s not exists!" % from_directory)
      return False
    if os.path.exists(to_directory):
      logging.error("dst path %s has exists!" % to_directory)
      return False
    shutil.copytree(from_directory, to_directory)

def zip_buildtools(dst_directory, chromium_src_directory):
  '''copy buildtools directory and zip.'''

  zip_file_path = os.path.join(dst_directory, 'buildtools_zip')
  if os.path.exists(zip_file_path):
    shutil.rmtree(zip_file_path)
  zip_directory = os.path.join(dst_directory, 'chromium_buildtools')
  copy_buildtools(zip_directory, chromium_src_directory)
  shutil.make_archive(zip_file_path, 'zip', zip_directory)
  shutil.rmtree(zip_directory,ignore_errors = True)

def set_project_environ_var():
  ''' set the necessary environment variables.'''

  os.environ["DEPOT_TOOLS_WIN_TOOLCHAIN"]='0'
  os.environ["GYP_GENERATORS"]='msvs-ninja,ninja'
  os.environ["GYP_MSVS_VERSION"]='2017'
  os.environ["DEPOT_TOOLS_UPDATE"]='0'
  os.environ["GYP_MSVS_OVERRIDE_PATH"]='C:/Program Files (x86)/Microsoft Visual Studio/2017/Community'
  os.environ["WINDOWSSDKDIR"]='C:/Program Files (x86)/Windows Kits/10'

def run_gn(is_debug, is_component_build):
  '''run gn to generate project.'''

  gn_exe = 'buildtools\win\gn.exe'
  out_directory = ''
  is_debug_string = ''
  is_component_build_string = ''
  if is_debug:
    is_debug_string='is_debug=true'
    out_directory = out_directory + 'debug'
  else:
    is_debug_string='is_debug=false'
    out_directory = out_directory + 'release'
  if is_component_build:
    is_component_build_string='is_component_build=true'
    out_directory = out_directory + '_shared'
  else:
    is_component_build_string='is_component_build=false'
    out_directory = out_directory + '_static'

  cmd  = '%s gen out/%s --ide=vs2017 --sln=all --args=\"%s %s target_cpu =\\"x86\\" is_clang = false\"' % (gn_exe, out_directory, is_debug_string, is_component_build_string)
  logging.info(cmd)
  subprocess.check_call(cmd)

def gen_project():
  '''generate all types project'''

  set_project_environ_var()
  run_gn(is_debug = True, is_component_build = True)
  run_gn(is_debug = False, is_component_build = True)
  run_gn(is_debug = True, is_component_build = False)
  run_gn(is_debug = False, is_component_build = False)

def run_ninja(out_directory):
  '''run ninja to build.'''

  cmd  = 'ninja -C out/%s all' % (out_directory)
  logging.info(cmd)
  subprocess.check_call(cmd)

def build_project(build_type):
  '''build project.'''

  set_project_environ_var()
  if build_type == 'all':
    run_ninja('release_static')
    run_ninja('debug_static')
    run_ninja('release_shared')
    run_ninja('debug_shared')
  elif build_type == 'release':
    run_ninja('release_static')
    run_ninja('release_shared')
  elif build_type == 'static':
    run_ninja('debug_static')
    run_ninja('release_static')
  elif build_type == 'shared':
    run_ninja('debug_shared')
    run_ninja('release_shared')
  else:
    run_ninja(build_type)

def collect_head_files():
  '''collect head files'''

  current_directory = get_current_directory()
  base_path = os.path.join(current_directory, 'base')
  package_include_path= os.path.join(current_directory, r'package\include')
  list_dirs = os.walk(base_path,topdown=True)
  for root,dirs,files, in list_dirs:
    for f in files:
      file_ext = os.path.splitext(f)[1]
      if file_ext == '.h':
        full_file_path = os.path.join(root,f)
        relative_path = os.path.relpath(full_file_path, current_directory)
        dst_path = os.path.join(package_include_path,relative_path)
        if not os.path.exists(os.path.dirname(dst_path)):
          os.makedirs(os.path.dirname(dst_path))
        shutil.copy(full_file_path, dst_path)

def collect_bin_files():
  '''collect dll,lib,pdb'''

  files = [
    {"from":r"debug_shared\base.dll","to":r"bin\win32\debug\base.dll"},
    {"from":r"debug_shared\base.dll.lib","to":r"lib\win32\debug\\base.dll.lib"},
    {"from":r"debug_shared\base.dll.pdb","to":r"symbol\win32\debug\base.dll.pdb"},
    {"from":r"release_shared\base.dll","to":r"bin\win32\release\base.dll"},
    {"from":r"release_shared\base.dll.lib","to":r"lib\win32\release\base.dll.lib"},
    {"from":r"release_shared\base.dll.pdb","to":r"symbol\win32\release\base.dll.pdb"},
    {"from":r"debug_static\obj\base\base.lib","to":r"lib\win32\debug\base.lib"},
    {"from":r"release_static\obj\base\base.lib","to":r"lib\win32\release\base.lib"}
  ]
  current_directory = get_current_directory()
  out_directory = os.path.join(current_directory, 'out')
  package_directory= os.path.join(current_directory, r'package')
  for f in files:
    from_path = os.path.join(out_directory, f['from'])
    to_path = os.path.join(package_directory, f['to'])
    if not os.path.exists(os.path.dirname(to_path)):
      os.makedirs(os.path.dirname(to_path))
    shutil.copy(from_path, to_path)

def package_project():
  '''gen,build,package'''

  gen_project()
  build_project('all')
  collect_head_files()
  collect_bin_files()

  current_directory = get_current_directory()
  zip_file_path = os.path.join(current_directory, 'package.zip')
  if os.path.exists(zip_file_path):
    os.remove(zip_file_path)
  zip_directory = os.path.join(current_directory, 'package')
  if not os.path.exists(zip_directory):
    logging.error("package path %s not exists!" % zip_directory)
    return
  shutil.make_archive(zip_directory, 'zip', zip_directory)

def main(args):
  parser = argparse.ArgumentParser(description='help tool.')
  mode_group = parser.add_mutually_exclusive_group()
  mode_group.add_argument('-c', '--copy', metavar='PATH', help='copy buildtools from chromium src directory to current directory.')
  mode_group.add_argument('-z', '--zip', metavar='PATH', help='zip buildtools from chromium src directory to current directory.')
  mode_group.add_argument('-g', '--gen', action='store_true', help='generate {release_static,debug_static, release_shared, debug_shared} projects.')
  mode_group.add_argument('-b', '--build', choices=['all', 'release', 'static','shared','release_static', 'debug_static', 'release_shared', 'debug_shared'], help='build project')
  mode_group.add_argument('-p', '--package', action='store_true', help='package all.')
  parser.add_argument('-l', '--log', action='store_true',help='show log infomation.')
  args = parser.parse_args()

  log_level = None
  if args.log:
    log_level = logging.INFO
  logging_format = '[%(filename)s:%(lineno)d] %(message)s'
  logging.basicConfig(format=logging_format, level=log_level)

  if not (args.copy or args.zip or args.gen or args.build or args.package):
    parser.print_help()
  if args.copy:
    current_directory = get_current_directory()
    copy_buildtools(current_directory, args.copy)
    return
  if args.zip:
    current_directory = get_current_directory()
    zip_buildtools(current_directory, args.zip)
    return
  if args.gen:
    gen_project()
    return
  if args.build:
    build_project(args.build)
    return
  if args.package:
    package_project()
    return

if __name__ == '__main__':
  sys.exit(main(sys.argv))



