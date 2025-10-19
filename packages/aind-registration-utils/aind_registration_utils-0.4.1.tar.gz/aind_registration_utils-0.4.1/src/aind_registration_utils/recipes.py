"""
Contains common registration recipes
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import ants
from aind_anatomical_utils.slicer import (
    create_slicer_fcsv,
    markup_json_to_dict,
)

from aind_registration_utils.ants import (
    ants_register_syn,
    apply_ants_transforms_to_point_dict,
)
from aind_registration_utils.utils import check_output_path

if TYPE_CHECKING:
    from typing import Any

    from aind_registration_utils.types import PathLike


def individual_to_template_with_points(
    individual: ants.ANTsImage,
    template: ants.ANTsImage,
    pts_in_template: dict[str, Any],
    output_prefix: str = "",
    syn_kwargs: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Register an individual image to a template image and transform points from
    the template to the individual image space.

    Parameters
    ----------
    individual : ants.ANTsImage
        The individual image that will be registered to the template.
    template : ants.ANTsImage
        The template image to which the individual image will be registered.
    pts_in_template : dict
        A dictionary of points in the template image space that need to be
        transformed to the individual image space.
    output_prefix : str
        The prefix for the output files generated during the registration
        process.
    syn_kwargs : dict, optional
        Additional keyword arguments to pass to the ANTs SyN registration
        function.

    Returns
    -------
    moving_fixed_tx_syn : dict
        A dictionary containing the results of the SyN registration, including
        the transforms.
    pts_in_individual : dict
        A dictionary of points transformed from the template image space to the
        individual image space.
    """
    if syn_kwargs is None:
        syn_kwargs = {}
    moving_fixed_tx_syn = ants_register_syn(
        fixed_img=template,
        moving_img=individual,
        syn_save_prefix=output_prefix,
        syn_kwargs=syn_kwargs,
    )
    pts_in_individual = apply_ants_transforms_to_point_dict(
        pts_in_template,
        moving_fixed_tx_syn["fwdtransforms"],
    )
    return moving_fixed_tx_syn, pts_in_individual


def individual_to_template_with_points_files(
    individual_scan: PathLike,
    individual_brain_mask: PathLike,
    template_path: PathLike,
    template_targets: PathLike,
    save_dir: PathLike | None = None,
    mouse_name: str | None = None,
    syn_kwargs: dict[str, Any] | None = None,
) -> None:
    """
    Registers an individual scan to a template and saves the transformed images
    and points.

    This function wraps `individual_to_template_with_points` but works only
    with files

    Parameters
    ----------
    individual_scan : str or Path
        Path to the individual scan image file.
    individual_brain_mask : str or Path
        Path to the individual brain mask image file.
    template_path : str or Path
        Path to the template image file.
    template_targets : str or Path
        Path to the template target points file.
    save_dir : str or Path
        Directory where the output files will be saved.
    mouse_id : str, optional
        Identifier for the mouse, used to prefix the output filenames.

    Returns
    -------
    None
        This function does not return any value. It saves the transformed
        images and points to the specified directory.
    """
    save_dir = check_output_path(save_dir)
    pt_save_name = "targets-from-template.fcsv"
    individual_in_template_save_name = "individual-in-template.nii.gz"
    template_in_individual_save_name = "template-in-individual.nii.gz"
    if mouse_name is not None:
        pt_save_name = f"{mouse_name}-{pt_save_name}"
        individual_in_template_save_name = (
            f"{mouse_name}-{individual_in_template_save_name}"
        )
        template_in_individual_save_name = (
            f"{mouse_name}-{template_in_individual_save_name}"
        )
    mouse_img = ants.image_read(str(individual_scan))
    mouse_img_mask = ants.image_read(str(individual_brain_mask))
    mouse_img_masked = mouse_img * mouse_img_mask

    template_img = ants.image_read(str(template_path))
    template_target_pts, _ = markup_json_to_dict(str(template_targets))
    individual_template_tx_syn, pts_in_individual = individual_to_template_with_points(
        mouse_img_masked,
        template_img,
        pts_in_template=template_target_pts,
        output_prefix=str(save_dir),
        syn_kwargs=syn_kwargs,
    )
    create_slicer_fcsv(str(save_dir / pt_save_name), pts_in_individual)
    ants.image_write(
        individual_template_tx_syn["warpedmovout"],
        str(save_dir / individual_in_template_save_name),
    )
    ants.image_write(
        individual_template_tx_syn["warpedfixout"],
        str(save_dir / template_in_individual_save_name),
    )
