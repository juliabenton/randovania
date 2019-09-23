from randovania.game_description import data_reader
from randovania.layout.layout_description import LayoutDescription
from randovania.resolver import resolver, debug


def test_resolver_with_log_file(test_files_dir,
                                skip_resolver_tests):
    # Setup
    debug._DEBUG_LEVEL = 0

    description = LayoutDescription.from_file(test_files_dir.joinpath("log_files", "seed_a.json"))
    configuration = description.permalink.layout_configuration
    game = data_reader.decode_data(configuration.game_data)
    patches = description.patches

    # Run
    final_state_by_resolve = resolver.resolve(configuration=configuration, game=game, patches=patches)

    # Assert
    assert final_state_by_resolve is not None
