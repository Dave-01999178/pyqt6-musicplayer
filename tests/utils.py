def make_files(tmp_path, file_names, as_str=False, create=True):
    expected_playlist = []
    file_paths = []

    for file_name in file_names:
        file_path = tmp_path / file_name  # Path under temporary directory

        if create:
            # Create the file in temporary directory to test `resolve(strict=True)`.
            file_path.touch()

            # The expected path in playlist (absolute path).
            expected_playlist.append(file_path.resolve())

        file_paths.append(str(file_path) if as_str else file_path)

    return file_paths, expected_playlist


def make_existing_files(tmp_path, file_names, as_str=False):
    return make_files(tmp_path, file_names, as_str=as_str, create=True)


def make_missing_files(tmp_path, file_names, as_str=False):
    return make_files(tmp_path, file_names, as_str=as_str, create=False)