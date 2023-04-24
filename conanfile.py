#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import load, update_conandata, copy, replace_in_file
import os


class AZMQConan(ConanFile):
    name = "azmq"
    version = "1.0.3"
    url = "https://github.com/TUM-CONAN/conan-azmq"
    homepage = "https://github.com/zeromq/azmq"
    description = "C++ language binding library integrating ZeroMQ with Boost Asio"
    license = "BSL-1.0"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires('zeromq/4.3.4')
        self.requires('boost/1.81.0')

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "6bb101eecb357ad9735ebc36e276b7526652d42d",
            "url": "https://github.com/zeromq/azmq.git"
        }})

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder)
        git.checkout(commit=sources["commit"])

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        if self.dependencies["boost"].options.shared:
            tc.preprocessor_definitions["Boost_USE_STATIC_LIBS"] = 'OFF'

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_folder")

    def build(self):

        # ensure our FindBoost.cmake is being used
        # tools.replace_in_file(os.path.join(self.source_folder, 'CMakeLists.txt'),
        #                       'set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/config")',
        #                       '#set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/config")')

        # disable tests, 1.0.2 doesn't have AZMQ_NO_TESTS yet...
        replace_in_file(self, os.path.join(self.source_folder, 'CMakeLists.txt'),
                              'add_subdirectory(test)',
                              '#add_subdirectory(test)')
        replace_in_file(self, os.path.join(self.source_folder, 'CMakeLists.txt'),
                              'add_subdirectory(doc)',
                              '#add_subdirectory(doc)')

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="BOOST_1_0", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []