import os, argparse, json, pdb
from pathlib import Path
from tqdm import tqdm

import numpy as np
import SimpleITK as sitk
from itkit.process.base_processor import DatasetProcessor


def parse_patch_size(patched_dataset_folder: str | Path) -> list[int]:
    patched_dataset_meta = Path(patched_dataset_folder) / 'crop_meta.json'
    if not patched_dataset_meta.exists():
        raise FileNotFoundError(f"Patched dataset meta file not found: {patched_dataset_meta}, cannot determine patch size.")

    return json.load(open(patched_dataset_meta, 'r'))['patch_size']


class PatchProcessor(DatasetProcessor):
    def __init__(self,
                 source_folder: Path | str,
                 dst_folder: Path | str,
                 patch_size: int | list[int],
                 patch_stride: int | list[int],
                 min_fg: float,
                 keep_empty_label_prob: float,
                 still_save: bool,
                 mp: bool = False,
                 workers: int | None = None):
        super().__init__(str(source_folder), str(dst_folder), mp, workers, recursive=True) # Patch extraction is inherently recursive
        self.patch_size = patch_size
        self.patch_stride = patch_stride
        self.min_fg = min_fg
        self.keep_empty_label_prob = keep_empty_label_prob
        self.still_save = still_save
        # Prepare global image/ and label/ output directories under destination
        self.image_dir = Path(self.dest_folder) / "image"
        self.label_dir = Path(self.dest_folder) / "label"
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.label_dir.mkdir(parents=True, exist_ok=True)

    def extract_patches(self,
                        image: sitk.Image,
                        label: sitk.Image | None,
                        patch_size: int | list[int],
                        patch_stride: int | list[int],
                        minimum_foreground_ratio: float,
                        still_save_when_no_label: bool) -> list[tuple[sitk.Image, sitk.Image | None]]:
        # Simplified version
        no_label = (label is None)
        img_arr = sitk.GetArrayFromImage(image)
        if no_label:
            lbl_arr = None
        else:
            lbl_arr = sitk.GetArrayFromImage(label)
        
        def to_triplet(x):
            if isinstance(x, int):
                return (x, x, x)
            if isinstance(x, (list, tuple)) and len(x) == 3:
                return tuple(x)
            raise ValueError('patch_size and patch_stride must be int or 3-length list/tuple')
        pZ, pY, pX = to_triplet(patch_size)
        sZ, sY, sX = to_triplet(patch_stride)
        Z, Y, X = img_arr.shape
        if pZ > Z or pY > Y or pX > X:
            return []
        
        origin = image.GetOrigin()
        spacing = image.GetSpacing()
        direction = image.GetDirection()
        
        def compute_starts(L, p, s):
            starts = list(range(0, L - p + 1, s))
            if starts[-1] != L - p:
                starts.append(L - p)
            return starts
        z_starts = compute_starts(Z, pZ, sZ)
        y_starts = compute_starts(Y, pY, sY)
        x_starts = compute_starts(X, pX, sX)
        
        patches = []
        for z in z_starts:
            for y in y_starts:
                for x in x_starts:
                    img_patch_np = img_arr[z:z+pZ, y:y+pY, x:x+pX]
                    save = True
                    if no_label:
                        if not still_save_when_no_label:
                            save = False
                        lbl_patch_np = None
                    else:
                        lbl_patch_np = lbl_arr[z:z+pZ, y:y+pY, x:x+pX]
                        fg_ratio = np.sum(lbl_patch_np > 0) / lbl_patch_np.size
                        if (fg_ratio < minimum_foreground_ratio):
                            save = False
                        if fg_ratio == 0 and (np.random.rand() > self.keep_empty_label_prob):
                            save = False
                    
                    if save:
                        img_patch = sitk.GetImageFromArray(img_patch_np)
                        new_origin = (
                            origin[0] + x * spacing[0],
                            origin[1] + y * spacing[1],
                            origin[2] + z * spacing[2]
                        )
                        img_patch.SetOrigin(new_origin)
                        img_patch.SetSpacing(spacing)
                        img_patch.SetDirection(direction)
                        
                        if no_label:
                            lbl_patch = None
                        else:
                            lbl_patch = sitk.GetImageFromArray(lbl_patch_np)
                            lbl_patch.SetOrigin(new_origin)
                            lbl_patch.SetSpacing(spacing)
                            lbl_patch.SetDirection(direction)
                        
                        patches.append((img_patch, lbl_patch))
        return patches

    def process_one(self, args: tuple[str, str]) -> dict | None:
        img_path, lbl_path = args
        case_name = os.path.basename(self._normalize_filename(img_path))

        try:
            image = sitk.ReadImage(str(img_path))
            label = sitk.ReadImage(str(lbl_path))
            img_arr = sitk.GetArrayFromImage(image)
            
            if not self.is_valid_sample(image, label):
                return None
            
            class_within_patch = {}
            patches = self.extract_patches(image, label, self.patch_size, self.patch_stride, self.min_fg, self.still_save)
            for idx, (img_patch, lbl_patch) in enumerate(patches):
                # Use unified filenames across image/ and label/ dirs so they correspond 1:1
                fname_base = f"{case_name}_p{idx}.mha"
                # Save image patch
                sitk.WriteImage(img_patch, str(self.image_dir / fname_base), True)
                if lbl_patch is not None:
                    # Log unique classes in this patch
                    class_within_patch[fname_base] = np.unique(sitk.GetArrayFromImage(lbl_patch)).tolist()
                    # Save label patch
                    sitk.WriteImage(lbl_patch, str(self.label_dir / fname_base), True)
            
            # Simplified per-series meta (no per-patch child meta and no per-case JSON file)
            series_meta = {
                "series_id": case_name,
                "shape": list(img_arr.shape),
                "num_patches": len(patches),
                "anno_available": True,
                "class_within_patch": class_within_patch
            }
            
            return {case_name: series_meta}
        
        except Exception as e:
            tqdm.write(f"Failed processing case {case_name}: {e}")
            return None

    def is_valid_sample(self, itk_img: sitk.Image, itk_lbl: sitk.Image) -> bool:
        img_size = itk_img.GetSize()
        lbl_size = itk_lbl.GetSize()
        if not np.allclose(img_size, lbl_size, atol=1.5):
            tqdm.write(f"Skipping for Size mismatch img size {img_size} | lbl size {lbl_size}.")
            return False
        
        img_spacing = itk_img.GetSpacing()
        lbl_spacing = itk_lbl.GetSpacing()
        if not np.allclose(img_spacing, lbl_spacing, atol=0.01):
            tqdm.write(f"Skipping for Spacing mismatch img spacing {img_spacing} | lbl spacing {lbl_spacing}.")
            return False
        
        if img_size[0] != img_size[1]:
            tqdm.write(f"Skipping for Non-isotropic size img size {img_size}.")
            return False
        
        return True


def parse_args():
    parser = argparse.ArgumentParser(description="Extract patches from a folder of MHA images")
    parser.add_argument('src_folder', type=Path,
                        help='Folder containing `image` and `label` subfolders')
    parser.add_argument('dst_folder', type=Path,
                        help='Destination root folder to save patches')
    parser.add_argument('--patch-size', type=int, nargs='+', required=True,
                        help='Patch size as int or three ints (Z Y X)')
    parser.add_argument('--patch-stride', type=int, nargs='+', required=True,
                        help='Patch stride as int or three ints (Z Y X)')
    parser.add_argument('--minimum-foreground-ratio', type=float, default=0.0,
                        help='Minimum label foreground ratio to keep patch')
    parser.add_argument('--keep-empty-label-prob', type=float, default=1.0,
                         help='Probability to keep patches that contain only background (0.0-1.0)')
    parser.add_argument('--still-save-when-no-label', action='store_true',
                        help='If label missing, still extract patches unconditionally')
    parser.add_argument('--mp', action='store_true',
                        help='Use multiprocessing to process cases')
    parser.add_argument("--workers", type=int, default=None, help="The number of workers for multiprocessing.")
    return parser.parse_args()


def main():
    args = parse_args()
    
    processor = PatchProcessor(
        source_folder = args.src_folder,
        dst_folder = args.dst_folder,
        patch_size = args.patch_size,
        patch_stride = args.patch_stride,
        min_fg = args.minimum_foreground_ratio,
        keep_empty_label_prob = args.keep_empty_label_prob,
        still_save = args.still_save_when_no_label,
        mp = args.mp,
        workers = args.workers
    )
    
    results: dict = {}
    try:
        results = processor.process("Patching")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        results = processor.meta
    
    finally:
        # Write overall crop metadata
        valid_series = list(results.keys())
        crop_meta = {
            "src_folder": str(args.src_folder),
            "dst_folder": str(args.dst_folder),
            "patch_size": args.patch_size,
            "patch_stride": args.patch_stride,
            "anno_available": valid_series,
            "patch_meta": results
        }
        os.makedirs(args.dst_folder, exist_ok=True)
        with open(args.dst_folder / "crop_meta.json", "w") as f:
            json.dump(crop_meta, f, indent=4)


if __name__ == '__main__':
    main()
