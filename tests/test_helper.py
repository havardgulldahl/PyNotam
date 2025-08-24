import os


def read_test_data():

    test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    filenames = []
    for _dirpath, _, _filenames in os.walk(test_data_dir):
        filenames = [
            os.path.join(_dirpath, filename)
            for filename in _filenames
            if filename.endswith(".txt")
        ]
        break

    def read_gen(filenames):
        for filename in filenames:
            try:
                with open(filename, "r", encoding="utf-8") as fh:
                    yield fh.read().splitlines()
            except Exception as e:
                yield [f"ERROR: Could not read {filename}: {e}"]

    return list(read_gen(filenames))


def read_single_notam(id):
    """'id' should be either the IAA internal integer identifier, or the NOTAM series and number/year --
    depending on the name of the test_data file containing it."""

    filename = "{}.txt".format(str(id))
    filename = filename.replace("/", "_")
    test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    file_path = os.path.join(test_data_dir, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception as e:
        return f"ERROR: Could not read {file_path}: {e}"
