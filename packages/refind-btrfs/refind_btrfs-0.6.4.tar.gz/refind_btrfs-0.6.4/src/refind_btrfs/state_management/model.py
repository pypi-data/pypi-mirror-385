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

from itertools import chain
from typing import Callable, NamedTuple, Optional, Self

from injector import inject
from more_itertools import only

from refind_btrfs.boot import BootStanza, RefindConfig
from refind_btrfs.common import ConfigurableMixin
from refind_btrfs.common.abc.factories import (
    BaseDeviceCommandFactory,
    BaseIconCommandFactory,
    BaseLoggerFactory,
    BaseSubvolumeCommandFactory,
)
from refind_btrfs.common.abc.providers import (
    BasePackageConfigProvider,
    BasePersistenceProvider,
    BaseRefindConfigProvider,
)
from refind_btrfs.device import BlockDevice, Partition, Subvolume
from refind_btrfs.utility.helpers import has_items, none_throws, replace_item_in

from .conditions import Conditions

# region Helper Tuples


class BlockDevices(NamedTuple):
    esp_device: Optional[BlockDevice]
    root_device: Optional[BlockDevice]
    boot_device: Optional[BlockDevice]

    @classmethod
    def none(cls) -> Self:
        return cls(None, None, None)


class PreparedSnapshots(NamedTuple):
    snapshots_for_addition: list[Subvolume]
    snapshots_for_removal: list[Subvolume]

    def has_changes(self) -> bool:
        return has_items(self.snapshots_for_addition) or has_items(
            self.snapshots_for_removal
        )


class BootStanzaWithSnapshots(NamedTuple):
    boot_stanza: BootStanza
    is_excluded: bool
    matched_snapshots: list[Subvolume]
    unmatched_snapshots: list[Subvolume]

    def has_matched_snapshots(self) -> bool:
        return has_items(self.matched_snapshots)

    def has_unmatched_snapshots(self) -> bool:
        return has_items(self.unmatched_snapshots)

    def is_usable(self) -> bool:
        return not self.is_excluded and self.has_matched_snapshots()

    def replace_matched_snapshot(
        self, current_snapshot: Subvolume, replacement_snapshot: Subvolume
    ) -> None:
        matched_snapshots = self.matched_snapshots

        replace_item_in(matched_snapshots, current_snapshot, replacement_snapshot)


class ProcessingResult(NamedTuple):
    bootable_snapshots: list[Subvolume]

    @classmethod
    def none(cls) -> Self:
        return cls([])

    def has_bootable_snapshots(self) -> bool:
        return has_items(self.bootable_snapshots)


# endregion


class Model(ConfigurableMixin):
    @inject
    def __init__(
        self,
        logger_factory: BaseLoggerFactory,
        device_command_factory: BaseDeviceCommandFactory,
        subvolume_command_factory: BaseSubvolumeCommandFactory,
        icon_command_factory: BaseIconCommandFactory,
        package_config_provider: BasePackageConfigProvider,
        refind_config_provider: BaseRefindConfigProvider,
        persistence_provider: BasePersistenceProvider,
    ) -> None:
        ConfigurableMixin.__init__(self, package_config_provider)

        self._device_command_factory = device_command_factory
        self._subvolume_command_factory = subvolume_command_factory
        self._icon_command_factory = icon_command_factory
        self._refind_config_provider = refind_config_provider
        self._persistence_provider = persistence_provider
        self._conditions = Conditions(logger_factory, self)
        self._filtered_block_devices: Optional[BlockDevices] = None
        self._matched_boot_stanzas: Optional[list[BootStanza]] = None
        self._prepared_snapshots: Optional[PreparedSnapshots] = None
        self._boot_stanzas_with_snapshots: Optional[
            list[BootStanzaWithSnapshots]
        ] = None

    def initialize_block_devices(self) -> None:
        device_command_factory = self._device_command_factory
        physical_device_command = device_command_factory.physical_device_command()
        all_block_devices = list(physical_device_command.get_block_devices())

        if has_items(all_block_devices):
            for block_device in all_block_devices:
                block_device.initialize_partition_tables_using(device_command_factory)

            def block_device_filter(
                filter_func: Callable[[BlockDevice], bool],
            ) -> Optional[BlockDevice]:
                return only(
                    block_device
                    for block_device in all_block_devices
                    if filter_func(block_device)
                )

            filtered_block_devices = BlockDevices(
                block_device_filter(BlockDevice.has_esp),
                block_device_filter(BlockDevice.has_root),
                block_device_filter(BlockDevice.has_boot),
            )
        else:
            filtered_block_devices = BlockDevices.none()

        self._filtered_block_devices = filtered_block_devices

    def initialize_root_subvolume(self) -> None:
        subvolume_command_factory = self._subvolume_command_factory
        root_partition = self.root_partition
        filesystem = none_throws(root_partition.filesystem)

        filesystem.initialize_subvolume_using(subvolume_command_factory)

    def initialize_matched_boot_stanzas(self) -> None:
        refind_config = self.refind_config
        include_paths = self._should_include_paths_during_generation()
        root_device = none_throws(self.root_device)
        matched_boot_stanzas = refind_config.get_boot_stanzas_matched_with(root_device)

        if include_paths:
            subvolume = self.root_subvolume
            include_sub_menus = self._should_include_sub_menus_during_generation()

            self._matched_boot_stanzas = [
                boot_stanza.with_boot_files_check_result(subvolume, include_sub_menus)
                for boot_stanza in matched_boot_stanzas
            ]
        else:
            self._matched_boot_stanzas = list(matched_boot_stanzas)

    def initialize_prepared_snapshots(self) -> None:
        persistence_provider = self._persistence_provider
        snapshot_manipulation = self.package_config.snapshot_manipulation
        subvolume = self.root_subvolume
        previous_run_result = persistence_provider.get_previous_run_result()
        selected_snapshots = none_throws(
            subvolume.select_snapshots(snapshot_manipulation.selection_count)
        )
        destination_directory = snapshot_manipulation.destination_directory
        snapshots_union = snapshot_manipulation.cleanup_exclusion.union(
            selected_snapshots
        )

        if previous_run_result.has_bootable_snapshots():
            bootable_snapshots = previous_run_result.bootable_snapshots
            snapshots_for_addition = [
                snapshot
                for snapshot in selected_snapshots
                if snapshot.can_be_added(bootable_snapshots)
            ]
            snapshots_for_removal = [
                snapshot
                for snapshot in bootable_snapshots
                if snapshot.can_be_removed(destination_directory, snapshots_union)
            ]
        else:
            destination_snapshots = self.destination_snapshots
            snapshots_for_addition = selected_snapshots
            snapshots_for_removal = [
                snapshot
                for snapshot in destination_snapshots.difference(snapshots_union)
                if snapshot.can_be_removed(destination_directory, selected_snapshots)
            ]

        if has_items(snapshots_for_addition):
            device_command_factory = self._device_command_factory

            for snapshot in snapshots_for_addition:
                snapshot.initialize_partition_table_using(device_command_factory)

        self._prepared_snapshots = PreparedSnapshots(
            snapshots_for_addition, snapshots_for_removal
        )

    def combine_boot_stanzas_with_snapshots(self) -> None:
        usable_boot_stanzas = self.usable_boot_stanzas
        actual_bootable_snapshots = self.actual_bootable_snapshots
        boot_stanza_generation = self.package_config.boot_stanza_generation
        include_paths = self._should_include_paths_during_generation()
        boot_stanza_preparation_results: list[BootStanzaWithSnapshots] = []

        for boot_stanza in usable_boot_stanzas:
            is_excluded = any(
                boot_stanza.is_matched_with(loader_filename)
                for loader_filename in boot_stanza_generation.source_exclusion
            )
            matched_snapshots: list[Subvolume] = []
            unmatched_snapshots: list[Subvolume] = []

            if include_paths:
                checked_bootable_snapshots = (
                    snapshot.with_boot_files_check_result(boot_stanza)
                    for snapshot in actual_bootable_snapshots
                )

                for snapshot in checked_bootable_snapshots:
                    append_func = (
                        unmatched_snapshots.append
                        if snapshot.has_unmatched_boot_files()
                        else matched_snapshots.append
                    )

                    append_func(snapshot)
            else:
                matched_snapshots.extend(actual_bootable_snapshots)

            boot_stanza_preparation_results.append(
                BootStanzaWithSnapshots(
                    boot_stanza, is_excluded, matched_snapshots, unmatched_snapshots
                )
            )

        self._boot_stanzas_with_snapshots = boot_stanza_preparation_results

    def process_changes(self) -> None:
        persistence_provider = self._persistence_provider
        bootable_snapshots = self._process_snapshots()

        self._process_boot_stanzas()

        persistence_provider.save_current_run_result(
            ProcessingResult(bootable_snapshots)
        )

    def _process_snapshots(self) -> list[Subvolume]:
        subvolume_command_factory = self._subvolume_command_factory
        actual_bootable_snapshots = self.actual_bootable_snapshots
        usable_snapshots_for_addition = self.usable_snapshots_for_addition
        subvolume_command = subvolume_command_factory.subvolume_command()

        if has_items(usable_snapshots_for_addition):
            device_command_factory = self._device_command_factory
            subvolume = self.root_subvolume
            boot_stanzas_with_snapshots = self.boot_stanzas_with_snapshots
            all_usable_snapshots = set(
                chain.from_iterable(self.usable_boot_stanzas_with_snapshots.values())
            )

            for addition in usable_snapshots_for_addition:
                if addition in all_usable_snapshots:
                    bootable_snapshot = subvolume_command.get_bootable_snapshot_from(
                        addition
                    )

                    bootable_snapshot.modify_partition_table_using(
                        subvolume, device_command_factory
                    )
                    replace_item_in(
                        actual_bootable_snapshots, addition, bootable_snapshot
                    )

                    for item in boot_stanzas_with_snapshots:
                        item.replace_matched_snapshot(addition, bootable_snapshot)
                else:
                    actual_bootable_snapshots.remove(addition)

        prepared_snapshots = self.prepared_snapshots
        snapshots_for_removal = prepared_snapshots.snapshots_for_removal

        if has_items(snapshots_for_removal):
            for removal in snapshots_for_removal:
                subvolume_command.delete_snapshot(removal)

        return actual_bootable_snapshots

    def _process_boot_stanzas(self) -> None:
        refind_config = self.refind_config
        root_device = none_throws(self.root_device)
        boot_device = self.boot_device
        usable_boot_stanzas_with_snapshots = self.usable_boot_stanzas_with_snapshots
        boot_stanza_generation = (
            self.package_config.boot_stanza_generation.with_include_paths(boot_device)
        )
        icon_command_factory = self._icon_command_factory
        generated_refind_configs = refind_config.generate_new_from(
            root_device,
            usable_boot_stanzas_with_snapshots,
            boot_stanza_generation,
            icon_command_factory,
        )

        refind_config_provider = self._refind_config_provider

        for generated_refind_config in generated_refind_configs:
            refind_config_provider.save_config(generated_refind_config)

        refind_config_provider.append_to_config(refind_config)

    def _should_include_paths_during_generation(self) -> bool:
        boot_stanza_generation = self.package_config.boot_stanza_generation

        if boot_stanza_generation.include_paths:
            return self.boot_device is None

        return False

    def _should_include_sub_menus_during_generation(self) -> bool:
        boot_stanza_generation = self.package_config.boot_stanza_generation

        return boot_stanza_generation.include_sub_menus

    @property
    def conditions(self) -> list[Callable[[], bool]]:
        conditions = self._conditions
        always_true_func = lambda: True

        return [
            always_true_func,
            conditions.check_filtered_block_devices,
            conditions.check_root_subvolume,
            conditions.check_matched_boot_stanzas,
            conditions.check_prepared_snapshots,
            conditions.check_boot_stanzas_with_snapshots,
            always_true_func,
        ]

    @property
    def refind_config(self) -> RefindConfig:
        refind_config_provider = self._refind_config_provider
        esp = self.esp

        return refind_config_provider.get_config(esp)

    @property
    def esp_device(self) -> Optional[BlockDevice]:
        return none_throws(self._filtered_block_devices).esp_device

    @property
    def esp(self) -> Partition:
        esp_device = none_throws(self.esp_device)

        return none_throws(esp_device.esp)

    @property
    def root_device(self) -> Optional[BlockDevice]:
        return none_throws(self._filtered_block_devices).root_device

    @property
    def root_partition(self) -> Partition:
        root_device = none_throws(self.root_device)

        return none_throws(root_device.root)

    @property
    def root_subvolume(self) -> Subvolume:
        root_partition = self.root_partition
        filesystem = none_throws(root_partition.filesystem)

        return none_throws(filesystem.subvolume)

    @property
    def boot_device(self) -> Optional[BlockDevice]:
        return none_throws(self._filtered_block_devices).boot_device

    @property
    def matched_boot_stanzas(self) -> list[BootStanza]:
        return none_throws(self._matched_boot_stanzas)

    @property
    def usable_boot_stanzas(self) -> list[BootStanza]:
        matched_boot_stanzas = self.matched_boot_stanzas

        return [
            boot_stanza
            for boot_stanza in matched_boot_stanzas
            if not boot_stanza.has_unmatched_boot_files()
        ]

    @property
    def prepared_snapshots(self) -> PreparedSnapshots:
        return none_throws(self._prepared_snapshots)

    @property
    def destination_snapshots(self) -> set[Subvolume]:
        subvolume_command_factory = self._subvolume_command_factory
        subvolume_command = subvolume_command_factory.subvolume_command()
        destination_snapshots = sorted(
            subvolume_command.get_all_destination_snapshots(), reverse=True
        )

        return set(destination_snapshots)

    @property
    def usable_snapshots_for_addition(self) -> list[Subvolume]:
        subvolume = self.root_subvolume
        prepared_snapshots = self.prepared_snapshots
        snapshots_for_addition = prepared_snapshots.snapshots_for_addition

        return [
            snapshot
            for snapshot in snapshots_for_addition
            if snapshot.is_static_partition_table_matched_with(subvolume)
        ]

    @property
    def actual_bootable_snapshots(self) -> list[Subvolume]:
        persistence_provider = self._persistence_provider
        prepared_snapshots = self.prepared_snapshots
        usable_snapshots_for_addition = self.usable_snapshots_for_addition
        previous_run_result = persistence_provider.get_previous_run_result()
        snapshots_for_removal = prepared_snapshots.snapshots_for_removal
        bootable_snapshots = set(previous_run_result.bootable_snapshots)

        if has_items(usable_snapshots_for_addition):
            bootable_snapshots |= set(usable_snapshots_for_addition)

        if has_items(snapshots_for_removal):
            bootable_snapshots -= set(snapshots_for_removal)

        return list(bootable_snapshots)

    @property
    def boot_stanzas_with_snapshots(self) -> list[BootStanzaWithSnapshots]:
        return none_throws(self._boot_stanzas_with_snapshots)

    @property
    def usable_boot_stanzas_with_snapshots(self) -> dict[BootStanza, list[Subvolume]]:
        boot_stanzas_with_snapshots = self.boot_stanzas_with_snapshots

        return {
            item.boot_stanza: item.matched_snapshots
            for item in boot_stanzas_with_snapshots
            if item.is_usable()
        }
