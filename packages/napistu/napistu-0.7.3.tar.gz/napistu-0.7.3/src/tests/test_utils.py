from __future__ import annotations

import gzip
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from fs.tarfs import TarFS
from fs.zipfs import ZipFS
from google.cloud import storage
from pytest import fixture
from testcontainers.core.container import DockerContainer

from napistu import utils
from napistu.constants import SBML_DFS
from napistu.network.constants import DISTANCES
from napistu.utils import drop_extra_cols


@fixture(scope="session")
def gcs_storage():
    """A container running a GCS emulator"""
    with (
        DockerContainer("fsouza/fake-gcs-server:1.44")
        .with_bind_ports(4443, 4443)
        .with_command("-scheme http -backend memory")
    ) as gcs:
        os.environ["STORAGE_EMULATOR_HOST"] = "http://0.0.0.0:4443"
        yield gcs


@fixture
def gcs_bucket_name(gcs_storage):
    bucket_name = f"testbucket-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    return bucket_name


@fixture
def gcs_bucket(gcs_bucket_name):
    """A GCS bucket"""
    client = storage.Client()
    client.create_bucket(gcs_bucket_name)
    bucket = client.bucket(gcs_bucket_name)
    yield bucket
    bucket.delete(force=True)


@fixture
def gcs_bucket_uri(gcs_bucket, gcs_bucket_name):
    return f"gs://{gcs_bucket_name}"


@fixture
def gcs_bucket_subdir_uri(gcs_bucket_uri):
    return f"{gcs_bucket_uri}/testdir"


@fixture
def tmp_new_subdir(tmp_path):
    """An empty temporary directory"""
    return tmp_path / "test_dir"


def create_blob(bucket, blob_name, content=b"test"):
    # create the marker file
    bucket.blob(blob_name).upload_from_string(content)


def test_get_source_base_and_path_gcs():
    source_base, source_path = utils.get_source_base_and_path(
        "gs://cpr-ml-dev-us-east1/cpr/tests/test_data/pw_index.tsv"
    )
    assert source_base == "gs://cpr-ml-dev-us-east1"
    assert source_path == "cpr/tests/test_data/pw_index.tsv"


def test_get_source_base_and_path_local():
    source_base, source_path = utils.get_source_base_and_path(
        "/test_data/bla/pw_index.tsv"
    )
    assert source_base == "/test_data/bla"
    assert source_path == "pw_index.tsv"


def test_get_source_base_and_path_local_rel():
    source_base, source_path = utils.get_source_base_and_path(
        "./test_data/bla/pw_index.tsv"
    )
    assert source_base == "./test_data/bla"
    assert source_path == "pw_index.tsv"


def test_get_source_base_and_path_local_direct():
    source_base, source_path = utils.get_source_base_and_path("pw_index.tsv")
    assert source_base == ""
    assert source_path == "pw_index.tsv"


def test_initialize_dir_new(tmp_new_subdir):
    utils.initialize_dir(tmp_new_subdir, overwrite=False)
    assert tmp_new_subdir.exists()


@pytest.mark.unix_only
def test_initialize_dir_new_gcs(gcs_bucket_uri):
    test_uri = f"{gcs_bucket_uri}/testdir"
    utils.initialize_dir(test_uri, overwrite=False)
    utils.path_exists(test_uri)


def test_initialize_dir_new_2_layers(tmp_new_subdir):
    target_sub_dir = tmp_new_subdir / "test_dir_2"
    utils.initialize_dir(target_sub_dir, overwrite=False)
    assert target_sub_dir.exists()


@pytest.mark.unix_only
def test_initialize_dir_new_2_layers_gcs(gcs_bucket_uri):
    test_uri = f"{gcs_bucket_uri}/testdir/testdir2"
    utils.initialize_dir(test_uri, overwrite=False)
    utils.path_exists(test_uri)


def test_initialize_dir_existing(tmp_new_subdir):
    tmp_new_subdir.mkdir()

    test_file = tmp_new_subdir / "test_file"
    test_file.touch()

    with pytest.raises(FileExistsError):
        utils.initialize_dir(tmp_new_subdir, overwrite=False)
    assert test_file.exists()

    utils.initialize_dir(tmp_new_subdir, overwrite=True)
    assert test_file.exists() is False


@pytest.mark.unix_only
def test_initialize_dir_existing_gcs(gcs_bucket, gcs_bucket_uri):
    # create the file
    create_blob(gcs_bucket, "testdir/file")
    # This is a drawback of the current implementation - folders are only
    # recognized if they have a marker file.
    create_blob(gcs_bucket, "testdir/")

    test_uri = f"{gcs_bucket_uri}/testdir"
    test_uri_file = f"{test_uri}/file"
    with pytest.raises(FileExistsError):
        utils.initialize_dir(test_uri, overwrite=False)
        assert utils.path_exists(test_uri_file)

    utils.initialize_dir(test_uri, overwrite=True)
    assert utils.path_exists(test_uri_file) is False


def mock_targ_gz(url, tmp_file):
    with TarFS(tmp_file, write=True) as fol:
        with fol.open("test.txt", "w") as f:
            f.write("test")


def mock_zip(url, tmp_file):
    with ZipFS(tmp_file, write=True) as fol:
        with fol.open("test.txt", "w") as f:
            f.write("test")


def mock_gz(url, tmp_file):
    with gzip.open(tmp_file, mode="wt") as f:
        f.write("test")


@patch("napistu.utils.download_wget", side_effect=mock_targ_gz)
def test_download_and_extract_tar_gz(mock_download, tmp_new_subdir):
    utils.download_and_extract(
        url="http://asdf/bla.tar.gz",
        output_dir_path=tmp_new_subdir,
        download_method="wget",
    )
    assert (tmp_new_subdir / "test.txt").exists()


@patch("napistu.utils.download_ftp", side_effect=mock_zip)
def test_download_and_extract_zip(mock_download, tmp_new_subdir):
    utils.download_and_extract(
        url="http://asdf/bla.txt.zip",
        output_dir_path=tmp_new_subdir,
        download_method="ftp",
    )
    assert (tmp_new_subdir / "test.txt").exists()


@patch("napistu.utils.download_wget", side_effect=mock_gz)
def test_download_and_extract_gz(mock_download, tmp_new_subdir):
    utils.download_and_extract(
        url="http://asdf/bla.txt.gz",
        output_dir_path=tmp_new_subdir,
        download_method="wget",
    )
    assert (tmp_new_subdir / "bla.txt").exists()


def test_download_and_extract_invalid_method(tmp_new_subdir):
    with pytest.raises(ValueError):
        utils.download_and_extract(
            url="http://asdf/bla.txt.zip",
            output_dir_path=tmp_new_subdir,
            download_method="bla",
        )


@patch("napistu.utils.download_ftp", side_effect=mock_zip)
def test_download_and_extract_invalid_ext(mock_download, tmp_new_subdir):
    with pytest.raises(ValueError):
        utils.download_and_extract(
            url="http://asdf/bla.txt.zipper",
            output_dir_path=tmp_new_subdir,
            download_method="ftp",
        )


def test_path_exists(tmp_path, tmp_new_subdir):
    assert utils.path_exists(tmp_path)
    assert utils.path_exists(tmp_new_subdir) is False
    fn = tmp_path / "test.txt"
    assert utils.path_exists(fn) is False
    fn.touch()
    assert utils.path_exists(fn)
    assert utils.path_exists(".")
    tmp_new_subdir.mkdir()
    assert utils.path_exists(tmp_new_subdir)


@pytest.mark.unix_only
def test_path_exists_gcs(gcs_bucket, gcs_bucket_uri):
    assert utils.path_exists(gcs_bucket_uri)
    test_dir = "testdir"
    gcs_test_dir_uri = f"{gcs_bucket_uri}/{test_dir}"
    assert utils.path_exists(gcs_test_dir_uri) is False
    # Create the marker file for the directory, such that it 'exists'
    create_blob(gcs_bucket, f"{test_dir}/")
    assert utils.path_exists(gcs_test_dir_uri)

    # Test if files exists
    test_file = f"{test_dir}/test.txt"
    gcs_test_file_uri = f"{gcs_bucket_uri}/{test_file}"
    assert utils.path_exists(gcs_test_file_uri) is False
    # create the file
    create_blob(gcs_bucket, test_file)
    assert utils.path_exists(gcs_test_file_uri)


@pytest.mark.unix_only
def test_save_load_pickle_existing_folder(tmp_path):
    fn = tmp_path / "test.pkl"
    payload = "test"
    utils.save_pickle(fn, payload)
    assert fn.exists()
    assert utils.load_pickle(fn) == payload


@pytest.mark.skip_on_windows
def test_save_load_pickle_new_folder(tmp_new_subdir):
    fn = tmp_new_subdir / "test.pkl"
    payload = "test"
    utils.save_pickle(fn, payload)
    assert fn.exists()
    assert utils.load_pickle(fn) == payload


@pytest.mark.unix_only
def test_save_load_pickle_existing_folder_gcs(gcs_bucket_uri):
    fn = f"{gcs_bucket_uri}/test.pkl"
    payload = "test"
    utils.save_pickle(fn, payload)
    assert utils.path_exists(fn)
    assert utils.load_pickle(fn) == payload


@pytest.mark.unix_only
def test_save_load_pickle_new_folder_gcs(gcs_bucket_subdir_uri):
    fn = f"{gcs_bucket_subdir_uri}/test.pkl"
    payload = "test"
    utils.save_pickle(fn, payload)
    assert utils.path_exists(fn)
    assert utils.load_pickle(fn) == payload


@pytest.mark.skip_on_windows
def test_copy_uri_file(tmp_path, tmp_new_subdir):
    basename = "test.txt"
    fn = tmp_path / basename
    fn.write_text("test")
    fn_out = tmp_new_subdir / "test_out.txt"
    utils.copy_uri(fn, fn_out)
    assert fn_out.read_text() == "test"


@pytest.mark.skip_on_windows
def test_copy_uri_fol(tmp_path, tmp_new_subdir):
    tmp_new_subdir.mkdir()
    (tmp_new_subdir / "test").touch()

    out_dir = tmp_path / "out"
    out_file = out_dir / "test"
    utils.copy_uri(tmp_new_subdir, out_dir, is_file=False)
    assert out_file.exists()


@pytest.mark.unix_only
def test_copy_uri_file_gcs(gcs_bucket_uri, gcs_bucket_subdir_uri):
    basename = "test.txt"
    content = "test"
    fn = f"{gcs_bucket_uri}/{basename}"
    utils.save_pickle(fn, content)
    fn_out = f"{gcs_bucket_subdir_uri}/{basename}"
    utils.copy_uri(fn, fn_out)
    assert utils.path_exists(fn_out)
    assert utils.load_pickle(fn_out) == content


@pytest.mark.unix_only
def test_copy_uri_fol_gcs(gcs_bucket_uri, gcs_bucket_subdir_uri):
    basename = "test.txt"
    content = "test"
    fn = f"{gcs_bucket_subdir_uri}/{basename}"
    utils.save_pickle(fn, content)
    out_dir = f"{gcs_bucket_uri}/new_dir"
    out_file = f"{out_dir}/{basename}"
    utils.copy_uri(gcs_bucket_subdir_uri, out_dir, is_file=False)
    assert utils.path_exists(out_file)


@pytest.mark.skip_on_windows
def test_pickle_cache(tmp_path):
    fn = tmp_path / "test.pkl"

    mock = Mock()
    result = "test"

    @utils.pickle_cache(fn)
    def test_func():
        mock()
        return result

    test_func()
    r = test_func()
    assert r == result
    # only called once as second
    # call should be cached
    assert mock.call_count == 1


def test_extract_regex():
    assert utils.extract_regex_search("ENS[GT][0-9]+", "ENST0005") == "ENST0005"
    assert utils.extract_regex_search("ENS[GT]([0-9]+)", "ENST0005", 1) == "0005"
    with pytest.raises(ValueError):
        utils.extract_regex_search("ENS[GT][0-9]+", "ENSA0005")

    assert utils.extract_regex_match(".*type=([a-zA-Z]+).*", "Ltype=abcd5") == "abcd"
    # use for formatting identifiers
    assert utils.extract_regex_match("^([a-zA-Z]+)_id$", "sc_id") == "sc"
    with pytest.raises(ValueError):
        utils.extract_regex_match(".*type=[a-zA-Z]+.*", "Ltype=abcd5")


def test_match_pd_vars():
    a_series = pd.Series({"foo": 1, "bar": 2})
    a_dataframe = pd.DataFrame({"foo": ["a", "b"], "bar": [1, 2]})

    assert utils.match_pd_vars(a_series, {"foo", "bar"}).are_present
    assert not utils.match_pd_vars(a_series, {"baz"}).are_present
    assert utils.match_pd_vars(a_dataframe, {"foo", "bar"}).are_present
    assert not utils.match_pd_vars(a_dataframe, {"baz"}).are_present


def test_ensure_pd_df():
    source_df = pd.DataFrame({"a": "b"}, index=[0])
    source_series = pd.Series({"a": "b"}).rename(0)

    converted_series = utils.ensure_pd_df(source_series)

    assert isinstance(utils.ensure_pd_df(source_df), pd.DataFrame)
    assert isinstance(converted_series, pd.DataFrame)
    assert all(converted_series.index == source_df.index)
    assert all(converted_series.columns == source_df.columns)
    assert all(converted_series == source_df)


def test_format_identifiers_as_edgelist():
    DEGEN_EDGELIST_DF_1 = pd.DataFrame(
        {
            "ind1": [0, 0, 1, 1, 1, 1],
            "ind2": ["a", "a", "b", "b", "c", "d"],
            "ont": ["X", "X", "X", "Y", "Y", "Y"],
            "val": ["A", "B", "C", "D", "D", "E"],
        }
    ).set_index(["ind1", "ind2"])

    DEGEN_EDGELIST_DF_2 = pd.DataFrame(
        {
            "ind": ["a", "a", "b", "b", "c", "d"],
            "ont": ["X", "X", "X", "Y", "Y", "Y"],
            "val": ["A", "B", "C", "D", "D", "E"],
        }
    ).set_index("ind")

    edgelist_df = utils.format_identifiers_as_edgelist(
        DEGEN_EDGELIST_DF_1, ["ont", "val"]
    )
    assert edgelist_df["ind"].iloc[0] == "ind_0_a"
    assert edgelist_df["id"].iloc[0] == "id_X_A"

    edgelist_df = utils.format_identifiers_as_edgelist(DEGEN_EDGELIST_DF_1, ["val"])
    assert edgelist_df["ind"].iloc[0] == "ind_0_a"
    assert edgelist_df["id"].iloc[0] == "id_A"

    edgelist_df = utils.format_identifiers_as_edgelist(
        DEGEN_EDGELIST_DF_2, ["ont", "val"]
    )
    assert edgelist_df["ind"].iloc[0] == "ind_a"
    assert edgelist_df["id"].iloc[0] == "id_X_A"

    with pytest.raises(ValueError):
        utils.format_identifiers_as_edgelist(
            DEGEN_EDGELIST_DF_2.reset_index(drop=True), ["ont", "val"]
        )


def test_find_weakly_connected_subgraphs():
    DEGEN_EDGELIST_DF_2 = pd.DataFrame(
        {
            "ind": ["a", "a", "b", "b", "c", "d"],
            "ont": ["X", "X", "X", "Y", "Y", "Y"],
            "val": ["A", "B", "C", "D", "D", "E"],
        }
    ).set_index("ind")

    edgelist_df = utils.format_identifiers_as_edgelist(
        DEGEN_EDGELIST_DF_2, ["ont", "val"]
    )
    edgelist = edgelist_df[["ind", "id"]]

    connected_indices = utils.find_weakly_connected_subgraphs(edgelist[["ind", "id"]])
    assert all(connected_indices["cluster"] == [0, 1, 1, 2])


def test_style_df():
    np.random.seed(0)
    simple_df = pd.DataFrame(np.random.randn(20, 4), columns=["A", "B", "C", "D"])
    simple_df.index.name = "foo"

    multiindexed_df = (
        pd.DataFrame(
            {
                "category": ["foo", "foo", "foo", "bar", "bar", "bar"],
                "severity": ["major", "minor", "minor", "major", "major", "minor"],
            }
        )
        .assign(message="stuff")
        .groupby(["category", "severity"])
        .count()
    )

    # style a few pd.DataFrames
    isinstance(utils.style_df(simple_df), pd.io.formats.style.Styler)
    isinstance(
        utils.style_df(simple_df, headers=None, hide_index=True),
        pd.io.formats.style.Styler,
    )
    isinstance(
        utils.style_df(simple_df, headers=["a", "b", "c", "d"], hide_index=True),
        pd.io.formats.style.Styler,
    )
    isinstance(utils.style_df(multiindexed_df), pd.io.formats.style.Styler)


def test_score_nameness():
    assert utils.score_nameness("p53") == 23
    assert utils.score_nameness("ENSG0000001") == 56
    assert utils.score_nameness("pyruvate kinase") == 15


def test_drop_extra_cols():
    """Test the _drop_extra_cols function for removing and reordering columns."""
    # Setup test DataFrames
    df_in = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6], "col3": [7, 8, 9]})

    df_out = pd.DataFrame(
        {
            "col2": [10, 11, 12],
            "col3": [13, 14, 15],
            "col4": [16, 17, 18],  # Extra column that should be dropped
            "col1": [19, 20, 21],  # Different order than df_in
        }
    )

    # Test basic functionality without always_include
    result = drop_extra_cols(df_in, df_out)

    # Check that extra column was dropped
    assert "col4" not in result.columns

    # Check that columns are in the same order as df_in
    assert list(result.columns) == list(df_in.columns)

    # Check that values are preserved
    pd.testing.assert_frame_equal(
        result,
        pd.DataFrame(
            {"col1": [19, 20, 21], "col2": [10, 11, 12], "col3": [13, 14, 15]}
        )[
            list(df_in.columns)
        ],  # Ensure same column order
    )

    # Test with always_include
    result_with_include = drop_extra_cols(df_in, df_out, always_include=["col4"])

    # Check that col4 is retained and appears at the end
    assert list(result_with_include.columns) == list(df_in.columns) + ["col4"]
    assert result_with_include["col4"].equals(df_out["col4"])

    # Test with always_include containing non-existent column
    result_non_existent = drop_extra_cols(
        df_in, df_out, always_include=["col4", "col5"]
    )
    assert list(result_non_existent.columns) == list(df_in.columns) + ["col4"]

    # Test with always_include containing column from df_in
    result_overlap = drop_extra_cols(df_in, df_out, always_include=["col1", "col4"])
    assert list(result_overlap.columns) == list(df_in.columns) + ["col4"]

    # Test with no overlapping columns but some in always_include
    df_out_no_overlap = pd.DataFrame({"col4": [1, 2, 3], "col5": [4, 5, 6]})
    result_no_overlap = drop_extra_cols(df_in, df_out_no_overlap)
    assert result_no_overlap.empty
    assert list(result_no_overlap.columns) == []

    result_no_overlap_with_include = drop_extra_cols(
        df_in, df_out_no_overlap, always_include=["col4"]
    )
    assert list(result_no_overlap_with_include.columns) == ["col4"]
    assert result_no_overlap_with_include["col4"].equals(df_out_no_overlap["col4"])

    # Test with subset of columns
    df_out_subset = pd.DataFrame(
        {"col1": [1, 2, 3], "col3": [7, 8, 9], "col4": [10, 11, 12]}
    )
    result_subset = drop_extra_cols(df_in, df_out_subset)

    assert list(result_subset.columns) == ["col1", "col3"]
    pd.testing.assert_frame_equal(result_subset, df_out_subset[["col1", "col3"]])

    result_subset_with_include = drop_extra_cols(
        df_in, df_out_subset, always_include=["col4"]
    )
    assert list(result_subset_with_include.columns) == ["col1", "col3", "col4"]
    pd.testing.assert_frame_equal(
        result_subset_with_include, df_out_subset[["col1", "col3", "col4"]]
    )


def test_merge_and_log_overwrites(caplog):
    """Test merge_and_log_overwrites function."""

    # Test basic merge with no conflicts
    df1 = pd.DataFrame({"id": [1, 2], "value1": ["a", "b"]})
    df2 = pd.DataFrame({"id": [1, 2], "value2": ["c", "d"]})
    result = utils._merge_and_log_overwrites(df1, df2, "test", on="id")
    assert set(result.columns) == {"id", "value1", "value2"}
    assert len(caplog.records) == 0

    # Test merge with column conflict
    df1 = pd.DataFrame({"id": [1, 2], "name": ["a", "b"], "value": [10, 20]})
    df2 = pd.DataFrame({"id": [1, 2], "name": ["c", "d"]})
    result = utils._merge_and_log_overwrites(df1, df2, "test", on="id")

    # Check that the right columns exist
    assert set(result.columns) == {"id", "name", "value"}
    # Check that we got df2's values for the overlapping column
    assert list(result["name"]) == ["c", "d"]
    # Check that we kept df1's non-overlapping column
    assert list(result["value"]) == [10, 20]
    # Check that the warning was logged
    assert len(caplog.records) == 1
    assert "test merge" in caplog.records[0].message
    assert "name" in caplog.records[0].message

    # Test merge with multiple column conflicts
    caplog.clear()
    df1 = pd.DataFrame(
        {"id": [1, 2], "name": ["a", "b"], "value": [10, 20], "status": ["ok", "ok"]}
    )
    df2 = pd.DataFrame(
        {"id": [1, 2], "name": ["c", "d"], "status": ["pending", "done"]}
    )
    result = utils._merge_and_log_overwrites(df1, df2, "test", on="id")

    # Check that the right columns exist
    assert set(result.columns) == {"id", "name", "value", "status"}
    # Check that we got df2's values for the overlapping columns
    assert list(result["name"]) == ["c", "d"]
    assert list(result["status"]) == ["pending", "done"]
    # Check that we kept df1's non-overlapping column
    assert list(result["value"]) == [10, 20]
    # Check that the warning was logged with both column names
    assert len(caplog.records) == 1
    assert "test merge" in caplog.records[0].message
    assert "name" in caplog.records[0].message
    assert "status" in caplog.records[0].message

    # Test merge with index
    caplog.clear()
    df1 = pd.DataFrame({"name": ["a", "b"], "value": [10, 20]}, index=[1, 2])
    df2 = pd.DataFrame({"name": ["c", "d"]}, index=[1, 2])
    result = utils._merge_and_log_overwrites(
        df1, df2, "test", left_index=True, right_index=True
    )

    # Check that the right columns exist
    assert set(result.columns) == {"name", "value"}
    # Check that we got df2's values for the overlapping column
    assert list(result["name"]) == ["c", "d"]
    # Check that we kept df1's non-overlapping column
    assert list(result["value"]) == [10, 20]
    # Check that the warning was logged
    assert len(caplog.records) == 1
    assert "test merge" in caplog.records[0].message
    assert "name" in caplog.records[0].message


def test_matrix_to_edgelist():
    # Test case 1: Basic functionality with numeric indices
    matrix = np.array([[1, 2, np.nan], [np.nan, 3, 4], [5, np.nan, 6]])
    expected_edgelist = pd.DataFrame(
        {
            "row": [0, 0, 1, 1, 2, 2],
            "column": [0, 1, 1, 2, 0, 2],
            "value": np.array([1, 2, 3, 4, 5, 6], dtype=np.float64),
        }
    )
    result = utils.matrix_to_edgelist(matrix)
    pd.testing.assert_frame_equal(result, expected_edgelist)

    # Test case 2: With row and column labels
    row_labels = ["A", "B", "C"]
    col_labels = ["X", "Y", "Z"]
    expected_labeled_edgelist = pd.DataFrame(
        {
            "row": ["A", "A", "B", "B", "C", "C"],
            "column": ["X", "Y", "Y", "Z", "X", "Z"],
            "value": np.array([1, 2, 3, 4, 5, 6], dtype=np.float64),
        }
    )
    result_labeled = utils.matrix_to_edgelist(
        matrix, row_labels=row_labels, col_labels=col_labels
    )
    pd.testing.assert_frame_equal(result_labeled, expected_labeled_edgelist)

    # Test case 3: Empty matrix (all NaN)
    empty_matrix = np.full((2, 2), np.nan)
    empty_result = utils.matrix_to_edgelist(empty_matrix)
    assert empty_result.empty

    # Test case 4: Single value matrix
    single_matrix = np.array([[1]])
    expected_single = pd.DataFrame(
        {"row": [0], "column": [0], "value": np.array([1], dtype=np.int64)}
    )
    result_single = utils.matrix_to_edgelist(single_matrix)
    pd.testing.assert_frame_equal(result_single, expected_single)


def test_safe_fill():
    safe_fill_test = ["a_very_long stringggg", ""]
    assert [utils.safe_fill(x) for x in safe_fill_test] == [
        "a_very_long\nstringggg",
        "",
    ]


def test_update_pathological_names():

    # All numeric
    s = pd.Series(["1", "2", "3"])
    out = utils.update_pathological_names(s, "prefix_")
    assert all(x.startswith("prefix_") for x in out)
    assert list(out) == ["prefix_1", "prefix_2", "prefix_3"]

    # Mixed numeric and non-numeric
    s2 = pd.Series(["1", "foo", "3"])
    out2 = utils.update_pathological_names(s2, "prefix_")
    assert list(out2) == ["1", "foo", "3"]

    # All non-numeric
    s3 = pd.Series(["foo", "bar", "baz"])
    out3 = utils.update_pathological_names(s3, "prefix_")
    assert list(out3) == ["foo", "bar", "baz"]


def test_parquet_save_load():
    """Test that write_parquet and read_parquet work correctly."""
    # Create test DataFrame
    original_df = pd.DataFrame(
        {
            DISTANCES.SC_ID_ORIGIN: ["A", "B", "C"],
            DISTANCES.SC_ID_DEST: ["B", "C", "A"],
            DISTANCES.PATH_LENGTH: [1, 2, 3],
            DISTANCES.PATH_WEIGHT: [0.1, 0.5, 0.8],
            "has_connection": [True, False, True],
        }
    )

    # Write and read using temporary file
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test.parquet"
        utils.save_parquet(original_df, file_path)
        result_df = utils.load_parquet(file_path)

        # Verify they're identical
        pd.testing.assert_frame_equal(original_df, result_df)


def test_safe_join_set():
    """Test safe_join_set function with various inputs."""
    # Test basic functionality and sorting
    assert utils.safe_join_set([1, 2, 3]) == "1 OR 2 OR 3"
    assert utils.safe_join_set(["c", "a", "b"]) == "a OR b OR c"

    # Test deduplication
    assert utils.safe_join_set([1, 1, 2, 3]) == "1 OR 2 OR 3"

    # Test None handling
    assert utils.safe_join_set([1, None, 3]) == "1 OR 3"
    assert utils.safe_join_set([None, None]) is None

    # Test pandas Series (use object dtype to preserve None)
    series = pd.Series([3, 1, None, 2], dtype=object)
    assert utils.safe_join_set(series) == "1 OR 2 OR 3"

    # Test string as single value
    assert utils.safe_join_set("hello") == "hello"

    # Test empty inputs
    assert utils.safe_join_set([]) is None


def test_show():
    """Test that utils.show() runs without errors."""
    import pandas as pd

    # Create a simple test DataFrame
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    # Test that show() runs without raising an exception
    # We can't easily test the output since it depends on the environment
    utils.show(df, method="string")
    utils.show(df, method="string", headers=["col1", "col2"])
    utils.show(df, method="string", hide_index=True)

    # Test with auto method (should work in test environment)
    utils.show(df, method="auto")


def test_infer_entity_type():
    """Test entity type inference with valid keys"""
    # when index matches primary key.
    # Test compartments with index as primary key
    df = pd.DataFrame(
        {SBML_DFS.C_NAME: ["cytoplasm"], SBML_DFS.C_IDENTIFIERS: ["GO:0005737"]}
    )
    df.index.name = SBML_DFS.C_ID
    result = utils.infer_entity_type(df)
    assert result == SBML_DFS.COMPARTMENTS

    # Test species with index as primary key
    df = pd.DataFrame(
        {SBML_DFS.S_NAME: ["glucose"], SBML_DFS.S_IDENTIFIERS: ["CHEBI:17234"]}
    )
    df.index.name = SBML_DFS.S_ID
    result = utils.infer_entity_type(df)
    assert result == SBML_DFS.SPECIES

    # Test entity type inference by exact column matching.
    # Test compartmentalized_species (has foreign keys)
    df = pd.DataFrame(
        {
            SBML_DFS.SC_ID: ["glucose_c"],
            SBML_DFS.S_ID: ["glucose"],
            SBML_DFS.C_ID: ["cytoplasm"],
        }
    )
    result = utils.infer_entity_type(df)
    assert result == "compartmentalized_species"

    # Test reaction_species (has foreign keys)
    df = pd.DataFrame(
        {
            SBML_DFS.RSC_ID: ["rxn1_glc"],
            SBML_DFS.R_ID: ["rxn1"],
            SBML_DFS.SC_ID: ["glucose_c"],
        }
    )
    result = utils.infer_entity_type(df)
    assert result == SBML_DFS.REACTION_SPECIES

    # Test reactions (only primary key)
    df = pd.DataFrame({SBML_DFS.R_ID: ["rxn1"]})
    result = utils.infer_entity_type(df)
    assert result == SBML_DFS.REACTIONS


def test_infer_entity_type_errors():
    """Test error cases for entity type inference."""
    # Test no matching entity type
    df = pd.DataFrame({"random_column": ["value"], "another_col": ["data"]})
    with pytest.raises(ValueError, match="No entity type matches DataFrame"):
        utils.infer_entity_type(df)

    # Test partial match (missing required foreign key)
    df = pd.DataFrame(
        {SBML_DFS.SC_ID: ["glucose_c"], SBML_DFS.S_ID: ["glucose"]}
    )  # Missing c_id
    with pytest.raises(ValueError):
        utils.infer_entity_type(df)

    # Test extra primary keys that shouldn't be there
    df = pd.DataFrame(
        {SBML_DFS.R_ID: ["rxn1"], SBML_DFS.S_ID: ["glucose"]}
    )  # Two primary keys
    with pytest.raises(ValueError):
        utils.infer_entity_type(df)


def test_infer_entity_type_multindex():
    # DataFrame with MultiIndex (r_id, foo), should infer as reactions
    df = pd.DataFrame({"some_col": [1, 2]})
    df.index = pd.MultiIndex.from_tuples(
        [("rxn1", "a"), ("rxn2", "b")], names=[SBML_DFS.R_ID, "foo"]
    )
    result = utils.infer_entity_type(df)
    assert result == SBML_DFS.REACTIONS

    # DataFrame with MultiIndex (sc_id, bar), should infer as compartmentalized_species
    df = pd.DataFrame({"some_col": [1, 2]})
    df.index = pd.MultiIndex.from_tuples(
        [("glucose_c", "a"), ("atp_c", "b")], names=[SBML_DFS.SC_ID, "bar"]
    )
    result = utils.infer_entity_type(df)
    assert result == SBML_DFS.COMPARTMENTALIZED_SPECIES


def test_safe_capitalize():
    """Test that safe_capitalize preserves acronyms."""
    assert utils.safe_capitalize("regulatory RNAs") == "Regulatory RNAs"
    assert utils.safe_capitalize("proteins") == "Proteins"
    assert utils.safe_capitalize("DNA sequences") == "DNA sequences"
    assert utils.safe_capitalize("") == ""
