import os
import sys
import configargparse
import compiletools.test_base as tb

from importlib import reload

import compiletools.dirnamer
import compiletools.headerdeps
import compiletools.apptools
import compiletools.testhelper as uth


def _make_cppflags_path(relative_path):
    """Helper to construct path within cppflags_macros sample directory."""
    return os.path.join(uth.samplesdir(), "cppflags_macros", relative_path)


def _make_cppflags_paths(relative_paths):
    """Helper to construct multiple paths within cppflags_macros sample directory."""
    return {_make_cppflags_path(path) for path in relative_paths}


def _assert_headers_present(result_set, expected_headers):
    """Assert that all expected headers are present in result set."""
    expected_paths = _make_cppflags_paths(expected_headers)
    assert expected_paths <= result_set, f"Missing headers: {expected_paths - result_set}"


def _assert_headers_absent(result_set, forbidden_headers):
    """Assert that none of the forbidden headers are present in result set."""
    forbidden_paths = _make_cppflags_paths(forbidden_headers)
    intersection = forbidden_paths & result_set
    assert not intersection, f"Unexpected headers found: {intersection}"


def _clean_cppflags(cppflags):
    """Remove -I{samplesdir()} from cppflags since it's handled by --include parameter."""
    if not cppflags:
        return None
    # Remove the include path part since --include handles it
    include_pattern = f"-I{uth.samplesdir()}"
    cleaned = cppflags.replace(include_pattern, "").strip()
    return cleaned if cleaned else None


def _run_scenario_test(filename, scenarios):
    """Helper to run multiple cppflags scenarios and compare headerdeps kinds."""
    for name, cppflags in scenarios:
        cleaned_cppflags = _clean_cppflags(cppflags)
        uth.compare_headerdeps_kinds(filename, cppflags=cleaned_cppflags, scenario_name=name)


def _reload_ct_with_cache(cache_home):
    """ Set the CTCACHE environment variable to cache_home
        and reload the compiletools.hunter module
    """
    with uth.EnvironmentContext({"CTCACHE": cache_home}):
        reload(compiletools.dirnamer)
        reload(compiletools.headerdeps)
        return cache_home


def _callprocess(headerobj, filenames):
    result = []
    for filename in filenames:
        realpath = compiletools.wrappedos.realpath(filename)
        result.extend(headerobj.process(realpath, frozenset()))
    return compiletools.utils.ordered_unique(result)


def _generatecache(tempdir, name, realpaths, extraargs=None):
    if extraargs is None:
        extraargs = []
    
    # Save original cache state for proper cleanup
    origcache = compiletools.dirnamer.user_cache_dir()
    
    try:
        with uth.TempConfigContext(tempdir=tempdir) as temp_config_name:
            argv = [
                "--headerdeps",
                name,
                "--include",
                uth.ctdir(),
                "-c",
                temp_config_name,
            ] + extraargs
            cachename = os.path.join(tempdir, name)
            with uth.EnvironmentContext({"CTCACHE": cachename}):
                reload(compiletools.dirnamer)
                reload(compiletools.headerdeps)
            cap = configargparse.getArgumentParser()
            compiletools.headerdeps.add_arguments(cap)
            args = compiletools.apptools.parseargs(cap, argv)
            headerdeps = compiletools.headerdeps.create(args)
            return cachename, _callprocess(headerdeps, realpaths)
    finally:
        # Properly restore module state
        with uth.EnvironmentContext({"CTCACHE": origcache}):
            reload(compiletools.dirnamer)
            reload(compiletools.headerdeps)


class TestHeaderDepsModule(tb.BaseCompileToolsTestCase):
    def setup_method(self):
        super().setup_method()
        cap = configargparse.getArgumentParser(
            description="Configargparser in test code",
            formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
            args_for_setting_config_path=["-c", "--config"],
            ignore_unknown_config_file_keys=False,
        )
        compiletools.headerdeps.add_arguments(cap)


    @uth.requires_functional_compiler
    def test_direct_and_cpp_generate_same_results(self):
        filenames = [
            "factory/test_factory.cpp",
            "numbers/test_direct_include.cpp",
            "dottypaths/dottypaths.cpp",
            "calculator/main.cpp",
        ]
        for filename in filenames:
            tb.compare_direct_cpp_headers(self, self._get_sample_path(filename))

    def _direct_and_cpp_generate_same_results_ex(self, extraargs=None):
        """ Test that HeaderTree and HeaderDependencies give the same results.
            Rather than polluting the real ct cache, use temporary cache
            directories.
        """
        if extraargs is None:
            extraargs = []

        # Use context manager for temp dir lifecycle
        with uth.TempDirContextNoChange() as tempdir:
            samplesdir = uth.samplesdir()
            relativepaths = [
                "factory/test_factory.cpp",
                "numbers/test_direct_include.cpp",
                "simple/helloworld_c.c",
                "simple/helloworld_cpp.cpp",
                "simple/test_cflags.c",
                "calculator/main.cpp",
            ]
            realpaths = [os.path.join(samplesdir, filename) for filename in relativepaths]

            directcache, directresults = _generatecache(
                tempdir, "direct", realpaths, extraargs
            )
            cppcache, cppresults = _generatecache(
                tempdir, "cpp", realpaths, extraargs
            )

            # The key test: both HeaderDeps implementations should produce the same results
            assert set(directresults) == set(cppresults)
    @uth.requires_functional_compiler
    def test_direct_and_cpp_generate_same_results_ex(self):
        self._direct_and_cpp_generate_same_results_ex()

    @uth.requires_functional_compiler
    def test_conditional_includes(self):
        """Test that DirectHeaderDeps correctly handles conditional includes"""
        filename = self._get_sample_path("conditional_includes/main.cpp")
        tb.compare_direct_cpp_headers(self, filename)

    @uth.requires_functional_compiler
    def test_user_defined_feature_headers(self):
        """Test that DirectHeaderDeps correctly handles user-defined feature macros"""
        filename = self._get_sample_path("feature_headers/main.cpp")
        tb.compare_direct_cpp_headers(self, filename)
        result_set = uth.headerdeps_result(filename, "direct")
        expected = {
            self._get_sample_path("feature_headers/feature_config.h"),
            self._get_sample_path("feature_headers/database.h"),
            self._get_sample_path("feature_headers/logging.h"),
        }
        unexpected = {
            self._get_sample_path("feature_headers/graphics.h"),
            self._get_sample_path("feature_headers/networking.h"),
        }
        assert expected <= result_set
        assert not (unexpected & result_set)

    def test_cppflags_macro_extraction(self):
        filename = self._get_sample_path("cppflags_macros/main.cpp")
        result_set = uth.headerdeps_result(
            filename,
            "direct",
            cppflags=f"-I{uth.samplesdir()} -DENABLE_ADVANCED_FEATURES",
        )
        assert _make_cppflags_path("advanced_feature.hpp") in result_set

    def test_macro_extraction_from_all_flag_sources(self):
        filename = self._get_sample_path("cppflags_macros/multi_flag_test.cpp")
        result_set = uth.headerdeps_result(
            filename,
            "direct",
            cppflags=f"-I{uth.samplesdir()} -DFROM_CPPFLAGS -DFROM_CFLAGS -DFROM_CXXFLAGS",
        )
        expected_headers = ["cppflags_feature.hpp", "cflags_feature.hpp", "cxxflags_feature.hpp"]
        _assert_headers_present(result_set, expected_headers)

    @uth.requires_functional_compiler
    def test_compiler_builtin_macro_recognition(self):
        filename = self._get_sample_path("cppflags_macros/compiler_builtin_test.cpp")
        result_set = uth.headerdeps_result(
            filename,
            "direct"
        )
        import platform
        arch = platform.machine().lower()
        expected_headers = ["gcc_feature.hpp"]
        if sys.platform.startswith("linux"):
            expected_headers.append("linux_feature.hpp")
        if arch in ["x86_64", "amd64"]:
            expected_headers.append("x86_64_feature.hpp")
        elif arch.startswith("arm") and not ("64" in arch or arch.startswith("aarch")):
            expected_headers.append("arm_feature.hpp")
        elif arch.startswith("aarch") or (arch.startswith("arm") and "64" in arch):
            expected_headers.append("aarch64_feature.hpp")
        elif "riscv" in arch:
            expected_headers.append("riscv_feature.hpp")
        _assert_headers_present(result_set, expected_headers)

    def test_riscv_architecture_macro_recognition(self):
        filename = self._get_sample_path("cppflags_macros/compiler_builtin_test.cpp")
        result_set = uth.headerdeps_result(
            filename,
            "direct",
            cppflags="-D__riscv -D__riscv64__",
        )
        assert _make_cppflags_path("riscv_feature.hpp") in result_set

    def test_additional_compiler_macro_recognition(self):
        filename = self._get_sample_path("cppflags_macros/compiler_builtin_test.cpp")
        result_set = uth.headerdeps_result(
            filename,
            "direct",
            cppflags="-D_MSC_VER -D__INTEL_COMPILER -D__EMSCRIPTEN__ -D__ARMCC_VERSION",
        )
        expected_headers = ["msvc_feature.hpp", "intel_feature.hpp", "emscripten_feature.hpp", "armcc_feature.hpp"]
        _assert_headers_present(result_set, expected_headers)

    def test_elif_conditional_compilation_support(self):
        filename = self._get_sample_path("cppflags_macros/elif_test.cpp")
        result_set = uth.headerdeps_result(
            filename,
            "direct",
            cppflags="-DVERSION_2",
        )
        _assert_headers_present(result_set, ["version2_feature.hpp"])
        _assert_headers_absent(result_set, ["version1_feature.hpp", "version3_feature.hpp", "default_feature.hpp"])

    @uth.requires_functional_compiler
    def test_elif_matches_cpp_preprocessor(self):
        filename = self._get_sample_path("cppflags_macros/elif_test.cpp")
        scenarios = [
            ("VERSION_1_defined", f"-I{uth.samplesdir()} -DVERSION_1"),
            ("VERSION_2_defined", f"-I{uth.samplesdir()} -DVERSION_2"),
            ("VERSION_3_defined", f"-I{uth.samplesdir()} -DVERSION_3"),
            ("no_version_defined", f"-I{uth.samplesdir()}")
        ]
        _run_scenario_test(filename, scenarios)

    def test_advanced_preprocessor_features(self):
        filename = self._get_sample_path("cppflags_macros/advanced_preprocessor_test.cpp")
        result_set = uth.headerdeps_result(
            filename,
            "direct",
            cppflags="-DFEATURE_A -DALT_FORM_TEST",
        )
        expected_headers = ["version_ge_2_feature.hpp", "partial_features.hpp", "temp_defined.hpp", "alt_form_feature.hpp", "version_205_plus.hpp"]
        forbidden_headers = ["temp_still_defined.hpp", "combined_features.hpp"]
        _assert_headers_present(result_set, expected_headers)
        _assert_headers_absent(result_set, forbidden_headers)

    @uth.requires_functional_compiler
    def test_advanced_preprocessor_matches_cpp_preprocessor(self):
        filename = self._get_sample_path("cppflags_macros/advanced_preprocessor_test.cpp")
        scenarios = [
            ("FEATURE_A_and_ALT_FORM_TEST", f"-I{uth.samplesdir()} -DFEATURE_A -DALT_FORM_TEST"),
            ("FEATURE_A_and_FEATURE_B", f"-I{uth.samplesdir()} -DFEATURE_A -DFEATURE_B"),
            ("FEATURE_C_only", f"-I{uth.samplesdir()} -DFEATURE_C"),
            ("no_feature_macros", f"-I{uth.samplesdir()}")
        ]
        _run_scenario_test(filename, scenarios)

    @uth.requires_functional_compiler
    def test_multiply_nested_macros_with_complex_logic(self):
        filename = self._get_sample_path("cppflags_macros/nested_macros_test.cpp")
        scenarios = [
            ("level2_linux_threading_numa", f"-I{uth.samplesdir()} -DBUILD_CONFIG=2 -D__linux__ -DUSE_EPOLL=1 -DENABLE_THREADING -DTHREAD_COUNT=4 -DNUMA_SUPPORT=1"),
            ("level3_expert_mode_with_profiling", f"-I{uth.samplesdir()} -DBUILD_CONFIG=3 -DENABLE_EXPERT_MODE=1 -DCUSTOM_ALLOCATOR -DALLOCATOR_TYPE=2 -DMEMORY_TRACKING=1 -DLEAK_DETECTION=1 -DSTACK_TRACE=1 -DENABLE_PROFILING=1 -DPROFILING_LEVEL=3 -DMEMORY_PROFILING=1 -DCPU_PROFILING=1 -DCACHE_PROFILING=1"),
            ("level1_basic_only", f"-I{uth.samplesdir()} -DBUILD_CONFIG=1"),
        ]
        
        # Expected headers for each scenario
        scenario_expectations = {
            "level2_linux_threading_numa": {
                "expected": ["basic_feature.hpp", "advanced_feature.hpp", "linux_advanced.hpp", "linux_epoll_threading.hpp", "numa_threading.hpp"],
                "forbidden": []
            },
            "level3_expert_mode_with_profiling": {
                "expected": ["basic_feature.hpp", "advanced_feature.hpp", "expert_feature.hpp"], 
                "forbidden": []
            },
            "level1_basic_only": {
                "expected": ["basic_feature.hpp"],
                "forbidden": ["advanced_feature.hpp", "expert_feature.hpp"]
            }
        }
        
        for name, cppflags in scenarios:
            direct = uth.compare_headerdeps_kinds(filename, cppflags=cppflags, scenario_name=name)["direct"]
            expectations = scenario_expectations[name]
            _assert_headers_present(direct, expectations["expected"])
            _assert_headers_absent(direct, expectations["forbidden"])

    def test_include_flag_parsing(self):
        """Test that -I flags are parsed correctly with and without spaces"""
        test_cases = [
            ("-I /usr/include -I/opt/local/include", ["/usr/include", "/opt/local/include"]),
            ("-Isrc -I build/include", ["src", "build/include"]),
            ("-I src", ["src"]),
            ("-Isrc", ["src"]),
        ]
        
        for cppflags, expected_includes in test_cases:
            cap = configargparse.getArgumentParser()
            compiletools.headerdeps.add_arguments(cap)
            compiletools.apptools.add_common_arguments(cap)
            
            argv = [f"--CPPFLAGS={cppflags}", "-q"]
            args = compiletools.apptools.parseargs(cap, argv)
            
            deps = compiletools.headerdeps.DirectHeaderDeps(args)
            assert deps.includes == expected_includes, f"CPPFLAGS: {cppflags}, Expected: {expected_includes}, Got: {deps.includes}"

    def test_quoted_include_paths_shell_parsing_bug(self):
        """Test that exposes the shell parsing bug in HeaderDeps with quoted include paths.
        
        This test demonstrates that the current regex-based approach fails to handle
        quoted paths with spaces correctly, just like the MagicFlags bug that was fixed.
        
        The regex pattern r"-(?:I)(?:\\s+|)([^\\s]+)" stops at the first whitespace,
        breaking quoted paths that should be treated as single arguments.
        """
        
        # This is the critical test case that exposes the bug  
        expected_includes = ["/path with spaces/include"]
        
        cap = configargparse.getArgumentParser()
        compiletools.headerdeps.add_arguments(cap)
        compiletools.apptools.add_common_arguments(cap)
        
        # Bypass command line parsing issues by setting CPPFLAGS directly
        argv = ["-q"]
        args = compiletools.apptools.parseargs(cap, argv)
        
        # Set the CPPFLAGS with properly quoted string directly
        args.CPPFLAGS = '-I "/path with spaces/include"'
        
        deps = compiletools.headerdeps.DirectHeaderDeps(args)
        actual_includes = deps.includes
        
        # This assertion should now PASS after the shlex.split() fix
        assert actual_includes == expected_includes, \
            f"SHELL PARSING BUG STILL EXISTS in HeaderDeps!\n" \
            f"CPPFLAGS: {args.CPPFLAGS}\n" \
            f"Expected: {expected_includes} (quoted path treated as single argument)\n" \
            f"Got:      {actual_includes} (shlex parsing should handle this correctly)\n" \
            f"The shlex.split() fix should handle quoted paths with spaces correctly!"

    def test_isystem_flag_parsing(self):
        """Test that -isystem flags are parsed correctly with and without spaces"""
        test_cases = [
            "-isystem /usr/include -isystem/opt/local/include",
            "-isystemsrc -isystem build/include", 
            "-isystem src",
            "-isystemsrc",
        ]
        
        for cppflags in test_cases:
            cap = configargparse.getArgumentParser()
            compiletools.headerdeps.add_arguments(cap)
            compiletools.apptools.add_common_arguments(cap)
            
            argv = [f"--CPPFLAGS={cppflags}", "-q"]
            args = compiletools.apptools.parseargs(cap, argv)
            
            # This should not raise an exception - the isystem parsing should work
            compiletools.headerdeps.DirectHeaderDeps(args)


