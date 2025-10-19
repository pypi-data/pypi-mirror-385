import os
import configargparse
import compiletools.testhelper as uth
import compiletools.namer
import compiletools.configutils
import compiletools.apptools


def test_executable_pathname():
    uth.reset()
    
    try:
        config_dir = os.path.join(uth.cakedir(), "ct.conf.d")
        config_files = [os.path.join(config_dir, "gcc.debug.conf")]
        cap = configargparse.getArgumentParser(
            description="TestNamer",
            formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
            default_config_files=config_files,
            args_for_setting_config_path=["-c", "--config"],
            ignore_unknown_config_file_keys=True,
        )
        argv = ["--no-git-root"]
        compiletools.apptools.add_common_arguments(cap=cap, argv=argv, variant="gcc.debug")
        compiletools.namer.Namer.add_arguments(cap=cap, argv=argv, variant="gcc.debug")
        args = compiletools.apptools.parseargs(cap, argv)
        namer = compiletools.namer.Namer(args, argv=argv, variant="gcc.debug")
        exename = namer.executable_pathname("/home/user/code/my.cpp")
        assert exename == "bin/gcc.debug/my"
    finally:
        uth.reset()


