import argparse
import re
import sys
from typing import Dict, Tuple


def convert_code(python_code: str) -> Tuple[str, Dict[str, int]]:
    """
    conversion of script files using older tilmedia versions.

    Args:
        python_code (str): python script file content

    Returns:
        Tuple[str, Dict[str, int]]: new python code, conversion statistics
    """
    statistics = {}
    python_code, statistics[r"\bsetState_(\w+)\b"] = re.subn(r"\bsetState_(\w+)\b", r"set_\g<1>", python_code)
    python_code, statistics[r"\bexperimental_setState_(\w+)\b"] = re.subn(
        r"\bexperimental_setState_(\w+)\b", r"set_\g<1>", python_code
    )
    python_code, statistics[r"\bgetAllLiquidNames\b"] = re.subn(
        r"\bgetAllLiquidNames\b", r"get_all_liquid_names", python_code
    )
    python_code, statistics[r"\bgetAllGasNames\b"] = re.subn(r"\bgetAllGasNames\b", r"get_all_gas_names", python_code)
    python_code, statistics[r"\bgetAllCondensingGasNames\b"] = re.subn(
        r"\bgetAllCondensingGasNames\b", r"get_all_condensing_gas_names", python_code
    )
    python_code, statistics[r"\bgetAllVLEFluidNames\b"] = re.subn(
        r"\bgetAllVLEFluidNames\b", r"get_all_vleFluid_names", python_code
    )
    python_code, statistics[r"\bgetAllAdsorptionAndAbsorptionNames\b"] = re.subn(
        r"\bgetAllAdsorptionAndAbsorptionNames\b", r"get_all_adsorption_and_absorption_names", python_code
    )
    python_code, statistics[r"(g|s)etDataPath"] = re.subn(r"\b(g|s)etDataPath\b", r"\g<1>et_data_path", python_code)
    python_code, statistics[r"\bclearMediumNameCache\b"] = re.subn(
        r"\bclearMediumNameCache\b", r"clear_medium_name_cache", python_code
    )
    python_code, statistics[r"\blicenseIsValid\b"] = re.subn(r"\blicenseIsValid\b", r"license_is_valid", python_code)
    python_code, statistics[r"\bgetClosestVLEFluid_dpT\b"] = re.subn(
        r"\bgetClosestVLEFluid_dpT\b", r"get_closest_vleFluid_dpT", python_code
    )
    python_code, statistics[r"\b(TILMediaError)_(\w+)\b"] = re.subn(
        r"\b(TILMediaError)_(\w+)\b", r"\g<1>\g<2>", python_code
    )
    python_code, statistics[r"\bcomputeTransportProperties\b"] = re.subn(
        r"\bcomputeTransportProperties\b", r"compute_transport_properties", python_code
    )
    python_code, statistics[r"\bcomputeVLETransportProperties\b"] = re.subn(
        r"\bcomputeVLETransportProperties\b", r"compute_vle_transport_properties", python_code
    )
    python_code, statistics[r"\bcomputeVLEAdditionalProperties\b"] = re.subn(
        r"\bcomputeVLEAdditionalProperties\b", r"compute_vle_additional_properties", python_code
    )
    python_code, statistics[r"\bdeactivateDensityDerivatives\b"] = re.subn(
        r"\bdeactivateDensityDerivatives\b", r"deactivate_density_derivatives", python_code
    )
    python_code, statistics[r"\bdeactivateTwoPhaseRegion\b"] = re.subn(
        r"\bdeactivateTwoPhaseRegion\b", r"deactivate_two_phase_region", python_code
    )
    python_code, statistics[r"\binstanceName\b"] = re.subn(r"\binstanceName\b", r"instance_name", python_code)
    python_code, statistics[r"\bfixedMixingRatio\b"] = re.subn(
        r"\bfixedMixingRatio\b", r"fixed_mixing_ratio", python_code
    )
    python_code, statistics[r"\bvleFluidName\b"] = re.subn(r"\bvleFluidName\b", r"vleFluid_name", python_code)
    python_code, statistics[r"\bgasName\b"] = re.subn(r"\bgasName\b", r"gas_name", python_code)
    python_code, statistics[r"\bliquidName\b"] = re.subn(r"\bliquidName\b", r"liquid_name", python_code)

    python_code, statistics[r"\b(import\s+)TILMedia(\s*\n)"] = re.subn(
        r"\b(import\s+)TILMedia(\s*\n)", r"\g<1>tilmedia\g<2>", python_code
    )
    python_code, statistics[r"([\(=\s,;:#\[])TILMedia\."] = re.subn(
        r"([\(=\s,;:#\[])TILMedia\.", r"\g<1>tilmedia.", python_code
    )
    python_code, statistics[r"\b(from\s+)TILMedia(\s*import\s+)"] = re.subn(
        r"\b(from\s+)TILMedia(\s*import\s+)", r"\g<1>tilmedia\g<2>", python_code
    )
    python_code, statistics[r"\b_TILMediaInternals\b"] = re.subn(r"\b_TILMediaInternals\b", r"_internals", python_code)

    python_code, statistics[r"\b\.VLE\.\b"] = re.subn(r"\b\.VLE\.\b", r".vle.", python_code)
    python_code, statistics[r"\b\.Sat\.\b"] = re.subn(r"\b\.Sat\.\b", r".sat.", python_code)
    python_code, statistics[r"\bmessageFunction\b"] = re.subn(r"\bmessageFunction\b", r"message_function", python_code)
    python_code, statistics[r"\berrorFunction\b"] = re.subn(r"\berrorFunction\b", r"error_function", python_code)

    return python_code, statistics


def convert_file(filename: str) -> None:
    """
    convert a script file

    Args:
        filename (str): filename
    """
    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        content = file.read()
    content, statistics = convert_code(content)
    with open(filename, "w", encoding="utf-8", errors="ignore") as file:
        file.write(content)
    import json

    print(json.dumps(statistics, indent=4))


def cli():
    """
    Command line interface for file conversion.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="file to be converted")
    setup = parser.parse_args(sys.argv[1:])

    try:
        convert_file(setup.filename)
        exit_code = 0
        print("file conversion - finished successfully")
    except Exception:
        import traceback

        exit_code = 1
        print("file conversion - failed")
        print(traceback.format_exc())
    print("Finished file conversion.")
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
