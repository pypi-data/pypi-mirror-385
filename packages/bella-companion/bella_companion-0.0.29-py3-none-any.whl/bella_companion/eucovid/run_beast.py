import json
import os
from glob import glob
from pathlib import Path

from bella_companion.utils import submit_job


def run_beast():
    base_output_dir = Path(os.environ["BELLA_BEAST_OUTPUT_DIR"])
    output_dir = base_output_dir / "eucovid"
    os.makedirs(output_dir, exist_ok=True)

    base_log_dir = Path(os.environ["BELLA_SBATCH_LOG_DIR"]) / "eucovid"

    data_dir = Path(__file__).parent / "data"
    beast_configs_dir = Path(__file__).parent / "beast_configs"
    msa_file = data_dir / "msa.fasta"

    predictors_dir = data_dir / "predictors"
    all_predictor_files = ",".join(glob(str(predictors_dir / "all" / "*.tsv")))
    all_predictors_data = " ".join(
        [
            f"-D msa_file={msa_file}",
            f"-D changeTimesFile={predictors_dir / 'changetimes_all_7e.tsv'}",
            f"-D predictorFiles={all_predictor_files}",
        ]
    )
    flight_predictor_data = " ".join(
        [
            f"-D msa_file={msa_file}",
            f"-D changeTimesFile={predictors_dir / 'changetimes_flights_4e.tsv'}",
            f"-D predictorFiles={predictors_dir / 'flight_pop_x_4e_ls.tsv'}",
        ]
    )

    job_ids = {}

    os.makedirs(output_dir / "Nonparametric", exist_ok=True)
    job_ids["Nonparametric"] = submit_job(
        " ".join(
            [
                os.environ["BELLA_RUN_BEAST_CMD"],
                f"-D aligned_fasta={msa_file}",
                f"-prefix {output_dir / 'Nonparametric'}{os.sep}",
                str(beast_configs_dir / "Nonparametric.xml"),
            ]
        ),
        base_log_dir / "Nonparametric",
        cpus=128,
        mem_per_cpu=12000,
    )

    os.makedirs(output_dir / "all-predictors-GLM", exist_ok=True)
    job_ids["all-predictors-GLM"] = submit_job(
        " ".join(
            [
                os.environ["BELLA_RUN_BEAST_CMD"],
                all_predictors_data,
                f"-prefix {output_dir / 'all-predictors-GLM'}{os.sep}",
                str(beast_configs_dir / "GLM.xml"),
            ]
        ),
        base_log_dir / "all-predictors-GLM",
        cpus=128,
        mem_per_cpu=12000,
    )

    os.makedirs(output_dir / "flights-GLM", exist_ok=True)
    job_ids["flights-GLM"] = submit_job(
        " ".join(
            [
                os.environ["BELLA_RUN_BEAST_CMD"],
                flight_predictor_data,
                f"-prefix {output_dir / 'flights-GLM'}{os.sep}",
                str(beast_configs_dir / "GLM.xml"),
            ]
        ),
        base_log_dir / "flights-GLM",
        cpus=128,
        mem_per_cpu=12000,
    )

    os.makedirs(output_dir / "all-predictors-MLP", exist_ok=True)
    job_ids["all-predictors-MLP"] = submit_job(
        " ".join(
            [
                os.environ["BELLA_RUN_BEAST_CMD"],
                f'-D layersRange="0,1,2",nodes="16 8"',
                all_predictors_data,
                f"-prefix {output_dir / 'all-predictors-MLP'}{os.sep}",
                str(beast_configs_dir / "MLP.xml"),
            ]
        ),
        base_log_dir / "all-predictors-MLP",
        cpus=128,
        mem_per_cpu=12000,
    )

    os.makedirs(output_dir / "flights-MLP", exist_ok=True)
    job_ids["flights-MLP"] = submit_job(
        " ".join(
            [
                os.environ["BELLA_RUN_BEAST_CMD"],
                f'-D layersRange="0,1,2",nodes="16 8"',
                flight_predictor_data,
                f"-prefix {output_dir / 'flights-MLP'}{os.sep}",
                str(beast_configs_dir / "MLP.xml"),
            ]
        ),
        base_log_dir / "flights-MLP",
        cpus=128,
        mem_per_cpu=12000,
    )

    with open(base_output_dir / "eucovid_job_ids.json", "w") as f:
        json.dump(job_ids, f)
