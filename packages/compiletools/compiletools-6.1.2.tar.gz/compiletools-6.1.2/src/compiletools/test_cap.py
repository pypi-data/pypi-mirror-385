
import configargparse

import compiletools.testhelper as uth


def add_to_parser_in_func(recursion_depth=0):
    if recursion_depth < 6:
        cap = configargparse.getArgumentParser()
        cap.add(
            "-v",
            "--verbose",
            help="Output verbosity. Add more v's to make it more verbose",
            action="count",
            default=0,
        )
        parsed_args = cap.parse_known_args(args=["-v"])
        assert parsed_args is not None
        assert parsed_args[0].verbose == 1

        # Note that is_config_file is False
        # The unit test fails if it is set to True
        # I wanted this knowledge to be written down somewhere
        # hence the reason for this unit tests existence
        cap.add(
            "-c",
            "--cfg",
            is_config_file=False,
            help="Manually specify the config file path if you want to override the variant default",
        )
        add_to_parser_in_func(recursion_depth + 1)
        cap.parse_known_args(args=["-v"])


def test_multiple_parse_known_args():
    uth.reset()
    
    try:
        non_existent_config_files = ["/blah/foo.conf", "/usr/bin/ba.conf"]
        cap = configargparse.getArgumentParser(
            prog="UnitTest",
            description="unit testing",
            formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
            default_config_files=non_existent_config_files,
            args_for_setting_config_path=["-c", "--config"],
        )

        cap.add(
            "--variant",
            help="Specifies which variant of the config should be used. Use the config name without the .conf",
            default="debug",
        )
        parsed_args = cap.parse_known_args()
        assert parsed_args is not None
        assert parsed_args[0].variant == "debug"

        add_to_parser_in_func()

        cap.add(
            "-c",
            "--cfg",
            is_config_file=True,
            help="Manually specify the config file path if you want to override the variant default",
        )
        cap.parse_known_args(args=["--variant", "release"])
    finally:
        uth.reset()


