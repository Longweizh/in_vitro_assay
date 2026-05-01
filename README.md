# README

## Quantification Pipeline of Fluorescent Cells within in vitro images

This pipeline can be used to perform analysis and quantification on images of in vitro images to determine how many fluorescent cells are present as a fraction of the total number of cells. The median brightness of those cells can subsequently be determined.

## Motivation

Quantification of in vitro transduction requires robust and reproducible pipelines. Due to significant variability in the DAPI signal in our images, a workflow to convert brightfield and signal images into masks was created.

## Workflow

1. Convert brightfield and signal images into masks.
2. Perform quantification of the number of cells and their median brightness using the generated masks.
3. Perform statistical analysis and visualization of the results.

The directory structure of the project is as follows:

```
data/
├── metadata.csv
├── images/
│   ├── 1_bf.tif
│   ├── 1_r.tif
│   ├── 2_0.tif
│   └── ...

## metadata.csv
figure_name,figure_id,channel,seeding_density,virus,cargo,dose_vg/well,image_time_h,receptor,include,notes
1_bf.tif,1,brightfield,0.5e5,AAV9,EGFP,0.5e10,24,EGFRvIII,1,
1_r.tif,1,brightfield,0.5e5,AAV9,EGFP,0.5e10,24,EGFRvIII,1,
```

## Notebooks

- `Demo.ipynb`: A demonstration of how to load or generate metadata using the `cellseg` library.
- `mask_check.ipynb`: A notebook to check the generated masks for the brightfield and signal images.

## Acknowledgements

This project was developed by Longwei Zhang in the Jang Lab at the University of Illinois. The code and methodologies were inspired by various sources in the field of image analysis and cell segmentation.