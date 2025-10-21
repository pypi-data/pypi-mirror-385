from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import SimpleITK as sitk

import stl2mask.stl2mask as stl2mask_module

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_stl2mask_calls_dependencies(tmp_path: Path, mocker: MockerFixture) -> None:
    mesh_path = tmp_path / "mesh.stl"
    mesh_path.write_text("")
    image_path = tmp_path / "image.nii"
    image_path.write_text("")
    output_path = tmp_path / "mask.nii.gz"

    read_mesh_mock = mocker.patch.object(stl2mask_module, "read_mesh")
    read_image_mock = mocker.patch.object(stl2mask_module, "read_image")
    voxelize_mock = mocker.patch.object(stl2mask_module, "voxelize_mesh")
    mask_to_image_mock = mocker.patch.object(stl2mask_module, "mask_to_image")
    save_mask_mock = mocker.patch.object(stl2mask_module, "save_mask")

    stl2mask_module.stl2mask(
        mesh_path=mesh_path,
        image_path=image_path,
        output_path=output_path,
        threshold=1.1,
        offset=0.25,
        mask_value=128,
    )

    assert read_mesh_mock.call_count == 1
    assert read_mesh_mock.call_args.args == (mesh_path,)

    assert read_image_mock.call_count == 1
    assert read_image_mock.call_args.args == (image_path,)

    assert voxelize_mock.call_count == 1
    assert voxelize_mock.call_args.args == (read_mesh_mock.return_value, read_image_mock.return_value, 1.1, 0.25, 128)

    assert mask_to_image_mock.call_count == 1
    assert mask_to_image_mock.call_args.args == (voxelize_mock.return_value, read_image_mock.return_value)

    assert save_mask_mock.call_count == 1
    assert save_mask_mock.call_args.args == (mask_to_image_mock.return_value, output_path)


def test_cli_uses_default_output_suffix(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mesh_path = tmp_path / "mesh.stl"
    mesh_path.write_text("")
    image_path = tmp_path / "image.nii"
    image_path.write_text("")

    stl2mask_mock = mocker.patch("stl2mask.stl2mask.stl2mask")

    result = runner.invoke(stl2mask_module.cli, [str(mesh_path), str(image_path)])

    assert result.exit_code == 0
    expected_output = mesh_path.with_suffix(".nii.gz")
    assert stl2mask_mock.call_args.kwargs == {
        "mesh_path": mesh_path,
        "image_path": image_path,
        "output_path": expected_output,
        "threshold": 0.0,
        "offset": 0.5,
        "mask_value": 255,
    }
    assert str(expected_output) in result.output


def test_cli_warns_on_suffix_mismatch(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mesh_path = tmp_path / "mesh.stl"
    mesh_path.write_text("")
    image_path = tmp_path / "image.nii"
    image_path.write_text("")
    output_path = tmp_path / "custom.nii.gz"

    stl2mask_mock = mocker.patch("stl2mask.stl2mask.stl2mask")

    result = runner.invoke(
        stl2mask_module.cli,
        [
            str(mesh_path),
            str(image_path),
            "--output",
            str(output_path),
            "--suffix",
            ".mha",
        ],
    )

    assert result.exit_code == 0
    assert "⚠️ Output suffix does not match provided suffix" in result.output
    assert stl2mask_mock.call_args.kwargs == {
        "mesh_path": mesh_path,
        "image_path": image_path,
        "output_path": output_path,
        "threshold": 0.0,
        "offset": 0.5,
        "mask_value": 255,
    }


def test_cli_rejects_suffix_without_dot(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mesh_path = tmp_path / "mesh.stl"
    mesh_path.write_text("")
    image_path = tmp_path / "image.nii"
    image_path.write_text("")

    stl2mask_mock = mocker.patch("stl2mask.stl2mask.stl2mask")

    result = runner.invoke(
        stl2mask_module.cli,
        [str(mesh_path), str(image_path), "--suffix", "nii.gz"],
    )

    assert stl2mask_mock.call_count == 0
    assert result.exit_code != 0
    assert "Suffix must start with a dot" in result.output


def test_mask_to_image_preserves_metadata() -> None:
    mask = np.arange(8, dtype=np.uint8).reshape((2, 2, 2))

    reference = sitk.Image(2, 2, 2, sitk.sitkUInt8)
    reference.SetOrigin((1.0, 2.0, 3.0))
    reference.SetSpacing((0.5, 0.75, 1.25))
    reference.SetDirection((1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0))

    result = stl2mask_module.mask_to_image(mask, reference)

    assert tuple(result.GetOrigin()) == tuple(reference.GetOrigin())
    assert tuple(result.GetSpacing()) == tuple(reference.GetSpacing())
    assert tuple(result.GetDirection()) == tuple(reference.GetDirection())
    expected = np.swapaxes(mask, 0, 2)
    np.testing.assert_array_equal(sitk.GetArrayFromImage(result), expected)
