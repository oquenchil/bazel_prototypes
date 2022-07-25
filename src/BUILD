cc_library(
    name = "a",
    srcs = ["a.cc"],
    deps = [
        ":b",
        ":c",
    ],
)

cc_library(
    name = "b",
    srcs = ["b.cc"],
    hdrs = ["b.h"],
)

cc_library(
    name = "c",
    srcs = ["c.cc"],
    hdrs = ["c.h"],
)

sh_binary(
    name = "used_deps_script",
    srcs = ["used_deps_script.sh"],
    visibility = ["//visibility:public"],
)

sh_binary(
    name = "unused_deps_script",
    srcs = ["unused_deps_script.sh"],
    visibility = ["//visibility:public"],
)
