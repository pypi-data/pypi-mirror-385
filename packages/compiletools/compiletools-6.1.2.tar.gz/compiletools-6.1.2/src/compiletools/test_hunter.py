import os
import configargparse
import compiletools.testhelper

from importlib import reload

import compiletools.testhelper as uth
import compiletools.wrappedos
import compiletools.headerdeps
import compiletools.magicflags
import compiletools.hunter


def callprocess(headerobj, filenames):
    result = set()
    for filename in filenames:
        realpath = compiletools.wrappedos.realpath(filename)
        result |= set(headerobj.process(realpath, frozenset()))
    return result


def _reload_ct_with_cache(cache_home):
    """ Set the CTCACHE environment variable to cache_home
        and reload the compiletools.* modules
    """
    with uth.EnvironmentContext({"CTCACHE": cache_home}):
        reload(compiletools.headerdeps)
        reload(compiletools.magicflags)
        reload(compiletools.hunter)
        return cache_home


class TestHunterModule:
    def setup_method(self):
        uth.reset()
        configargparse.getArgumentParser(
            description="Configargparser in test code",
            formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
            args_for_setting_config_path=["-c", "--config"],
            ignore_unknown_config_file_keys=False,
        )

    def test_hunter_follows_source_files_from_header(self):
        origcache = compiletools.dirnamer.user_cache_dir("ct")
        with uth.TempDirContextNoChange() as tempdir:
            with uth.EnvironmentContext({"CTCACHE": tempdir}):
                reload(compiletools.headerdeps)
                reload(compiletools.magicflags)
                reload(compiletools.hunter)

            with uth.TempConfigContext() as temp_config:
                argv = ["-c", temp_config, "--include", uth.ctdir()]
                cap = configargparse.getArgumentParser()
                compiletools.hunter.add_arguments(cap)
                args = compiletools.apptools.parseargs(cap, argv)
                headerdeps = compiletools.headerdeps.create(args)
                magicparser = compiletools.magicflags.create(args, headerdeps)
                hntr = compiletools.hunter.Hunter(args, headerdeps, magicparser)

                relativepath = "factory/widget_factory.hpp"
                realpath = os.path.join(uth.samplesdir(), relativepath)
                filesfromheader = hntr.required_source_files(realpath)
                filesfromsource = hntr.required_source_files(compiletools.utils.implied_source(realpath))
                assert set(filesfromheader) == set(filesfromsource)
        
        with uth.EnvironmentContext({"CTCACHE": origcache}):
            reload(compiletools.headerdeps)
            reload(compiletools.magicflags)
            reload(compiletools.hunter)

    @staticmethod
    def _hunter_is_not_order_dependent(precall):
        samplesdir = uth.samplesdir()
        relativepaths = [
            "factory/test_factory.cpp",
            "numbers/test_direct_include.cpp",
            "simple/helloworld_c.c",
            "simple/helloworld_cpp.cpp",
            "simple/test_cflags.c",
        ]
        bulkpaths = [os.path.join(samplesdir, filename) for filename in relativepaths]
        with uth.TempConfigContext() as temp_config:
            argv = ["--config", temp_config, "--include", uth.ctdir()]
            cap = configargparse.getArgumentParser()
            compiletools.hunter.add_arguments(cap)
            args = compiletools.apptools.parseargs(cap, argv)
            headerdeps = compiletools.headerdeps.create(args)
            magicparser = compiletools.magicflags.create(args, headerdeps)
            hntr = compiletools.hunter.Hunter(args, headerdeps, magicparser)

        realpath = os.path.join(samplesdir, "dottypaths/dottypaths.cpp")
        if precall:
            result = hntr.required_source_files(realpath)
            return result
        else:
            for filename in bulkpaths:
                hntr.required_source_files(filename)
            result = hntr.required_source_files(realpath)
            return result

    def test_hunter_is_not_order_dependent(self):
        origcache = compiletools.dirnamer.user_cache_dir("ct")
        with uth.TempDirContextNoChange() as tempdir:
            with uth.EnvironmentContext({"CTCACHE": tempdir}):
                reload(compiletools.headerdeps)
                reload(compiletools.magicflags)
                reload(compiletools.hunter)

            result2 = self._hunter_is_not_order_dependent(True)
            result1 = self._hunter_is_not_order_dependent(False)
            result3 = self._hunter_is_not_order_dependent(False)
            result4 = self._hunter_is_not_order_dependent(True)

            assert set(result1) == set(result2)
            assert set(result3) == set(result2)
            assert set(result4) == set(result2)

        with uth.EnvironmentContext({"CTCACHE": origcache}):
            reload(compiletools.headerdeps)
            reload(compiletools.magicflags)
            reload(compiletools.hunter)

    def teardown_method(self):
        uth.reset()


