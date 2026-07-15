import gzip
import glob
import struct
from pathlib import Path

import numpy as np


ROI_DIR = glm_dir = Path("/Users/alex/university/Neuroscience_Master/short-term internship/derivatives_MNIcohort3/mask")


DTYPES = {
    2: ("u1", 1),
    4: ("i2", 2),
    8: ("i4", 4),
    16: ("f4", 4),
    64: ("f8", 8),
    256: ("i1", 1),
    512: ("u2", 2),
    768: ("u4", 4),
}


def read_nifti_mask(path):
    raw = gzip.open(path, "rb").read()
    sizeof_hdr_le = struct.unpack("<i", raw[:4])[0]
    endian = "<" if sizeof_hdr_le == 348 else ">"

    dims = struct.unpack(endian + "8h", raw[40:56])
    shape = tuple(int(v) for v in dims[1 : 1 + dims[0]])
    datatype = struct.unpack(endian + "h", raw[70:72])[0]
    vox_offset = int(struct.unpack(endian + "f", raw[108:112])[0])
    sform_code = struct.unpack(endian + "h", raw[254:256])[0]

    if datatype not in DTYPES:
        raise ValueError(f"Unsupported datatype {datatype} in {path}")

    dtype_code, nbytes = DTYPES[datatype]
    dtype = np.dtype(endian + dtype_code)
    count = int(np.prod(shape))
    data = np.frombuffer(raw, dtype=dtype, count=count, offset=vox_offset)
    data = data.reshape(shape, order="F")

    if sform_code > 0:
        srow_x = struct.unpack(endian + "4f", raw[280:296])
        srow_y = struct.unpack(endian + "4f", raw[296:312])
        srow_z = struct.unpack(endian + "4f", raw[312:328])
        affine = np.array([srow_x, srow_y, srow_z, [0, 0, 0, 1]], dtype=float)
    else:
        pixdim = struct.unpack(endian + "8f", raw[76:108])
        affine = np.diag([pixdim[1], pixdim[2], pixdim[3], 1.0])

    return data, affine


def mask_stats(path):
    data, affine = read_nifti_mask(path)
    ijk = np.column_stack(np.nonzero(data > 0))
    xyz = np.c_[ijk, np.ones(len(ijk))] @ affine.T
    xyz = xyz[:, :3]
    centroid = xyz.mean(axis=0)
    bbox_center = (xyz.min(axis=0) + xyz.max(axis=0)) / 2
    radius_centroid = np.linalg.norm(xyz - centroid, axis=1).max()
    radius_bbox = np.linalg.norm(xyz - bbox_center, axis=1).max()
    return {
        "name": Path(path).name.replace("_sphere.nii.gz", ""),
        "n_voxels": len(ijk),
        "centroid": centroid,
        "bbox_center": bbox_center,
        "radius_centroid": radius_centroid,
        "radius_bbox": radius_bbox,
    }


def main():
    for path in sorted(glob.glob(str(ROI_DIR / "*_sphere.nii.gz"))):
        s = mask_stats(path)
        c = s["centroid"]
        b = s["bbox_center"]
        print(
            f"{s['name']},"
            f" n_voxels={s['n_voxels']},"
            f" centroid=({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}),"
            f" bbox_center=({b[0]:.2f}, {b[1]:.2f}, {b[2]:.2f}),"
            f" radius_max_from_centroid={s['radius_centroid']:.2f},"
            f" radius_max_from_bbox_center={s['radius_bbox']:.2f}"
        )


if __name__ == "__main__":
    main()
