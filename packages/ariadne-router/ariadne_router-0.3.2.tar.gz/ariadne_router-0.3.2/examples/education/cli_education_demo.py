"""
Ariadne CLI Educational Features Demo

This script demonstrates the educational features of the Ariadne CLI.
"""

import os
import subprocess
from pathlib import Path


def run_cli_command(cmd):
    """Run a CLI command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent  # Run from project root
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def demo_cli_education_features():
    """Demonstrate the CLI education features."""
    print("=" * 70)
    print("ARIADNE CLI EDUCATIONAL FEATURES DEMO")
    print("=" * 70)

    print("\n1. SHOWING CLI HELP")
    print("-" * 20)
    stdout, stderr, code = run_cli_command("python -m ariadne.cli.main --help")
    print(stdout)

    print("\n2. SHOWING EDUCATION COMMAND HELP")
    print("-" * 35)
    stdout, stderr, code = run_cli_command("python -m ariadne.cli.main education --help")
    print(stdout)

    print("\n3. SHOWING LEARNING COMMAND HELP")
    print("-" * 33)
    stdout, stderr, code = run_cli_command("python -m ariadne.cli.main learning --help")
    print(stdout)

    print("\n4. LISTING AVAILABLE LEARNING RESOURCES")
    print("-" * 40)
    stdout, stderr, code = run_cli_command("python -m ariadne.cli.main learning list --category all")
    print(stdout)

    print("\n5. EDUCATION DEMO - BELL STATE")
    print("-" * 30)
    # Create a simple circuit file for the demo
    circuit_content = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""
    circuit_file = "demo_bell.qasm"
    with open(circuit_file, 'w') as f:
        f.write(circuit_content)

    try:
        stdout, stderr, code = run_cli_command("python -m ariadne.cli.main education demo bell --qubits 2")
        print(stdout)
        if stderr:
            print(f"ERROR: {stderr}")
    finally:
        # Clean up
        if os.path.exists(circuit_file):
            os.remove(circuit_file)

    print("\n6. EDUCATION QUIZ DEMO")
    print("-" * 22)
    stdout, stderr, code = run_cli_command("python -m ariadne.cli.main education quiz gates")
    print(stdout)

    print("\n7. SCALABILITY BENCHMARK")
    print("-" * 24)
    stdout, stderr, code = run_cli_command("python -m ariadne.cli.main benchmark-suite --algorithms bell,ghz --backends auto,qiskit --shots 100")
    print(stdout)

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("The Ariadne CLI provides extensive educational and benchmarking features!")
    print("=" * 70)

if __name__ == "__main__":
    demo_cli_education_features()
