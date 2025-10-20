import logging
import warnings
from datetime import timedelta

import pandas as pd

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")


def chunk_insulin_data(processed_basal: pd.DataFrame) -> pd.DataFrame:
    processed_basal = processed_basal.sort_values(by=['FADTC']).reset_index(drop=True)
    processed_basal['FADTC'] = pd.to_datetime(processed_basal['FADTC'])
    processed_basal['next_timestamp'] = processed_basal['FADTC'].shift(-1)
    processed_basal['FADUR'] = (processed_basal['next_timestamp'] - processed_basal['FADTC']).dt.total_seconds()
    processed_basal = processed_basal.dropna(subset=['FADUR']).reset_index(drop=True)
    processed_basal['insulin_per_second'] = processed_basal['commanded_basal_rate'] / 3600
    processed_basal['FASTRESN'] = processed_basal['insulin_per_second'] * processed_basal['FADUR']

    new_rows = []
    indices_to_remove = []

    for i in range(len(processed_basal)):
        row = processed_basal.iloc[i]

        if row['FADUR'] > 360:
            indices_to_remove.append(i)
            timestamp_current = row['FADTC']
            insulin_per_second = row['insulin_per_second']
            base_basal_rate = row['base_basal_rate']
            time_diff = row['FADUR']
            commanded_basal_rate = row['commanded_basal_rate']

            full_chunks = int(time_diff // 300)
            remainder = time_diff % 300
            for j in range(full_chunks):
                chunk_start = timestamp_current + pd.Timedelta(seconds=j * 300)
                chunk_insulin = insulin_per_second * 300
                new_rows.append({
                    'FADTC': chunk_start,
                    'FASTRESN': chunk_insulin,
                    'INSSTYPE': 'basal_chunk',
                    'FATEST': 'BASAL INSULIN',
                    'FACAT': 'BASAL',
                    'commanded_basal_rate': commanded_basal_rate,
                    'FADUR': 300,
                    'base_basal_rate': base_basal_rate
                })
            if remainder > 0:
                chunk_start = timestamp_current + pd.Timedelta(seconds=full_chunks * 300)
                chunk_insulin = insulin_per_second * remainder
                new_rows.append({
                    'FADTC': chunk_start,
                    'FASTRESN': chunk_insulin,
                    'INSSTYPE': 'basal_chunk',
                    'FATEST': 'BASAL INSULIN',
                    'FACAT': 'BASAL',
                    'commanded_basal_rate': commanded_basal_rate,
                    'FADUR': remainder,
                    'base_basal_rate': base_basal_rate
                })

    chunked_df = pd.DataFrame(new_rows)
    processed_basal = processed_basal.drop(index=indices_to_remove).reset_index(drop=True)
    if not processed_basal.empty:
        if 'INSSTYPE' not in processed_basal.columns:
            processed_basal['INSSTYPE'] = 'basal'
        if 'FATEST' not in processed_basal.columns:
            processed_basal['FATEST'] = 'BASAL INSULIN'
        if 'FACAT' not in processed_basal.columns:
            processed_basal['FACAT'] = 'BASAL'

    chunked_basal_df = pd.concat([processed_basal, chunked_df], ignore_index=True)
    chunked_basal_df = chunked_basal_df.sort_values(by=['FADTC']).reset_index(drop=True)
    if 'next_timestamp' in chunked_basal_df.columns:
        chunked_basal_df = chunked_basal_df.drop(columns=['next_timestamp'])
    if 'insulin_per_second' in chunked_basal_df.columns:
        chunked_basal_df = chunked_basal_df.drop(columns=['insulin_per_second'])
    return chunked_basal_df


def process_extended_bolus_group(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values('event_ts')

    original_value = float(group['original_value'].iloc[0])
    start_time = group['event_ts'].min()
    end_time = group['event_ts'].max()
    total_duration_seconds = (end_time - start_time).total_seconds()

    if total_duration_seconds == 0:
        group['delivered_total'] = original_value / len(group)
        return group

    insulin_per_second = original_value / total_duration_seconds

    time_intervals = []

    timestamps = sorted(group['event_ts'])

    if len(timestamps) > 0:
        first_interval = timestamps[0] - start_time
        time_intervals.append(first_interval.total_seconds())

    for i in range(1, len(timestamps)):
        interval = timestamps[i] - timestamps[i - 1]
        time_intervals.append(interval.total_seconds())

    delivered_amounts = [interval * insulin_per_second for interval in time_intervals]

    for i, amount in enumerate(delivered_amounts):
        group.iloc[i, group.columns.get_loc('delivered_total')] = amount

    return group


def preprocess_basal_data(basal_df: pd.DataFrame) -> pd.DataFrame:
    processed_basal = pd.DataFrame(columns=[
        'FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSSTYPE',
        'commanded_basal_rate', 'base_basal_rate', 'FADUR'
    ])

    if basal_df.empty or 'event_ts' not in basal_df.columns:
        return processed_basal

    try:
        basal_df = basal_df.copy()
        basal_df['event_ts'] = pd.to_datetime(basal_df['event_ts'], format='%Y-%m-%d %H:%M:%S')

        required_cols = ['event_ts', 'commanded_basal_rate', 'base_basal_rate']
        if all(col in basal_df.columns for col in required_cols):
            basal_df = basal_df[required_cols]
            basal_df = basal_df.rename(columns={'event_ts': 'FADTC'})
            basal_df['INSSTYPE'] = 'basal'
            basal_df['FATEST'] = 'BASAL INSULIN'
            basal_df['FACAT'] = 'BASAL'
            processed_basal = basal_df.sort_values(by='FADTC')

            processed_basal = chunk_insulin_data(processed_basal)
            processed_basal = processed_basal[
                ['FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSSTYPE',
                 'commanded_basal_rate', 'base_basal_rate', 'FADUR']]
    except Exception:
        processed_basal = pd.DataFrame(columns=processed_basal.columns)

    return processed_basal


def preprocess_bolus_data(bolus_df: pd.DataFrame) -> pd.DataFrame:
    processed_bolus = pd.DataFrame(columns=[
        'FADTC', 'FATEST', 'FACAT', 'INSNMBOL', 'INSEXBOL',
        'INSSTYPE', 'original_value', 'bolus_id'
    ])

    if bolus_df.empty or 'event_ts' not in bolus_df.columns:
        return processed_bolus

    try:
        bolus_df = bolus_df.copy()
        bolus_df['event_ts'] = pd.to_datetime(bolus_df['event_ts'], format='%Y-%m-%d %H:%M:%S')

        required_cols = ['event_ts', 'requested_later', 'bolus_delivery_status', 'bolus_id', 'delivered_total']
        if not all(col in bolus_df.columns for col in required_cols):
            return processed_bolus

        bolus_df['INSSTYPE'] = bolus_df['requested_later'].apply(lambda x: 'extended' if x != 0 else 'normal')

        # Normal bolus
        normal = bolus_df[
            (bolus_df['INSSTYPE'] == 'normal') &
            (bolus_df['bolus_delivery_status'].isin([0, "Bolus Completed"]))
            ][['event_ts', 'bolus_id', 'delivered_total', 'INSSTYPE']].copy()
        if not normal.empty:
            normal['delivered_total'] = normal['delivered_total'] / 1000
            normal['original_value'] = None

        # Extended bolus
        extended = bolus_df[bolus_df['INSSTYPE'] == 'extended'].copy()
        total_delivered = extended[extended['bolus_delivery_status'] == "Bolus Completed"][
            ['bolus_id', 'delivered_total']
        ].rename(columns={'delivered_total': 'original_value'})

        extended_started = extended[extended['bolus_delivery_status'] == "Bolus Started"]
        processed_ext_list = []
        for bid in extended_started['bolus_id'].unique():
            group = extended_started[extended_started['bolus_id'] == bid].copy()
            group = group.merge(total_delivered, on='bolus_id', how='left')
            if not group.empty:
                processed_group = process_extended_bolus_group(group)
                processed_ext_list.append(processed_group)

        if processed_ext_list:
            extended = pd.concat(processed_ext_list)
            extended['delivered_total'] = extended['delivered_total'] / 1000
            extended['original_value'] = extended['original_value'] / 1000
            extended['INSSTYPE'] = 'extended'
        else:
            extended = pd.DataFrame(columns=['event_ts', 'bolus_id', 'delivered_total', 'original_value', 'INSSTYPE'])

        combined = pd.concat([normal, extended], ignore_index=True)
        if not combined.empty:
            combined = combined.rename(columns={'event_ts': 'FADTC', 'delivered_total': 'INSNMBOL'})
            combined['FATEST'] = 'BOLUS INSULIN'
            combined['FACAT'] = 'BOLUS'
            combined['INSEXBOL'] = combined.apply(
                lambda r: r['INSNMBOL'] if r['INSSTYPE'] == 'extended' else None, axis=1)
            combined['INSNMBOL'] = combined.apply(
                lambda r: r['INSNMBOL'] if r['INSSTYPE'] == 'normal' else None, axis=1)
            processed_bolus = combined[
                ['FADTC', 'FATEST', 'FACAT', 'INSNMBOL', 'INSEXBOL', 'INSSTYPE', 'original_value', 'bolus_id']
            ]
    except Exception:
        processed_bolus = pd.DataFrame(columns=processed_bolus.columns)

    return processed_bolus


def preprocess_carbs_data(carbs_df: pd.DataFrame) -> pd.DataFrame:
    processed_carbs = pd.DataFrame(columns=['MLDTC', 'MLDOSE'])

    if carbs_df.empty or 'event_ts' not in carbs_df.columns or 'carbs' not in carbs_df.columns:
        return processed_carbs

    try:
        carbs_df = carbs_df.copy()
        carbs_df = carbs_df[['event_ts', 'carbs']]
        carbs_df['event_ts'] = pd.to_datetime(carbs_df['event_ts'], format='%Y-%m-%d %H:%M:%S')
        carbs_df = carbs_df.rename(columns={'event_ts': 'MLDTC', 'carbs': 'MLDOSE'})
        processed_carbs = carbs_df.sort_values(by='MLDTC')
    except Exception:
        processed_carbs = pd.DataFrame(columns=processed_carbs.columns)

    return processed_carbs


def preprocess_cgm_data(cgm_df: pd.DataFrame) -> pd.DataFrame:
    processed_glucose = pd.DataFrame(columns=['LBDTC', 'LBORRES'])

    if cgm_df.empty or 'event_ts' not in cgm_df.columns or 'current_glucose_display_value' not in cgm_df.columns:
        return processed_glucose

    try:
        cgm_df = cgm_df.copy()
        cgm_df = cgm_df[['event_ts', 'current_glucose_display_value']]
        cgm_df['event_ts'] = pd.to_datetime(cgm_df['event_ts'], format='%Y-%m-%d %H:%M:%S')
        cgm_df = cgm_df.rename(columns={'event_ts': 'LBDTC', 'current_glucose_display_value': 'LBORRES'})
        processed_glucose = cgm_df.sort_values(by='LBDTC')
    except Exception:
        processed_glucose = pd.DataFrame(columns=processed_glucose.columns)

    return processed_glucose


def preprocess_insulin_data(processed_basal: pd.DataFrame, processed_bolus: pd.DataFrame) -> pd.DataFrame:
    insulin_data_list = []
    if not processed_bolus.empty:
        insulin_data_list.append(processed_bolus)
    if not processed_basal.empty:
        insulin_data_list.append(processed_basal)

    if not insulin_data_list:
        return pd.DataFrame(columns=[
            'FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSNMBOL', 'INSEXBOL',
            'INSSTYPE', 'original_value', 'bolus_id', 'commanded_basal_rate',
            'base_basal_rate', 'FADUR'
        ])

    insulin_df = pd.concat(insulin_data_list).sort_values(by='FADTC')
    required_cols = [
        'FADTC', 'FATEST', 'FACAT', 'FASTRESN', 'INSNMBOL', 'INSEXBOL',
        'INSSTYPE', 'original_value', 'bolus_id', 'commanded_basal_rate',
        'base_basal_rate', 'FADUR'
    ]
    for col in required_cols:
        if col not in insulin_df.columns:
            insulin_df[col] = None
    return insulin_df[required_cols]


def preprocess_user_data(basal_df, bolus_df, carbs_df, cgm_df):
    processed_basal = preprocess_basal_data(basal_df)
    processed_bolus = preprocess_bolus_data(bolus_df)
    processed_carbs = preprocess_carbs_data(carbs_df)
    processed_glucose = preprocess_cgm_data(cgm_df)
    insulin_df = preprocess_insulin_data(processed_basal, processed_bolus)

    return processed_basal, processed_bolus, processed_carbs, processed_glucose, insulin_df


def get_last_x_hr(dataframe: pd.DataFrame, real_time, revert_by: float) -> pd.DataFrame:
    x_hour_ago = pd.to_datetime(real_time) - timedelta(hours=revert_by)
    filtered_df = dataframe[(pd.to_datetime(dataframe['FADTC']) > x_hour_ago) & \
                            (pd.to_datetime(dataframe['FADTC']) < pd.to_datetime(real_time))] \
        .sort_values(by='FADTC', ascending=False)
    return filtered_df


def avg_basal_rate(basal_insulin_data: pd.DataFrame):
    # Expect columns: FADTC, commanded_basal_rate (U/hr)
    df = basal_insulin_data[
        (basal_insulin_data['FACAT'] == 'BASAL') &
        (basal_insulin_data['FATEST'] == 'BASAL INSULIN') &
        (basal_insulin_data['INSSTYPE'].isin(['basal', 'basal_chunk']))
    ].copy()

    if 'base_basal_rate' not in df.columns:
        df['base_basal_rate'] = df.get('commanded_basal_rate', 0)

    df['HOUR'] = pd.to_datetime(df['FADTC']).dt.hour
    hours = pd.DataFrame({'HOUR': range(24)})

    # Build profile from BASE rates, not commanded/delivered
    hourly = df.groupby('HOUR')['base_basal_rate'].last()  # or .mean()
    hours = hours.merge(hourly, on='HOUR', how='left').rename(columns={'base_basal_rate':'RATE'})
    hours['RATE'] = hours['RATE'].fillna(method='ffill').fillna(method='bfill')
    hours.loc[hours['RATE'].isna(), 'RATE'] = 0.0

    basal_profile = [
        {'i': i, 'start': f'{h:02d}:00:00', 'minutes': h*60, 'rate': float(r)}
        for i, (h, r) in enumerate(hours.set_index('HOUR')['RATE'].to_dict().items())
    ]
    profile = {'dia': 5, 'basalprofile': basal_profile}
    return basal_profile, profile


def compute_basal_duration(basal_records: pd.DataFrame) -> pd.DataFrame:
    br = basal_records.sort_values('FADTC').copy()
    br['DURATION'] = (pd.to_datetime(br['FADTC'].shift(-1)) - pd.to_datetime(br['FADTC'])).dt.total_seconds() / 60
    return br


def datetime_to_zoned_iso(time, timezone):
    return time.strftime(f'%Y-%m-%dT%H:%M:%S{timezone}')
