import argparse
import subprocess


def run_checks(platform: str):
    subprocess.run(["pytest", "--cov"], check=True)
    flake8_cmd = [
        "flake8",
        "--suppress-none-returning",
        "--ignore",
        "ANN101",
    ]
    if platform == "local":
        flake8_cmd.extend(["--exclude", ".env,.pytest_cache,project_pb2.py"])
    elif platform == "travis":
        flake8_cmd.extend(["--exclude", "project_pb2.py"])
    else:
        print("Platform must be either 'local' ot 'travis'.")
        exit(code=1)
    flake8_cmd.append("./")
    subprocess.run(flake8_cmd, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CI checks script.")

    parser.add_argument(
        "--platform",
        type=str,
        help=(
            "'local' for running locally and 'travis' when running as part of"
            " the CI."
        )
    )
    args = parser.parse_args()

    run_checks(platform=args.platform)
