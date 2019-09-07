from typing import Generator

from influxdb import InfluxDBClient


class InfluxDB(InfluxDBClient):
    @property
    def database(self):
        class Database:
            switch = self.switch_database
            create = self.create_database
            drop = self.drop_database
            all = self.get_list_database

        return Database()

    @property
    def user(self):
        class User:
            switch = self.switch_user
            create = self.create_user
            drop = self.drop_user
            all = self.get_list_users
            password = self.set_user_password

        return User()

    @property
    def policy(self):
        class RetentionPolicy:
            alter = self.alter_retention_policy
            create = self.create_retention_policy
            drop = self.drop_retention_policy
            all = self.get_list_retention_policies

        return RetentionPolicy()

    @property
    def measurement(self):
        class Measurement:
            tag_values = self._tag_values
            tag_keys = self._tag_keys
            drop = self.drop_measurement
            all = self.get_list_measurements

        return Measurement()

    def _tag_values(self, measurement: str, key: str, *args, **kwargs) -> Generator:
        """
        Returns generator with tag's values for measurement.
        :param measurement: name of the measurement
        :param key: tag key
        :return:
        """
        q = f"SHOW TAG VALUES ON {self._database} FROM {measurement} WITH KEY = {key}"
        result = self.query(query=q, *args, **kwargs)
        values = (p["value"] for p in result.get_points())
        return values

    def _tag_keys(self, measurement: str, *args, **kwargs) -> Generator:
        """
        Returns generator with tag's keys for measurement.
        :param measurement: name of the measurement
        :return:
        """
        q = f"SHOW TAG KEYS ON {self._database} FROM {measurement}"
        result = self.query(query=q, *args, **kwargs)
        keys = (p["tagKey"] for p in result.get_points())
        return keys
