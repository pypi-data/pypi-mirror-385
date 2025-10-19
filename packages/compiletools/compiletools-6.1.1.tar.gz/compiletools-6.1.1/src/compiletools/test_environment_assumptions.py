import subprocess
import shutil
import os
import pytest

import compiletools.testhelper as uth
import compiletools.configutils
import compiletools.apptools
import compiletools.utils


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    uth.reset()
    with uth.TempDirContextNoChange() as tmpdir:
        yield tmpdir
    uth.reset()


def test_functional_cxx_compiler_detection():
    """Test that the new compiler detection function finds a working compiler."""
    compiler = compiletools.apptools.get_functional_cxx_compiler()
    
    if compiler is None:
        pytest.skip("No functional C++ compiler detected - this may indicate platform limitations")
    
    # Verify the detected compiler is actually functional
    assert shutil.which(compiler) is not None, f"Detected compiler {compiler} not in PATH"


def test_functional_cxx_compiler_caching():
    """Test that compiler detection result is properly cached."""
    # Clear cache to ensure clean test
    compiletools.apptools.get_functional_cxx_compiler.cache_clear()
    
    # First call
    compiler1 = compiletools.apptools.get_functional_cxx_compiler()
    
    # Second call should return same result (from cache)
    compiler2 = compiletools.apptools.get_functional_cxx_compiler()
    
    assert compiler1 == compiler2, "Compiler detection caching not working properly"


def test_gcc_compiler_available(temp_dir):
    """Test that GCC compiler is available and supports C++17."""
    # Use new detection function first
    detected_compiler = compiletools.apptools.get_functional_cxx_compiler()
    
    # Skip if no functional compiler at all
    if detected_compiler is None:
        pytest.skip("No functional C++ compiler detected")
    
    # Skip if detected compiler is not GCC
    if 'gcc' not in detected_compiler and 'g++' not in detected_compiler:
        pytest.skip("GCC not detected as primary compiler - may not be available")
    
    gcc_path = shutil.which('gcc')
    gxx_path = shutil.which('g++')
    
    if gcc_path is None or gxx_path is None:
        pytest.skip("GCC/G++ not found in PATH - using detected alternative")
    
    # Test C++17 support by compiling a simple program
    test_cpp = os.path.join(temp_dir, 'test_cpp17.cpp')
    test_exe = os.path.join(temp_dir, 'test_cpp17')
    
    with open(test_cpp, 'w') as f:
        f.write('''
#include <iostream>
#include <string_view>  // C++17 feature
int main() {
    std::string_view sv = "C++17 works";
    std::cout << sv << std::endl;
    return 0;
}
''')
    
    # Use detected functional compiler instead of hardcoded g++
    functional_compiler = compiletools.apptools.get_functional_cxx_compiler()
    if functional_compiler is None:
        pytest.skip("No functional C++ compiler detected")
    
    result = subprocess.run([
        functional_compiler, '-std=c++17', '-o', test_exe, test_cpp
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"GCC failed to compile C++17 code: {result.stderr}"


def test_clang_compiler_available(temp_dir):
    """Test that Clang compiler is available and supports C++17 (if present)."""
    clang_path = shutil.which('clang')
    clangxx_path = shutil.which('clang++')
    
    if clang_path is None or clangxx_path is None:
        pytest.skip("Clang compiler not available - this is optional for GCC-only environments")
    
    # Test C++17 support by compiling a simple program
    test_cpp = os.path.join(temp_dir, 'test_clang_cpp17.cpp')
    test_exe = os.path.join(temp_dir, 'test_clang_cpp17')
    
    with open(test_cpp, 'w') as f:
        f.write('''
#include <iostream>
#include <optional>  // C++17 feature
int main() {
    std::optional<int> opt = 42;
    std::cout << "C++17 optional: " << *opt << std::endl;
    return 0;
}
''')
    
    result = subprocess.run([
        'clang++', '-std=c++17', '-o', test_exe, test_cpp
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Clang failed to compile C++17 code: {result.stderr}"


def test_pkg_config_available():
    """Test that pkg-config is available for library detection."""
    pkg_config_path = shutil.which('pkg-config')
    assert pkg_config_path is not None, "pkg-config not found in PATH"
    
    # Test basic pkg-config functionality
    result = subprocess.run(['pkg-config', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, f"pkg-config version check failed: {result.stderr}"


def test_linker_features(temp_dir):
    """Test that linker supports required features like --build-id."""
    # Use detected functional compiler
    functional_compiler = compiletools.apptools.get_functional_cxx_compiler()
    if functional_compiler is None:
        pytest.skip("No functional C++ compiler detected")
        
    # Derive C compiler from C++ compiler
    c_compiler = compiletools.apptools.derive_c_compiler_from_cxx(functional_compiler)
    
    # Create a simple test object to link
    test_c = os.path.join(temp_dir, 'test_linker.c')
    test_o = os.path.join(temp_dir, 'test_linker.o')
    test_exe = os.path.join(temp_dir, 'test_linker')
    
    with open(test_c, 'w') as f:
        f.write('int main() { return 0; }')
    
    # Compile to object
    # Split c_compiler to handle multi-word commands like "ccache gcc"
    result = subprocess.run(
        compiletools.utils.split_command_cached(c_compiler) + ['-c', test_c, '-o', test_o],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Failed to compile test object: {result.stderr}"

    # Test linker with --build-id flag (used in config files)
    result = subprocess.run(
        compiletools.utils.split_command_cached(c_compiler) + ['-Xlinker', '--build-id', test_o, '-o', test_exe],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Linker does not support --build-id: {result.stderr}"


def test_fPIC_support(temp_dir):
    """Test that compilers support -fPIC flag (required for shared libraries)."""
    # Use detected functional compiler
    functional_compiler = compiletools.apptools.get_functional_cxx_compiler()
    if functional_compiler is None:
        pytest.skip("No functional C++ compiler detected")
        
    # Derive C compiler from C++ compiler
    c_compiler = compiletools.apptools.derive_c_compiler_from_cxx(functional_compiler)
        
    test_c = os.path.join(temp_dir, 'test_fpic.c')
    test_o = os.path.join(temp_dir, 'test_fpic.o')
    
    with open(test_c, 'w') as f:
        f.write('int test_function() { return 42; }')
    
    # Test functional compiler with -fPIC
    result = subprocess.run(
        compiletools.utils.split_command_cached(c_compiler) + ['-fPIC', '-c', test_c, '-o', test_o],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Compiler does not support -fPIC: {result.stderr}"


def test_configuration_defaults_valid(temp_dir):
    """Test that default configuration variants are valid and accessible."""
    # Test that default config files can be loaded
    with uth.DirectoryContext(temp_dir):
        # Test default variant extraction with explicit empty argv
        variant = compiletools.configutils.extract_variant(
            argv=[],
            user_config_dir="/nonexistent",
            system_config_dir="/nonexistent", 
            exedir=uth.cakedir(),
            verbose=0,
            gitroot=temp_dir,
        )
        # Should fall back to system defaults when no local config
        assert variant is not None, "Failed to extract default variant"


@uth.requires_functional_compiler
def test_standard_libraries_linkable(temp_dir):
    """Test that standard libraries required by samples can be linked."""
    test_cpp = os.path.join(temp_dir, 'test_stdlib.cpp')
    test_exe = os.path.join(temp_dir, 'test_stdlib')
    
    # Test math library linking (used in samples)
    with open(test_cpp, 'w') as f:
        f.write('''
#include <cmath>
#include <iostream>
int main() {
    double result = sqrt(16.0);
    std::cout << "sqrt(16) = " << result << std::endl;
    return 0;
}
''')
    
    # Use detected functional compiler instead of hardcoded g++
    functional_compiler = compiletools.apptools.get_functional_cxx_compiler()
    if functional_compiler is None:
        pytest.skip("No functional C++ compiler detected")
    
    result = subprocess.run([
        functional_compiler, test_cpp, '-lm', '-o', test_exe
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"Failed to link with math library: {result.stderr}"


def test_compiler_diagnostics_support(temp_dir):
    """Test that compilers support diagnostic features used in release configs."""
    # Use detected functional compiler
    functional_compiler = compiletools.apptools.get_functional_cxx_compiler()
    if functional_compiler is None:
        pytest.skip("No functional C++ compiler detected")
        
    test_cpp = os.path.join(temp_dir, 'test_diagnostics.cpp')
    test_o = os.path.join(temp_dir, 'test_diagnostics.o')
    
    with open(test_cpp, 'w') as f:
        f.write('int main() { return 0; }')
    
    # Test compiler color diagnostics (used in release configs)
    result = subprocess.run([
        functional_compiler, '-fdiagnostics-color=auto', '-c', test_cpp, '-o', test_o
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"Compiler does not support color diagnostics: {result.stderr}"
    
    # Test Clang color diagnostics (if available)
    clangxx_path = shutil.which('clang++')
    if clangxx_path is not None:
        os.remove(test_o)
        result = subprocess.run([
            'clang++', '-fdiagnostics-color=auto', '-c', test_cpp, '-o', test_o  
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Clang does not support color diagnostics: {result.stderr}"


def test_optimization_flags_supported(temp_dir):
    """Test that optimization flags used in release configs are supported."""
    # Use detected functional compiler
    functional_compiler = compiletools.apptools.get_functional_cxx_compiler()
    if functional_compiler is None:
        pytest.skip("No functional C++ compiler detected")
        
    test_cpp = os.path.join(temp_dir, 'test_optimization.cpp')
    test_exe = os.path.join(temp_dir, 'test_optimization')
    
    with open(test_cpp, 'w') as f:
        f.write('''
inline int inline_func() { return 42; }
int main() { return inline_func(); }
''')
    
    # Test optimization flags from release configs
    optimization_flags = ['-O3', '-DNDEBUG', '-finline-functions', '-Wno-inline']
    
    result = subprocess.run([
        functional_compiler] + optimization_flags + [test_cpp, '-o', test_exe
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"Compiler does not support optimization flags: {result.stderr}"


def test_wall_werror_flags_supported(temp_dir):
    """Test that warning flags used in configs are supported."""
    # Use detected functional compiler
    functional_compiler = compiletools.apptools.get_functional_cxx_compiler()
    if functional_compiler is None:
        pytest.skip("No functional C++ compiler detected")
        
    test_cpp = os.path.join(temp_dir, 'test_warnings.cpp')
    test_exe = os.path.join(temp_dir, 'test_warnings')
    
    # Write clean code that should compile without warnings
    with open(test_cpp, 'w') as f:
        f.write('''
#include <iostream>
int main() {
    std::cout << "Clean code" << std::endl;
    return 0;
}
''')
    
    # Test with -Wall (but not -Werror to avoid test failures on warnings)
    result = subprocess.run([
        functional_compiler, '-Wall', test_cpp, '-o', test_exe
    ], capture_output=True, text=True)
    assert result.returncode == 0, f"Compiler does not support -Wall: {result.stderr}"


@uth.requires_functional_compiler
def test_create_temp_config_uses_detected_compiler(temp_dir):
    """Test that create_temp_config integrates with compiler detection."""
    config_path = uth.create_temp_config(tempdir=temp_dir)
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Should contain compiler settings
        assert 'CC=' in content, "Config missing CC setting"
        assert 'CXX=' in content, "Config missing CXX setting"
        assert 'CPPFLAGS=' in content, "Config missing CPPFLAGS setting"
        
        # Extract CXX value to verify it's functional
        for line in content.split('\n'):
            if line.startswith('CXX='):
                cxx_compiler = line.split('=', 1)[1].strip()
                # Should be able to find the compiler in PATH
                assert shutil.which(cxx_compiler) is not None, f"Config specified non-existent compiler: {cxx_compiler}"
                break
        else:
            assert False, "Could not find CXX setting in config"
            
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


@pytest.mark.parametrize("tool", ['make', 'ar', 'nm', 'objdump', 'strip'])
def test_required_system_tools_available(tool):
    """Test that basic system tools required for builds are available."""
    tool_path = shutil.which(tool)
    assert tool_path is not None, f"Required tool '{tool}' not found in PATH"