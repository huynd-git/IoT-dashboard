from quixstreams import Application
import pandas as pd
import geocoder

essential_columns = ['Timestamp', 'Src IP', 'Dst IP', 'Protocol', 'TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Flow Duration', 'Tot Fwd Pkts', 'Tot Bwd Pkts']


def enrich_geoip(ip):
    result = {
        'city': None,
        'country': None,
        'latitude': None,
        'longtitude': None
    }

    geo_data = geocoder.ip(ip)
    
    if geo_data.ok:
        result['city'] = geo_data.city
        result['country'] = geo_data.country

        if geo_data.latlng:
            result['latitude'] = geo_data.latlng[0]
            result['longtitude'] = geo_data.latlng[1]
        else:
            result['latitude'] = None
            result['longtitude'] = None    

    return result


def process_row(row):
    # 1. Data Type Conversion

    # Convert 'Timestamp' to datetime format
    row['Timestamp'] = pd.to_datetime(row['Timestamp'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

    row['hour'] = str(row['Timestamp'].hour)
    row['day'] = str(row['Timestamp'].day)
    row['week'] = str(row['Timestamp'].week)
    row['Timestamp'] = str(row['Timestamp'])

    # Convert numerical columns to numeric types (if needed)
    for col in ['TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Flow Duration', 'Tot Fwd Pkts', 'Tot Bwd Pkts']:
        row[col] = float(pd.to_numeric(row[col], errors='coerce'))

    # 2. Missing Value Handling

    # Create a pandas Series from the essential columns of the row
    essential_series = pd.Series(row)

    # Check for missing values in essential columns
    if essential_series.isnull().any():
        return None  # Return None to indicate that the row should be dropped

    # Geo IP enrichment

    # Source IP
    geo_data = enrich_geoip(row['Src IP'])
    if geo_data:
        row['Src_Latitude'] = geo_data['latitude']
        row['Src_Longtidude'] = geo_data['longtitude']
        row['Src_City'] = geo_data['city']
        row['Src_Country'] = geo_data['country']

    # Destination IP
    geo_data = enrich_geoip(row['Dst IP'])
    if geo_data:
        row['Dst_Latitude'] = geo_data['latitude']
        row['Dst_Longtidude'] = geo_data['longtitude']
        row['Dst_City'] = geo_data['city']
        row['Dst_Country'] = geo_data['country']

    return row


def round_up(row):
    row['Data_Transfer_Rate'] = "{:.3f}".format(row['Data_Transfer_Rate'])
    row['Packet_Rate'] = "{:.3f}".format(row['Packet_Rate'])

    return row


app = Application(broker_address="kafka-broker:9092", consumer_group="T-gr1", auto_offset_reset='earliest')

input_topic = app.topic('raw-data')
output_topic = app.topic('transformed-data')

sdf = app.dataframe(input_topic)

sdf = sdf[essential_columns]

sdf = sdf.apply(process_row)

sdf['Total_Data_Transferred'] = sdf["TotLen Fwd Pkts"] + sdf['TotLen Bwd Pkts']

# Calculate data transfer rate and packet rate
sdf['Data_Transfer_Rate'] = (sdf['Total_Data_Transferred'] * 1000000) / sdf['Flow Duration']          # convert millisecond to second
sdf['Packet_Rate'] = ((sdf['Tot Fwd Pkts'] + sdf['Tot Bwd Pkts']) * 1000000) / sdf['Flow Duration']   # convert millisecond to second

sdf = sdf.apply(round_up)

sdf = sdf.update(lambda row: print(row))
sdf = sdf.to_topic(output_topic)

if __name__ == '__main__':
    app.run(sdf)
