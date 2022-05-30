import pytest
import pkg_resources
from itertools import product
import bids
import bids.layout.utils as bidsutils
import bids.layout.writing as bidswriting
import niviz_rater.index as index

# Force default path patterns to be what is used in data/bids.json
# Used for constructing filename paths
config_file = pkg_resources.resource_filename("niviz_rater", "data/bids.json")
bids.config.from_file(config_file)
DEFAULT_PATH_PATTERNS = bids.config.get_option("default_path_patterns")


class MockBIDSFile:
    """
    Class mocking basic BIDSFile interfaces
    needed by Niviz-Rater
    """

    __slots__ = "entities", "path"

    def __init__(self, filename):
        self.entities = bidsutils.parse_file_entities(filename)
        self.path = str(filename)


@pytest.fixture
def make_bidsfile():
    """
    Fixture factory function to generate
    list of MockBIDSFile objects
    Receives a dict of Entity, [values..]
    """

    def _make_bidsfile(**kwargs):
        value_combinations = product(*kwargs.values())
        keys = list(kwargs.keys())
        results = []
        for entity_values in value_combinations:
            entity_dict = dict(zip(keys, entity_values))
            path = bidswriting.build_path(entity_dict, DEFAULT_PATH_PATTERNS)
            results.append(MockBIDSFile(path))
        return results

    return _make_bidsfile


def test_group_by_entities(make_bidsfile):
    """
    Ensure that ConfigComponent returns the correct
    grouping of entities for a list of BIDSFiles
    containing a set of entities
    """

    group_entities = {"subject", "session"}
    entities = {
        "subject": ["A", "B"],
        "session": ["01", "02"],
        "description": ["x", "y"],
        "suffix": ["T1w"],
        "extension": [".nii.gz"]
    }

    expected_results = {
        ("A", "01"): [
            "sub-A/ses-01/anat/sub-A_ses-01_desc-x_T1w.nii.gz",
            "sub-A/ses-01/anat/sub-A_ses-01_desc-y_T1w.nii.gz"
        ],
        ("A", "02"): [
            "sub-A/ses-02/anat/sub-A_ses-02_desc-x_T1w.nii.gz",
            "sub-A/ses-02/anat/sub-A_ses-02_desc-y_T1w.nii.gz"
        ],
        ("B", "01"): [
            "sub-B/ses-01/anat/sub-B_ses-01_desc-x_T1w.nii.gz",
            "sub-B/ses-01/anat/sub-B_ses-01_desc-y_T1w.nii.gz"
        ],
        ("B", "02"): [
            "sub-B/ses-02/anat/sub-B_ses-02_desc-x_T1w.nii.gz",
            "sub-B/ses-02/anat/sub-B_ses-02_desc-y_T1w.nii.gz"
        ],
    }

    bidsfiles = make_bidsfile(**entities)

    # Convert to frozenset, key order doesn't matter
    result = index._group_by_entities(bidsfiles, group_entities)
    converted_result = {
        frozenset(k): set([b.path for b in v])
        for k, v in result
    }

    converted_expect = {
        frozenset(k): set(v)
        for k, v in expected_results.items()
    }

    assert converted_result == converted_expect


def test_raises_exception_with_more_than_one_match(make_bidsfile):
    """
    Ensure that if more than one match is found a value error is
    raised
    """

    entities = {
        "subject": ["A", "B"],
        "description": ["x", "y"],
        "suffix": ["T1w"],
        "extension": [".nii.gz"]
    }
    bidsfiles = make_bidsfile(**entities)
    image_description = {"subject": "A"}

    with pytest.raises(ValueError):
        index.find_matches(bidsfiles, image_description)


def test_config_component_raises_exception_with_zero_matches(make_bidsfile):
    """
    If no matches are found raise an exception
    """

    entities = {
        "subject": ["A", "B"],
        "description": ["x", "y"],
        "suffix": ["T1w"],
        "extension": [".nii.gz"]
    }
    bidsfiles = make_bidsfile(**entities)
    image_description = {"subject": "C"}

    with pytest.raises(IndexError):
        index.find_matches(bidsfiles, image_description)


def test_qc_entities_returns_correct_column():

    qc_entity = index.QCEntity(images=[
        "sub-A/anat/sub-A_desc-x_T1w.nii.gz",
        "sub-A/anat/sub-A_desc-y_T1w.nii.gz",
    ],
                   entities={"subject": "A"},
                   tpl_name="${subject} TEST",
                   tpl_column_name="HELLO")

    assert qc_entity.name == "A TEST"
    assert qc_entity.column_name == "HELLO"


def test_correct_qc_entities_are_built(make_bidsfile):
    """
    Full test on behaviour of ConfigComponent
    Return the correct QCEntity's when given a list
    of BIDSFiles
    """

    entities = {
        "subject": ["A", "B"],
        "description": ["x", "y"],
        "suffix": ["T1w"],
        "extension": [".nii.gz"]
    }
    bidsfiles = make_bidsfile(**entities)
    component = {
        "entities": ["subject"],
        "name": "${subject} TEST",
        "column": "HELLO",
        "annotations": ["GOOD", "BAD"],
        "images": [{
            "desc": "x"
        }, {
            "desc": "y"
        }]
    }
    config_component = index.ConfigComponent(**component)
    result = config_component.build_qc_entities(bidsfiles)

    expected_qc_entities = [
        index.QCEntity(images=[
            "sub-A/anat/sub-A_desc-x_T1w.nii.gz",
            "sub-A/anat/sub-A_desc-y_T1w.nii.gz",
        ],
                       entities={"subject": "A"},
                       tpl_name="${subject} TEST",
                       tpl_column_name="HELLO"),
        index.QCEntity(images=[
            "sub-B/anat/sub-B_desc-x_T1w.nii.gz",
            "sub-B/anat/sub-B_desc-y_T1w.nii.gz",
        ],
                       entities={"subject": "B"},
                       tpl_name="${subject} TEST",
                       tpl_column_name="HELLO"),
    ]

    assert len(result) == len(expected_qc_entities)
    assert all([q for q in result if q in expected_qc_entities])


def test_make_database_constructs_correct_qc_entity():
    """
    Ensure that the correct information is being created when
    converting a QCEntity into a database table
    """


def test_is_subdict_returns_true_when_given_subset():
    """
    Ensure that _test_subdict method is correctly checking
    if one dict is a subset of another
    """

    small = {"x": 123}
    big = {"x": 123, "y": 456}
    assert index._is_subdict(big, small)
