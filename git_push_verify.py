import subprocess
import sys

def run_command(command):
    # Ejecuta comandos en la terminal y devuelve el resultado
    return subprocess.run(command, shell=True, capture_output=True, text=True)

print("🔍 1. Checking main.py for syntax errors...")
# Compila el archivo en segundo plano para ver si tiene errores de sintaxis
check_syntax = run_command("py -m py_compile main.py")

if check_syntax.returncode != 0:
    print("\n❌ SYNTAX ERROR DETECTED! Fix it before pushing:")
    print("-" * 50)
    print(check_syntax.stderr.strip())
    print("-" * 50)
    sys.exit(1)

print("✅ Syntax is perfect! No errors found.")

# Pedir mensaje de commit al usuario
commit_msg = input("\n✍️ Enter commit message (or press Enter for 'code update'): ").strip()
if not commit_msg:
    commit_msg = "code update"

print("\n📦 2. Staging files (git add .)...")
run_command("git add .")

print(f"💾 3. Committing changes: '{commit_msg}'...")
commit_run = run_command(f'git commit -m "{commit_msg}"')
print(commit_run.stdout.strip())

print("\n📤 4. Pushing to Git...")
push_run = run_command("git push")

if push_run.returncode == 0:
    print("\n🎉 SUCCESS! Your code has been verified and pushed successfully.")
    if push_run.stderr: # Git a veces manda información de subida por stderr
        print(push_run.stderr.strip())
else:
    print("\n❌ PUSH FAILED! Check the Git output below:")
    print("-" * 50)
    print(push_run.stderr.strip())
    print("-" * 50)