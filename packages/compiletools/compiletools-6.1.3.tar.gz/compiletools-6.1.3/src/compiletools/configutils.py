import sys
import os
import ast
import appdirs
from functools import lru_cache

# Work around an incompatibility between configargparse 0.10 and 0.11
try:
    from configargparse import DefaultConfigFileParser as CfgFileParser
except ImportError:
    from configargparse import ConfigFileParser as CfgFileParser

import compiletools.wrappedos
import compiletools.utils
import compiletools.git_utils


def extract_value_from_argv(key, argv=None, default=None, verbose=0):
    """ Extract the value for the given key from the argv.
        Return the given default if no key was identified
    """
    if argv is None:
        argv = sys.argv

    value = default

    hyphens = ("-", "--")
    for hh in hyphens:
        for arg in argv:
            try:
                keywithhyphens = "".join([hh, key, "="])
                if arg.startswith(keywithhyphens):
                    value = arg.split("=")[1]
                else:
                    keywithhyphens = "".join([hh, key])
                    if arg.startswith(keywithhyphens):
                        index = argv.index(keywithhyphens)
                        if index + 1 < len(argv):
                            value = argv[index + 1]
            except ValueError:
                pass

    if verbose >= 4:
        msg = "argv extraction: " + key + " "
        if value:
            msg += str(value)
        print(msg)
    return value


def extract_item_from_ct_conf(
    key,
    user_config_dir=None,
    system_config_dir=None,
    exedir=None,
    default=None,
    verbose=0,
    gitroot=None,
):
    """ Extract the value for the given key from the ct.conf files.
        Return the given default if no key was identified
    """
    fileparser = CfgFileParser()
    for cfgpath in reversed(
        get_existing_config_files(
            filename="ct.conf",
            user_config_dir=user_config_dir,
            system_config_dir=system_config_dir,
            exedir=exedir,
            gitroot=gitroot,
        )
    ):
        with open(cfgpath) as cfg:
            items = fileparser.parse(cfg)
            try:
                value = items[key]
                if verbose >= 2:
                    print(" ".join([cfgpath, "contains", key, "=", value]))
                return value
            except KeyError:
                continue

    return default


def removedotconf(config):
    if config[-5:] == ".conf":
        return config[:-5]
    else:
        return config


def extractconfig(argv):
    config = None
    config = extract_value_from_argv(key="config", argv=argv, default=None)

    if not config:
        config = extract_value_from_argv(key="c", argv=argv, default=None)
    return config


def impliedvariant(argv):
    """ If the user specified a config directly then we imply the variant name """
    config = extractconfig(argv)

    if config:
        return removedotconf(os.path.basename(config))
    else:
        return None


def extract_variant(
    argv=None, user_config_dir=None, system_config_dir=None, exedir=None, verbose=0, gitroot=None
):
    """ The variant argument is parsed directly from the command line arguments
        so that it can be used to specify the default config for configargparse.
        The ct.conf files are also checked.
        Remember that the hierarchy of values is
        command line > environment variables > config file values > defaults
        If the user specified a config directly (rather than a variant) then
        return the implied variant.
    """
    if argv is None:
        argv = sys.argv

    # If the user specified a config directly then we imply the variant name
    implied = impliedvariant(argv)
    if implied:
        if verbose >= 1:
            print("Using implied variant from directly specified config")
        return implied

    # Parse the command line, et al, extract the variant the user wants,
    # then use that as the default config file for configargparse.
    # Be careful to make use of the variant aliases defined in the ct.conf files
    variantaliases = extract_item_from_ct_conf(
        key="variantaliases",
        user_config_dir=user_config_dir,
        system_config_dir=system_config_dir,
        exedir=exedir,
        verbose=verbose,
        gitroot=gitroot,
    )
    if variantaliases is None:
        variantaliases = {}
    else:
        variantaliases = ast.literal_eval(variantaliases)

    variant = "debug"
    variant = extract_item_from_ct_conf(
        key="variant",
        user_config_dir=user_config_dir,
        system_config_dir=system_config_dir,
        exedir=exedir,
        default=variant,
        verbose=verbose,
        gitroot=gitroot,
    )
    try:
        variant = os.environ["variant"]
    except KeyError:
        pass
    variant = extract_value_from_argv(key="variant", argv=argv, default=variant)

    try:
        result = variantaliases[variant]
    except KeyError:
        result = variant

    if verbose >= 4:
        print("Extract variant: " + result)

    return result


@lru_cache(maxsize=None)
def default_config_directories(
    user_config_dir=None, system_config_dir=None, exedir=None, repoonly=False, verbose=0, gitroot=None, current_dir=None
):
    # Use configuration in the order (lowest to highest priority)
    # If repoonly is true, start the procedure at step 4
    # 1) same path as exe,
    # 2) system config (XDG compliant.  /etc/xdg/ct)
    # 2b)   python virtual environment system configs (${python-site-packages}/etc/xdg/ct/ct.conf.d)
    # 3) user config   (XDG compliant. ~/.config/ct)
    # 4) repoconfig (usually <gitroot>/ct.conf.d TODO:make this configurable)
    # 5) gitroot
    # 6) current working directory
    # 7) environment variables
    # 8) given on the command line

    # These variables are settable to assist writing tests
    if user_config_dir is None:
        user_config_dir = appdirs.user_config_dir(appname="ct")

    system_dirs = []
    if system_config_dir is not None:
        system_dirs.append(system_config_dir)
    else:
        # Add package's bundled config directory (step 2b - highest priority among system configs)
        package_config_dir = os.path.join(os.path.dirname(__file__), "ct.conf.d")
        if compiletools.wrappedos.isdir(package_config_dir):
            system_dirs.append(package_config_dir)

        for python_config_dir in sys.path[::-1]:
            trialpath = os.path.join(python_config_dir, "ct", "ct.conf.d")
            if compiletools.wrappedos.isdir(trialpath) and trialpath not in system_dirs:
                system_dirs.append(trialpath)
        system_dirs.append(appdirs.site_config_dir(appname="ct"))

    if exedir is None:
        exedir = compiletools.wrappedos.dirname(compiletools.wrappedos.realpath(sys.argv[0]))

    executable_config_dir = os.path.join(exedir, "ct", "ct.conf.d")
    if current_dir is None:
        current_dir = os.getcwd()
    if gitroot is None:
        gitroot = compiletools.git_utils.find_git_root()
    results = [current_dir, gitroot]
    
    # Add config directories that actually exist
    project_config_dir = os.path.join(gitroot, "ct.conf.d")
    if compiletools.wrappedos.isdir(project_config_dir):
        results.append(project_config_dir)
    
    repo_config_dir = os.path.join(gitroot, "src", "compiletools", "ct.conf.d")
    if compiletools.wrappedos.isdir(repo_config_dir):
        results.append(repo_config_dir)
    if not repoonly:
        results.extend([user_config_dir] + system_dirs + [executable_config_dir])
    results = compiletools.utils.ordered_unique(results)
    if verbose >= 9:
        print(" ".join(["Default config directories"] + list(results)))

    return results


def get_existing_config_files(filename="ct.conf", **kwargs):
    """Get list of existing config files in standard directories"""
    # Always resolve current_dir explicitly for proper caching
    if 'current_dir' not in kwargs or kwargs['current_dir'] is None:
        kwargs['current_dir'] = os.getcwd()
    directories = default_config_directories(**kwargs)
    
    configs = [
        os.path.join(directory, filename) 
        for directory in reversed(directories)
    ]
    
    # Only return files that actually exist
    existing_configs = [cfg for cfg in configs if compiletools.wrappedos.isfile(cfg)]
    
    if kwargs.get('verbose', 0) >= 8:
        print(" ".join(["Existing config files:"] + existing_configs))
    
    return existing_configs


def clear_cache():
    """Clear LRU caches for testing"""
    default_config_directories.cache_clear()


def config_files_from_variant(
    variant=None,
    argv=None,
    user_config_dir=None,
    system_config_dir=None,
    exedir=None,
    verbose=0,
    gitroot=None,
):
    if variant is None:
        variant = extract_variant(
            argv,
            user_config_dir=user_config_dir,
            system_config_dir=system_config_dir,
            exedir=exedir,
            verbose=verbose,
            gitroot=gitroot,
        )

    # Start with the default ct.conf files
    variantconfigs = get_existing_config_files(
        filename="ct.conf",
        user_config_dir=user_config_dir,
        system_config_dir=system_config_dir,
        exedir=exedir,
        verbose=verbose,
        gitroot=gitroot,
    )

    # If a config file was specified directly then use that
    argvconfig = extractconfig(argv)
    if argvconfig:
        variantconfigs.append(argvconfig)
    else:
        # Otherwise look for a file called variant or variant.conf
        for ext in ("", ".conf"):
            variantconfigs += [
                os.path.join(defaultdir, variant) + ext
                for defaultdir in reversed(
                    default_config_directories(
                        user_config_dir=user_config_dir,
                        system_config_dir=system_config_dir,
                        exedir=exedir,
                        verbose=verbose,
                        gitroot=gitroot,
                        current_dir=os.getcwd()
                    )
                )
            ]

    # Check that a config file exists for the specified variant
    if not any([compiletools.wrappedos.isfile(cfg) for cfg in variantconfigs]):
        sys.stderr.write(
            " ".join(["Could not find a config file for variant =", variant, "\n"])
        )
        sys.stderr.write("\n".join(["Checked for "] + variantconfigs))
        sys.exit(1)

    # Only return the configs that exist
    configs = [cfg for cfg in variantconfigs if compiletools.wrappedos.isfile(cfg)]
    if verbose >= 1:
        print("Using config files = ")
        print(configs)

    # Make sure that if the user specified a variant then that a config file for the variant exists
    if variant is not None and not any(
        cfg.endswith(variant + ".conf") for cfg in configs
    ):
        sys.stderr.write(
            " ".join(
                [
                    "Could not find a config file for variant =",
                    variant,
                    ".  Did you make a typo in the variant?\n",
                ]
            )
        )
        if verbose >= 2:
            sys.stderr.write("\n".join(["Checked for "] + variantconfigs))
        sys.exit(1)

    return configs
