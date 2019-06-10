import json
import shutil
from pathlib import Path
from typing import List

from randovania.games.prime import iso_packager, claris_randomizer, patcher_file
from randovania.games.prime.banner_patcher import patch_game_name_and_id
from randovania.interface_common import status_update_lib, echoes
from randovania.interface_common.cosmetic_patches import CosmeticPatches
from randovania.interface_common.data_paths import DataPaths
from randovania.interface_common.status_update_lib import ProgressUpdateCallable, ConstantPercentageCallback
from randovania.interface_common.user_preferences import UserPreferences
from randovania.layout.layout_description import LayoutDescription


def delete_files_location(data_paths: DataPaths,
                          ):
    """
    Deletes an extracted game in given options.
    :param data_paths:
    :return:
    """
    game_files_path = data_paths.game_files_path
    if game_files_path.exists():
        shutil.rmtree(game_files_path)

    backup_files_path = data_paths.backup_files_path
    if backup_files_path.exists():
        shutil.rmtree(backup_files_path)


def unpack_iso(input_iso: Path,
               data_paths: DataPaths,
               progress_update: ProgressUpdateCallable,
               ):
    """
    Unpacks the given ISO to the files listed in options
    :param input_iso:
    :param data_paths:
    :param progress_update:
    :return:
    """
    game_files_path = data_paths.game_files_path

    delete_files_location(data_paths)
    iso_packager.unpack_iso(
        iso=input_iso,
        game_files_path=game_files_path,
        progress_update=progress_update,
    )


def generate_layout(user_preferences: UserPreferences,
                    progress_update: ProgressUpdateCallable,
                    ) -> LayoutDescription:
    """
    Creates a LayoutDescription for the configured permalink
    :param user_preferences:
    :param progress_update:
    :return:
    """
    return echoes.generate_layout(
        permalink=user_preferences.permalink,
        status_update=ConstantPercentageCallback(progress_update, -1),
        validate_after_generation=user_preferences.advanced_validate_seed_after,
        timeout_during_generation=user_preferences.advanced_timeout_during_generation,
    )


def apply_layout(layout: LayoutDescription,
                 data_paths: DataPaths,
                 user_preferences: UserPreferences,
                 progress_update: ProgressUpdateCallable):
    """
    Applies the given LayoutDescription to the files listed in options
    :param layout:
    :param data_paths:
    :param user_preferences:
    :param progress_update:
    :return:
    """
    game_files_path = data_paths.game_files_path
    backup_files_path = data_paths.backup_files_path

    patch_game_name_and_id(game_files_path, "Metroid Prime 2: Randomizer - {}".format(layout.shareable_hash))

    claris_randomizer.apply_layout(description=layout,
                                   cosmetic_patches=user_preferences.cosmetic_patches,
                                   backup_files_path=backup_files_path,
                                   progress_update=progress_update,
                                   game_root=game_files_path,
                                   )


def pack_iso(output_iso: Path,
             data_paths: DataPaths,
             progress_update: ProgressUpdateCallable,
             ):
    """
    Unpacks the files listed in options to the given path
    :param output_iso:
    :param data_paths:
    :param progress_update:
    :return:
    """
    game_files_path = data_paths.game_files_path

    iso_packager.pack_iso(
        iso=output_iso,
        game_files_path=game_files_path,
        progress_update=progress_update,
    )


def _output_name_for(layout: LayoutDescription) -> str:
    return "Echoes Randomizer - {}".format(layout.shareable_hash)


def _internal_patch_iso(updaters: List[ProgressUpdateCallable],
                        layout: LayoutDescription,
                        data_paths: DataPaths,
                        user_preferences: UserPreferences,
                        ):
    output_iso = user_preferences.output_directory.joinpath("{}.iso".format(_output_name_for(layout)))

    # Patch ISO
    apply_layout(layout=layout,
                 data_paths=data_paths,
                 user_preferences=user_preferences,
                 progress_update=updaters[0])

    # Pack ISO
    pack_iso(output_iso=output_iso,
             data_paths=data_paths,
             progress_update=updaters[1])

    # Save the layout to a file
    if user_preferences.create_spoiler:
        export_layout(layout, user_preferences)


def write_patcher_file_to_disk(path: Path, layout: LayoutDescription, cosmetic: CosmeticPatches):
    with path.open("w") as out_file:
        json.dump(patcher_file.create_patcher_file(layout, cosmetic),
                  out_file, indent=4, separators=(',', ': '))


def export_layout(layout: LayoutDescription,
                  user_preferences: UserPreferences,
                  ):
    """
    Creates a seed log file for the given layout and saves it to the configured path
    :param layout:
    :param user_preferences:
    :return:
    """

    output_directory = user_preferences.output_directory
    output_json = output_directory.joinpath("{}.json".format(_output_name_for(layout)))
    write_patcher_file_to_disk(output_directory.joinpath("{}-patcher.json".format(_output_name_for(layout))),
                               layout,
                               user_preferences.cosmetic_patches)

    # Save the layout to a file
    layout.save_to_file(output_json)


def patch_game_with_existing_layout(progress_update: ProgressUpdateCallable,
                                    layout: LayoutDescription,
                                    data_paths: DataPaths,
                                    user_preferences: UserPreferences,
                                    ):
    """
    Patches the game with the given layout and exports an ISO
    :param progress_update:
    :param layout:
    :param data_paths:
    :param user_preferences:
    :return:
    """
    _internal_patch_iso(
        updaters=status_update_lib.split_progress_update(
            progress_update,
            2
        ),
        layout=layout,
        data_paths=data_paths,
        user_preferences=user_preferences,
    )


def create_layout_then_export_iso(progress_update: ProgressUpdateCallable,
                                  data_paths: DataPaths,
                                  user_preferences: UserPreferences,
                                  ) -> LayoutDescription:
    """
    Creates a new layout with the given seed and configured layout, then patches and exports an ISO
    :param progress_update:
    :param data_paths:
    :param user_preferences:
    :return:
    """
    updaters = status_update_lib.split_progress_update(
        progress_update,
        3
    )

    # Create a LayoutDescription
    resulting_layout = generate_layout(user_preferences=user_preferences,
                                       progress_update=updaters[0])

    _internal_patch_iso(
        updaters=updaters[1:],
        layout=resulting_layout,
        data_paths=data_paths,
        user_preferences=user_preferences,
    )

    return resulting_layout


def create_layout_then_export(progress_update: ProgressUpdateCallable,
                              user_preferences: UserPreferences,
                              ) -> LayoutDescription:
    """
    Creates a new layout with the given seed and configured layout, then exports that layout
    :param progress_update:
    :param user_preferences:
    :return:
    """

    # Create a LayoutDescription
    resulting_layout = generate_layout(user_preferences=user_preferences,
                                       progress_update=progress_update)
    export_layout(resulting_layout, user_preferences)

    return resulting_layout
