"""
Python script that allows for quicker deployment by
automatically filling in the parameters for the build_and_deploy script
"""
import subprocess
import argparse

PROJECT_DICT = {
    'sbx': 'df-dds-ml-dev-e015',
    'dev': 'housing-dev',
    'acc': 'housing-acc',
    'prd': 'housing-prd'
}


def run_command(command, return_output=False):
    """Prints output of subprocess command in real-time.
    Args:
        command (TYPE): Description
        return_output (bool): Return output of command as an array or not.

    Returns:
        TYPE: Description
    """
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, shell=True)
    output_arr = []
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        elif output:
            cleaned_output = output.strip().decode('UTF-8')
            if return_output:
                output_arr.append(cleaned_output)
            else:
                print(cleaned_output)
    return_code = process.poll()
    if return_output:
        return output_arr
    return return_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--env',
                        help='Choose environment',
                        choices=['sbx', 'dev', 'acc', 'prd'],
                        required=True)
    parser.add_argument('--grant_access', action='store_true')
    args = parser.parse_args()
    env = args.env
    project_id = PROJECT_DICT[env]
    api_name = "housing-area-predictor"

    print(f"Building {api_name} to {env}")
    print("Configuring gcloud")
    _ = run_command(f"gcloud config set project {project_id}")
    print("Starting build_and_deploy script")
    cmd = f"""sh build_and_deploy.sh --project {project_id} --name {api_name} --env {env}"""
    _ = run_command(cmd)

