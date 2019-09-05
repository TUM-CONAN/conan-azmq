#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile, CMake, tools
import os


class AZMQConan(ConanFile):
    name = "azmq"
    version = "1.0.3"
    url = "https://github.com/bincrafters/conan-azmq"
    homepage = "https://github.com/zeromq/azmq"
    description = "C++ language binding library integrating ZeroMQ with Boost Asio"
    license = "BSL-1.0"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"


    scm = {
         "type": "git",
         "subfolder": source_subfolder,
         "url": "https://github.com/zeromq/azmq.git",
         "revision": "6bb101eecb357ad9735ebc36e276b7526652d42d"
      }

    def requirements(self):
        self.requires.add('zmq/4.3.2@camposs/stable')
        self.requires.add('Boost/1.70.0@camposs/stable')

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.options["Boost"].shared == True:
          cmake.definitions["Boost_USE_STATIC_LIBS"] = 'OFF'
        cmake.configure(build_folder=self.build_subfolder)
        return cmake
                              
    def build(self):

        # ensure our FindBoost.cmake is being used
        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                              'set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/config")',
                              '#set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/config")')

        # disable tests, 1.0.2 doesn't have AZMQ_NO_TESTS yet...
        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                              'add_subdirectory(test)',
                              '#add_subdirectory(test)')
        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                              'add_subdirectory(doc)',
                              '#add_subdirectory(doc)')

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE-BOOST_1_0", dst='licenses', src=self.source_subfolder)

    def package_info(self):
        self.info.header_only()
