from argparse import ArgumentParser

from randovania.layout.layout_configuration import LayoutSkyTempleKeyMode, LayoutConfiguration, \
    LayoutElevators
from randovania.layout.starting_location import StartingLocation
from randovania.layout.trick_level import LayoutTrickLevel, TrickLevelConfiguration


def add_debug_argument(parser: ArgumentParser):
    parser.add_argument(
        "--debug",
        choices=range(4),
        type=int,
        default=0,
        help="The level of debug logging to print.")


def add_layout_configuration_arguments(parser: ArgumentParser):
    parser.add_argument(
        "--trick-level",
        type=str,
        choices=[layout.value for layout in LayoutTrickLevel],
        default=LayoutTrickLevel.NO_TRICKS.value,
        help="The level of tricks to use.")
    parser.add_argument(
        "--sky-temple-keys",
        type=str,
        choices=[str(mode.value) for mode in LayoutSkyTempleKeyMode],
        default=LayoutSkyTempleKeyMode.default().value,
        help="The Sky Temple Keys randomization mode.")
    parser.add_argument(
        "--skip-item-loss",
        action="store_true",
        help="Disables the item loss cutscene, disabling losing your items."
    )


def get_layout_configuration_from_args(args) -> LayoutConfiguration:
    try:
        sky_temple_keys = int(args.sky_temple_keys)
    except ValueError:
        sky_temple_keys = args.sky_temple_keys

    # TODO: support for item loss
    return LayoutConfiguration.from_params(
        trick_level_configuration=TrickLevelConfiguration(LayoutTrickLevel(args.trick_level)),
        sky_temple_keys=LayoutSkyTempleKeyMode(sky_temple_keys),
        elevators=LayoutElevators.VANILLA,
        starting_location=StartingLocation.default(),
    )


def add_validate_argument(parser: ArgumentParser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--validate", action="store_true", dest="validate", default=True,
                       help="After generating a layout, validate if it's possible. Default behaviour.")
    group.add_argument("--no-validate", action="store_false", dest="validate", default=True,
                       help="After generating a layout, don't validate if it's possible.")
