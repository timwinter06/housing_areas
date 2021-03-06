"""
Python script that allows for quicker deployment by
automatically filling in the parameters for the build_and_deploy script
"""
import subprocess
import argparse

PROJECT_DICT = {
    'sbx': 'housing-sbx',
    'dev': 'housing-dev',
    'acc': 'housing-acc',
    'prd': 'housing-prd'
}


def run_command(command, return_output=False):
    """Prints output of subprocess command in real-time.
    Args:
        command: command to run in prompt
        return_output (bool): Return output of command as an array or not.
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
    args = parser.parse_args()
    env = args.env
    project_id = PROJECT_DICT[env]
    API_NAME = "housing-area-predictor"
    print(f"Building {API_NAME} to {env}")
    print("Configuring gcloud")
    _ = run_command(f"gcloud config set project {project_id}")
    print("Starting build_and_deploy script")
    cmd = f"""sh build_and_deploy.sh --project {project_id} --name {API_NAME} --env {env}"""
    _ = run_command(cmd)
