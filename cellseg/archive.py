
def overlap_quant(im1, im2, min_red_area = 5000):
    """
    im1: red/reference signal
    im2: green/query signal

    Calculate how much im2 signal is inside im1 signal.
    """

    signal_areas_1, signal_total_area_1 = signal_segmentation(im1)
    signal_areas_2, signal_total_area_2 = signal_segmentation(im2)

    # If red or green cannot be segmented / no positive area
    if signal_total_area_1 < min_red_area or signal_total_area_2 == 0:
        return {
            'Red Area': signal_total_area_1,
            'Green Area': signal_total_area_2,
            'Overlap Area': 0,
            'Green in Red Fraction': np.nan,
            'Green in Red Percent': np.nan,
            'Green Brightness in Red': np.nan,
            'Green Mean Brightness in Red': np.nan,
        }

    overlap_mask = signal_areas_1 & signal_areas_2
    overlap_area = np.sum(overlap_mask)

    green_in_red_fraction = overlap_area / signal_total_area_1

    green_brightness_in_red = np.sum(im2[overlap_mask])

    green_mean_brightness_in_red = (
        green_brightness_in_red / overlap_area
        if overlap_area > 0 else np.nan
    )

    return {
        'Red Area': signal_total_area_1,
        'Green Area': signal_total_area_2,
        'Overlap Area': overlap_area,
        'Green in Red Fraction': green_in_red_fraction,
        'Green in Red Percent': green_in_red_fraction * 100,
        'Green Brightness in Red': green_brightness_in_red,
        'Green Mean Brightness in Red': green_mean_brightness_in_red,
    }

def bf_quant(im_bf, im_sig, bf_gauss_sigma = 30, truncate = 0.35, dark_thresh = 10000, light_thresh = 3000, disk_radius = 2, sig_gauss_sigma = 100, sig_thresh = 1000, min_size = 5, h_max = 0.01, collected_percentiles = [5,95]):
    brightfield_areas, total_area = brightfield_segmentation(im_bf, bf_gauss_sigma, truncate, dark_thresh, light_thresh, disk_radius)
    signal_areas, signal_total_area = signal_segmentation(im_sig, sig_gauss_sigma, sig_thresh, min_size)
    print(f"Signal area: {signal_total_area}")
    
    original_sig = signal_areas*im_sig
    
    total_brightness = np.sum(np.sum(original_sig))
    
    #Determine the local maxima, considering pixels above the originally obtained threshold
    image_max = skimage.morphology.h_maxima(im_sig, h_max)

    #Label the maxima
    maxima = skimage.measure.label(image_max)

    #Using the labeled maxima, watershed the intensity in the original image
    labels = watershed(signal_areas, maxima, mask = signal_areas)

    im_labeled, n_labels = skimage.measure.label(labels, background=0, return_num=True)
    
    cell_list, cell_intensity_list = brightness_counter(im_labeled, im_sig)

    
    if len(cell_list) > 0:
        
        median = np.median(list(cell_intensity_list.values()))
        nintyfifth = np.percentile(list(cell_intensity_list.values()), collected_percentiles[1])
        fifth = np.percentile(list(cell_intensity_list.values()), collected_percentiles[0])

        return(n_labels, cell_list, cell_intensity_list, total_area, signal_total_area, total_brightness, median, nintyfifth, fifth)
    
    else: 
        return(n_labels, cell_list, cell_intensity_list, total_area, signal_total_area, total_brightness, [], [], [])
