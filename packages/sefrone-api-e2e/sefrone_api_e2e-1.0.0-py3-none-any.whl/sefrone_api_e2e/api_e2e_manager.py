import yaml
import requests
import re
import os
import datetime

class ApiE2ETestsManager:
    @staticmethod
    def run_all_tests(folder_path, is_verbose=False):
        print("\nRunning API E2E tests...")
        for filename in os.listdir(folder_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_path = os.path.join(folder_path, filename)
                print(f"\n--- Running scenario: {filename} ---")
                ApiE2ETestsManager.run_yaml_test(file_path, is_verbose)
        print("\nAPI E2E tests completed.")

    @staticmethod
    def load_yaml(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def check_type(value, expected_type):
        """Check if value matches expected type keyword."""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "datetime": str  # basic check; could extend with parsing
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
        """Recursively validate structure & type expectations."""
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
        elif isinstance(expected, str):  # type keyword
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
            for root_key in context:
                if expr.startswith(root_key + "."):
                    val = resolve_path(expr, context)
                    if isinstance(val, str):
                        return repr(val) if add_quotes else str(val) # adds quotes safely
                    elif val is True:
                        return "True"
                    elif val is False:
                        return "False"
                    elif val is None:
                        return "None"
                    else:
                        return str(val)
            raise KeyError(f"Unknown variable: {expr}")

        return re.sub(r"\{\{\s*([^}]+?)\s*\}\}", replacer, template_str)

    @staticmethod
    def substitute_stored(endpoint, stored):
        """Substitute {$stored.key} placeholders."""
        def repl(match):
            key = match.group(1)
            return str(stored.get(key, f"<MISSING:{key}>"))
        return re.sub(r"\{\$stored\.([a-zA-Z0-9_]+)\}", repl, endpoint)

    @staticmethod
    def run_yaml_test(path, is_verbose=False):
        spec = ApiE2ETestsManager.load_yaml(path)
        base_url = spec.get("base_url", "")
        steps = spec.get("steps", [])
        stored = {}

        print(f"Running test: {spec['name']}")
        print("=" * 60)

        for step in steps:
            print(f"Step: {step['name']}")
            url = base_url + ApiE2ETestsManager.substitute_stored(step['endpoint'], stored)
            method = step['method'].upper()
            body = step.get("body")
            expect = step.get("expect", {})

            # Make HTTP request
            resp = requests.request(method, url, json=body)
            print(f" → {method} {url} -> {resp.status_code}")

            # Validate status code
            expected_status = expect.get("status")
            if expected_status and resp.status_code != expected_status:
                if is_verbose:
                    print(f"Response body: {resp.text}")
                raise AssertionError(f"Expected {expected_status}, got {resp.status_code}")

            # Parse response JSON
            try:
                resp_json = resp.json()
            except Exception:
                raise AssertionError("Response is not valid JSON")

            # Validate body structure
            if "body" in expect:
                if is_verbose:
                    print(f"Response body: {resp_json}")
                ApiE2ETestsManager.validate_structure(resp_json, expect["body"])

            # Save variables
            if "save" in step:
                for key, path_expr in step["save"].items():
                    rendered = ApiE2ETestsManager.render_template(path_expr, {"body": resp_json, "stored": stored})
                    stored[key] = rendered
                    print(f"   Saved: {key} = {rendered}")

            # Assertions
            if "assertions" in step:
                for expr in step["assertions"]:
                    rendered = ApiE2ETestsManager.render_template(expr, {"body": resp_json, "stored": stored}, add_quotes=True)
                    try:
                        if not eval(rendered):
                            raise AssertionError(f"Assertion failed: {expr}, rendered as '{rendered}'")
                    except Exception as e:
                        raise AssertionError(f"Assertion error in '{expr}', rendered as '{rendered}': {e}")

            print(" ✅ Step passed.\n")

        print("=" * 60)
        print("🎉 All steps passed successfully!")
