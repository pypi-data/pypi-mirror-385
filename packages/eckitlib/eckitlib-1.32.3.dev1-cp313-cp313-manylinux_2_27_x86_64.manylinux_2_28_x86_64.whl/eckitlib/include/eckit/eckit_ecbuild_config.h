/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef ECKIT_ecbuild_config_h
#define ECKIT_ecbuild_config_h

/* ecbuild info */

#ifndef ECBUILD_VERSION_STR
#define ECBUILD_VERSION_STR "3.12.0"
#endif
#ifndef ECBUILD_VERSION
#define ECBUILD_VERSION "3.12.0"
#endif
#ifndef ECBUILD_MACROS_DIR
#define ECBUILD_MACROS_DIR  "/src/ecbuild/cmake"
#endif

/* config info */

#define ECKIT_OS_NAME          "Linux-4.18.0-372.26.1.el8_6.x86_64"
#define ECKIT_OS_BITS          64
#define ECKIT_OS_BITS_STR      "64"
#define ECKIT_OS_STR           "linux.64"
#define ECKIT_OS_VERSION       "4.18.0-372.26.1.el8_6.x86_64"
#define ECKIT_SYS_PROCESSOR    "x86_64"

#define ECKIT_BUILD_TIMESTAMP  "20251018114104"
#define ECKIT_BUILD_TYPE       "RelWithDebInfo"

#define ECKIT_C_COMPILER_ID      "GNU"
#define ECKIT_C_COMPILER_VERSION "13.3.1"

#define ECKIT_CXX_COMPILER_ID      "GNU"
#define ECKIT_CXX_COMPILER_VERSION "13.3.1"

#define ECKIT_C_COMPILER       "/opt/rh/gcc-toolset-13/root/usr/bin/cc"
#define ECKIT_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define ECKIT_CXX_COMPILER     "/opt/rh/gcc-toolset-13/root/usr/bin/c++"
#define ECKIT_CXX_FLAGS        " -pipe -Wall -Wextra -Wno-unused-parameter -Wno-unused-variable -Wno-sign-compare -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define ECKIT_INSTALL_DIR       "/tmp/eckit/target/eckit"
#define ECKIT_INSTALL_BIN_DIR   "/tmp/eckit/target/eckit/bin"
#define ECKIT_INSTALL_LIB_DIR   "/tmp/eckit/target/eckit/lib64"
#define ECKIT_INSTALL_DATA_DIR  "/tmp/eckit/target/eckit/share/eckit"

#define ECKIT_DEVELOPER_SRC_DIR "/src/eckit"
#define ECKIT_DEVELOPER_BIN_DIR "/tmp/eckit/build"

/* Fortran support */

#if 0

#define ECKIT_Fortran_COMPILER_ID      ""
#define ECKIT_Fortran_COMPILER_VERSION ""

#define ECKIT_Fortran_COMPILER "/opt/intel/oneapi/compiler/latest/bin/ifx"
#define ECKIT_Fortran_FLAGS    ""

#endif

#endif /* ECKIT_ecbuild_config_h */
