import logging
from pathlib import Path
from piket import NEDCENC, NEVPK, HEADERFIX
from piket.constants import SIZE_INFO, VPK_SIZE, VPK
from . import _to_bytes, _run_tool

logger = logging.getLogger(__file__)

def encode(
    data: bytes | bytearray | str | Path,
    original: bytes | bytearray | str | Path,
    partial_encode: bool = False,
) -> bytearray:
    # handle all input types
    original = _to_bytes(original)
    original_file = NEDCENC.parent.resolve() / "original.raw"
    logger.debug(f"Writing .raw original to '{original_file}'.")
    original_file.write_bytes(original)

    data = _to_bytes(data)
    data_file = NEDCENC.parent.resolve() / "in.bin"
    logger.debug(f"Writing .bin data to '{data_file}'.")
    data_file.write_bytes(data)

    PARENT = NEDCENC.parent.resolve()

    # decode original raw to use as template
    raw_decoded_path = PARENT / "raw_decoded.bin"
    logger.debug(f"Running nedcenc, output to '{raw_decoded_path}'.")
    _run_tool(f'"{NEDCENC}" -i "{original_file}" -d -o "{raw_decoded_path}"')
    if not raw_decoded_path.exists():
        raise Exception("nedcenc did not output a file.")
    logger.debug(f"Removing '{original_file}'.")
    original_file.unlink()

    decoded = bytearray(raw_decoded_path.read_bytes())
    logger.debug(f"Removing '{raw_decoded_path}'.")
    raw_decoded_path.unlink()

    # compress new data with nevpk
    compressed_path = PARENT / "trimmed.vpk"
    logger.debug(f"Running nevpk, output to '{compressed_path}'.")
    _run_tool(f'"{NEVPK}" -i "{data_file}" -c -o "{compressed_path}"')
    if not compressed_path.exists():
        raise Exception("nevpk did not output a file.")
    logger.debug(f"Removing '{data_file}'.")
    data_file.unlink()

    vpk = compressed_path.read_bytes()
    logger.debug(f"Removing '{compressed_path}'.")
    compressed_path.unlink()
    
    size = len(vpk)
    if size > 0xFFFF:
        raise ValueError(f"VPK size larger than maximum (expected <= 0xFFFF, got {size:#x}).")

    # re-write size info section
    logger.debug("Using template decoded data to build new deocded data.")
    size_info = int.from_bytes(decoded[SIZE_INFO:SIZE_INFO+4], "little")
    size_info = (size_info & ~(0xFFFF << 9)) | ((size + 2) << 9)
    decoded[SIZE_INFO:SIZE_INFO+4] = size_info.to_bytes(4, "little")
    # re-write vpk size
    decoded[VPK_SIZE:VPK_SIZE+2] = size.to_bytes(2, "little")
    # re-write vpk
    for i in range(size):
        decoded[VPK+i] = vpk[i]
    # write incremenetal padding
    for i in range(VPK + size, 0x530):
        decoded[i] = (i - (VPK + size)) % 0x100
    
    decoded_path = PARENT / "decoded.bin"
    logger.debug(f"Writing rebuilt decoded data to '{decoded_path}'.")
    decoded_path.write_bytes(bytes(decoded))
    
    # run headerfix to fix the checksum
    # note that headerfix writes the new file in-place
    logger.debug("Running headerfix, output in-place at '{decoded_path}'.")
    _run_tool(f'"{HEADERFIX}" "{decoded_path}"')

    if partial_encode:
        decoded = decoded_path.read_bytes()
        logger.debug(f"Removing '{decoded_path}'.")
        decoded_path.unlink()
        return bytearray(decoded)

    raw_path = PARENT / "card.raw"
    logger.debug(f"Running nedcenc, output to '{raw_path}'.")
    _run_tool(f'"{NEDCENC}" -i "{decoded_path}" -e -o "{raw_path}"')
    logger.debug(f"Removing '{decoded_path}'.")
    decoded_path.unlink()
    
    raw = raw_path.read_bytes()
    logger.debug(f"Removing '{raw_path}'.")
    raw_path.unlink()
    
    logger.info("Conversion from (.bin + .raw) to .raw complete.")
    return bytearray(raw)
