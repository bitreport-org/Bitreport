from config import BaseConfig, Production, Test, Development


class TestConfig:
    def test_base(self):
        config = BaseConfig
        assert config.MARGIN > 0
        assert config.MAGIC_LIMIT >= 79
        assert not config.SENTRY
        assert not config.TESTING

    def test_production(self):
        config = Production
        assert not config.ADMIN_ENABLED
        assert not config.DEVELOPMENT
        assert not config.DEBUG
        assert not config.TESTING
        assert config.SENTRY

    def test_development(self):
        config = Development
        assert config.ADMIN_ENABLED
        assert config.DEVELOPMENT
        assert config.DEBUG
        assert not config.TESTING
        assert not config.SENTRY

    def test_test(self):
        config = Test
        assert config.ADMIN_ENABLED
        assert not config.DEVELOPMENT
        assert not config.DEBUG
        assert config.TESTING
        assert not config.SENTRY
