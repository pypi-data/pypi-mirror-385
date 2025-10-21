from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
import SimpleITK as sitk

import stl2mask.mask2stl as mask2stl_module

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner


def _make_mask_image(values: np.ndarray) -> sitk.Image:
    image = sitk.GetImageFromArray(values.astype(np.uint8))
    image.SetSpacing((0.5, 0.5, 0.5))
    image.SetOrigin((1.0, 2.0, 3.0))
    image.SetDirection((1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0))
    return image


def test_mask2stl_without_reference_image(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    output_path = tmp_path / "mesh.stl"

    mask_image = _make_mask_image(np.array([[[0, 255], [0, 0]], [[0, 0], [0, 0]]]))

    read_calls: list[Path] = []
    saved_meshes: list[tuple[object, Path]] = []
    mask_to_mesh_calls: list[tuple[sitk.Image, float | None]] = []
    transform_calls: list[tuple[object, sitk.Image, sitk.Image]] = []
    mesh_sentinel = object()

    def fake_read_image(path: Path) -> sitk.Image:
        read_calls.append(path)
        if path == mask_path:
            return mask_image
        msg = f"Unexpected path {path}"
        raise AssertionError(msg)

    def fake_mask_to_mesh(mask: sitk.Image, iso_value: float | None) -> object:
        mask_to_mesh_calls.append((mask, iso_value))
        return mesh_sentinel

    def fake_transform_mesh(mesh: object, mask: sitk.Image, image: sitk.Image) -> None:
        transform_calls.append((mesh, mask, image))

    def fake_save_mesh(mesh: object, path: Path) -> None:
        saved_meshes.append((mesh, path))

    monkeypatch.setattr(mask2stl_module, "read_image", fake_read_image)
    monkeypatch.setattr(mask2stl_module, "mask_to_mesh", fake_mask_to_mesh)
    monkeypatch.setattr(mask2stl_module, "transform_mesh", fake_transform_mesh)
    monkeypatch.setattr(mask2stl_module.mm, "saveMesh", fake_save_mesh)

    mask2stl_module.mask2stl(mask_path, None, output_path, iso_value=64.0)

    assert read_calls == [mask_path]
    assert mask_to_mesh_calls == [(mask_image, 64.0)]
    assert transform_calls == []
    assert saved_meshes == [(mesh_sentinel, output_path)]


def test_mask2stl_with_reference_image(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    image_path = tmp_path / "image.nii.gz"
    output_path = tmp_path / "mesh.stl"

    mask_image = _make_mask_image(np.array([[[0, 255]], [[0, 0]]]))
    reference_image = sitk.Image(1, 1, 2, sitk.sitkUInt8)
    reference_image.SetOrigin((5.0, 6.0, 7.0))

    read_calls: list[Path] = []
    mask_to_mesh_calls: list[tuple[sitk.Image, float | None]] = []
    transform_calls: list[tuple[object, sitk.Image, sitk.Image]] = []
    saved_meshes: list[tuple[object, Path]] = []
    mesh_sentinel = object()

    def fake_read_image(path: Path) -> sitk.Image:
        read_calls.append(path)
        if path == mask_path:
            return mask_image
        if path == image_path:
            return reference_image
        msg = f"Unexpected path {path}"
        raise AssertionError(msg)

    def fake_mask_to_mesh(mask: sitk.Image, iso_value: float | None) -> object:
        mask_to_mesh_calls.append((mask, iso_value))
        return mesh_sentinel

    def fake_transform_mesh(mesh: object, mask: sitk.Image, image: sitk.Image) -> None:
        transform_calls.append((mesh, mask, image))

    def fake_save_mesh(mesh: object, path: Path) -> None:
        saved_meshes.append((mesh, path))

    monkeypatch.setattr(mask2stl_module, "read_image", fake_read_image)
    monkeypatch.setattr(mask2stl_module, "mask_to_mesh", fake_mask_to_mesh)
    monkeypatch.setattr(mask2stl_module, "transform_mesh", fake_transform_mesh)
    monkeypatch.setattr(mask2stl_module.mm, "saveMesh", fake_save_mesh)

    mask2stl_module.mask2stl(mask_path, image_path, output_path, iso_value=None)

    assert read_calls == [mask_path, image_path]
    assert mask_to_mesh_calls == [(mask_image, None)]
    assert transform_calls == [(mesh_sentinel, mask_image, reference_image)]
    assert saved_meshes == [(mesh_sentinel, output_path)]


def test_mask2stl_rejects_non_binary_mask(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    output_path = tmp_path / "mesh.stl"
    mask_image = _make_mask_image(np.array([[[0, 1, 2]]]))

    def fake_read_image(path: Path) -> sitk.Image:
        if path == mask_path:
            return mask_image
        pytest.fail("unexpected path")

    monkeypatch.setattr(mask2stl_module, "read_image", fake_read_image)

    with pytest.raises(ValueError, match="binary image"):
        mask2stl_module.mask2stl(mask_path, None, output_path)


def test_mask2stl_rejects_out_of_range_iso_value(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    output_path = tmp_path / "mesh.stl"
    mask_image = _make_mask_image(np.array([[[0, 255]]]))

    def fake_read_image(path: Path) -> sitk.Image:
        if path == mask_path:
            return mask_image
        pytest.fail("unexpected path")

    monkeypatch.setattr(mask2stl_module, "read_image", fake_read_image)

    with pytest.raises(ValueError, match="iso value"):
        mask2stl_module.mask2stl(mask_path, None, output_path, iso_value=300.0)


def test_cli_uses_default_suffix(tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    mask_path.write_text("")

    captured_kwargs: dict[str, object] = {}

    def fake_mask2stl(mask: Path, image: Path | None, output: Path, iso_value: float | None) -> None:
        captured_kwargs.update(
            {
                "mask": mask,
                "image": image,
                "output": output,
                "iso_value": iso_value,
            }
        )

    monkeypatch.setattr(mask2stl_module, "mask2stl", fake_mask2stl)

    result = runner.invoke(mask2stl_module.cli, [str(mask_path)])

    assert result.exit_code == 0
    expected_output = mask_path.with_suffix(".stl")
    assert captured_kwargs == {
        "mask": mask_path,
        "image": None,
        "output": expected_output,
        "iso_value": None,
    }
    assert str(expected_output) in result.output


def test_cli_warns_on_suffix_mismatch(tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    mask_path.write_text("")
    output_path = tmp_path / "custom.stl"

    captured_kwargs: dict[str, object] = {}

    def fake_mask2stl(mask: Path, image: Path | None, output: Path, iso_value: float | None) -> None:
        captured_kwargs.update(
            {
                "mask": mask,
                "image": image,
                "output": output,
                "iso_value": iso_value,
            }
        )

    monkeypatch.setattr(mask2stl_module, "mask2stl", fake_mask2stl)

    result = runner.invoke(
        mask2stl_module.cli,
        [
            str(mask_path),
            "--output",
            str(output_path),
            "--suffix",
            ".obj",
        ],
    )

    assert result.exit_code == 0
    assert "⚠️ Output suffix does not match provided suffix" in result.output
    assert captured_kwargs == {
        "mask": mask_path,
        "image": None,
        "output": output_path,
        "iso_value": None,
    }


def test_cli_rejects_suffix_without_dot(tmp_path: Path, runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    mask_path.write_text("")

    def fail_mask2stl(*_: object, **__: object) -> None:
        pytest.fail("mask2stl should not be called")

    monkeypatch.setattr(mask2stl_module, "mask2stl", fail_mask2stl)

    result = runner.invoke(
        mask2stl_module.cli,
        [str(mask_path), "--suffix", "stl"],
    )

    assert result.exit_code != 0
    assert "Suffix must start with a dot" in result.output
