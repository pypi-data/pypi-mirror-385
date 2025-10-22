import sys
from textwrap import dedent


def generate_copy_assignment_script(
    extra_file_required="n",
    assignment_name="C1M2_Assignment.ipynb",
    extra_file_name="foo.txt",
):
    """
    Generate copy_assignment_to_submission.sh script with optional extra file copying.

    Args:
        extra_file_required (str): Include extra file copying if "y"
        assignment_name (str): The name of the assignment notebook file
        extra_file_name (str): The name of the extra file to copy (if required)

    Returns:
        str: The complete script content

    """
    # Common script header and initial variables
    header = [
        "#!/bin/bash",
        "set -euo pipefail",
        "",
        "# each grader should modify Assignment and Submission file to fulfill the grader setting",
        f"Assignment={assignment_name}",
    ]

    # Add extra file declaration if required
    if extra_file_required == "y":
        header.append(f"Extra_file={extra_file_name}")

    # Common script variables
    variables = [
        "",
        "SubmissionFile=submission.ipynb",
        "SubmissionPath=/shared/submission",
        "SharedDiskPath=/learner_workplace/$UserId/$CourseId/$LessonId",
        "",
        "# copy synced files (exam image typically sync all files in lesson folder)",
        'echo "Copy learner submission from $SharedDiskPath/$Assignment to $SubmissionPath/$SubmissionFile"',
        "cp $SharedDiskPath/$Assignment $SubmissionPath/$SubmissionFile",
    ]

    # Add extra file copying if required
    extra_file_copy = []
    if extra_file_required == "y":
        extra_file_copy = [
            'echo "Copy learner submission from $SharedDiskPath/$Extra_file to $SubmissionPath/$Extra_file"',
            "cp $SharedDiskPath/$Extra_file $SubmissionPath/$Extra_file",
        ]

    # Combine all sections
    content = header + variables + extra_file_copy

    return "\n".join(content)


def generate_entry_py(
    non_notebook_grading="n",
    extra_file_name="foo.txt",
):
    """
    Generate entry.py with optional non-notebook grading capability.

    Args:
        non_notebook_grading (str): Include non-notebook grading if "y"
        extra_file_name (str): Name of extra file to grade

    Returns:
        str: The complete entry.py content

    """
    # Common imports for both versions
    imports = [
        "from dlai_grader.config import Config, get_part_id",
        "from dlai_grader.compiler import compile_partial_module",
        "from dlai_grader.io import read_notebook, copy_submission_to_workdir, send_feedback",
        "from dlai_grader.notebook import keep_tagged_cells",
        "from dlai_grader.grading import (",
        "    compute_grading_score,",
        "    graded_obj_missing,",
        "    LearnerSubmission,",
        ")",
        "from grader import handle_part_id",
        "",
    ]

    # Notebook grading function (common to both versions)
    notebook_grading_func = [
        "",
        "def notebook_grading(config, compile_solution=False):",
        "    try:",
        "        nb = read_notebook(config.submission_file_path)",
        "    except Exception as e:",
        '        msg = f"There was a problem reading your notebook. Details:\\n{e!s}"',
        "        send_feedback(0.0, msg, err=True)",
        "",
        "    transformations = [keep_tagged_cells()]",
        "    for t in transformations:",
        "        nb = t(nb)",
        "",
        "    try:",
        '        learner_mod = compile_partial_module(nb, "learner_mod", verbose=False)',
        "    except Exception as e:",
        '        msg = f"There was a problem compiling the code from your notebook, please check that you saved before submitting. Details:\\n{e!s}"',
        "        send_feedback(0.0, msg, err=True)",
        "",
        "    solution_mod = None",
        "    if compile_solution:",
        "        solution_nb = read_notebook(config.solution_file_path)",
        "        for t in transformations:",
        "            solution_nb = t(solution_nb)",
        "        solution_mod = compile_partial_module(",
        '            solution_nb, "solution_mod", verbose=False',
        "        )",
        "",
        "    return learner_mod, solution_mod",
        "",
    ]

    # Non-notebook grading function (only for version with non_notebook_grading)
    non_notebook_grading_func = [
        "",
        "def non_notebook_grading(config):",
        "    try:",
        '        with open(config.submission_file_path, "r") as file:',
        "            contents = file.read()",
        "    except Exception as e:",
        '        msg = f"There was an error reading your submission. Details:\\n{e!s}"',
        "        send_feedback(0.0, msg, err=True)",
        "",
        "    return LearnerSubmission(submission=contents)",
        "",
    ]

    # Main function for version without non-notebook grading
    main_func_simple = [
        "def main() -> None:",
        "    copy_submission_to_workdir()",
        "",
        "    part_id = get_part_id()",
        "",
        "    c = Config()",
        "",
        "    learner_mod, _ = notebook_grading(c)",
        "",
        "    g_func = handle_part_id(part_id)(learner_mod)",
        "",
        "    try:",
        "        cases = g_func()",
        "    except Exception as e:",
        '        msg = f"There was an error grading your submission. Details:\\n{e!s}"',
        "        send_feedback(0.0, msg, err=True)",
        "",
        "    if graded_obj_missing(cases):",
        '        msg = "Object required for grading not found. If you haven\'t completed the exercise this might be expected. Otherwise, check your solution as grader omits cells that throw errors."',
        "        send_feedback(0.0, msg, err=True)",
        "",
        "    score, feedback = compute_grading_score(cases)",
        "    send_feedback(score, feedback)",
        "",
    ]

    # Main function for version with non-notebook grading
    main_func_with_non_notebook = [
        "def main() -> None:",
        "    copy_submission_to_workdir()",
        "",
        "    part_id = get_part_id()",
        "",
        "    match part_id:",
        '        case "123":',
        f'            c = Config(submission_file="{extra_file_name}")',
        "            learner_mod = non_notebook_grading(c)",
        "        case _:",
        "            c = Config()",
        "            learner_mod, _ = notebook_grading(c)",
        "",
        "    g_func = handle_part_id(part_id)(learner_mod)",
        "",
        "    try:",
        "        cases = g_func()",
        "    except Exception as e:",
        '        msg = f"There was an error grading your submission. Details:\\n{e!s}"',
        "        send_feedback(0.0, msg, err=True)",
        "",
        "    if graded_obj_missing(cases):",
        '        msg = "Object required for grading not found. If you haven\'t completed the exercise this might be expected. Otherwise, check your solution as grader omits cells that throw errors."',
        "        send_feedback(0.0, msg, err=True)",
        "",
        "    score, feedback = compute_grading_score(cases)",
        "    send_feedback(score, feedback)",
        "",
    ]

    # Common script entry point
    entry_point = [
        'if __name__ == "__main__":',
        "    main()",
        "",
    ]

    # Combine all sections based on configuration
    content = imports + notebook_grading_func

    if non_notebook_grading == "y":
        content.extend(non_notebook_grading_func)
        content.extend(main_func_with_non_notebook)
    else:
        content.extend(main_func_simple)

    content.extend(entry_point)

    return "\n".join(content)


def generate_dockerfile(data_dir_required="n", sol_dir_required="n"):
    """
    Generate a Dockerfile with optional data and solution directories.

    Args:
        data_dir_required (str): Include data directory if "y"
        sol_dir_required (str): Include solution directory if "y"

    Returns:
        str: The complete Dockerfile content

    """
    base_content = [
        "FROM continuumio/miniconda3@sha256:d601a04ea48fd45e60808c7072243d33703d29434d2067816b7f26b0705d889a",
        "",
        "RUN apk update && apk add libstdc++",
        "",
        "COPY requirements.txt .",
        "",
        "RUN pip install -r requirements.txt && rm requirements.txt",
        "",
        "RUN mkdir /grader && \\ \nmkdir /grader/submission",
        "",
        "COPY .conf /grader/.conf",
    ]

    # Add optional file copies based on config
    if data_dir_required == "y":
        base_content.append("COPY data/ /grader/data/")

    if sol_dir_required == "y":
        base_content.append("COPY solution/ /grader/solution/")

    # Add final common parts
    base_content.extend(
        [
            "COPY entry.py /grader/entry.py",
            "COPY grader.py /grader/grader.py",
            "",
            "RUN chmod a+rwx /grader/",
            "",
            "WORKDIR /grader/",
            "",
            'ENTRYPOINT ["python", "entry.py"]',
        ]
    )

    return "\n".join(base_content)


def load_templates() -> dict[str, str]:
    specialization = input("Name of the specialization: ")
    course = input("Number of the course: ")
    module = input("Number of the module: ")

    unit_test_filename = input("Filename for unit tests (leave empty for unittests): ")
    unit_test_filename = unit_test_filename if unit_test_filename else "unittests"
    version = input("Version of the grader (leave empty for version 1): ")
    version = version if version else "1"
    data_dir_required = input("Do you require a data dir? y/n (leave empty for n): ")
    data_dir_required = data_dir_required if data_dir_required else "n"

    if data_dir_required not in ["y", "n"]:
        print("invalid option selected")
        sys.exit(1)

    sol_dir_required = input(
        "Do you require a solution file? y/n (leave empty for n): "
    )
    sol_dir_required = sol_dir_required if sol_dir_required else "n"
    if sol_dir_required not in ["y", "n"]:
        print("invalid option selected")
        sys.exit(1)

    non_notebook_grading = input(
        "Will you grade a file different from a notebook? y/n (leave empty for n): ",
    )
    non_notebook_grading = non_notebook_grading if non_notebook_grading else "n"
    if non_notebook_grading not in ["y", "n"]:
        print("invalid option selected")
        sys.exit(1)

    extra_file_name = ""
    if non_notebook_grading == "y":
        extra_file_name = input(
            "Name of the extra file to grade: ",
        )

    dockerfile = generate_dockerfile(
        data_dir_required=data_dir_required,
        sol_dir_required=sol_dir_required,
    )

    conf = f"""
    ASSIGNMENT_NAME=C{course}M{module}_Assignment
    UNIT_TESTS_NAME={unit_test_filename}
    IMAGE_NAME={specialization}c{course}m{module}-grader
    GRADER_VERSION={version}
    TAG_ID=V$(GRADER_VERSION)
    SUB_DIR=mount
    MEMORY_LIMIT=4096
    """

    assignment_name = f"C{course}M{module}_Assignment.ipynb"

    copy_assignment_to_submission_sh = generate_copy_assignment_script(
        extra_file_required=non_notebook_grading,
        assignment_name=assignment_name,
        extra_file_name=extra_file_name,
    )

    makefile = """
	.PHONY: sync learner build debug-unsafe debug-safe grade versioning tag undeletable uneditable init upgrade coursera zip

	include .conf

	PARTIDS = 123 456
	OS := $(shell uname)

	sync:
		cp mount/submission.ipynb ../$(ASSIGNMENT_NAME)_Solution.ipynb
		cp learner/$(ASSIGNMENT_NAME).ipynb ../$(ASSIGNMENT_NAME).ipynb
		cp mount/$(UNIT_TESTS_NAME).py ../$(UNIT_TESTS_NAME).py

	learner:
		dlai_grader --learner --output_notebook=./learner/$(ASSIGNMENT_NAME).ipynb
		rsync -a --exclude="submission.ipynb" --exclude="__pycache__" --exclude=".mypy_cache" ./mount/ ./learner/

	build:
		docker build -t $(IMAGE_NAME):$(TAG_ID) .

	debug-unsafe:
		docker run -it --rm --mount type=bind,source=$(PWD)/mount,target=/shared/submission --mount type=bind,source=$(PWD),target=/grader/ --env-file $(PWD)/.env --entrypoint ash $(IMAGE_NAME):$(TAG_ID)

	debug-safe:
		docker run -it --rm --mount type=bind,source=$(PWD)/mount,target=/shared/submission --env-file $(PWD)/.env --entrypoint ash $(IMAGE_NAME):$(TAG_ID)

	grade:
		docker run -it --rm --mount type=bind,source=$(PWD)/mount,target=/shared/submission --env-file $(PWD)/.env --entrypoint ash $(IMAGE_NAME):$(TAG_ID) -c 'for partId in $(PARTIDS); do export partId=$$partId; echo "Processing part $$partId"; python entry.py; done'

	versioning:
		dlai_grader --versioning

	tag:
		dlai_grader --tag

	undeletable:
		dlai_grader --undeletable

	uneditable:
		dlai_grader --uneditable

	init:
		dlai_grader --versioning
		dlai_grader --tag
		dlai_grader --undeletable
		dlai_grader --uneditable

	upgrade:
		dlai_grader --upgrade

	coursera:
		dlai_grader --grade --partids="$(PARTIDS)" --docker=$(IMAGE_NAME):$(TAG_ID) --memory=$(MEMORY_LIMIT) --submission=$(SUB_DIR)

	zip:
		zip -r $(IMAGE_NAME)$(TAG_ID).zip .

	"""

    grader_py = """
    from types import ModuleType, FunctionType
    from dlai_grader.grading import test_case, object_to_grade
    from dlai_grader.types import grading_function, grading_wrapper, learner_submission


    def part_1(
        learner_mod: learner_submission,
        solution_mod: ModuleType | None = None,
    ) -> grading_function:
        @object_to_grade(learner_mod, "learner_func")
        def g(learner_func: FunctionType) -> list[test_case]:

            cases: list[test_case] = []

            t = test_case()
            if not isinstance(learner_func, FunctionType):
                t.fail()
                t.msg = "learner_func has incorrect type"
                t.want = FunctionType
                t.got = type(learner_func)
                return [t]

            return cases

        return g


    def handle_part_id(part_id: str) -> grading_wrapper:
        grader_dict: dict[str, grading_wrapper] = {
            "": part_1,
        }
        return grader_dict[part_id]
    """

    entry_py = generate_entry_py(
        non_notebook_grading=non_notebook_grading,
        extra_file_name=extra_file_name,
    )

    template_dict = {
        "dockerfile": dedent(dockerfile),
        "makefile": dedent(makefile[1:]),
        "conf": dedent(conf[1:]),
        "grader_py": dedent(grader_py[1:]),
        "entry_py": dedent(entry_py),
        "copy_assignment_to_submission_sh": dedent(copy_assignment_to_submission_sh),
    }

    return template_dict
