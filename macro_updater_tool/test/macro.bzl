def macro(name, the_deps):
    native.cc_library(name = name, deps = the_deps)
