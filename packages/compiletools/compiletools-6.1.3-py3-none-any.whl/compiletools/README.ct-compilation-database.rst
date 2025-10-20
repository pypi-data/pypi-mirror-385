=========================
ct-compilation-database
=========================

--------------------------------------------------------------------------------
Generate compile_commands.json for clang tooling and IDE integration
--------------------------------------------------------------------------------

:Author: drgeoffathome@gmail.com
:Date:   2025-10-08
:Copyright: Copyright (C) 2011-2025 Zomojo Pty Ltd
:Version: 6.1.3
:Manual section: 1
:Manual group: developers

SYNOPSIS
========
ct-compilation-database [-h] [-c CONFIG_FILE] [--variant VARIANT] [-v] [-q]
                        [--version] [--compilation-database-output OUTPUT]
                        [--relative-paths]
                        [filename ...]

DESCRIPTION
===========
ct-compilation-database generates a compilation database (compile_commands.json)
for C/C++ projects. This JSON file contains the exact compiler commands used to
build each source file, enabling integration with modern development tools.

The compilation database format is used by:

* **Language servers**: clangd, ccls for IDE features (autocomplete, go-to-definition)
* **Static analyzers**: clang-tidy, clang-format, cppcheck
* **Code indexers**: rtags, ycmd
* **Refactoring tools**: clang-rename, clang-include-fixer

ct-compilation-database is automatically invoked by ct-cake when building projects.
You can also run it standalone to regenerate the compilation database without
rebuilding.

The tool uses the same dependency analysis as ct-cake to ensure the compilation
database reflects the actual build configuration, including:

* Automatic detection of source files
* Magic flags from source comments
* Variant-specific compiler settings
* Include paths and preprocessor definitions

OUTPUT FORMAT
=============
The generated compile_commands.json follows the JSON Compilation Database
specification. Each entry contains:

.. code-block:: json

    {
      "directory": "/path/to/project",
      "command": "g++ -std=c++11 -Wall -c main.cpp",
      "file": "main.cpp"
    }

OPTIONS
=======
--compilation-database-output OUTPUT
    Output filename for compilation database.
    Default: <gitroot>/compile_commands.json

--relative-paths
    Use relative paths instead of absolute paths in the database.
    Useful for portable compilation databases.

EXAMPLES
========

Generate compilation database for current project::

    ct-compilation-database

Generate with specific output location::

    ct-compilation-database --compilation-database-output build/compile_commands.json

Generate with relative paths for portability::

    ct-compilation-database --relative-paths

Generate for specific source files (disables auto-detection)::

    ct-compilation-database --no-auto src/main.cpp src/utils.cpp

INTEGRATION WITH ct-cake
=========================
ct-cake automatically generates compile_commands.json by default. To control this
behavior, use these flags:

--compilation-database / --no-compilation-database
    Enable or disable automatic generation (default: enabled)

--compilation-database-output OUTPUT
    Customize output location

--compilation-database-relative-paths
    Use relative paths

Example ct-cake usage::

    ct-cake --no-compilation-database    # Disable generation
    ct-cake --compilation-database-output .compile_db.json

CLANGD CONFIGURATION
====================
For best results with clangd, create a .clangd config file in your project root:

.. code-block:: yaml

    CompileFlags:
      CompilationDatabase: .

This tells clangd to use the compile_commands.json in the project root.

SEE ALSO
========
``compiletools`` (1), ``ct-cake`` (1), ``ct-config`` (1)

REFERENCES
==========
* JSON Compilation Database: https://clang.llvm.org/docs/JSONCompilationDatabase.html
* clangd: https://clangd.llvm.org/
