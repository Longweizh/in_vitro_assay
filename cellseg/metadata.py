import os
import pandas as pd
import glob


METADATA_COLUMNS = [
    'figure_name',
    'figure_id',
    'experiment_id',
    'magnification',
    'channel',
    'seeding_density',
    'virus',
    'cargo',
    'dose_vg/well',
    'image_time_h',
    'receptor',
    'include',
    'notes',
]


def scan_images(images_dir):
    if not os.path.isdir(images_dir):
        return []

    tiff_files = sorted(glob.glob(os.path.join(images_dir, '*.tif*')))
    return [os.path.basename(f) for f in tiff_files]



def generate_metadata(tiff_files, default_magnification='4x', 
                                  default_seeding_density=0.5e5):
    if not tiff_files:
        return pd.DataFrame(columns=METADATA_COLUMNS)
    
    df_metadata = pd.DataFrame({
        'figure_name': tiff_files,
        'figure_id': list(range(1, len(tiff_files) + 1)),
        'experiment_id': [1] * len(tiff_files),
        'magnification': [default_magnification] * len(tiff_files),
        'channel': [''] * len(tiff_files),
        'seeding_density': [default_seeding_density] * len(tiff_files),
        'virus': [''] * len(tiff_files),
        'cargo': ['EGFP'] * len(tiff_files),
        'dose_vg/well': [0.0] * len(tiff_files),
        'image_time_h': [0] * len(tiff_files),
        'receptor': [''] * len(tiff_files),
        'include': [1] * len(tiff_files),
        'notes': [''] * len(tiff_files)
    })
    
    return df_metadata


def metadata(data_dir, verbose=True):
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    metadata_file = os.path.join(data_dir, 'metadata.csv')
    images_dir = os.path.join(data_dir, 'images')
    if not os.path.isdir(images_dir):
        images_dir = data_dir
    
    if verbose:
        print(f"Looking for metadata file at: {metadata_file}")
        print(f"Looking for images in: {images_dir}")
    
    # Try to load existing metadata
    if os.path.exists(metadata_file):
        df_metadata = pd.read_csv(metadata_file)
        if verbose:
            print(f"✓ Found and loaded metadata file ({len(df_metadata)} rows)")
        return df_metadata
    
    # Generate metadata from TIFF files
    if verbose:
        print(f"✗ Metadata file not found. Scanning for TIFF files...")
    
    tiff_files = scan_images(images_dir)
    
    if verbose:
        print(f"✓ Found {len(tiff_files)} TIFF files")
        if tiff_files:
            print(f"  Files: {tiff_files}")
    
    # Generate metadata from found files
    df_metadata = generate_metadata(tiff_files)
    if df_metadata.empty:
        raise FileNotFoundError(
            f"No TIFF files found in {images_dir}. "
            "Create metadata.csv manually or place TIFF files in the data directory."
        )
    
    # Save generated metadata
    os.makedirs(data_dir, exist_ok=True)
    df_metadata.to_csv(metadata_file, index=False)
    
    if verbose:
        print(f"✓ Generated and saved metadata to: {metadata_file}")
    
    return df_metadata
