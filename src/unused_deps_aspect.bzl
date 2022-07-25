MNEMONICS = ["CppCompile"]

def _unused_deps_aspect_impl(target, ctx):
    # ----Beginning of what could be native to Bazel----
    # Instead of this loop we could have the functionality implemented
    # natively by Bazel. Each action could output the list of files that were
    # used by using something like inotifywait.
    used_deps_output = None
    for action in target.actions:
        if action.mnemonic not in MNEMONICS:
            continue

        used_deps_output = ctx.actions.declare_file(ctx.label.name + "_used_deps_output.txt")

        ctx.actions.run(
            mnemonic = action.mnemonic + "UsedDepsWatch",
            inputs = action.inputs,
            outputs = [used_deps_output],
            arguments = [used_deps_output.path] + action.argv,
            executable = ctx.executable._used_deps_script,
            shadowed_action = action,
        )

    # ---end of native bazel-------

    # ----- Beginning of C++ specific code--------
    # Processing of files to figure out the unused deps. This code should not
    # be in Java. It's specific to each language. This example deals with C++.
    # In general it doesn't make sense to use this for C++ as it would be
    # better to use the .d file instead.
    important_files_from_deps_map = []
    for dep in ctx.rule.attr.deps:
        if CcInfo in dep:
            # We could just look at every input to the compilation action but if
            # we look at the inputs we will see files like the runtime middlemen
            # and not the real file.
            for direct_hdr in dep[CcInfo].compilation_context.direct_headers:
                important_files_from_deps_map.append(str(dep.label) + "," + direct_hdr.path)

    important_files_from_deps_map_output = ctx.actions.declare_file(ctx.label.name + "_important_files_maps.txt")
    ctx.actions.write(important_files_from_deps_map_output, "\n".join(important_files_from_deps_map) + "\n")

    # This is missing logic specific to C++, for example logic necessary not to remove cc_library targets
    # that only contain one object file (no header files) and have alwayslink=1.

    # ---------- End of C++ specific code -----------------

    # ----Code that could be generally useful -------"
    buildozer_commands_output = ctx.actions.declare_file(ctx.label.name + "_buildozer_commands.txt")
    ctx.actions.run(
        mnemonic = "BuildozerCommandWriter",
        inputs = depset([important_files_from_deps_map_output, used_deps_output]),
        outputs = [buildozer_commands_output],
        arguments = [str(target.label), buildozer_commands_output.path, important_files_from_deps_map_output.path, used_deps_output.path],
        executable = ctx.executable._unused_deps_script,
    )
    # ----end of generally useful code -------"

    return [OutputGroupInfo(unused_deps = depset([buildozer_commands_output]))]

unused_deps_aspect = aspect(
    # No propagation. Just the target it is applied on.
    attrs = {
        "_unused_deps_script": attr.label(
            executable = True,
            cfg = "exec",
            default = "//src:unused_deps_script",
        ),
        "_used_deps_script": attr.label(
            executable = True,
            cfg = "exec",
            default = "//src:used_deps_script",
        ),
    },
    implementation = _unused_deps_aspect_impl,
)
