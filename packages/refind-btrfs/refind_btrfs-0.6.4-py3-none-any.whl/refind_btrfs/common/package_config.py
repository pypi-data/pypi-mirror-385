# region Licensing
# SPDX-FileCopyrightText: 2020-2024 Luka Žaja <luka.zaja@protonmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

""" refind-btrfs - Generate rEFInd manual boot stanzas from Btrfs snapshots
Copyright (C) 2020-2024 Luka Žaja

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
# endregion

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple, Optional, Self, Set
from uuid import UUID

from refind_btrfs.common import constants
from refind_btrfs.common.abc import BaseConfig
from refind_btrfs.common.enums import (
    BootStanzaIconGenerationMode,
    BtrfsLogoHorizontalAlignment,
    BtrfsLogoSize,
    BtrfsLogoVariant,
    BtrfsLogoVerticalAlignment,
)
from refind_btrfs.device import BlockDevice, Subvolume
from refind_btrfs.utility.helpers import find_all_directories_in, has_items


class SnapshotSearch(NamedTuple):
    directory: Path
    is_nested: bool
    max_depth: int

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True

        if isinstance(other, SnapshotSearch):
            self_directory_resolved = self.directory.resolve()
            other_directory_resolved = other.directory.resolve()

            return self_directory_resolved == other_directory_resolved

        return False


class SnapshotManipulation(NamedTuple):
    selection_count: int
    modify_read_only_flag: bool
    destination_directory: Path
    cleanup_exclusion: Set[Subvolume]


class BtrfsLogo(NamedTuple):
    variant: BtrfsLogoVariant
    size: BtrfsLogoSize
    horizontal_alignment: BtrfsLogoHorizontalAlignment
    vertical_alignment: BtrfsLogoVerticalAlignment


class Icon(NamedTuple):
    mode: BootStanzaIconGenerationMode
    path: Path
    btrfs_logo: BtrfsLogo


class BootStanzaGeneration(NamedTuple):
    refind_config: str
    include_paths: bool
    include_sub_menus: bool
    source_exclusion: Set[str]
    icon: Icon

    def with_include_paths(self, boot_device: Optional[BlockDevice]) -> Self:
        include_paths = self.include_paths

        if include_paths:
            include_paths = boot_device is None

        return BootStanzaGeneration(
            self.refind_config,
            include_paths,
            self.include_sub_menus,
            self.source_exclusion,
            self.icon,
        )


class PackageConfig(BaseConfig):
    def __init__(
        self,
        esp_uuid: UUID,
        exit_if_root_is_snapshot: bool,
        exit_if_no_changes_are_detected: bool,
        snapshot_searches: Iterable[SnapshotSearch],
        snapshot_manipulation: SnapshotManipulation,
        boot_stanza_generation: BootStanzaGeneration,
    ) -> None:
        super().__init__(constants.PACKAGE_CONFIG_FILE)

        self._esp_uuid = esp_uuid
        self._exit_if_root_is_snapshot = exit_if_root_is_snapshot
        self._exit_if_no_changes_are_detected = exit_if_no_changes_are_detected
        self._snapshot_searches = list(snapshot_searches)
        self._snapshot_manipulation = snapshot_manipulation
        self._boot_stanza_generation = boot_stanza_generation

    def _get_directories_for_watch(self) -> Iterator[Path]:
        snapshot_searches = self.snapshot_searches

        if has_items(snapshot_searches):
            for snapshot_search in snapshot_searches:
                directory = snapshot_search.directory
                max_depth = snapshot_search.max_depth - 1

                yield from find_all_directories_in(directory, max_depth)

    @property
    def esp_uuid(self) -> UUID:
        return self._esp_uuid

    @property
    def exit_if_root_is_snapshot(self) -> bool:
        return self._exit_if_root_is_snapshot

    @property
    def exit_if_no_changes_are_detected(self) -> bool:
        return self._exit_if_no_changes_are_detected

    @property
    def snapshot_searches(self) -> list[SnapshotSearch]:
        return self._snapshot_searches

    @property
    def snapshot_manipulation(self) -> SnapshotManipulation:
        return self._snapshot_manipulation

    @property
    def boot_stanza_generation(self) -> BootStanzaGeneration:
        return self._boot_stanza_generation

    @cached_property
    def directories_for_watch(self) -> Set[Path]:
        return set(self._get_directories_for_watch())
