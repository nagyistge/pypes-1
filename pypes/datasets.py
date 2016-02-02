# -*- coding: utf-8 -*-
"""
Functions to create pipelines for public and not so public available datasets.
"""

import os.path as op

from   .run  import in_out_workflow, in_out_crumb_wf
from   .anat import attach_spm_anat_preprocessing
from   .pet  import attach_spm_mrpet_preprocessing


def cobre_workflow(wf_name, base_dir, cache_dir, output_dir, subject_ids=None):
    """ Returns a workflow for the COBRE database.

    Parameters
    ----------
    wf_name: str
        A name for the workflow.

    base_dir: str
        The folder path where the raw data is.

    cache_dir: str
        The working directory of the workflow.

    output_dir: str
        The output folder path

    subject_ids: list of str
        A list of the subjects IDs that you want to process.
    """

    data_dir = base_dir
    if not data_dir or not op.exists(data_dir):
        raise IOError("Expected an existing folder for `data_dir`, got {}.".format(data_dir))

    wfs = {"spm_anat_preproc": attach_spm_anat_preprocessing,
           # TODO: "spm_rest_preproc": attach_rest_preprocessing,
          }

    if wf_name not in wfs:
        raise ValueError("Expected `wf_name` to be in {}, got {}.".format(list(wfs.keys()),
                                                                          wf_name))

    # check some args
    if not output_dir:
        output_dir = op.join(op.dirname(data_dir), "out")

    if not cache_dir:
        cache_dir = op.join(op.dirname(data_dir), "wd")

    # generate the workflow
    main_wf = in_out_workflow(work_dir=cache_dir,
                              data_dir=data_dir,
                              output_dir=output_dir,
                              session_names=['session_1'],
                              file_names={'anat': 'anat_1/mprage.nii.gz',
                                          'rest': 'rest_1/rest.nii.gz'},
                              subject_ids=subject_ids,
                              input_wf_name='input_files')

    wf = wfs[wf_name](main_wf=main_wf)

    # move the crash files folder elsewhere
    wf.config["execution"]["crashdump_dir"] = op.join(wf.base_dir, wf.name, "log")

    return wf


def clinical_workflow(wf_name, base_dir, cache_dir, output_dir, subject_ids, **kwargs):
    """ Run a specific pipeline.

    Parameters
    ----------
    wf_name: str
        A name for the workflow.

    base_dir: hansel.Crumb or str
        The folder path structure where the raw data is.
        For example: Crumb('/home/hansel/data/clinical/raw/{year}/{subject_ids}/')

    cache_dir: str
        The working directory of the workflow.

    output_dir: str
        The output folder path

    subject_ids: list of str
        A list of the subjects IDs that you want to process.
    """
    year = kwargs.get('year', '')

    if not year:
        data_dir = base_dir
    else:
        data_dir = op.join(base_dir, year)

    if not data_dir or not op.exists(data_dir):
        raise IOError("Expected an existing folder for `data_dir`, got {}.".format(data_dir))

    wfs = {"spm_anat_preproc": attach_spm_anat_preprocessing,
           "spm_mrpet_preproc": attach_spm_mrpet_preprocessing,
          }

    if wf_name not in wfs:
        raise ValueError("Expected `wf_name` to be in {}, got {}.".format(list(wfs.keys()),
                                                                          wf_name))

    # check some args
    if not output_dir:
        output_dir = op.join(op.dirname(data_dir), "out", year)

    if not cache_dir:
        cache_dir = op.join(op.dirname(data_dir), "wd", year)

    # generate the workflow
    main_wf = in_out_workflow(work_dir=cache_dir,
                              data_dir=data_dir,
                              output_dir=output_dir,
                              session_names=['session_0'],
                              file_names={'anat': 'anat_hc.nii.gz',
                                          'pet': 'pet_fdg.nii.gz',
                                          'diff': 'diff.nii.gz',},
                              subject_ids=subject_ids,
                              input_wf_name='input_files')

    wf = wfs[wf_name](main_wf=main_wf)

    # move the crash files folder elsewhere
    wf.config["execution"]["crashdump_dir"] = op.join(wf.base_dir, wf.name, "log")

    return wf



def clinical_crumb_workflow(wf_name, data_crumb, cache_dir, output_dir='', **kwargs):
    """ Run a specific pipeline.

    Parameters
    ----------
    wf_name: str
        A name for the workflow.

    data_crumb: hansel.Crumb
        The crumb until the subject files.
        Example: Crumb('/home/hansel/data/{subject_id}/{session_id}/{modality}/{image_file})
        The last crumb argument of `data_crumb` must be '{image}', which indicates each of the
        subject/session files. This argument will be replaced by the corresponding image name.

    cache_dir: str
        The working directory of the workflow.

    output_dir: str
        The output folder path

    kwargs: keyword arguments
        Keyword arguments with values for the data_crumb crumb path.
    """
    if kwargs:
        data_crumb = data_crumb.replace(**kwargs)

    if not data_crumb.exists():
        raise IOError("Expected an existing folder for `data_crumb`, got {}.".format(data_crumb))

    wfs = {"spm_anat_preproc": attach_spm_anat_preprocessing,
           "spm_mrpet_preproc": attach_spm_mrpet_preprocessing,
          }

    if wf_name not in wfs:
        raise ValueError("Expected `wf_name` to be in {}, got {}.".format(list(wfs.keys()),
                                                                          wf_name))

    if not cache_dir:
        cache_dir = op.join(op.dirname(output_dir), "wd")

    # generate the workflow
    main_wf = in_out_crumb_wf(work_dir=cache_dir,
                              data_crumb=data_crumb,
                              output_dir=output_dir,
                              crumb_arg_values=dict(**kwargs),
                              files_crumb_args={'anat': [('image', 'anat_hc.nii.gz')],
                                                'pet':  [('image', 'pet_fdg.nii.gz')],
                                                #'diff': [('image', 'diff.nii.gz')],
                                               },
                              input_wf_name='input_files')

    wf = wfs[wf_name](main_wf=main_wf)

    # move the crash files folder elsewhere
    wf.config["execution"]["crashdump_dir"] = op.join(wf.base_dir, wf.name, "log")

    return wf
