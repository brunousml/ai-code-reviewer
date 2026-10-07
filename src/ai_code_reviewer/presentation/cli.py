import argparse
import logging
import os
import sys
import threading
import time
from typing import Optional
from urllib.parse import quote, unquote

from src.ai_code_reviewer.application.use_cases.review_mr import ReviewMRUseCase
from src.ai_code_reviewer.application.use_cases.get_pipelines import GetPipelinesUseCase
from src.ai_code_reviewer.application.use_cases.get_dora_metrics import GetDoraMetricsUseCase
from src.ai_code_reviewer.application.use_cases.get_merged_mrs import GetMergedMRsUseCase
from src.ai_code_reviewer.application.use_cases.get_project_labels import GetProjectLabelsUseCase
from src.ai_code_reviewer.application.utils import get_project_path_and_mr_iid_from_url
from src.ai_code_reviewer.presentation.formatters import format_as_table, format_as_json, format_as_csv
from src.ai_code_reviewer.domain.ports.llm_service import LLMService

logger = logging.getLogger(__name__)

def braille_animation():
    animation_chars = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    while True:
        for char in animation_chars:
            yield char

def run_with_animation(target_func, message):
    result_container = {}
    exception_container = {}

    def target_wrapper():
        try:
            result_container['result'] = target_func()
        except Exception as e:
            logger.error("Exception in background thread", exc_info=True)
            exception_container['exception'] = e

    thread = threading.Thread(target=target_wrapper)
    thread.start()
    spinner = braille_animation()
    sys.stdout.write(f"{message}  ")
    while thread.is_alive():
        sys.stdout.write(f"\b{next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.08)
    thread.join()
    if 'exception' in exception_container:
        sys.stdout.write("\b✗\n")
        sys.stdout.flush()
        raise exception_container['exception']
    sys.stdout.write("\b✓\n")
    sys.stdout.flush()
    return result_container.get('result')

class CLI:
    def __init__(self, review_mr_use_case: ReviewMRUseCase, get_pipelines_use_case: GetPipelinesUseCase, get_dora_metrics_use_case: GetDoraMetricsUseCase, get_merged_mrs_use_case: GetMergedMRsUseCase, get_project_labels_use_case: GetProjectLabelsUseCase, gemini_service: LLMService, openai_service: Optional[LLMService]):
        self.review_mr_use_case = review_mr_use_case
        self.get_pipelines_use_case = get_pipelines_use_case
        self.get_dora_metrics_use_case = get_dora_metrics_use_case
        self.get_merged_mrs_use_case = get_merged_mrs_use_case
        self.get_project_labels_use_case = get_project_labels_use_case
        self.gemini_service = gemini_service
        self.openai_service = openai_service
        self.parser = argparse.ArgumentParser(description="AI Code Reviewer CLI")
        self.setup_parsers()

    def setup_parsers(self):
        subparsers = self.parser.add_subparsers(dest="command")

        # Review MR command
        review_parser = subparsers.add_parser("review-mr", help="Review a Merge Request")
        review_parser.add_argument("--mr-url", help="The full URL of the Merge Request")
        review_parser.add_argument("--mr-iid", type=int, help="The IID of the Merge Request (requires GITLAB_PROJECT_PATH)")
        review_parser.add_argument("--llm", choices=["gemini", "openai"], help="The LLM to use for the review (gemini or openai)", default='gemini')
        review_parser.add_argument("--publish", action="store_true", help="Publish the review as a comment on the MR", default="")

        # Get Pipelines command
        pipelines_parser = subparsers.add_parser("get-pipelines", help="Get recent pipelines")
        pipelines_parser.add_argument("--project-path", help="The project path (e.g., group/project). Overrides GITLAB_PROJECT_PATH.")
        pipelines_parser.add_argument("--days", type=int, help="Number of days to filter pipelines (optional)")

        # DORA Metrics command
        dora_parser = subparsers.add_parser("dora-metrics", help="Calculate DORA metrics")
        dora_parser.add_argument("--metric", choices=["deployment-frequency", "change-failure-rate"], help="The DORA metric to calculate")
        dora_parser.add_argument("--project-path", help="The project path (e.g., group/project). Overrides GITLAB_PROJECT_PATH.")
        dora_parser.add_argument("--start-date", help="Start date for analysis (YYYY-MM-DD)")
        dora_parser.add_argument("--end-date", help="End date for analysis (YYYY-MM-DD)")
        dora_parser.add_argument("--output-format", default="table", choices=["table", "json", "csv"], help="Output format")

        # Get Merged MRs command
        merged_mrs_parser = subparsers.add_parser("get-merged-mrs", help="Get merged merge requests")
        merged_mrs_parser.add_argument("--project-path", help="The project path (e.g., group/project). Overrides GITLAB_PROJECT_PATH.")
        merged_mrs_parser.add_argument("--days", type=int, help="Number of days to look back for merged MRs")
        merged_mrs_parser.add_argument("--label", help="Filter MRs by a specific label (optional)")
        merged_mrs_parser.add_argument("--output-format", default="table", choices=["table", "json", "csv"], help="Output format")

    def run(self):
        if len(sys.argv) <= 1:
            self.interactive_menu()
            return

        args = self.parser.parse_args()
        if args.command == "review-mr":
            self.run_review_mr(args)
        elif args.command == "get-pipelines":
            self.run_get_pipelines(args)
        elif args.command == "dora-metrics":
            self.run_dora_metrics(args)
        elif args.command == "get-merged-mrs":
            self.run_get_merged_mrs(args)
        else:
            self.parser.print_help(sys.stderr)

    def interactive_menu(self):
        print("\nSelect an action:")
        print("1. Review a Merge Request")
        print("2. Get Recent Pipelines")
        print("3. Get DORA Metrics")
        print("4. Get Merged Merge Requests")
        action = input("Enter the number of the action: ")

        args = argparse.Namespace()
        if action == "1":
            self.run_review_mr(args)
        elif action == "2":
            self.run_get_pipelines(args)
        elif action == "3":
            self.run_dora_metrics(args)
        elif action == "4":
            self.run_get_merged_mrs(args)
        else:
            print("Invalid action.", file=sys.stderr)

    def run_review_mr(self, args):
        is_interactive = not any(getattr(args, arg, None) for arg in ['mr_url', 'mr_iid', 'llm', 'publish'])

        # 1. Get MR Details
        mr_url = getattr(args, 'mr_url', None)
        mr_iid = getattr(args, 'mr_iid', None)
        project_path = os.getenv("GITLAB_PROJECT_PATH")

        if not mr_url and not mr_iid:
            mr_url = input("Please enter the Merge Request URL: ")

        if mr_url:
            project_path, mr_iid = get_project_path_and_mr_iid_from_url(mr_url)
            if not project_path or not mr_iid:
                print("Could not parse project path or MR IID from the provided URL.", file=sys.stderr)
                return
        elif mr_iid:
            if not project_path:
                project_path = input("Please enter the project path (e.g., group/subgroup/project) for the MR IID: ")
            if not project_path:
                print("Project path is required when providing MR IID.", file=sys.stderr)
                return
        else:
            # This case is for when the script is run interactively from the main menu
            if is_interactive:
                pass # Handled by the input prompt above
            else:
                print("Merge Request URL or IID is required.", file=sys.stderr)
                return

        # 2. Select LLM Service
        llm_service = None
        llm_choice = getattr(args, 'llm', None)

        if llm_choice == 'openai':
            if not self.openai_service:
                print("OpenAI service is not available. Please check your OPENAI_API_KEY.", file=sys.stderr)
                return
            llm_service = self.openai_service
        elif llm_choice == 'gemini':
            llm_service = self.gemini_service
        else:
            if is_interactive and self.openai_service:
                print("\nSelect the LLM for the review:")
                print("1. Gemini")
                print("2. OpenAI")
                choice = input("Enter the number of the LLM [default: 1]: ")
                if choice == '2':
                    llm_service = self.openai_service
                else:
                    if choice not in ["", "1"]:
                        print("Invalid selection. Defaulting to Gemini.", file=sys.stderr)
                    llm_service = self.gemini_service
            else:
                llm_service = self.gemini_service

        # 3. Execute Review
        print(f"Reviewing MR: {project_path}!{mr_iid} using {type(llm_service).__name__}")
        review_result = run_with_animation(
            lambda: self.review_mr_use_case.execute(
                project_path=project_path,
                mr_iid=mr_iid,
                llm_service=llm_service
            ),
            f"Generating review for MR !{mr_iid}"
        )
        print("\nReview Result:")
        review_text = review_result['review']
        parsed_comments = review_result.get('parsed_comments', [])

        # Mostra preview com separação visual dos comentários
        if len(parsed_comments) > 1:
            print(f"\n📝 O review será dividido em {len(parsed_comments)} comentários ao publicar:\n")
            for i, comment in enumerate(parsed_comments, 1):
                print(f"━━━ Comentário {i}/{len(parsed_comments)} ━━━")
                # Mostra preview truncado de cada comentário
                preview = comment.content[:300] + "..." if len(comment.content) > 300 else comment.content
                print(preview)
                print()
        else:
            # Se houver apenas 1 comentário, mostra o review completo
            print(review_result.get('full_review', review_text))

        # O arquivo local sempre contém o review completo e unificado
        print(f"\n📁 Review completo salvo em: {review_result['review_file_path']}")

        # 4. Publish Review
        publish = getattr(args, 'publish', False)
        if not publish and is_interactive:
            publish_choice = input("\nDo you want to post this review as a comment on the Merge Request? (y/n): ")
            if publish_choice.lower() == 'y':
                publish = True

        if publish:
            num_comments = len(review_result.get('parsed_comments', []))
            run_with_animation(
                lambda: self.review_mr_use_case.publish_review(
                    project_path=project_path,
                    merge_request_iid=mr_iid,
                    review=review_text  # Passa o review cru (sem prefixo/sufixo)
                ),
                f"Posting {num_comments} comment(s) to MR !{mr_iid} (with auto-retry)"
            )
            print(f"✅ {num_comments} comentário(s) postado(s) com sucesso.")

    def run_get_pipelines(self, args):
        project_path = getattr(args, 'project_path', None) or os.getenv("GITLAB_PROJECT_PATH")
        if not project_path:
            project_path = input("Please enter the project path (e.g., group/subgroup/project): ")
        elif not getattr(args, 'project_path', None):
            print(f"Using project path from GITLAB_PROJECT_PATH: {project_path}")

        if not project_path:
            print("Project path is required.", file=sys.stderr)
            return

        days = getattr(args, 'days', None)
        if days is None:
            days_input = input("Number of days to filter pipelines (optional, press Enter to skip): ")
            if days_input:
                try:
                    days = int(days_input)
                except ValueError:
                    print("Invalid number of days. Skipping filter.", file=sys.stderr)
                    days = None

        print(f"Getting pipelines for project: {project_path}")
        pipelines = run_with_animation(
            lambda: self.get_pipelines_use_case.execute(
                project_path=project_path,
                days=days
            ),
            f"Fetching pipelines for {project_path}"
        )
        if pipelines:
            print("\nRecent Pipelines:")
            print(format_as_table(pipelines))
        else:
            print("No pipelines found.")

    def run_dora_metrics(self, args):
        is_interactive = not any(getattr(args, arg, None) for arg in ['metric', 'project_path', 'start_date', 'end_date'])
        metric = getattr(args, 'metric', None)
        if not metric:
            print("\nSelect a DORA metric to calculate:")
            print("1. Deployment Frequency")
            print("2. Change Failure Rate")
            metric_choice = input("Enter the number of the metric: ")
            if metric_choice == "1":
                metric = "deployment-frequency"
            elif metric_choice == "2":
                metric = "change-failure-rate"
            else:
                print("Invalid selection.", file=sys.stderr)
                return

        project_path = getattr(args, 'project_path', None) or os.getenv("GITLAB_PROJECT_PATH")
        if not project_path:
            project_path = input("Please enter the project path (e.g., group/subgroup/project): ")
        elif not getattr(args, 'project_path', None):
            print(f"Using project path from GITLAB_PROJECT_PATH: {project_path}")

        start_date = getattr(args, 'start_date', None)
        if not start_date:
            start_date = input("Please enter the start date (YYYY-MM-DD): ")

        end_date = getattr(args, 'end_date', None)
        if not end_date:
            end_date = input("Please enter the end date (YYYY-MM-DD): ")

        output_format = getattr(args, 'output_format', 'table')
        if is_interactive:
            output_format_input = input("Please enter the output format (table, json, csv) [default: table]: ")
            if output_format_input:
                output_format = output_format_input

        metrics = run_with_animation(
            lambda: self.get_dora_metrics_use_case.execute(
                metric=metric,
                project_path=project_path,
                start_date=start_date,
                end_date=end_date,
            ),
            f"Calculating DORA metric: {metric}"
        )

        if output_format == "table":
            print(format_as_table(metrics))
        elif output_format == "json":
            print(format_as_json(metrics))
        elif output_format == "csv":
            print(format_as_csv(metrics))

    def run_get_merged_mrs(self, args):
        is_interactive = not any(getattr(args, arg, None) for arg in ['project_path', 'days', 'label'])
        project_path = getattr(args, 'project_path', None) or os.getenv("GITLAB_PROJECT_PATH")
        if not project_path:
            project_path = input("Please enter the project path (e.g., group/subgroup/project): ")
        elif not getattr(args, 'project_path', None):
            print(f"Using project path from GITLAB_PROJECT_PATH: {project_path}")

        if not project_path:
            print("Project path is required.", file=sys.stderr)
            return

        days = getattr(args, 'days', None)
        if days is None:
            while days is None:
                days_input = input("Number of days to look back for merged MRs: ")
                try:
                    days = int(days_input)
                except ValueError:
                    print("Invalid number of days. Please enter an integer.", file=sys.stderr)

        label = getattr(args, 'label', None)
        if is_interactive and label is None:
            if input("Do you want to filter by a label? (y/n): ").lower() == 'y':
                labels = run_with_animation(
                    lambda: self.get_project_labels_use_case.execute(project_path=project_path),
                    f"Fetching labels for {project_path}"
                )
                if not labels:
                    print("No labels found for this project.")
                else:
                    print("Available labels:")
                    for i, l in enumerate(labels, 1):
                        print(f"{i}. {l}")
                    while label is None:
                        label_choice = input(f"Select a label (1-{len(labels)}): ")
                        try:
                            label_index = int(label_choice) - 1
                            if 0 <= label_index < len(labels):
                                label = labels[label_index]
                            else:
                                print("Invalid selection.", file=sys.stderr)
                        except ValueError:
                            print("Invalid input.", file=sys.stderr)

        output_format = getattr(args, 'output_format', 'table')
        if is_interactive:
            output_format_input = input("Please enter the output format (table, json, csv) [default: table]: ")
            if output_format_input:
                output_format = output_format_input

        mrs = run_with_animation(
            lambda: self.get_merged_mrs_use_case.execute(
                project_path=project_path,
                days=days,
                label=label
            ),
            f"Fetching merged MRs for {project_path}"
        )

        if mrs:
            print("\nMerged Merge Requests:")
            if output_format == "table":
                print(format_as_table(mrs))
            elif output_format == "json":
                print(format_as_json(mrs))
            elif output_format == "csv":
                print(format_as_csv(mrs))
        else:
            print("No merged MRs found.")
