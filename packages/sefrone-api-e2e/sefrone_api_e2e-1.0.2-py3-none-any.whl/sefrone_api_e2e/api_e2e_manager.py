import yaml
import requests
import re
import os
import datetime
import time
from pathlib import Path
from typing import Any, Dict, List

class ApiE2ETestsManager:
    # Precompiled patterns and defaults
    VAR_PATTERN = re.compile(r"\$var\(([A-Za-z0-9_]+)\)")
    STORED_PATTERN = re.compile(r"\{\$stored\.([a-zA-Z0-9_.]+)\}")
    TEMPLATE_PATTERN = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")
    DEFAULT_TIMEOUT = 10  # seconds for HTTP requests

    # Mutable state (reset at run start)
    global_store: Dict[str, Any] = {}
    scenario_results: List[Dict[str, Any]] = []  # holds timing + status info for all scenarios

    @staticmethod
    def run_all_tests(folder_path, env_file_path, is_verbose=False):
        print("\nRunning API E2E tests...")

        # Reset shared state to avoid leakage between runs
        ApiE2ETestsManager.global_store = {}
        ApiE2ETestsManager.scenario_results = []

        p = Path(folder_path)
        scenario_files = sorted([f.name for f in p.iterdir() if f.is_file() and f.suffix == ".yaml"]) 
        total_start = time.time()

        for filename in scenario_files:
            yaml_file_path = os.path.join(folder_path, filename)
            scenario_name = os.path.splitext(filename)[0]

            try:
                print(f"\n--- Running scenario: {filename} ---")
                spec = ApiE2ETestsManager.parse_and_load_yaml(yaml_file_path, env_file_path)
                start_time = time.time()
                step_metrics = ApiE2ETestsManager.run_yaml_test(spec, scenario_name, is_verbose)
                elapsed = time.time() - start_time

                if all(step["result"] == "PASS" for step in step_metrics):
                    ApiE2ETestsManager.scenario_results.append({
                        "scenario": scenario_name,
                        "status": "[PASS]",
                        "steps": step_metrics,
                        "total_time": elapsed
                    })
                else:
                    ApiE2ETestsManager.scenario_results.append({
                        "scenario": scenario_name,
                        "status": "[FAIL]",
                        "steps": step_metrics,
                        "total_time": elapsed
                    })
                    # mark remaining scenarios as skipped
                    remaining = scenario_files[scenario_files.index(filename)+1:]
                    for skipped_file in remaining:
                        skipped_name = os.path.splitext(skipped_file)[0]
                        ApiE2ETestsManager.scenario_results.append({
                            "scenario": skipped_name,
                            "status": "[SKIP]",
                            "steps": [],
                            "total_time": 0
                        })
                    break

            except AssertionError:
                # mark the failed one
                failed_elapsed = time.time() - start_time if 'start_time' in locals() else 0
                ApiE2ETestsManager.scenario_results.append({
                    "scenario": scenario_name,
                    "status": "[FAIL]",
                    "steps": step_metrics if 'step_metrics' in locals() else [],
                    "total_time": failed_elapsed
                })
                # mark remaining scenarios as skipped
                remaining = scenario_files[scenario_files.index(filename)+1:]
                for skipped_file in remaining:
                    skipped_name = os.path.splitext(skipped_file)[0]
                    ApiE2ETestsManager.scenario_results.append({
                        "scenario": skipped_name,
                        "status": "[SKIP]",
                        "steps": [],
                        "total_time": 0
                    })
                break  # stop all further execution

        total_elapsed = time.time() - total_start
        print("\nAPI E2E tests completed.")
        ApiE2ETestsManager.print_summary(total_elapsed)

    @staticmethod
    def read_env_value_from_file(env_file_path, env_var):
        try:
            with open(env_file_path, 'r', encoding='utf-8') as file:
                for raw in file:
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if line.startswith(f'{env_var}='):
                        return line[len(f'{env_var}='):].strip()
        except FileNotFoundError:
            print(f"[WARN] Environment file not found: {env_file_path}")
            return ""
        print(f"[WARN] Environment variable '{env_var}' not found in {env_file_path}.")
        return ""

    @staticmethod
    def parse_and_load_yaml(yaml_file_path, env_file_path):
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        def replacer(match):
            key = match.group(1)
            return ApiE2ETestsManager.read_env_value_from_file(env_file_path, key)

        resolved_content = ApiE2ETestsManager.VAR_PATTERN.sub(replacer, content)
        return yaml.safe_load(resolved_content)

    @staticmethod
    def check_type(value, expected_type):
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "datetime": str
        }
        if expected_type not in type_map:
            raise ValueError(f"Unknown type in YAML: {expected_type}")
        if expected_type == "datetime":
            try:
                datetime.datetime.fromisoformat(value)
                return True
            except Exception:
                try:
                    if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$", value):
                        datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                    return True
                except Exception:
                    return False
        return isinstance(value, type_map[expected_type])

    @staticmethod
    def validate_structure(data, expected):
        if isinstance(expected, dict):
            if not isinstance(data, dict):
                raise AssertionError(f"Expected dict but got {type(data)}")
            for k, v in expected.items():
                if k not in data:
                    raise AssertionError(f"Missing key: {k} (Data keys: {list(data.keys())})")
                ApiE2ETestsManager.validate_structure(data[k], v)
        elif isinstance(expected, list):
            if not isinstance(data, list):
                raise AssertionError(f"Expected list but got {type(data)}")
            if len(expected) > 0:
                for item in data:
                    ApiE2ETestsManager.validate_structure(item, expected[0])
        elif isinstance(expected, str):
            if not ApiE2ETestsManager.check_type(data, expected):
                raise AssertionError(f"Expected {expected}, got {data} ({type(data)})")
        else:
            raise ValueError(f"Invalid expected type: {expected}")

    @staticmethod
    def render_template(template_str, context, add_quotes=False):
        def resolve_path(expr, ctx):
            parts = expr.split(".")
            val = ctx
            for p in parts:
                if isinstance(val, dict) and p in val:
                    val = val[p]
                else:
                    raise KeyError(f"Cannot resolve '{expr}' in context: {p} not found")
            return val

        def replacer(match):
            expr = match.group(1).strip()
            val = resolve_path(expr, context)
            if isinstance(val, str):
                return repr(val) if add_quotes else str(val)
            elif val is True:
                return "True"
            elif val is False:
                return "False"
            elif val is None:
                return "None"
            else:
                return str(val)

        return ApiE2ETestsManager.TEMPLATE_PATTERN.sub(replacer, template_str)

    @staticmethod
    def substitute_stored(expr, scenario_name):
        def repl(match):
            key = match.group(1).strip()
            parts = key.split(".")
            if len(parts) == 1:
                subkey = parts[0]
                return str(ApiE2ETestsManager.global_store.get(f"{scenario_name}.{subkey}", f"<MISSING:{subkey}>"))
            elif len(parts) == 2:
                scen, subkey = parts
                return str(ApiE2ETestsManager.global_store.get(f"{scen}.{subkey}", f"<MISSING:{key}>"))
            else:
                raise ValueError(f"Invalid stored key reference: {key} (Too many dots)")

        return ApiE2ETestsManager.STORED_PATTERN.sub(repl, expr)

    @staticmethod
    def store_value(key, value, scenario_name):
        namespaced_key = f"{scenario_name}.{key}"
        ApiE2ETestsManager.global_store[namespaced_key] = value
        print(f"   Saved: {namespaced_key} = {value}")

    @staticmethod
    def try_eval(rendered, expr):
    # Basic supported operators
        operators = [">=", "<=", ">", "<", "==", "!=", "in", "not in", "include"]

        matched_op = None
        for op in operators:
            if f" {op} " in rendered:
                matched_op = op
                left, right = [part.strip() for part in rendered.split(f" {op} ", 1)]
                break

        if not matched_op:
            raise AssertionError(f"Unsupported assertion format: '{expr}'")

        # Try to evaluate left and right sides
        def try_eval_part(value):
            # Try to interpret as int/float/bool/None/string
            if re.match(r"^-?\d+\.\d+$", value):
                return float(value)
            elif re.match(r"^-?\d+$", value):
                return int(value)
            elif value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            elif value.lower() == "none":
                return None
            elif value.startswith('"') and value.endswith('"'):
                return value.strip('"')
            elif value.startswith("'") and value.endswith("'"):
                return value.strip("'")
            else:
                return value  # treat as literal string

        left_val = try_eval_part(left)
        right_val = try_eval_part(right)

        # Comparison logic
        result = False
        if matched_op == "==":
            result = left_val == right_val
        elif matched_op == "!=":
            result = left_val != right_val
        elif matched_op == ">":
            result = left_val > right_val
        elif matched_op == "<":
            result = left_val < right_val
        elif matched_op == ">=":
            result = left_val >= right_val
        elif matched_op == "<=":
            result = left_val <= right_val
        elif matched_op == "in":
            result = left_val in right_val
        elif matched_op == "not in":
            result = left_val not in right_val
        elif matched_op == "include":
            result = right_val in left_val

        if not result:
            raise AssertionError(
                f"Assertion failed: {expr}  =>  evaluated as {left_val} {matched_op} {right_val}"
            )
        return True

    @staticmethod
    def run_yaml_test(spec, scenario_name, is_verbose=False):
        base_url = spec.get("base_url", "")
        steps = spec.get("steps", [])
        step_metrics = []

        print(f"Running test: {spec.get('name', scenario_name)}")
        print("=" * 60)
        # use a session for connection pooling and to set a default timeout
        session = requests.Session()
        for step in steps:
            try:
                step_start = time.time()
                print(f"Step: {step['name']}")
                url = base_url + ApiE2ETestsManager.substitute_stored(step['endpoint'], scenario_name)
                method = step['method'].upper()

                request_headers = {}
                if "request_headers" in step:
                    for header in step["request_headers"]:
                        for header_key, header_value in header.items():
                            if isinstance(header_value, str):
                                header_value = ApiE2ETestsManager.substitute_stored(header_value, scenario_name)
                            request_headers[header_key] = header_value

                body = step.get("body")
                expect = step.get("expect", {})

                resp = session.request(method, url, json=body, headers=request_headers, timeout=ApiE2ETestsManager.DEFAULT_TIMEOUT)
                print(f" -> {method} {url} -> {resp.status_code}")

                expected_status = expect.get("status")
                if expected_status and resp.status_code != expected_status:
                    raise AssertionError(f"Expected {expected_status}, got {resp.status_code}")

                try:
                    resp_json = resp.json()
                except Exception:
                    raise AssertionError("Response is not valid JSON")

                if "body" in expect:
                    if is_verbose:
                        print(f"Response body: {resp_json}")
                    ApiE2ETestsManager.validate_structure(resp_json, expect["body"])

                if "save" in step:
                    for key, path_expr in step["save"].items():
                        rendered = ApiE2ETestsManager.render_template(path_expr, {"body": resp_json})
                        ApiE2ETestsManager.store_value(key, rendered, scenario_name)

                if "assertions" in step:
                    for expr in step["assertions"]:
                        rendered = ApiE2ETestsManager.render_template(expr, {"body": resp_json}, add_quotes=True)
                        ApiE2ETestsManager.try_eval(rendered, expr)

                elapsed = time.time() - step_start
                step_metrics.append({"name": step["name"], "time": elapsed, "result": "PASS"})
                print(f"[OK  ] Step passed in {elapsed:.2f}s\n")
            except Exception as e:
                failed_elapsed = time.time() - step_start
                step_metrics.append({"name": step["name"], "time": failed_elapsed, "result": "FAIL", "error": str(e)})
                print(f"[FAIL] Step failed in {failed_elapsed:.2f}s error: {str(e)}\n")
                break
        print("=" * 60)
        return step_metrics

    @staticmethod
    def print_summary(total_time):
        print("\n[SUMMARY] TEST RESULTS")
        print("=" * 80)

        headers = ["Scenario", "Status", "Time (s)", "Steps"]
        col_widths = [30, 7, 8, 50]

        header_line = f"{headers[0]:<{col_widths[0]}} | {headers[1]:<{col_widths[1]}} | {headers[2]:<{col_widths[2]}} | {headers[3]}"
        print(header_line)
        print("-" * len(header_line))

        for result in ApiE2ETestsManager.scenario_results:
            print(f"{result['scenario']:<{col_widths[0]}} | "
                  f"{result['status']:<{col_widths[1]}} | "
                  f"{result['total_time']:<{col_widths[2]}.2f} | ")

            if result["steps"]:
                for step in result["steps"]:
                    parsed = f"[{step['result']}] {step['name']} ({step['time']:.2f}s)"
                    print(f"{'':<{col_widths[0]}} | "
                          f"{'':<{col_widths[1]}} | "
                          f"{'':<{col_widths[2]}} | "
                          f"{parsed:<{col_widths[3]}}")
                    if step['result'] == "FAIL" and 'error' in step:
                        print(f"{'':<{col_widths[0]}} | "
                              f"{'':<{col_widths[1]}} | "
                              f"{'':<{col_widths[2]}} | "
                              f"===> {step['error']}")
            else:
                print(f"{'':<{col_widths[0]}} | "
                      f"{'':<{col_widths[1]}} | "
                      f"{'':<{col_widths[2]}} | "
                      f"{'(no steps run)':<{col_widths[3]}}")

        print("=" * 80)
        print(f"Total Execution Time: {total_time:.2f}s\n")
