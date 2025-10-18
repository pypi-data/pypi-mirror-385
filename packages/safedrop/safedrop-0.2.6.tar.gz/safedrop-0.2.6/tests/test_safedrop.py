from pathlib import Path
import pytest
from utils import compare_folders

# Add the project root to sys.path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from safedrop import safedrop
from decode import decode_files
TEST_USERNAME = "testuser1"

def parametrize_by_folder(argstring, folder_path):
    """
    argstring: comma separated list of argument names
    folder_path: folder with subfolders each containing test case files

    Example:
    @parametrize_by_folder("payload,reply", r"tests/test_da_assets/ai_update_analysis")
    """

    arg_names = [arg.strip() for arg in argstring.split(",")]
    print("Looking for test cases in", folder_path)

    folder_path = Path(folder_path)
    test_folders = [item for item in folder_path.iterdir() if item.is_dir()]
    test_cases = []

    for folder in test_folders:
        print("Checking folder:", folder)
        case = [folder.stem]

        # build dict: stem -> file path
        files_by_stem = {f.stem: f for f in folder.glob("*")}

        # collect in arg order
        case_args = []
        for arg in arg_names:
            if arg not in files_by_stem:
                raise FileNotFoundError(
                    f"Missing required file '{arg}' in folder {folder}"
                )
            case_args.append(files_by_stem[arg])

        test_cases.append([folder.stem, *case_args])

    return parametrize(argstring, test_cases)


def parametrize(argstring, list_of_tuples):
    "first element of each tuple is the id"

    params = [pytest.param(*t[1:], id=t[0]) for t in list_of_tuples]

    def decorator(func):
        return pytest.mark.parametrize(argstring, params)(func)

    return decorator

def test_utf8_image_name_safedrop(tmp_path):
    fout = tmp_path / "output.png"
    files_out = tmp_path / "decoded"
    image = "/app/src/tests/assets/20250101微信图片.png"
    contents = "/app/src/tests/cases/safedrop/01 UTF8 file names/contents"
    print(image)
    print(contents)
    safedrop(TEST_USERNAME, contents, image, str(fout))
    decode_files(TEST_USERNAME, str(fout), image, str(files_out))
    compare_folders(contents, files_out)

def test_dropping_too_much_content(tmp_path):
    fout = tmp_path / "output.png"
    contents = tmp_path / "contents"
    files_out = tmp_path / "decoded"
    image = "/app/src/tests/assets/20250101微信图片.png"

    # create a huge file to encode
    contents.mkdir()
    file1 = contents / "file1.txt"
    file1.write_text("Hello" * 1000000)
    
    print(image)
    print(contents)
    with pytest.raises(Exception):
        safedrop(TEST_USERNAME, contents, image, str(fout))


@parametrize_by_folder("image,contents", r"tests/cases/safedrop")
def test_safedrop(tmp_path, image, contents):
    fout = tmp_path / "output.png"
    files_out = tmp_path / "decoded"
    print(image)
    print(contents)
    safedrop(TEST_USERNAME, contents, image, str(fout))
    decode_files(TEST_USERNAME, str(fout), image, str(files_out))
    compare_folders(contents, files_out)

    with pytest.raises(ValueError):
        decode_files("different_username", str(fout), image, str(files_out))
