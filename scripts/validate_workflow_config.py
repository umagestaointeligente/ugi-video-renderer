"""Read-only syntax and structure checks; never execute workflow commands."""
import ast
from pathlib import Path
import re
import subprocess
import sys
import yaml


class WorkflowLoader(yaml.SafeLoader):
    pass


# GitHub interprets `on` as a key, not YAML 1.1's boolean True.
WorkflowLoader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in values
          if tag != 'tag:yaml.org,2002:bool']
    for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'duplicate YAML key: {key!r}, line {key_node.start_mark.line + 1}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


WorkflowLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def validate_text(text, name='<workflow>'):
    doc = yaml.load(text, Loader=WorkflowLoader)
    if not isinstance(doc, dict) or not doc.get('on') or not doc.get('jobs'):
        raise ValueError(f'{name}: missing triggers or jobs')
    jobs = doc['jobs']
    if not isinstance(jobs, dict):
        raise ValueError(f'{name}: jobs must be a mapping')
    counts = {'yaml': 1, 'bash': 0, 'python': 0}
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            raise ValueError(f'{name}: invalid job {job_id}')
        needs = job.get('needs', [])
        needs = [needs] if isinstance(needs, str) else needs
        if any(need not in jobs or need == job_id for need in needs):
            raise ValueError(f'{name}: invalid needs for {job_id}')
        if 'uses' in job:
            continue
        if not job.get('runs-on') or not job.get('steps'):
            raise ValueError(f'{name}: missing runner or steps for {job_id}')
        for step in job['steps']:
            if not isinstance(step, dict) or ('uses' in step) == ('run' in step):
                raise ValueError(f'{name}: step requires exactly one of uses/run')
            script = step.get('run')
            if script is None:
                continue
            shell = step.get('shell', job.get('defaults', {}).get('run', {}).get(
                'shell', doc.get('defaults', {}).get('run', {}).get('shell', 'bash')))
            # Substitute GitHub expressions only for parsing, never evaluate them.
            script = re.sub(r'\$\{\{.*?\}\}', 'EXPRESSION', script, flags=re.S)
            if shell.startswith('python'):
                ast.parse(script, filename=name)
                counts['python'] += 1
            elif shell.startswith(('bash', 'sh')):
                check = subprocess.run(['bash', '-n'], input=script, text=True,
                                       capture_output=True)
                if check.returncode:
                    raise ValueError(f'{name}/{job_id}: {check.stderr.strip()}')
                counts['bash'] += 1
                for match in re.finditer(
                    r'(?m)^\s*python(?:3)?\s+-\s*<<\s*[\'\"]?(\w+)[\'\"]?\s*\n', script
                ):
                    remainder = script[match.end():]
                    end = re.search(r'(?m)^' + re.escape(match[1]) + r'\s*$', remainder)
                    if end is None:
                        raise ValueError(f'{name}: unclosed Python heredoc')
                    ast.parse(remainder[:end.start()], filename=name)
                    counts['python'] += 1
    return counts


def main(root):
    counts = {'yaml': 0, 'bash': 0, 'python': 0}
    errors = []
    paths = sorted((root / '.github/workflows').glob('*.y*ml'))
    if not paths:
        errors.append('No workflow files found')
    for path in paths:
        try:
            result = validate_text(path.read_text(), str(path))
            for key in counts:
                counts[key] += result[key]
        except (ValueError, TypeError, SyntaxError, yaml.YAMLError) as error:
            errors.append(f'{path}: {error}')
    for error in errors:
        print(error, file=sys.stderr)
    print(f'WORKFLOW_CONFIG={"FAIL" if errors else "PASS"} {counts}')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]))
