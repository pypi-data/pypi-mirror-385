# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Padchest database for computer-aided diagnosis.

A large chest x-ray image dataset with multi-label annotated reports. This
dataset includes more than 160,000 images from 67,000 patients that were
interpreted and reported by radiologists at Hospital San Juan (Spain) from 2009
to 2017, covering six different position views and additional information on
image acquisition and patient demography.

We keep only postero-anterior "PA" images in our setup.

* Reference: :cite:p:`bustos_padchest_2020`
* Raw data input (on disk):

  * PNG grayscale 16-bit depth images
  * Resolution: varying resolution

* Labels: :cite:p:`bustos_padchest_2020`
* Output image:

  * Transforms:

    * Load raw 16-bit PNG with :py:mod:`PIL`
    * Remove excess black borders
    * Convert image to 32-bit floats between 0. and 1.
    * Convert to tensor

  * Final specifications

    * Grayscale, encoded as a 1-plane 32-bit float image, square with
      varying resolutions depending on the raw input image
    * Labels, in order (some of which may not be present in all splits):

      * COPD signs
      * Chilaiditi sign
      * NSG tube
      * abnormal foreign body
      * abscess
      * adenopathy
      * air bronchogram
      * air fluid level
      * air trapping
      * alveolar pattern
      * aortic aneurysm
      * aortic atheromatosis
      * aortic button enlargement
      * aortic elongation
      * aortic endoprosthesis
      * apical pleural thickening
      * artificial aortic heart valve
      * artificial heart valve
      * artificial mitral heart valve
      * asbestosis signs
      * ascendent aortic elongation
      * atelectasis
      * atelectasis basal
      * atypical pneumonia
      * axial hyperostosis
      * azygoesophageal recess shift
      * azygos lobe
      * blastic bone lesion
      * bone cement
      * bone metastasis
      * breast mass
      * bronchiectasis
      * bronchovascular markings
      * bullas
      * calcified adenopathy
      * calcified densities
      * calcified fibroadenoma
      * calcified granuloma
      * calcified mediastinal adenopathy
      * calcified pleural plaques
      * calcified pleural thickening
      * callus rib fracture
      * cardiomegaly
      * catheter
      * cavitation
      * central vascular redistribution
      * central venous catheter
      * central venous catheter via jugular vein
      * central venous catheter via subclavian vein
      * central venous catheter via umbilical vein
      * cervical rib
      * chest drain tube
      * chronic changes
      * clavicle fracture
      * consolidation
      * costochondral junction hypertrophy
      * costophrenic angle blunting
      * cyst
      * dai
      * descendent aortic elongation
      * dextrocardia
      * diaphragmatic eventration
      * double J stent
      * dual chamber device
      * electrical device
      * emphysema
      * empyema
      * end on vessel
      * endoprosthesis
      * endotracheal tube
      * esophagic dilatation
      * exclude
      * external foreign body
      * fibrotic band
      * fissure thickening
      * flattened diaphragm
      * fracture
      * gastrostomy tube
      * goiter
      * granuloma
      * ground glass pattern
      * gynecomastia
      * heart insufficiency
      * heart valve calcified
      * hemidiaphragm elevation
      * hiatal hernia
      * hilar congestion
      * hilar enlargement
      * humeral fracture
      * humeral prosthesis
      * hydropneumothorax
      * hyperinflated lung
      * hypoexpansion
      * hypoexpansion basal
      * increased density
      * infiltrates
      * interstitial pattern
      * kerley lines
      * kyphosis
      * laminar atelectasis
      * lepidic adenocarcinoma
      * lipomatosis
      * lobar atelectasis
      * loculated fissural effusion
      * loculated pleural effusion
      * lung metastasis
      * lung vascular paucity
      * lymphangitis carcinomatosa
      * lytic bone lesion
      * major fissure thickening
      * mammary prosthesis
      * mass
      * mastectomy
      * mediastinal enlargement
      * mediastinal mass
      * mediastinal shift
      * mediastinic lipomatosis
      * metal
      * miliary opacities
      * minor fissure thickening
      * multiple nodules
      * nephrostomy tube
      * nipple shadow
      * nodule
      * non axial articular degenerative changes
      * normal
      * obesity
      * osteopenia
      * osteoporosis
      * osteosynthesis material
      * pacemaker
      * pectum carinatum
      * pectum excavatum
      * pericardial effusion
      * pleural effusion
      * pleural mass
      * pleural plaques
      * pleural thickening
      * pneumomediastinum
      * pneumonia
      * pneumoperitoneo
      * pneumothorax
      * post radiotherapy changes
      * prosthesis
      * pseudonodule
      * pulmonary artery enlargement
      * pulmonary artery hypertension
      * pulmonary edema
      * pulmonary fibrosis
      * pulmonary hypertension
      * pulmonary mass
      * pulmonary venous hypertension
      * reservoir central venous catheter
      * respiratory distress
      * reticular interstitial pattern
      * reticulonodular interstitial pattern
      * rib fracture
      * right sided aortic arch
      * round atelectasis
      * sclerotic bone lesion
      * scoliosis
      * segmental atelectasis
      * single chamber device
      * soft tissue mass
      * sternoclavicular junction hypertrophy
      * sternotomy
      * subacromial space narrowing
      * subcutaneous emphysema
      * suboptimal study
      * superior mediastinal enlargement
      * supra aortic elongation
      * surgery
      * surgery breast
      * surgery heart
      * surgery humeral
      * surgery lung
      * surgery neck
      * suture material
      * thoracic cage deformation
      * total atelectasis
      * tracheal shift
      * tracheostomy tube
      * tuberculosis
      * tuberculosis sequelae
      * unchanged
      * vascular hilar enlargement
      * vascular redistribution
      * ventriculoperitoneal drain tube
      * vertebral anterior compression
      * vertebral compression
      * vertebral degenerative changes
      * vertebral fracture
      * volume loss

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import numpy
import PIL.Image
import torch
from torchvision import tv_tensors
from torchvision.transforms.v2.functional import to_dtype, to_image

from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..image_utils import remove_black_borders
from ..split import JSONDatabaseSplit
from ..typing import RawDataLoader as BaseDataLoader
from ..typing import Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(BaseDataLoader):
    """A specialized raw-data-loader for the PadChest database."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(
                CONFIGURATION_KEY_DATADIR,
                os.path.realpath(os.curdir),
            ),
        )

    def sample(self, sample: typing.Any) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the database root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
            The sample representation.
        """

        # N.B.: PadChest images are encoded as 16-bit grayscale images
        image = PIL.Image.open(self.datadir / sample[0])
        image, _ = remove_black_borders(image)
        image = numpy.array(image).astype(numpy.float32) / 65535
        image = to_dtype(to_image(image), torch.float32, scale=True)
        image = tv_tensors.Image(image)

        # use the code below to view generated images
        # from torchvision.transforms.v2.functional import to_pil_image
        # to_pil_image(tensor).show()
        # __import__("pdb").set_trace()

        return dict(image=image, target=self.target(sample), name=sample[0])

    def target(self, sample: typing.Any) -> torch.Tensor:
        """Load only sample target from its raw representation.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
            The labels corresponding to all radiological signs present in the
            specified sample, encapsulated as a 1D torch float tensor.
        """

        return torch.FloatTensor(sample[1])


class DataModule(CachingDataModule):
    """Padchest database for computer-aided diagnosis.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    """

    def __init__(self, split_path: pathlib.Path | importlib.resources.abc.Traversable):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="classification",
            num_classes=193,
        )
