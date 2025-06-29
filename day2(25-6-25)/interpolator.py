import pandas as pd
import numpy as np
from config import INTERPOLATION_NEAREST_K, REGIONAL_ADJUSTMENT_FACTOR, SERVICES
from us import states

def interpolate_city(target, city_df):
    """
    Given a target city with missing values and a DataFrame of cities with complete pricing,
    perform KNN geographic + regional adjustment interpolation.
    """
    # Determine the number of samples to take, ensuring it does not exceed available data
    n_samples_available = len(city_df)
    if target.name in city_df.index:
        n_samples_available -= 1

    if n_samples_available <= 0:
        return {svc: None for svc in SERVICES} # Cannot interpolate if no other data is available

    k = min(INTERPOLATION_NEAREST_K, n_samples_available)

    # Simplification: group by state, use nearest K by cost-of-living
    state = target['state']
    regional = city_df[city_df.state == state]
    
    # Exclude the target city itself from the pool of potential neighbors
    if target.name in regional.index:
        regional = regional.drop(target.name)

    # Decide whether to sample from regional or national data
    if len(regional) >= k:
        sample = regional.sample(k)
    else:
        # Fallback to national pool, excluding the target city
        national_pool = city_df.drop(target.name, errors='ignore')
        k_national = min(k, len(national_pool))
        if k_national > 0:
            sample = national_pool.sample(k_national)
        else:
            return {svc: None for svc in SERVICES} # No data to sample from

    interpolated = {}
    for svc in SERVICES:
        # Only calculate for services that are actually missing
        if pd.isna(target.get(svc)):
            vals = sample[svc].dropna()
            if not vals.empty:
                avg = vals.mean()
                interp = avg * REGIONAL_ADJUSTMENT_FACTOR
                interpolated[svc] = round(interp, 2)
            else:
                interpolated[svc] = None
    return interpolated
