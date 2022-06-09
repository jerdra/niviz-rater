import niviz_rater.config.utils as confutils

_db_defaults = confutils.parse_db_defaults()

DEFAULT_ANNOTATION = confutils.remove_quotes(
    _db_defaults.get("qc-settings", "default_annotation"))

DEFAULT_RATING = confutils.remove_quptes(
    _db_defaults.get("qc-settings", "default_rating"))

RATINGS = confutils.remove_empty(
    confutils.remove_quotes(
        _db_defaults.get("qc-settings", "ratings").split("\n")))
