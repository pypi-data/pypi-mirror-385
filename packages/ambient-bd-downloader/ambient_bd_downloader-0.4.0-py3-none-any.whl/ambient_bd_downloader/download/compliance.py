import datetime
import pandas as pd


class ComplianceChecker:

    def __init__(self, flag_shorter_than_hours: float = 5):
        self.flag_shorter_than_hours = flag_shorter_than_hours

    def aggregate_session_records(self, records: pd.DataFrame) -> pd.DataFrame:

        records['session_end'] = pd.to_datetime(records['session_end'], format='ISO8601', utc=True)
        records['night_date'] = records['session_end'].dt.date

        stats = records.groupby('night_date').agg(
            number_of_long_sessions=('id', 'count'),
            max_time_in_bed_h=('time_in_bed', 'max'),
            max_time_asleep_h=('time_asleep', 'max'),
            total_sleep_time_h=('time_asleep', 'sum')
        ).reset_index()

        stats['max_time_asleep_h'] = (stats['max_time_asleep_h'] / 3600).round(2)
        stats['max_time_in_bed_h'] = (stats['max_time_in_bed_h'] / 3600).round(2)
        stats['total_sleep_time_h'] = (stats['total_sleep_time_h'] / 3600).round(2)
        stats['valid'] = stats['total_sleep_time_h'] >= self.flag_shorter_than_hours

        return stats

    def add_missing_nights(self, compliance_info, start_date, end_date) -> pd.DataFrame:

        # if end_date is not a datetime object, convert it to one
        if not isinstance(end_date, datetime.date):
            end_date = pd.to_date(end_date)
        if not isinstance(start_date, datetime.date):
            start_date = pd.to_date(start_date)

        range = set(pd.date_range(start_date, end_date, freq='D').date)
        missing_dates = range.difference(compliance_info['night_date'])

        missing_nights = pd.DataFrame(missing_dates, columns=['night_date'])
        missing_nights['valid'] = False
        missing_nights['number_of_long_sessions'] = 0
        missing_nights['max_time_asleep_h'] = 0
        missing_nights['max_time_in_bed_h'] = 0
        missing_nights['total_sleep_time_h'] = 0

        stats = pd.concat([compliance_info, missing_nights], ignore_index=True)
        return stats

    def calculate_compliance(self, records: pd.DataFrame, dates) -> pd.DataFrame:
        start_date = dates[0]
        end_date = dates[1]

        compliance_info = self.aggregate_session_records(records)
        compliance_info = self.add_missing_nights(compliance_info, start_date, end_date)
        compliance_info = compliance_info.sort_values('night_date', ascending=True)

        return compliance_info
