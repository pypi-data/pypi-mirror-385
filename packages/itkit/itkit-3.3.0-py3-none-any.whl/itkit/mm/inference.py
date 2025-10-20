import os
import pdb
from tqdm import tqdm
from collections import defaultdict
from abc import abstractmethod

import torch
import numpy as np
import SimpleITK as sitk
from torch import Tensor

from mmcv.transforms import Compose
from mmengine.config import Config
from mmengine.registry import MODELS
from mmengine.runner import load_checkpoint
from mmseg.apis.inference import _preprare_data

from ..io.sitk_toolkit import LoadDcmAsSitkImage, sitk_resample_to_size, sitk_resample_to_spacing
from ..process.GeneralPreProcess import SetWindow


INFERENCER_WORK_DIR = "/fileser51/zhangyiqin.sx/mmseg/work_dirs_inferencer/"


class Inferencer:
    def __init__(self, cfg_path, ckpt_path, fp16:bool=False, allow_tqdm:bool=True):
        self.fp16 = fp16
        self.allow_tqdm = allow_tqdm
        self.cfg = Config.fromfile(cfg_path)
        self.model:torch.nn.Module = MODELS.build(self.cfg.model)
        load_checkpoint(self.model, ckpt_path, map_location='cpu')
        self.pipeline = Compose(self.cfg.test_pipeline)
        self.model.eval()
        self.model.cuda()
        self.model.requires_grad_(False)
        if fp16:
            self.model.half()

    @abstractmethod
    @torch.inference_mode()
    def Inference_FromNDArray(self, image_array:np.ndarray) -> Tensor:
        ...
    
    def _preprocess(self, imgs:np.ndarray|list[np.ndarray]) -> tuple[Tensor, dict]:
        is_batch = True
        if not isinstance(imgs, (list, tuple)):
            imgs = [imgs]
            is_batch = False

        data = defaultdict(list)
        for img in imgs:
            initial_dict = {
                'img': img,
                'img_shape': img.shape,
                'ori_shape': img.shape,
            }
            data_:dict[str, Tensor|dict] = self.pipeline(initial_dict)
            data['inputs'].append(data_['inputs'])
            data['data_samples'].append(data_['data_samples'])

        return data, is_batch


class SegInferencer(Inferencer):
    def Inference_FromITK(self, itk_image:sitk.Image) -> tuple[sitk.Image, sitk.Image]:
        image_array = sitk.GetArrayFromImage(itk_image) # [Z, Y, X]
        pred = self.Inference_FromNDArray(image_array) # [Class, Z, Y, X]
        pred = pred.argmax(dim=0).to(dtype=torch.uint8, device='cpu').numpy() # [Z, Y, X]
        itk_pred = sitk.GetImageFromArray(pred)
        itk_pred.CopyInformation(itk_image)
        return itk_image, itk_pred

    def Inference_FromDcm(self, dcm_slide_folder:str, spacing=None):
        image, _, _, _ = LoadDcmAsSitkImage('engineering', dcm_slide_folder, spacing=spacing)
        return self.Inference_FromITK(image)

    def Inference_FromITKFolder(self, folder:str, check_exist_path:str|None=None):
        mha_files = []
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.mha'):
                    if check_exist_path is not None:
                        if os.path.exists(os.path.join(check_exist_path, file)):
                            print(f"Already inferenced: {file}.")
                            continue
                    mha_files.append(os.path.join(root, file))
        
        print(f"\nInferencing from Folder: {folder}, Total {len(mha_files)} mha files.\n")
        
        for mha_path in tqdm(sorted(mha_files),
                             desc='Inference_FromITKFolder',
                             leave=False,
                             dynamic_ncols=True,
                             disable=not self.allow_tqdm):
            itk_image = sitk.ReadImage(mha_path)
            itk_image, itk_pred = self.Inference_FromITK(itk_image)
            tqdm.write(f"Successfully inferenced: {os.path.basename(mha_path)}.")
            yield itk_image, itk_pred, mha_path


class Inferencer_2D(SegInferencer):
    @torch.inference_mode()
    def Inference_FromNDArray(self, image_array:np.ndarray) -> Tensor:
        assert image_array.ndim == 3, "Input image must be (Z,Y,X), got: {}.".format(image_array.shape)
        image_array = [i for i in image_array]
        data, is_batch = self._preprocess(image_array)

        # forward the model
        results = []
        data = self.model.data_preprocessor(data, False)
        inputs = torch.stack(data['inputs'])
        data_samples = [sample.to_dict() for sample in data['data_samples']]
        for array, sample in tqdm(zip(inputs, data_samples),
                                  desc="Inferencing",
                                  total=len(inputs),
                                  dynamic_ncols=True,
                                  leave=False,
                                  mininterval=1,
                                  disable=not self.allow_tqdm):
            result:torch.Tensor = self.model.inference(array[None], [sample])
            results.append(result)

        pred = torch.cat(results, dim=0).transpose(0,1) # [Class, D, H, W]
        return pred


class Inferencer_2D_ONNX(Inferencer_2D):
    def __init__(self, onnx_path):
        import onnxruntime as ort # type: ignore
        self.model = ort.InferenceSession(
            onnx_path,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    
    @torch.inference_mode()
    def Inference_FromNDArray(self, image_array):
        results = []
        for array in tqdm(
                image_array,
                desc="Inferencing",
                total=len(image_array),
                dynamic_ncols=True,
                leave=False,
                mininterval=1,
                disable=not self.allow_tqdm):
            result = self.inference(array)
            results.append(result)
        pred = torch.cat(results, axis=0).transpose(0,1)
        return pred # [Class, D, H, W]

    def forward(self, inputs: np.ndarray) -> Tensor:
        inputs = self._set_window(inputs)[None, None]
        assert inputs.ndim == 4
        result = self.model.run(['OUTPUT__0'], {'INPUT__0': inputs}) # [1,1,5,H,W]
        result = np.array(result).squeeze()[None]
        result = torch.from_numpy(result)
        return result


class Inferencer_3D(SegInferencer):
    def __init__(self, spacings=[None,None,None], sizes=[None,None,None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert len(spacings) == 3, "Spacings must be a list of 3 elements, got: {}.".format(spacings)
        assert len(sizes) == 3, "Sizes must be a list of 3 elements, got: {}.".format(sizes)
        assert not any([spacing is not None and size is not None 
                        for spacing, size in zip(spacings, sizes)]), \
            "Can not specify spacing and size for one dimension at the same time, got spacings: {}, sizes: {}.".format(spacings, sizes)
        self.spacings = spacings
        self.sizes = sizes
    
    @torch.inference_mode()
    def Inference_FromNDArray(self, image_array) -> Tensor:
        data, is_batch = _preprare_data(image_array, self.model)
        data = self.model.data_preprocessor(data, False)
        with torch.autocast('cuda'):
            img_input = data['inputs'][0][None]
            img_meta = [d.to_dict() for d in data['data_samples']]
            seg_result = self.model.inference(img_input, img_meta)
            return seg_result.squeeze(0) # [N, Class, Z, Y, X] -> [Class, Z, Y, X]

    def Inference_FromITK(self, itk_image:sitk.Image) -> tuple[sitk.Image, sitk.Image]:
        if any(self.spacings):
            # the dimension order aligns to Z Y X.
            # complementation on each dimension
            ori_spacing = itk_image.GetSpacing()[::-1]
            ori_size = itk_image.GetSize()[::-1]
            target_spacing = [target or ori for ori, target in zip(ori_spacing, self.spacings)]
            target_size = [target or ori for ori, target in zip(ori_size, self.sizes)]
            # resampling
            if any(self.spacings):
                itk_image = sitk_resample_to_spacing(itk_image, target_spacing, "image")
            if any(self.sizes):
                itk_image = sitk_resample_to_size(itk_image, target_size, "image")
            # inference
            return super().Inference_FromITK(itk_image)


class Inferencer_3D_ONNX(SegInferencer):
    def __init__(
        self, 
        onnx_path,
        patch_size:list[int],
        patch_stride:list[int],
        ww:int,
        wl:int,
        allow_tqdm:bool=True,
        input_dtype=np.float32,
    ):
        import onnxruntime as ort
        self.allow_tqdm = allow_tqdm
        self.ww = ww
        self.wl = wl
        self.model = ort.InferenceSession(
            onnx_path,
            providers=['CUDAExecutionProvider'])
        self.inference_PatchSize = patch_size
        self.inference_PatchStride = patch_stride
        self.input_dtype = input_dtype

    @torch.inference_mode()
    def Inference_FromNDArray(self, image_array: np.ndarray) -> np.ndarray:
        """
        image_array: np.ndarray, shape [Z, Y, X] or [C, Z, Y, X]
        Returns: torch.Tensor, shape [C, Z, Y, X]
        """
        # ONNX expects input shape [N, 1, Z, Y, X]
        if image_array.ndim == 3:
            image_array = image_array[None, None]  # [1, 1, Z, Y, X]
        elif image_array.ndim == 4:
            image_array = image_array[None]        # [1, C, Z, Y, X]
        else:
            raise ValueError(f"Unsupported input shape: {image_array.shape}")
        image_array = SetWindow(image_array, self.ww, self.wl).astype(self.input_dtype)  # [1, C, Z, Y, X]
        seg_logits = self.slide_inference(image_array)
        return seg_logits.squeeze(0)  # [C, Z, Y, X]

    def _forward(self, patch_np: np.ndarray) -> np.ndarray:
        return self.model.run(['OUTPUT__0'], {'INPUT__0': patch_np})[0]

    def slide_inference(self, inputs: np.ndarray) -> np.ndarray:
        """Input [N, C, Z, Y, X], Output[N, C, Z, Y, X]"""
        assert self.inference_PatchSize is not None and self.inference_PatchStride is not None, \
            f"Slide window inference must specify Inference_PatchSize({self.inference_PatchSize}) and inference_PatchStride({self.inference_PatchStride})"
        z_stride, y_stride, x_stride = self.inference_PatchStride
        z_crop, y_crop, x_crop = self.inference_PatchSize
        batch_size, in_channels, z_img, y_img, x_img = inputs.shape

        # use one-time forward to get the output channels
        with torch.no_grad():
            temp_output = self._forward(inputs[:, :, :min(z_crop, z_img), :min(y_crop, y_img), :min(x_crop, x_img)])
            out_channels = temp_output.shape[1]

        # Calculate the grid and initialize temperal array.
        z_grids = max(z_img - z_crop + z_stride - 1, 0) // z_stride + 1
        y_grids = max(y_img - y_crop + y_stride - 1, 0) // y_stride + 1
        x_grids = max(x_img - x_crop + x_stride - 1, 0) // x_stride + 1
        preds = np.zeros((batch_size, out_channels, z_img, y_img, x_img), dtype=np.float16)
        count_mat = np.zeros((batch_size, 1, z_img, y_img, x_img), dtype=np.uint8)
        
        for z_idx in tqdm(range(z_grids),
                          desc="SlideWindow Infer",
                          disable=not self.allow_tqdm,
                          leave=False,
                          dynamic_ncols=True,
                          position=1):
            for y_idx in range(y_grids):
                for x_idx in range(x_grids):
                    z1 = z_idx * z_stride
                    y1 = y_idx * y_stride
                    x1 = x_idx * x_stride
                    z2 = min(z1 + z_crop, z_img)
                    y2 = min(y1 + y_crop, y_img)
                    x2 = min(x1 + x_crop, x_img)
                    z1 = max(z2 - z_crop, 0)
                    y1 = max(y2 - y_crop, 0)
                    x1 = max(x2 - x_crop, 0)
                    crop_vol = inputs[:, :, z1:z2, y1:y2, x1:x2]
                    crop_seg_logit = self._forward(crop_vol).astype(np.float16)
                    preds[:, :, z1:z2, y1:y2, x1:x2] += crop_seg_logit
                    count_mat[:, :, z1:z2, y1:y2, x1:x2] += 1

        assert np.all(count_mat > 0), "There exists some voxels not covered by any patch, check slide inference logic or report this issue plz."
        seg_logits = preds / count_mat
        return seg_logits

    def Inference_FromITK(self, itk_image:sitk.Image) -> tuple[sitk.Image, sitk.Image]:
        itk_image = sitk.DICOMOrient(itk_image, 'LPI')
        image_array = sitk.GetArrayFromImage(itk_image) # [Z, Y, X]
        pred = self.Inference_FromNDArray(image_array)  # [C, Z, Y, X]
        pred = pred.argmax(axis=0).astype(np.uint8) # [Z, Y, X]
        itk_pred = sitk.GetImageFromArray(pred)
        itk_pred.CopyInformation(itk_image)
        return itk_image, itk_pred
