load(":macro.bzl", "macro")

cc_binary(
    name = "main",
    deps = ["foo"],
)

cc_library(
    name = "foo",
    deps = ["bar"],
)

macro(
    name = "bar",
    the_deps = ["//test:baz"],
)

cc_library(
    name = "baz",
)

filegroup(
    name = "qux",
    srcs = [],
)
